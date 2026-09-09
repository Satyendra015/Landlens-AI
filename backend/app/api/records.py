import io
import csv
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.app.database.session import get_db
from backend.app.models.models import (
    LandRecord,
    AIResult,
    Verification,
    AuditLog,
    User,
    VerificationStatus,
)
from backend.app.schemas.schemas import (
    LandRecordOut,
    LandRecordUpdate,
    RecordVerifyRequest,
    RecordRejectRequest,
)
from backend.app.services.auth import get_current_user
from backend.app.validators.validation_engine import LandRecordValidator
from backend.app.ai.duplicate_detector import DuplicateDetector

router = APIRouter(prefix="/api/records", tags=["Land Records"])


@router.get("", response_model=List[LandRecordOut])
def list_records(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = Query(None),
    village: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves paginated land records with optional status/village filters."""
    query = db.query(LandRecord)
    if status:
        query = query.filter(LandRecord.verification_status == status)
    if village:
        query = query.filter(LandRecord.village.ilike(f"%{village}%"))
    if district:
        query = query.filter(LandRecord.district.ilike(f"%{district}%"))

    return query.order_by(LandRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/search", response_model=List[LandRecordOut])
def search_records(
    q: str = Query("", description="Universal search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search land records across Owner Name, Khasra No, Khata No, Survey No,
    Village, Tehsil, District, and Registration Number.
    """
    if not q or not q.strip():
        return db.query(LandRecord).order_by(LandRecord.created_at.desc()).limit(50).all()

    term = f"%{q.strip()}%"
    results = (
        db.query(LandRecord)
        .filter(
            or_(
                LandRecord.owner_name.ilike(term),
                LandRecord.khasra_number.ilike(term),
                LandRecord.khata_number.ilike(term),
                LandRecord.survey_number.ilike(term),
                LandRecord.plot_number.ilike(term),
                LandRecord.village.ilike(term),
                LandRecord.tehsil.ilike(term),
                LandRecord.district.ilike(term),
                LandRecord.registration_number.ilike(term),
                LandRecord.mutation_number.ilike(term),
            )
        )
        .order_by(LandRecord.created_at.desc())
        .limit(100)
        .all()
    )
    return results


@router.get("/export")
def export_records(
    format: str = Query("csv", pattern="^(csv|json)$"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exports digitized land records to CSV or JSON format."""
    query = db.query(LandRecord)
    if status:
        query = query.filter(LandRecord.verification_status == status)
    records = query.all()

    if format == "json":
        data = [
            {
                "id": r.id,
                "owner_name": r.owner_name,
                "father_name": r.father_name,
                "khasra_number": r.khasra_number,
                "khata_number": r.khata_number,
                "village": r.village,
                "tehsil": r.tehsil,
                "district": r.district,
                "land_area": r.land_area,
                "verification_status": r.verification_status,
                "overall_confidence": r.overall_confidence,
            }
            for r in records
        ]
        return data

    # Default CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Record ID",
            "Owner Name",
            "Father Name",
            "Khasra No",
            "Khata No",
            "Village",
            "Tehsil",
            "District",
            "Land Area",
            "Status",
            "Confidence",
        ]
    )
    for r in records:
        writer.writerow(
            [
                r.id,
                r.owner_name or "",
                r.father_name or "",
                r.khasra_number or "",
                r.khata_number or "",
                r.village or "",
                r.tehsil or "",
                r.district or "",
                r.land_area or "",
                r.verification_status,
                f"{r.overall_confidence * 100:.1f}%",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=land_records_export.csv"},
    )


@router.get("/{record_id}")
def get_record_detail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves full record details including AI results, duplicate info, and verification logs."""
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")

    ai_results = (
        db.query(AIResult)
        .filter(AIResult.record_id == record_id)
        .all()
    )
    verifications = (
        db.query(Verification)
        .filter(Verification.record_id == record_id)
        .order_by(Verification.timestamp.desc())
        .all()
    )
    audit_logs = (
        db.query(AuditLog)
        .filter(AuditLog.record_id == record_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    return {
        "record": record,
        "ai_results": ai_results,
        "verifications": verifications,
        "audit_logs": audit_logs,
        "document": record.document,
    }


@router.put("/{record_id}", response_model=LandRecordOut)
def update_record_fields(
    record_id: int,
    payload: LandRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates fields of a land record with audit trail tracking."""
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")

    update_data = payload.dict(exclude_unset=True)
    edit_reason = update_data.pop("edit_reason", "Officer updated fields")

    changes = []
    for field, new_val in update_data.items():
        old_val = getattr(record, field)
        if str(old_val) != str(new_val):
            changes.append(f"{field}: '{old_val}' -> '{new_val}'")
            setattr(record, field, new_val)

            # Record in Verifications table
            ver = Verification(
                record_id=record.id,
                verified_by=current_user.id,
                field_name=field,
                original_value=str(old_val),
                corrected_value=str(new_val),
                verification_status="edited",
                reason=edit_reason,
            )
            db.add(ver)

    if changes:
        # Re-validate after edits
        current_dict = {
            "owner_name": record.owner_name,
            "khasra_number": record.khasra_number,
            "khata_number": record.khata_number,
            "village": record.village,
            "tehsil": record.tehsil,
            "district": record.district,
            "land_area": record.land_area,
            "date": record.date,
        }
        val_issues = LandRecordValidator.validate_record(current_dict, db=db, exclude_record_id=record.id)
        record.validation_flags = json.dumps([v.to_dict() for v in val_issues])

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            record_id=record.id,
            action="RECORD_EDIT",
            old_value=None,
            new_value="; ".join(changes) + f" | Reason: {edit_reason}",
        )
        db.add(audit)
        db.commit()
        db.refresh(record)

        # Human-in-the-Loop Real-Time Model Adaptation on Corrections
        try:
            from backend.app.ai.online_learner import OnlineContinuousLearner
            learner = OnlineContinuousLearner()
            learner.adapt_on_record(record.id, db=db)
        except Exception:
            pass

    return record


@router.post("/{record_id}/verify", response_model=LandRecordOut)
def verify_record(
    record_id: int,
    payload: RecordVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Human-in-the-Loop Verification:
    Approves the land record, applying any individual field corrections.
    """
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")

    # Apply individual field corrections if present
    for corr in payload.corrections:
        old_val = getattr(record, corr.field_name, None)
        setattr(record, corr.field_name, corr.corrected_value)

        ver = Verification(
            record_id=record.id,
            verified_by=current_user.id,
            field_name=corr.field_name,
            original_value=str(old_val),
            corrected_value=str(corr.corrected_value),
            verification_status="corrected",
            reason=corr.reason,
        )
        db.add(ver)

    # Update overall status
    record.verification_status = VerificationStatus.VERIFIED.value

    # Master verification record
    master_ver = Verification(
        record_id=record.id,
        verified_by=current_user.id,
        field_name="ALL",
        original_value=None,
        corrected_value=None,
        verification_status=VerificationStatus.VERIFIED.value,
        reason=payload.officer_notes or "Record approved by officer",
    )
    db.add(master_ver)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        record_id=record.id,
        action="RECORD_VERIFY_APPROVE",
        new_value=f"Approved by {current_user.name} ({current_user.role}). Note: {payload.officer_notes}",
    )
    db.add(audit)
    db.commit()
    db.refresh(record)

    # Human-in-the-Loop Real-Time Model Adaptation
    try:
        from backend.app.ai.online_learner import OnlineContinuousLearner
        learner = OnlineContinuousLearner()
        learner.adapt_on_record(record.id, db=db)
    except Exception:
        pass

    return record


@router.post("/{record_id}/reject", response_model=LandRecordOut)
def reject_record(
    record_id: int,
    payload: RecordRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rejects the land record with a mandatory reason."""
    record = db.query(LandRecord).filter(LandRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Land record not found")

    record.verification_status = VerificationStatus.REJECTED.value

    ver = Verification(
        record_id=record.id,
        verified_by=current_user.id,
        field_name="ALL",
        verification_status=VerificationStatus.REJECTED.value,
        reason=payload.reason,
    )
    db.add(ver)

    audit = AuditLog(
        user_id=current_user.id,
        record_id=record.id,
        action="RECORD_REJECT",
        new_value=f"Rejected by {current_user.name}. Reason: {payload.reason}",
    )
    db.add(audit)
    db.commit()
    db.refresh(record)

    return record
