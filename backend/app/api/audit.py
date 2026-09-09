from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import AuditLog, User
from backend.app.schemas.schemas import AuditLogOut
from backend.app.services.auth import get_current_user

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    record_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns audit trail events demonstrating system governance and transparency.
    """
    query = db.query(AuditLog)
    if record_id:
        query = query.filter(AuditLog.record_id == record_id)
    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Enrich with username
    result = []
    for log in logs:
        result.append(
            AuditLogOut(
                id=log.id,
                user_id=log.user_id,
                user_name=log.user.name if log.user else "System / AI Pipeline",
                record_id=log.record_id,
                action=log.action,
                old_value=log.old_value,
                new_value=log.new_value,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
            )
        )
    return result
