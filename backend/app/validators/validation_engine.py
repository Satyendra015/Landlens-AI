import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import LandRecord


class ValidationIssue:
    def __init__(self, field: str, issue_type: str, message: str, severity: str = "warning"):
        self.field = field
        self.issue_type = issue_type  # missing_field, invalid_format, unusual_range, conflict, anomaly
        self.message = message
        self.severity = severity  # warning, error, info

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "type": self.issue_type,
            "message": self.message,
            "severity": self.severity,
        }


class LandRecordValidator:
    """
    Comprehensive Validation & Anomaly Engine for LandLens AI.
    Performs Required Field, Format, Range, Cross-Field, and Consistency validation.
    """

    # Essential fields that must not be empty
    REQUIRED_FIELDS = ["owner_name", "khasra_number", "village", "land_area"]

    # Maximum typical agricultural land parcel in Hectares for anomaly threshold
    MAX_REASONABLE_HECTARES = 50.0

    # Common Tehsil-District lookup mapping for MP and UP
    TEHSIL_DISTRICT_MAP = {
        "rau": "indore",
        "kanadia": "indore",
        "mhow": "indore",
        "sanwer": "indore",
        "depalpur": "indore",
        "mangliya": "indore",
        "ujjain": "ujjain",
        "dewas": "dewas",
        "dhar": "dhar",
        "bhopal": "bhopal",
        "sehore": "sehore",
        "lucknow": "lucknow",
        "varanasi": "varanasi",
        "agra": "agra",
        "ghaziabad": "ghaziabad",
        "modinagar": "ghaziabad",
        "loni": "ghaziabad",
    }

    @classmethod
    def _get_expanded_taxonomy(cls) -> Dict[str, str]:
        """Loads and merges master administrative taxonomy from data.gov.in dataset."""
        mapping = dict(cls.TEHSIL_DISTRICT_MAP)
        import os, json
        tax_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "datasets", "administrative_geo", "india_land_taxonomy.json")
        )
        if os.path.exists(tax_path):
            try:
                with open(tax_path, "r", encoding="utf-8") as f:
                    tax = json.load(f)
                    for state, districts in tax.items():
                        for dist, tehsils in districts.items():
                            dist_clean = dist.lower().strip()
                            mapping[dist_clean] = dist_clean
                            for teh in tehsils:
                                mapping[teh.lower().strip()] = dist_clean
            except Exception:
                pass
        return mapping


    @classmethod
    def validate_document_classification(
        cls, is_land_record: bool, doc_type: str, warning_msg: Optional[str] = None
    ) -> Optional[ValidationIssue]:
        """Flags non-land record documents as high-severity validation errors."""
        if not is_land_record:
            msg = warning_msg or f"Invalid Document Type: File identified as '{doc_type}' rather than an authentic land record."
            return ValidationIssue(
                field="document_type",
                issue_type="invalid_document_type",
                message=msg,
                severity="error",
            )
        return None

    @classmethod
    def validate_record(
        cls, fields: Dict[str, Any], db: Optional[Session] = None, exclude_record_id: Optional[int] = None
    ) -> List[ValidationIssue]:
        """
        Executes all validation suites on extracted or edited land record fields.
        """
        issues: List[ValidationIssue] = []

        # 1. Required Field Validation
        for req in cls.REQUIRED_FIELDS:
            val = fields.get(req)
            if not val or not str(val).strip():
                issues.append(
                    ValidationIssue(
                        field=req,
                        issue_type="missing_field",
                        message=f"Missing Required Field: '{req.replace('_', ' ').title()}' is required for legal land registry.",
                        severity="error",
                    )
                )

        # 2. Format Validation
        khasra = str(fields.get("khasra_number") or "").strip()
        if khasra:
            is_valid_rural = bool(re.match(r"^\d{1,4}(\/\d{1,3})?[A-Za-z\u0900-\u097F]?$", khasra))
            is_valid_urban_or_deed = bool(re.search(r"\b(sec(?:tor)?[\s\-]*\d+|plot[\s\-]*\d+|flat[\s\-]*\d+|khasra[\s\-]*\d+|\d+)\b", khasra, re.IGNORECASE))
            if not (is_valid_rural or is_valid_urban_or_deed):
                issues.append(
                    ValidationIssue(
                        field="khasra_number",
                        issue_type="invalid_format",
                        message=f"Possible Invalid Format: Khasra number '{khasra}' does not match standard pattern (e.g. 245/2 or 105).",
                        severity="warning",
                    )
                )

        date_val = str(fields.get("date") or "").strip()
        if date_val:
            if not re.match(r"^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}$", date_val):
                issues.append(
                    ValidationIssue(
                        field="date",
                        issue_type="invalid_format",
                        message=f"Possible Invalid Format: Date '{date_val}' should be in DD/MM/YYYY format.",
                        severity="warning",
                    )
                )

        # 3. Range & Anomaly Validation (Land Area)
        area_str = str(fields.get("land_area") or "").strip()
        if area_str:
            numeric_area = cls._parse_area_to_hectares(area_str)
            if numeric_area is not None:
                if numeric_area > cls.MAX_REASONABLE_HECTARES:
                    issues.append(
                        ValidationIssue(
                            field="land_area",
                            issue_type="unusual_range",
                            message=f"Possible anomaly detected: Unusual Land Area ({numeric_area} Hectares exceeds typical parcel threshold of {cls.MAX_REASONABLE_HECTARES} Ha) — Please Verify.",
                            severity="warning",
                        )
                    )
                elif numeric_area <= 0.0:
                    issues.append(
                        ValidationIssue(
                            field="land_area",
                            issue_type="unusual_range",
                            message="Possible anomaly detected: Land area cannot be zero or negative.",
                            severity="error",
                        )
                    )

        # 4. Cross-Field Validation (Tehsil vs District)
        tehsil = str(fields.get("tehsil") or "").strip().lower()
        district = str(fields.get("district") or "").strip().lower()
        tax_map = cls._get_expanded_taxonomy()
        if tehsil and district and tehsil in tax_map:
            expected_dist = tax_map[tehsil]
            if expected_dist not in district and district not in expected_dist:
                issues.append(
                    ValidationIssue(
                        field="tehsil",
                        issue_type="conflict",
                        message=f"Cross-Field Discrepancy: Tehsil '{fields.get('tehsil')}' is typically located in district '{expected_dist.title()}', but record lists '{fields.get('district')}'.",
                        severity="warning",
                    )
                )

        # 5. Consistency Validation against existing database records
        if db and khasra:
            village = str(fields.get("village") or "").strip()
            owner = str(fields.get("owner_name") or "").strip()
            if village:
                query = db.query(LandRecord).filter(
                    LandRecord.khasra_number == khasra,
                    LandRecord.village.ilike(f"%{village}%"),
                )
                if exclude_record_id:
                    query = query.filter(LandRecord.id != exclude_record_id)
                prior_records = query.all()

                for prior in prior_records:
                    if prior.owner_name and owner:
                        # If owners differ substantially for the same Khasra in the same Village
                        if prior.owner_name.strip().lower() != owner.lower():
                            issues.append(
                                ValidationIssue(
                                    field="owner_name",
                                    issue_type="conflict",
                                    message=f"Possible Inconsistency: Existing Record #{prior.id} has owner '{prior.owner_name}' for Khasra {khasra}, while this document lists '{owner}'. Mutation or verification required.",
                                    severity="warning",
                                )
                            )

        return issues

    @classmethod
    def _parse_area_to_hectares(cls, area_str: str) -> Optional[float]:
        """Converts area strings (Hectare, Bigha, Acre, Sq m, Sq ft) to normalized Hectares for evaluation."""
        lower_str = area_str.lower().strip()
        # Urban flat, floor, or unit descriptors are not agricultural land parcel areas
        if re.search(r"\b(flat|floor|unit|apartment|shop|room)\b", lower_str):
            return None

        # Look for numeric value associated with explicit area units
        unit_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(hectare|hectares|हेक्टेयर|ha|bigha|बीघा|acre|एकड़|sq\.?\s*(?:m|meter|ft|feet|yd|yard)|वर्ग\s*(?:मीटर|फुट|गज))",
            lower_str,
        )
        if unit_match:
            val = float(unit_match.group(1))
            unit = unit_match.group(2)
            if "bigha" in unit or "बीघा" in unit:
                return val * 0.2529  # approx 1 Bigha = ~0.25 Ha
            elif "acre" in unit or "एकड़" in unit:
                return val * 0.4047  # 1 Acre = 0.4047 Ha
            elif "ft" in unit or "फुट" in unit:
                return val * 0.00000929
            elif "yd" in unit or "गज" in unit:
                return val * 0.0000836
            elif "m" in unit or "मीटर" in unit:
                return val / 10000.0  # 1 Ha = 10,000 sq m
            else:
                return val

        # Purely numeric strings (fallback for systems recording bare hectares)
        match = re.match(r"^(\d+(?:\.\d+)?)$", lower_str)
        if match:
            return float(match.group(1))

        return None
