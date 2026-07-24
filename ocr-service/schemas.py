"""
Pydantic schemas for the OCR Extraction Service.
Includes Phase 2 single-field contract and Phase 3 expanded contract models.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Phase2SingleFieldContract(BaseModel):
    """
    Phase 2 Single-Image OCR Extraction Contract.
    Guarantees key presence with empty string default if omitted.
    """
    complaint: str = ""
    diagnosis: str = ""
    investigation: str = ""
    medicine: str = ""
    dose: str = ""
    frequency: str = ""
    duration: str = ""

class MedicationItem(BaseModel):
    name: str = ""
    dose: str = ""
    frequency: str = ""
    duration: str = ""

class Phase3ExpandedContract(BaseModel):
    """
    Phase 3 Expanded Medical Prescription Schema.
    """
    patient_name: str = ""
    age: str = ""
    complaint: str = ""
    complaints: List[str] = Field(default_factory=list)
    diagnosis: str = ""
    investigation: str = ""
    medications: List[MedicationItem] = Field(default_factory=list)
    notes: str = ""
    raw_text: Optional[str] = ""
