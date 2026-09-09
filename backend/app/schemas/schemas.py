from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "officer"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# Document Schemas
class DocumentOut(BaseModel):
    id: int
    filename: str
    file_path: str
    preprocessed_path: Optional[str] = None
    file_type: str
    file_size: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime
    processing_status: str

    class Config:
        from_attributes = True


# AI Extraction & Confidence
class FieldScore(BaseModel):
    value: Optional[str] = ""
    confidence: float = 0.0  # 0.0 to 1.0
    level: str = "LOW"  # HIGH, MEDIUM, LOW
    status: str = "valid"  # valid, warning, error
    flag: Optional[str] = None
    raw_ocr: Optional[str] = None
    source_text: Optional[str] = None


class ValidationFlag(BaseModel):
    field: str
    type: str  # missing_field, invalid_format, unusual_range, conflict, anomaly
    message: str
    severity: str = "warning"  # warning, error, info


class DuplicateMatch(BaseModel):
    is_duplicate: bool = False
    similarity_score: float = 0.0
    matched_record_id: Optional[int] = None
    matched_khasra: Optional[str] = None
    matched_owner: Optional[str] = None
    matched_village: Optional[str] = None
    reasons: List[str] = []


class AIProcessingResponse(BaseModel):
    document_id: int
    record_id: int
    status: str
    overall_confidence: float
    fields: Dict[str, FieldScore]
    validation_flags: List[ValidationFlag]
    duplicate_detection: DuplicateMatch
    raw_text: Optional[str] = None
    raw_ocr_text: Optional[str] = None
    ocr_status: str = "SUCCESS"
    ocr_confidence: float = 0.0
    ocr_engine_used: str = ""
    ocr_time_ms: int = 0
    file_metadata: Optional[Dict[str, Any]] = None
    father_husband_name: Optional[str] = None
    land_area_unit: Optional[str] = None
    preprocessed_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    is_land_record: bool = True
    document_type: str = "land_record"
    classification_confidence: float = 1.0
    warning_message: Optional[str] = None
    classification_reasons: List[str] = []
    is_handwritten: bool = False


# Land Record Schemas
class LandRecordBase(BaseModel):
    owner_name: Optional[str] = None
    father_name: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    village: Optional[str] = None
    tehsil: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = "Madhya Pradesh"
    land_area: Optional[str] = None
    land_type: Optional[str] = None
    registration_number: Optional[str] = None
    mutation_number: Optional[str] = None
    document_number: Optional[str] = None
    date: Optional[str] = None


class LandRecordUpdate(BaseModel):
    owner_name: Optional[str] = None
    father_name: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    survey_number: Optional[str] = None
    plot_number: Optional[str] = None
    village: Optional[str] = None
    tehsil: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    land_area: Optional[str] = None
    land_type: Optional[str] = None
    registration_number: Optional[str] = None
    mutation_number: Optional[str] = None
    document_number: Optional[str] = None
    date: Optional[str] = None
    edit_reason: Optional[str] = "Manual correction during verification"


class LandRecordOut(LandRecordBase):
    id: int
    document_id: Optional[int] = None
    verification_status: str
    overall_confidence: float
    validation_flags: Optional[str] = None
    duplicate_info: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Verification Schemas
class FieldCorrection(BaseModel):
    field_name: str
    original_value: Optional[str] = None
    corrected_value: str
    reason: Optional[str] = "Field corrected by officer"


class RecordVerifyRequest(BaseModel):
    status: str = "verified"  # verified, rejected
    corrections: List[FieldCorrection] = []
    officer_notes: Optional[str] = "Approved after review"


class RecordRejectRequest(BaseModel):
    reason: str


# Audit Log Schemas
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    record_id: Optional[int] = None
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# Dashboard Statistics Schema
class DashboardStatsOut(BaseModel):
    total_documents: int
    processed_documents: int
    pending_verification: int
    verified_records: int
    rejected_records: int
    possible_duplicates: int
    validation_errors: int
    low_confidence_records: int
    average_confidence: float
    status_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# Real-Time Continuous Adaptation Schemas
class AdaptationRequest(BaseModel):
    text: str
    entities: Dict[str, str]
    doc_type: Optional[str] = "custom"
    doc_name: Optional[str] = None


class AdaptationResponse(BaseModel):
    success: bool
    message: str
    latency_ms: float
    adaptation_accuracy: float
    f1_score: float
    replay_buffer_size: int
    total_tokens_trained: int
    total_adapted_documents: int

