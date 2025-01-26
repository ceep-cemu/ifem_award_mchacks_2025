from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import json
import os
import random
from .patients import generate_mock_patient, Patient
from .enums import InvestigationState


app = Flask(__name__)
CORS(app)

class RedisEDState:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis = redis.from_url(redis_url)
    
    def get_patients(self):
        patients = {}
        for key in self.redis.scan_iter("patient:*"):
            patient_data = json.loads(self.redis.get(key))
            patients[patient_data['id']] = Patient(**patient_data)
        return patients
    
    def add_patient(self, patient):
        key = f"patient:{patient.id}"
        self.redis.set(key, json.dumps(patient.serialize()))
        self.redis.expire(key, 24*60*60)  # Expire after 24 hours

    def remove_patient(self, patient_id):
        self.redis.delete(f"patient:{patient_id}")

ed_state = RedisEDState()

def progress_patient_phase(patient):
    current_phase = patient.status['current_phase']
    
    phase_transitions = {
        'registered': 'triaged',
        'triaged': 'investigations_pending',
        'investigations_pending': 'treatment',
        'treatment': random.choices(['admitted', 'discharged'], weights=[15, 85])[0]
    }
    
    if current_phase in phase_transitions:
        new_phase = phase_transitions[current_phase]
        patient.status['current_phase'] = new_phase
        
        # Update investigations if moving to investigations phase
        if new_phase == 'investigations_pending':
            patient.status['investigations'] = {
                'labs': InvestigationState.ORDERED.value,
                'imaging': InvestigationState.ORDERED.value
            }
        # Progress investigations if in that phase
        elif current_phase == 'investigations_pending':
            if 'investigations' in patient.status:
                for test_type in ['labs', 'imaging']:
                    current_state = patient.status['investigations'][test_type]
                    if current_state == 'ordered':
                        patient.status['investigations'][test_type] = 'pending'
                    elif current_state == 'pending':
                        patient.status['investigations'][test_type] = 'reported'

def update_patients():
    patients = ed_state.get_patients()
    current_time = datetime.now()
    ed_state.redis.set('last_update', current_time.isoformat())
    
    removed_count = 0
    patient_list = list(patients.values())
    
    # Sort by triage category and arrival time
    patient_list.sort(key=lambda p: (p.triage_category, p.arrival_time))
    
    # Track removed patients
    removed_patients = []
    
    # First pass: identify removals and update phases
    for patient in patient_list:
        if patient.status['current_phase'] in ['discharged', 'admitted']:
            ed_state.remove_patient(patient.id)
            removed_patients.append(patient)
            removed_count += 1
            continue
            
        progress_patient_phase(patient)
    
    # Second pass: update queue positions
    if removed_patients:
        global_pos = 1
        category_positions = {i: 1 for i in range(1, 6)}
        
        for patient in patient_list:
            if patient not in removed_patients:
                patient.queue_position = {
                    'global': global_pos,
                    'category': category_positions[patient.triage_category]
                }
                global_pos += 1
                category_positions[patient.triage_category] += 1
                ed_state.add_patient(patient)
    
        # Add replacement patients at the back of the queue
        for _ in range(removed_count):
            new_patient = generate_mock_patient()
            new_patient.queue_position = {
                'global': global_pos,
                'category': category_positions[new_patient.triage_category]
            }
            global_pos += 1
            category_positions[new_patient.triage_category] += 1
            ed_state.add_patient(new_patient)
    

    if len(patients) < 30 and random.random() < 0.3:
        new_patient = generate_mock_patient()
        new_patient.queue_position = {
            'global': global_pos,
            'category': category_positions[new_patient.triage_category]
        }
        ed_state.add_patient(new_patient)
    

def generate_mock_patients(count=25):
    return [generate_mock_patient() for _ in range(count)]

@app.route('/api/v1/queue')
def get_queue():

    last_update = ed_state.redis.get('last_update')
    current_time = datetime.now()
    
    if last_update:
        last_update = datetime.fromisoformat(last_update.decode('utf-8'))
        minutes_passed = int((current_time - last_update).total_seconds() / 60)
        updates_needed = minutes_passed // 15
        
        for _ in range(1):
            update_patients()

        if updates_needed > 0:
            ed_state.redis.set('last_update', current_time.isoformat())
    else:
        ed_state.redis.set('last_update', current_time.isoformat())

    # Check if we have any patients
    patients = list(ed_state.get_patients().values())
    
    # If no patients, generate mock data
    if not patients:
        patients = generate_mock_patients()
        
        # Sort by triage category first, then arrival time
        patients.sort(key=lambda p: (p.triage_category, p.arrival_time))
        
        # Update queue positions
        global_pos = 1
        category_positions = {i: 1 for i in range(1, 6)}  # Counter for each triage category
        
        for patient in patients:
            patient.queue_position = {
                'global': global_pos,
                'category': category_positions[patient.triage_category]
            }
            global_pos += 1
            category_positions[patient.triage_category] += 1
            
            # Store in Redis
            ed_state.add_patient(patient)
    
    # Sort based on request parameter
    sort = request.args.get('sort', 'arrival_time')
    patients.sort(key=lambda p: getattr(p, sort))
    
    return jsonify({
        'waitingCount': len(patients),
        'longestWaitTime': max((p.time_elapsed for p in patients), default=0),
        'patients': [p.serialize() for p in patients]
    })

@app.route('/api/v1/stats/current')
def get_stats():
    mock_patients = generate_mock_patients()
    category_breakdown = {i: 0 for i in range(1, 6)}
    wait_times = {i: [] for i in range(1, 6)}
    
    for patient in mock_patients:
        category = patient.triage_category
        category_breakdown[category] += 1
        wait_times[category].append(patient.time_elapsed)
    
    average_wait_times = {
        category: round(sum(times) / len(times)) if times else 0
        for category, times in wait_times.items()
    }
    
    return jsonify({
        'categoryBreakdown': category_breakdown,
        'averageWaitTimes': average_wait_times
    })

@app.route('/api/v1/patient/<id>')
def get_patient(id):
    patients = ed_state.get_patients()
    if id not in patients:
        return jsonify({'error': 'Patient not found'}), 404
    return jsonify(patients[id].serialize())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)