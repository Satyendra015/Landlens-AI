import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    REVIEWER = "reviewer"


class ProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class VerificationStatus(str, enum.Enum):
    REQUIRES_VERIFICATION = "requires_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    VALIDATION_ERROR = "validation_error"


class ConfidenceLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.OFFICER.value, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")
    verifications = relationship("Verification", back_populates="verifier")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    preprocessed_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    processing_status = Column(String(50), default=ProcessingStatus.UPLOADED.value)

    uploader = relationship("User", back_populates="documents")
    land_record = relationship("LandRecord", back_populates="document", uselist=False)


class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # Core 16 Fields for Indian Land Records
    owner_name = Column(String(200), nullable=True, index=True)
    father_name = Column(String(200), nullable=True)
    khasra_number = Column(String(100), nullable=True, index=True)
    khata_number = Column(String(100), nullable=True, index=True)
    survey_number = Column(String(100), nullable=True, index=True)
    plot_number = Column(String(100), nullable=True)
    village = Column(String(150), nullable=True, index=True)
    tehsil = Column(String(150), nullable=True, index=True)
    district = Column(String(150), nullable=True, index=True)
    state = Column(String(100), default="Madhya Pradesh", nullable=True)
    land_area = Column(String(100), nullable=True)
    land_type = Column(String(100), nullable=True)
    registration_number = Column(String(100), nullable=True, index=True)
    mutation_number = Column(String(100), nullable=True)
    document_number = Column(String(100), nullable=True)
    date = Column(String(50), nullable=True)

    # Verification and Quality status
    verification_status = Column(
        String(50), default=VerificationStatus.REQUIRES_VERIFICATION.value, index=True
    )
    overall_confidence = Column(Float, default=0.0)
    validation_flags = Column(Text, nullable=True)  # JSON serialized list of warnings/errors
    duplicate_info = Column(Text, nullable=True)  # JSON serialized duplicate match details
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="land_record")
    ai_results = relationship("AIResult", back_populates="record", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="record", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="record", cascade="all, delete-orphan")


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    extracted_value = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    confidence_level = Column(String(20), default=ConfidenceLevel.LOW.value)  # HIGH, MEDIUM, LOW
    raw_ocr_confidence = Column(Float, default=0.0)
    validation_status = Column(String(50), default="valid")  # valid, warning, error
    flags = Column(Text, nullable=True)

    record = relationship("LandRecord", back_populates="ai_results")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    field_name = Column(String(100), nullable=True)  # Specific field or 'ALL'
    original_value = Column(Text, nullable=True)
    corrected_value = Column(Text, nullable=True)
    verification_status = Column(String(50), default=VerificationStatus.VERIFIED.value)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    record = relationship("LandRecord", back_populates="verifications")
    verifier = relationship("User", back_populates="verifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    record_id = Column(Integer, ForeignKey("land_records.id"), nullable=True)
    action = Column(String(100), nullable=False)  # CREATE, PROCESS, VERIFY, EDIT, REJECT, EXPORT
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
    record = relationship("LandRecord", back_populates="audit_logs")
