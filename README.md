# IFEM Emergency Department API Documentation

This API provides access to Emergency Department patient queue and status information. It returns mock data suitable for developing ED patient experience applications. 

> [!NOTE]
> This API is provided to help you get started and provide some examples of what data is available. **There is no requirement that you use it!** If you do choose to use it, you can either access the deployed version or clone this repo and use the data generation functions directly. A javascript version of `generate_mock_patient` is included for your convenience.



## Base URL
`/api/v1`

## Endpoints

### Get Queue Information
`GET /queue`

Returns information about current ED queue status including waiting patients and wait times.

#### Query Parameters
- `sort` (optional): Field to sort patients by
  - Default: `arrival_time`

#### Response
```json
{
  "waitingCount": 25,
  "longestWaitTime": 240,
  "patients": [
    {
      "id": "anon_1234",
      "arrival_time": "2024-12-30T10:00:00",
      "triage_category": 3,
      "queue_position": {
        "global": 5,
        "category": 2
      },
      "status": {
        "current_phase": "triaged",
        "investigations": {
          "labs": "pending",
          "imaging": "ordered"
        }
      },
      "time_elapsed": 45
    }
  ]
}
```

### Get Current Statistics
`GET /stats/current`

Returns aggregate statistics about current ED state.

#### Response
```json
{
  "categoryBreakdown": {
    "1": 1,
    "2": 4,
    "3": 11,
    "4": 7,
    "5": 2
  },
  "averageWaitTimes": {
    "1": 2,
    "2": 20,
    "3": 75,
    "4": 150,
    "5": 240
  }
}
```

### Get Patient Details
`GET /patient/<id>`

Returns detailed information for a specific patient.

#### Parameters
- `id`: Patient identifier (anonymized)

#### Response
Same format as individual patient objects in queue response.

## Data Models

### Triage Categories
1. RESUSCITATION (Blue) - Severely ill
2. EMERGENT (Red) - Requires rapid intervention
3. URGENT (Yellow) - Requires urgent care
4. LESS_URGENT (Green) - Requires less-urgent care
5. NON_URGENT (White) - Requires non-urgent care

### Patient Phases
- `registered` - Initial registration complete
- `triaged` - Triage assessment complete
- `investigations_pending` - Tests/imaging ordered
- `treatment` - Receiving treatment
- `admitted` - Being admitted to hospital
- `discharged` - Discharge process complete

### Investigation States
- `ordered` - Test/imaging ordered
- `pending` - In progress
- `reported` - Results available

## Notes
- All patient IDs are anonymized
- Times are provided in ISO 8601 format
- Wait times and elapsed times are in minutes
- Queue positions start at 1
- Mock data is randomly generated but follows realistic distributions for triage categories and wait times