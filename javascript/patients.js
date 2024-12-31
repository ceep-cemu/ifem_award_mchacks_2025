export const PatientPhase = {
  REGISTERED: "registered",
  TRIAGED: "triaged",
  INVESTIGATIONS_PENDING: "investigations_pending",
  TREATMENT: "treatment",
  ADMITTED: "admitted",
  DISCHARGED: "discharged"
};

export const InvestigationState = {
  ORDERED: "ordered",
  PENDING: "pending",
  REPORTED: "reported"
};

export const TriageCategory = {
  RESUSCITATION: 1,
  EMERGENT: 2,
  URGENT: 3,
  LESS_URGENT: 4,
  NON_URGENT: 5
};

const generateMockPatientId = () => 
  `anon_${Math.floor(Math.random() * 9000) + 1000}`;

const generateMockTriageCategory = () => {
  const roll = Math.random() * 100;
  if (roll < 1) return TriageCategory.RESUSCITATION;
  if (roll < 16) return TriageCategory.EMERGENT;
  if (roll < 61) return TriageCategory.URGENT;
  if (roll < 91) return TriageCategory.LESS_URGENT;
  return TriageCategory.NON_URGENT;
};

const generateMockWaitTime = (triageCategory) => {
  const waitRanges = {
    [TriageCategory.RESUSCITATION]: [0, 5],
    [TriageCategory.EMERGENT]: [15, 30],
    [TriageCategory.URGENT]: [30, 120],
    [TriageCategory.LESS_URGENT]: [60, 240],
    [TriageCategory.NON_URGENT]: [120, 360]
  };
  const [min, max] = waitRanges[triageCategory];
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const generateMockPatientStatus = () => {
  const phases = Object.values(PatientPhase);
  const phase = phases[Math.floor(Math.random() * phases.length)];
  
  const status = { current_phase: phase };

  if (phase === PatientPhase.REGISTERED || phase === PatientPhase.TRIAGED) {
    return status;
  }

  if (phase === PatientPhase.INVESTIGATIONS_PENDING) {
    const states = [InvestigationState.ORDERED, InvestigationState.PENDING];
    status.investigations = {
      labs: states[Math.floor(Math.random() * states.length)],
      imaging: states[Math.floor(Math.random() * states.length)]
    };
  } else {
    status.investigations = {
      labs: InvestigationState.REPORTED,
      imaging: InvestigationState.REPORTED
    };
  }

  return status;
};

const generateMockQueuePosition = () => ({
  global: Math.floor(Math.random() * 25) + 1,
  category: Math.floor(Math.random() * 5) + 1
});

export const generateMockPatient = (overrides = {}) => {
  const triageCategory = overrides.triageCategory || generateMockTriageCategory();
  const timeElapsed = overrides.timeElapsed || generateMockWaitTime(triageCategory);
  const arrivalTime = overrides.arrivalTime || new Date(Date.now() - timeElapsed * 60000);

  return {
    id: overrides.id || generateMockPatientId(),
    arrival_time: arrivalTime.toISOString(),
    triage_category: triageCategory,
    queue_position: overrides.queuePosition || generateMockQueuePosition(),
    status: overrides.status || generateMockPatientStatus(),
    time_elapsed: timeElapsed
  };
};