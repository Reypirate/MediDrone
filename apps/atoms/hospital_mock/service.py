HOSPITALS = [
    {"hospital_id": "HOSP-001", "name": "Central General Hospital", "lat": 1.3140, "lng": 103.8442},
    {"hospital_id": "HOSP-002", "name": "East Coast Medical Center", "lat": 1.3413, "lng": 103.9533},
    {"hospital_id": "HOSP-003", "name": "West Jurong Hospital", "lat": 1.3329, "lng": 103.7436},
    {"hospital_id": "HOSP-004", "name": "North Woodlands Hospital", "lat": 1.4382, "lng": 103.7891},
    {"hospital_id": "HOSP-005", "name": "Southern Heights Medical", "lat": 1.2819, "lng": 103.8239},
]


def get_all_hospitals():
    return HOSPITALS


def find_hospital(hospital_id: str):
    for h in HOSPITALS:
        if h["hospital_id"] == hospital_id:
            return h
    return None
