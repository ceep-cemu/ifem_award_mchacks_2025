from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from .enums import PatientPhase, InvestigationState, TriageCategory


@dataclass
class Patient:
    id: str
    arrival_time: datetime
    triage_category: str
    queue_position: dict
    status: dict
    time_elapsed: int

    def serialize(self):
        """Convert patient to JSON-serializable dict."""
        serialized = {**self.__dict__}
        if isinstance(self.arrival_time, datetime):
            serialized['arrival_time'] = self.arrival_time.isoformat()
        else:
            serialized['arrival_time'] = self.arrival_time
        serialized['triage_category'] = self.triage_category
        serialized['status']['current_phase'] = self.status['current_phase']
        
        if 'investigations' in self.status:
            serialized['status']['investigations'] = {
                'labs': self.status['investigations']['labs'],
                'imaging': self.status['investigations']['imaging']
            }
        
        return serialized


def generate_mock_patient_id():
    return f'anon_{random.randint(1000, 9999)}'

def generate_mock_triage_category():
    # Triage distributions are roughly:
    # CTAS 1: 1%
    # CTAS 2: 15%
    # CTAS 3: 45%
    # CTAS 4: 30%
    # CTAS 5: 9%
    roll = random.random() * 100
    
    if roll < 1:
        return TriageCategory.RESUSCITATION.value
    elif roll < 16:
        return TriageCategory.EMERGENT.value
    elif roll < 61:
        return TriageCategory.URGENT.value
    elif roll < 91:
        return TriageCategory.LESS_URGENT.value
    else:
        return TriageCategory.NON_URGENT.value

def generate_mock_wait_time(triage_category) -> int:
    # Average wait times by category (in minutes):
    # CTAS 1: 0-5 mins
    # CTAS 2: 15-30 mins
    # CTAS 3: 30-120 mins
    # CTAS 4: 60-240 mins
    # CTAS 5: 120-360 mins
    
    wait_ranges = {
        TriageCategory.RESUSCITATION.value: (0, 5),
        TriageCategory.EMERGENT.value: (15, 30),
        TriageCategory.URGENT.value: (30, 120),
        TriageCategory.LESS_URGENT.value: (60, 240),
        TriageCategory.NON_URGENT.value: (120, 360)
    }
    
    min_wait, max_wait = wait_ranges[triage_category]
    return random.randint(min_wait, max_wait)

def generate_mock_patient_status():
    phase = random.choice(list(PatientPhase))
    
    status = {'current_phase': phase.value}

    if phase in [PatientPhase.REGISTERED.value, PatientPhase.TRIAGED.value]:
        return status
        
    if phase == PatientPhase.INVESTIGATIONS_PENDING.value:
        status['investigations'] = {
            'labs': random.choice([InvestigationState.ORDERED.value, InvestigationState.PENDING.value]),
            'imaging': random.choice([InvestigationState.ORDERED.value, InvestigationState.PENDING.value])
        }
    else:  # TREATMENT, ADMITTED, DISCHARGED
        status['investigations'] = {
            'labs': InvestigationState.REPORTED.value,
            'imaging': InvestigationState.REPORTED.value
        }
    
    return status

def generate_mock_queue_position():
    category_position = random.randint(1, 5)
    global_position = random.randint(category_position, 25)
    return {
        'global': global_position,
        'category': category_position,
    }

def generate_mock_patient(**kwargs):
    """Generate a mock ED patient with somewhat realistic attributes.

    Args:
        **kwargs: Optional overrides for patient attributes
            id (str): Patient identifier
            triage_category (TriageCategory): CTAS level
            time_elapsed (int): Minutes since arrival
            arrival_time (datetime): When patient arrived
            status (dict): Current phase and investigation status
            queue_position (dict): Position in global and category queues
            existing_patients (list[Patient]): Other patients in ED, used for queue position

    Returns:
        Patient: Dataclass containing patient information with realistic:
            - Triage category distribution
            - Wait times based on triage level
            - Investigation status appropriate to treatment phase
    """
    triage_category = kwargs.get('triage_category', generate_mock_triage_category())
    time_elapsed = kwargs.get('time_elapsed', generate_mock_wait_time(triage_category))
    arrival_time = kwargs.get('arrival_time', datetime.now() - timedelta(minutes=time_elapsed))
    
    patient_data = {
        'id': kwargs.get('id', generate_mock_patient_id()),
        'arrival_time': arrival_time,
        'triage_category': triage_category,
        'queue_position': kwargs.get('queue_position', generate_mock_queue_position()),
        'status': kwargs.get('status', generate_mock_patient_status()),
        'time_elapsed': time_elapsed
    }
    
    return Patient(**patient_data)
