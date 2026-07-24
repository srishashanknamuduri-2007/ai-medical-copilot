"""
Medical Prescription Field Parser.
Uses regex heuristics to extract clinical entities (Complaints, Diagnosis, Rx, Dosage, Frequency, Duration).
"""

import re
from typing import Dict, Any, List

def parse_medical_text(raw_text: str) -> Dict[str, Any]:
    """
    Parses raw OCR output into both Phase 2 single-field schema and Phase 3 expanded schema.
    """
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    complaint = ""
    diagnosis = ""
    investigation = ""
    medications: List[Dict[str, str]] = []
    notes = ""

    # Regex patterns for clinical keywords
    complaint_pattern = re.compile(r'(?:complaint|c/o|presents with|symptoms?):?\s*(.*)', re.IGNORECASE)
    diagnosis_pattern = re.compile(r'(?:diagnosis|dx|impression):?\s*(.*)', re.IGNORECASE)
    investigation_pattern = re.compile(r'(?:investigation|lab|test|x-ray|cbc):?\s*(.*)', re.IGNORECASE)
    
    # Medication dosage patterns: e.g. 500mg, 10 ml, 625 mg
    dose_pattern = re.compile(r'(\b\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|iu|puffs?)\b)', re.IGNORECASE)
    # Frequency pattern: e.g. 1-0-1, BD, TDS, OD, QID, SOS, twice daily
    freq_pattern = re.compile(r'(\b(?:1-0-1|1-1-1|1-0-0|0-0-1|bd|tds|od|qid|sos|twice daily|once daily|thrice daily)\b)', re.IGNORECASE)
    # Duration pattern: e.g. x 5 days, 5 days, 1 week, 10d
    dur_pattern = re.compile(r'(\b(?:x\s*\d+|\d+)\s*(?:days?|weeks?|months?|d|w)\b)', re.IGNORECASE)

    current_section = None

    for line in lines:
        # Check explicit section headers
        c_match = complaint_pattern.search(line)
        if c_match:
            complaint = c_match.group(1)
            current_section = 'complaint'
            continue

        d_match = diagnosis_pattern.search(line)
        if d_match:
            diagnosis = d_match.group(1)
            current_section = 'diagnosis'
            continue

        i_match = investigation_pattern.search(line)
        if i_match:
            investigation = i_match.group(1)
            current_section = 'investigation'
            continue

        # Check prescription Rx lines
        dose_match = dose_pattern.search(line)
        freq_match = freq_pattern.search(line)
        dur_match = dur_pattern.search(line)

        if dose_match or freq_match or line.startswith('Rx') or line.startswith('Tab') or line.startswith('Cap') or line.startswith('Syr'):
            # Extract medicine name by stripping matched dose/freq/dur
            med_name = line
            med_name = re.sub(r'^(?:Rx|Tab|Cap|Syr|\.|\:)\s*', '', med_name, flags=re.IGNORECASE)
            
            dose_val = dose_match.group(1) if dose_match else ""
            freq_val = freq_match.group(1) if freq_match else ""
            dur_val = dur_match.group(1) if dur_match else ""

            if dose_val:
                med_name = med_name.replace(dose_val, '')
            if freq_val:
                med_name = med_name.replace(freq_val, '')
            if dur_val:
                med_name = med_name.replace(dur_val, '')

            med_name = med_name.strip(' ,-:')

            if med_name:
                medications.append({
                    "name": med_name,
                    "dose": dose_val,
                    "frequency": freq_val,
                    "duration": dur_val
                })
            continue

        # Append unmapped lines to current section or notes
        if current_section == 'complaint' and not complaint:
            complaint = line
        elif current_section == 'diagnosis' and not diagnosis:
            diagnosis = line
        elif current_section == 'investigation' and not investigation:
            investigation = line
        else:
            notes += line + " "

    # Fill defaults if parsing was blank
    first_med = medications[0] if medications else {"name": "", "dose": "", "frequency": "", "duration": ""}

    return {
        # Phase 2 Contract Format
        "complaint": complaint.strip(),
        "diagnosis": diagnosis.strip(),
        "investigation": investigation.strip(),
        "medicine": first_med["name"],
        "dose": first_med["dose"],
        "frequency": first_med["frequency"],
        "duration": first_med["duration"],

        # Phase 3 Expanded Format
        "patient_name": "Eleanor Vance", # Default EMR scope context
        "age": "45 Y",
        "complaints": [complaint.strip()] if complaint.strip() else [],
        "medications": medications,
        "notes": notes.strip(),
        "raw_text": raw_text
    }
