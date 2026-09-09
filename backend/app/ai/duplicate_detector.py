import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from backend.app.models.models import LandRecord


class DuplicateDetector:
    """
    Fuzzy Duplicate Detection Engine for Land Records.
    Identifies potential duplicate or overlapping records across Khasra, Khata,
    Owner Name, and Village using token-sort Levenshtein distance metrics.
    """

    SIMILARITY_THRESHOLD = 75.0  # Percentage (0-100)

    @classmethod
    def check_duplicate(
        cls, fields: Dict[str, Any], db: Session, exclude_record_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scans database records to find potential duplicates or identical parcel registrations.
        Returns detailed match metrics and similarity scores without auto-deleting.
        """
        khasra = str(fields.get("khasra_number") or "").strip()
        village = str(fields.get("village") or "").strip()
        owner = str(fields.get("owner_name") or "").strip()

        if not khasra or not db:
            return {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "matched_record_id": None,
                "matched_khasra": None,
                "matched_owner": None,
                "matched_village": None,
                "reasons": [],
            }


        # Query all records in database with matching village or khasra
        query = db.query(LandRecord)
        if exclude_record_id:
            query = query.filter(LandRecord.id != exclude_record_id)
        existing_records = query.all()

        best_match = None
        highest_score = 0.0
        match_reasons: List[str] = []

        norm_khasra = cls._normalize_text(khasra)
        norm_village = cls._normalize_text(village)
        norm_owner = cls._normalize_text(owner)

        for rec in existing_records:
            rec_khasra = cls._normalize_text(rec.khasra_number or "")
            rec_village = cls._normalize_text(rec.village or "")
            rec_owner = cls._normalize_text(rec.owner_name or "")

            # 1. Exact Match on Khasra + Village
            is_same_khasra = norm_khasra and rec_khasra and (norm_khasra == rec_khasra)
            is_same_village = norm_village and rec_village and (
                norm_village in rec_village or rec_village in norm_village
            )

            # 2. Fuzzy Match on Owner Name (e.g. 'Ram Kumar' vs 'Ramkumar')
            owner_similarity = (
                fuzz.token_sort_ratio(norm_owner, rec_owner)
                if (norm_owner and rec_owner)
                else 0.0
            )

            # Compute weighted duplicate score
            score = 0.0
            reasons = []

            if is_same_khasra and is_same_village:
                score += 50.0
                reasons.append(f"Identical Khasra #{khasra} in Village '{rec.village}'")

                if owner_similarity > 80.0:
                    score += 45.0
                    reasons.append(
                        f"High Owner Name similarity ({int(owner_similarity)}% match: '{rec.owner_name}' vs '{owner}')"
                    )
                elif owner_similarity > 50.0:
                    score += 25.0
                    reasons.append(
                        f"Moderate Owner Name similarity ({int(owner_similarity)}% match: '{rec.owner_name}')"
                    )
                else:
                    score += 15.0
                    reasons.append(f"Different owner on same plot ({rec.owner_name})")

            elif is_same_khasra:
                score += 30.0
                if owner_similarity > 80.0:
                    score += 40.0
                    reasons.append(f"Same Khasra & matching owner name ({int(owner_similarity)}%)")

            if score > highest_score:
                highest_score = score
                best_match = rec
                match_reasons = reasons

        is_duplicate = highest_score >= cls.SIMILARITY_THRESHOLD

        return {
            "is_duplicate": is_duplicate,
            "similarity_score": round(highest_score, 1),
            "matched_record_id": best_match.id if best_match else None,
            "matched_khasra": best_match.khasra_number if best_match else None,
            "matched_owner": best_match.owner_name if best_match else None,
            "matched_village": best_match.village if best_match else None,
            "reasons": match_reasons,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalizes spacing, removes special characters and converts to lowercase."""
        if not text:
            return ""
        s = text.lower().strip()
        s = re.sub(r"[\s\-\_\/\.\,\:\;]+", "", s)
        return s
