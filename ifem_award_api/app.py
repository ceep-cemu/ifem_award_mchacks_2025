from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from .patients import generate_mock_patient


app = Flask(__name__)
CORS(app)

def generate_mock_patients(count=25):
    return [generate_mock_patient() for _ in range(count)]

@app.route('/api/v1/queue')
def get_queue():
    sort = request.args.get('sort', 'arrival_time')
    mock_patients = generate_mock_patients()
    
    mock_patients.sort(key=lambda p: getattr(p, sort))
    
    return jsonify({
        'waitingCount': len(mock_patients),
        'longestWaitTime': max(p.time_elapsed for p in mock_patients),
        'patients': [p.serialize() for p in mock_patients]
    })

@app.route('/api/v1/stats/current')
def get_stats():
    mock_patients = generate_mock_patients()
    category_breakdown = {i: 0 for i in range(1, 6)}
    wait_times = {i: [] for i in range(1, 6)}
    
    for patient in mock_patients:
        category = patient.triage_category.value
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
    patient = generate_mock_patient(id=id)
    return jsonify(patient.serialize())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)