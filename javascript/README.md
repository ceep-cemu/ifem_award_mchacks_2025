# Javascript Mock Data Generation

This module provides functions to generate realistic mock ED patient data. It mirrors the functionality of the Python implementation used by the API.

## Usage

```javascript
import { generateMockPatient, TriageCategory, PatientPhase } from './mockPatient';

// Generate a random patient
const patient = generateMockPatient();

// Generate a patient with specific attributes
const customPatient = generateMockPatient({
  triageCategory: TriageCategory.URGENT,
  timeElapsed: 45,
  status: {
    current_phase: PatientPhase.INVESTIGATIONS_PENDING,
    investigations: {
      labs: "pending",
      imaging: "ordered"
    }
  }
});
```

The generated data follows realistic distributions for triage categories, wait times, and investigation states based on typical ED patterns.

## Notes
- Patient IDs are anonymized
- Times are in ISO 8601 format
- Wait times are in minutes
- Queue positions start at 1