import os
import sys

# Ensure workspace root is in python search path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import json
from backend.app.database.session import engine, Base, SessionLocal

from backend.app.models.models import (
    User,
    UserRole,
    Document,
    LandRecord,
    AIResult,
    Verification,
    AuditLog,
    VerificationStatus,
    ProcessingStatus,
)
from backend.app.services.auth import get_password_hash


def init_db():
    """Initializes database schema and populates initial demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Seed default users if not already present
        if db.query(User).count() == 0:
            users = [
                User(
                    name="Super Administrator",
                    email="admin@landlens.gov.in",
                    password_hash=get_password_hash("admin123"),
                    role=UserRole.ADMIN.value,
                ),
                User(
                    name="Rajesh Sharma (Tehsildar)",
                    email="officer@landlens.gov.in",
                    password_hash=get_password_hash("officer123"),
                    role=UserRole.OFFICER.value,
                ),
                User(
                    name="Pooja Verma (Patwari)",
                    email="reviewer@landlens.gov.in",
                    password_hash=get_password_hash("reviewer123"),
                    role=UserRole.REVIEWER.value,
                ),
            ]
            db.add_all(users)
            db.commit()
            print(">> Seeded default users (admin, officer, reviewer).")

        # Seed baseline demo land records for duplicate & anomaly demonstration
        if db.query(LandRecord).count() == 0:
            officer = db.query(User).filter(User.role == "officer").first()
            user_id = officer.id if officer else 1

            # Baseline 1: Ram Kumar (Rau Village, Khasra 245/2)
            rec1 = LandRecord(
                owner_name="Ram Kumar",
                father_name="Shyam Lal",
                khasra_number="245/2",
                khata_number="112",
                survey_number="SN-882",
                plot_number="P-12",
                village="Rau",
                tehsil="Rau",
                district="Indore",
                state="Madhya Pradesh",
                land_area="1.25 Hectare",
                land_type="Agricultural (Irrigated)",
                registration_number="MP-IND-2023-9901",
                mutation_number="MUT-441",
                document_number="DOC-JAMABANDI-01",
                date="14/08/2023",
                verification_status=VerificationStatus.VERIFIED.value,
                overall_confidence=0.96,
                validation_flags=json.dumps([]),
                duplicate_info=json.dumps({"is_duplicate": False, "similarity_score": 0.0}),
            )

            # Baseline 2: Sita Sharma (Kanadia, Khasra 318/1)
            rec2 = LandRecord(
                owner_name="Sita Sharma",
                father_name="Rameshwar Sharma",
                khasra_number="318/1",
                khata_number="207",
                survey_number="SN-402",
                plot_number="P-04",
                village="Kanadia",
                tehsil="Kanadia",
                district="Indore",
                state="Madhya Pradesh",
                land_area="2.10 Hectare",
                land_type="Agricultural (Non-Irrigated)",
                registration_number="MP-IND-2022-8104",
                mutation_number="MUT-129",
                document_number="DOC-JAMABANDI-02",
                date="05/11/2022",
                verification_status=VerificationStatus.VERIFIED.value,
                overall_confidence=0.94,
                validation_flags=json.dumps([]),
                duplicate_info=json.dumps({"is_duplicate": False, "similarity_score": 0.0}),
            )

            # Baseline 3: Mohan Singh (Mangliya, Khasra 102/3)
            rec3 = LandRecord(
                owner_name="Mohan Singh",
                father_name="Pratap Singh",
                khasra_number="102/3",
                khata_number="89",
                survey_number="SN-109",
                plot_number="P-33",
                village="Mangliya",
                tehsil="Sanwer",
                district="Indore",
                state="Madhya Pradesh",
                land_area="0.85 Hectare",
                land_type="Agricultural (Irrigated)",
                registration_number="MP-IND-2021-3329",
                mutation_number="MUT-884",
                document_number="DOC-JAMABANDI-03",
                date="22/01/2021",
                verification_status=VerificationStatus.VERIFIED.value,
                overall_confidence=0.95,
                validation_flags=json.dumps([]),
                duplicate_info=json.dumps({"is_duplicate": False, "similarity_score": 0.0}),
            )

            db.add_all([rec1, rec2, rec3])
            db.commit()

            # Add initial audit trail
            audit = AuditLog(
                user_id=user_id,
                action="SYSTEM_INITIALIZE",
                new_value="Initialized baseline demonstration land records (Synthetic Data for SIH26018)",
            )
            db.add(audit)
            db.commit()
            print(">> Seeded baseline land records (Rau, Kanadia, Mangliya).")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
