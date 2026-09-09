from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.session import get_db
from backend.app.models.models import (
    Document,
    LandRecord,
    AuditLog,
    VerificationStatus,
    User,
)
from backend.app.schemas.schemas import DashboardStatsOut
from backend.app.services.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/statistics", response_model=DashboardStatsOut)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Computes real-time statistics directly from the database for the LandLens AI Dashboard.
    Provides accurate metrics, status distributions, and recent audit activity.
    """
    total_docs = db.query(Document).count()
    processed_docs = (
        db.query(Document)
        .filter(Document.processing_status == "processed")
        .count()
    )

    total_records = db.query(LandRecord).count()
    pending_verif = (
        db.query(LandRecord)
        .filter(LandRecord.verification_status == VerificationStatus.REQUIRES_VERIFICATION.value)
        .count()
    )
    verified = (
        db.query(LandRecord)
        .filter(LandRecord.verification_status == VerificationStatus.VERIFIED.value)
        .count()
    )
    rejected = (
        db.query(LandRecord)
        .filter(LandRecord.verification_status == VerificationStatus.REJECTED.value)
        .count()
    )
    duplicates = (
        db.query(LandRecord)
        .filter(LandRecord.verification_status == VerificationStatus.POSSIBLE_DUPLICATE.value)
        .count()
    )
    validation_errors = (
        db.query(LandRecord)
        .filter(LandRecord.verification_status == VerificationStatus.VALIDATION_ERROR.value)
        .count()
    )
    low_confidence = (
        db.query(LandRecord)
        .filter(LandRecord.overall_confidence < 0.70, LandRecord.overall_confidence > 0.0)
        .count()
    )

    avg_conf_query = db.query(func.avg(LandRecord.overall_confidence)).scalar()
    avg_confidence = round(float(avg_conf_query or 0.0), 3)

    # Status distribution
    status_distribution = {
        "Verified": verified,
        "Requires Verification": pending_verif,
        "Possible Duplicate": duplicates,
        "Validation Error": validation_errors,
        "Rejected": rejected,
    }

    # Confidence distribution
    high_conf = db.query(LandRecord).filter(LandRecord.overall_confidence >= 0.90).count()
    med_conf = (
        db.query(LandRecord)
        .filter(LandRecord.overall_confidence >= 0.70, LandRecord.overall_confidence < 0.90)
        .count()
    )
    low_conf = (
        db.query(LandRecord)
        .filter(LandRecord.overall_confidence < 0.70, LandRecord.overall_confidence > 0.0)
        .count()
    )

    confidence_distribution = {
        "High (90-100%)": high_conf,
        "Medium (70-89%)": med_conf,
        "Low (<70%)": low_conf,
    }

    # Recent activity from audit logs
    recent_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(10)
        .all()
    )
    recent_activity = [
        {
            "id": log.id,
            "action": log.action,
            "user": log.user.name if log.user else "System",
            "details": log.new_value or log.old_value or "",
            "timestamp": log.timestamp.isoformat(),
        }
        for log in recent_logs
    ]

    return DashboardStatsOut(
        total_documents=total_docs,
        processed_documents=processed_docs,
        pending_verification=pending_verif,
        verified_records=verified,
        rejected_records=rejected,
        possible_duplicates=duplicates,
        validation_errors=validation_errors,
        low_confidence_records=low_confidence,
        average_confidence=avg_confidence,
        status_distribution=status_distribution,
        confidence_distribution=confidence_distribution,
        recent_activity=recent_activity,
    )
