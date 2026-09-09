import os
import re
import json
import time
from typing import Dict, Any, List, Optional, Tuple

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "weights")
MODEL_PATH = os.path.join(WEIGHTS_DIR, "doc_classifier.joblib")
MEMORY_PATH = os.path.join(WEIGHTS_DIR, "doc_classifier_memory.json")


class ClassificationResult:
    """Encapsulates document discrimination and classification outcome."""

    def __init__(
        self,
        is_land_record: bool,
        document_type: str,
        confidence: float,
        reasons: List[str],
        warning_message: Optional[str] = None,
        detected_keywords: Optional[List[str]] = None,
        is_handwritten: bool = False,
    ):
        self.is_land_record = is_land_record
        self.document_type = document_type
        self.confidence = round(confidence, 3)
        self.reasons = reasons or []
        self.warning_message = warning_message
        self.detected_keywords = detected_keywords or []
        self.is_handwritten = is_handwritten

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_land_record": self.is_land_record,
            "document_type": self.document_type,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "warning_message": self.warning_message,
            "detected_keywords": self.detected_keywords,
            "is_handwritten": self.is_handwritten,
        }


class DocumentClassifier:
    """
    Intelligent Hybrid Document Classifier & Discriminator (SIH26018).
    Distinguishes genuine Indian Land Records (RoR, Jamabandi, Khasra, Khatauni,
    e-Stamp Conveyance Deed, Mutation Registers) from unrelated non-land documents
    (invoices, receipts, resumes, generic text, blank images, selfies).

    Uses a two-stage ensemble:
    1. Lexical & Domain Semantic Feature Scoring (Devanagari + English)
    2. Regularized Machine Learning Discriminator (TF-IDF + Calibrated Linear Model)
    3. Structural & Cadastral Regex Validator
    """

    # --- Domain Keywords for Land Records ---
    LAND_RECORD_KEYWORDS = {
        "jamabandi_ror": [
            r"अधिकार\s*अभिलेख",
            r"जमाबंदी",
            r"record\s*of\s*rights",
            r"भूस्वामी",
            r"खातेदार",
            r"काश्तकार",
            r"काश्त",
            r"पट्टेदार",
            r"pattadar",
            r"khatedar",
            r"रकबा",
            r"खसरा",
            r"khasra",
            r"खाता",
            r"khata",
            r"खेवट",
            r"khewat",
            r"पटवारी",
            r"patwari",
            r"तहसीलदार",
            r"tehsildar",
            r"राजस्व\s*विभाग",
            r"revenue\s*department",
            r"land\s*records",
        ],
        "khasra_khatauni": [
            r"खसरा\s*(?:नं|नम्बर|संख्या|क्रमांक)?",
            r"खतौनी\s*(?:नकल|संख्या)?",
            r"panchsala",
            r"पंचसाला",
            r"सर्वे\s*(?:नं|क्रमांक)?",
            r"survey\s*number",
            r"भूलेख",
            r"bhulekh",
            r"nakal",
            r"नकल",
            r"किस्म\s*जमीन",
            r"सिंचित",
            r"असिंचित",
        ],
        "estamp_conveyance_deed": [
            r"e\-stamp",
            r"estamp",
            r"india\s*non\s*judicial",
            r"article\s*23\s*conveyance",
            r"conveyance\s*deed",
            r"subin",
            r"certificate\s*no",
            r"sub\-registrar",
            r"उप\-पंजीयक",
            r"stamp\s*duty",
            r"purchased\s*by",
            r"first\s*party",
            r"second\s*party",
            r"consideration\s*price",
            r"unique\s*doc(?:\.|\s)*reference",
            r"vendor",
            r"vendee",
            r"transferor",
            r"transferee",
            r"विलेख",
            r"बिक्री\s*नामा",
            r"sale\s*deed",
        ],
        "mutation_register": [
            r"नामांतरण\s*(?:पंजी|क्रमांक|संख्या)?",
            r"दाखिल\s*खारिज",
            r"dakhil\s*kharij",
            r"mutation\s*(?:register|number|no)?",
            r"पंजीकरण\s*क्रमांक",
            r"registration\s*no",
        ],
    }

    # Common Indian Cadastral & Administrative Indicators
    CADASTRAL_TERMS = [
        r"\bग्राम\b|\bगाँव\b|\bvillage\b|\bmauza\b|\bमौजा\b",
        r"\bतहसील\b|\btehsil\b|\btaluka\b|\btaluk\b",
        r"\bजिला\b|\bdistrict\b|\bdist\b",
        r"\bराज्य\b|\bstate\b",
        r"\bmadhya\s*pradesh\b|\bm\.p\.\b|\bम\.प्र\.",
        r"\buttar\s*pradesh\b|\bu\.p\.\b|\bउ\.प्र\.",
        r"\bhectare\b|\bहेक्टेयर\b|\bbigha\b|\bबीघा\b|\bacre\b|\bएकड़\b",
        r"\bowner(?:\s*name)?\b|\bमालिक\s*(?:का\s*नाम)?\b",
        r"\bfather(?:'s)?(?:\s*name)?\b|\bपिता\s*(?:का\s*नाम)?\b",
    ]

    # --- Negative Domain Indicators (Non-Land Documents) ---
    NON_LAND_PATTERNS = {
        "invoice_or_billing": [
            r"\btax\s*invoice\b",
            r"\binvoice\s*(?:no|number|#|date)?\b",
            r"\bbill\s*to\b",
            r"\bship\s*to\b",
            r"\bgstin\b|\bgst\s*no\b",
            r"\bsubtotal\b|\bsub\-total\b",
            r"\btotal\s*amount\b|\bgrand\s*total\b|\bbalance\s*due\b",
            r"\bpayment\s*(?:terms|mode|due|received|method)\b",
            r"\bpurchase\s*order\b|\bp\.o\.\s*no\b",
            r"\bhsn\s*code\b|\bhsn\/sac\b",
            r"\bunit\s*price\b|\bqty\b|\bquantity\b",
            r"\bcgst\b|\bsgst\b|\bigst\b",
            r"\bcash\s*memo\b|\breceipt\s*voucher\b",
            r"\bbilling\s*address\b",
        ],
        "resume_or_curriculum_vitae": [
            r"\bcurriculum\s*vitae\b|\bresume\b",
            r"\bwork\s*experience\b|\bprofessional\s*experience\b",
            r"\beducation(?:al)?\s*qualifications?\b",
            r"\btechnical\s*skills\b|\bcore\s*competencies\b",
            r"\bacademic\s*projects\b|\bcareer\s*objective\b",
            r"\blinkedin\.com\/in\b|\bgithub\.com\b",
        ],
        "medical_or_clinical": [
            r"\bpatient\s*name\b|\bprescription\b|\bdosage\b",
            r"\bhospital\s*(?:admission|discharge)\b",
            r"\bdiagnosis\b|\bdoctor(?:'s)?\s*signature\b|\brx\b",
            r"\blab(?:oratory)?\s*report\b",
        ],
        "academic_or_article": [
            r"\babstract\b|\bintroduction\b|\bmethodology\b",
            r"\bliterature\s*review\b|\bbibliography\b|\breferences\s*cited\b",
            r"\btable\s*of\s*contents\b|\bchapter\s*\d+\b",
        ],
        "financial_or_banking": [
            r"\bbank\s*statement\b|\baccount\s*statement\b",
            r"\bdebit\s*card\b|\bcredit\s*card\b|\bcard\s*ending\b",
            r"\bavailable\s*balance\b|\bclosing\s*balance\b|\bopening\s*balance\b",
            r"\btransaction\s*id\b|\bneft\b|\brtgs\b|\bupi\s*ref\b|\bifsc\b",
        ],
        "utility_bill": [
            r"\belectricity\s*bill\b|\bwater\s*bill\b|\bpower\s*distribution\b",
            r"\bconsumer\s*(?:no|number)\b|\bmeter\s*number\b|\bkwh\b|\buniss?\s*consumed\b",
            r"\bbill\s*month\b|\bconnected\s*load\b",
        ],
        "identity_document": [
            r"\bdriving\s*licen[sc]e\b|\bdriver\s*licen[sc]e\b",
            r"\bpassport\s*(?:no|number)?\b",
            r"\baadhaar\b|\buidai\b|\benrolment\s*no\b",
            r"\belection\s*commission\b|\bvoter\s*id\b|\bepic\s*no\b",
            r"\bincome\s*tax\s*department\b|\bpermanent\s*account\s*number\b",
        ],
    }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocumentClassifier, cls).__new__(cls)
            cls._instance._init_classifier()
        return cls._instance

    def _init_classifier(self):
        """Initializes ML model artifacts or trains on startup if absent."""
        self.ml_model = None
        self.vectorizer = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Loads cached model or trains baseline discriminator on startup."""
        if os.path.exists(MODEL_PATH):
            try:
                import joblib
                artifact = joblib.load(MODEL_PATH)
                self.ml_model = artifact.get("classifier")
                self.vectorizer = artifact.get("vectorizer")
                return
            except Exception:
                pass

        # If not cached, train initial lightweight discriminator
        self._train_baseline_model()

    def _load_memory(self) -> List[Dict[str, Any]]:
        """Loads persistent exemplar memory buffer for continuous learning."""
        if os.path.exists(MEMORY_PATH):
            try:
                with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_memory(self, exemplars: List[Dict[str, Any]]):
        """Persists exemplar buffer atomically to prevent data corruption."""
        try:
            os.makedirs(WEIGHTS_DIR, exist_ok=True)
            temp_path = MEMORY_PATH + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(exemplars, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, MEMORY_PATH)
        except Exception:
            pass

    def _train_baseline_model(self):
        """Trains and saves lightweight linear discriminator from synthetic corpus and exemplar memory."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            import joblib

            corpus_data, labels = self._build_training_dataset()
            exemplars = self._load_memory()
            for ex in exemplars:
                corpus_data.append(ex["text"])
                labels.append(1 if ex.get("is_land_record", True) else 0)

            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=2500,
                token_pattern=r"(?u)\b[A-Za-z0-9\u0900-\u097F]{2,}\b",
            )
            X = vectorizer.fit_transform(corpus_data)

            clf = LogisticRegression(C=2.0, max_iter=250, random_state=42)
            clf.fit(X, labels)

            self.ml_model = clf
            self.vectorizer = vectorizer

            os.makedirs(WEIGHTS_DIR, exist_ok=True)
            artifact = {
                "classifier": clf,
                "vectorizer": vectorizer,
                "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "version": "1.2.0",
                "adapted_samples": len(corpus_data),
            }
            joblib.dump(artifact, MODEL_PATH, compress=3)
        except Exception:
            # Non-fatal; heuristic discriminator remains 100% active
            self.ml_model = None
            self.vectorizer = None

    def _build_training_dataset(self) -> Tuple[List[str], List[int]]:
        """Constructs synthetic multilingual training set of land records vs non-land docs."""
        land_records = [
            "GOVERNMENT OF MADHYA PRADESH REVENUE DEPARTMENT RECORD OF RIGHTS अधिकार अभिलेख जमाबंदी "
            "Owner Name मालिक का नाम Ram Kumar Khasra Number खसरा नं 245/2 Khata Number खाता नं 112 "
            "Village ग्राम Rau Tehsil तहसील Rau District जिला Indore Land Area रकबा 1.25 Hectare",

            "GOVERNMENT OF MADHYA PRADESH REVENUE DEPARTMENT KHATONI NAKAL खतौनी नकल "
            "Owner Name Sita Sharma Khasra Number 318/1 Khata Number 207 Survey Number SN-402 "
            "Village Kanadia Tehsil Kanadia District Indore Land Area 2.10 Hectare Agricultural",

            "GOVERNMENT OF MADHYA PRADESH REVENUE DEPARTMENT KHASRA PANCHSALA खसरा पंचसाला "
            "Owner Name Mohan Singh Khasra Number 102/3 Khata Number 89 Village Mangliya "
            "Tehsil Sanwer District Indore Land Area 0.85 Hectare Bhu-Abhilekh पटवारी रिपोर्ट",

            "INDIA NON JUDICIAL Government of Uttar Pradesh e-Stamp Certificate No IN-UP76993801475378T "
            "Article 23 Conveyance Property Description Flat No 1101 Ramprastha Greens Vaishali Extn Ghaziabad "
            "Purchased by Pankaj Tyagi First Party Kiran Verma Second Party Pankaj Tyagi Consideration Rs 690000",

            "MUTATION REGISTER नामांतरण पंजी दाखिल खारिज राजस्व विभाग "
            "Owner Name Ramkumar Khasra Number 245/2 Khata Number 112 Village Rau Tehsil Rau District Indore "
            "Registration No MP-IND-2024-1188 Mutation No MUT-992 Date 12/02/2024",

            "GOVERNMENT OF UTTAR PRADESH REVENUE DEPARTMENT KHATAUNI NAKAL "
            "खातेदार का नाम राजेश कुमार पिता महेश कुमार खसरा संख्या 555/1 ग्राम मलीहाबाद तहसील मलीहाबाद जिला लखनऊ "
            "रकबा 1.50 हेक्टेयर भूमि प्रकार सिंचित कृषि",

            "पुराना हस्तलिखित भू-अभिलेख खसरा नकल मौजा राऊ तहसील राऊ "
            "काश्तकार का नाम राम कुमार पिता श्याम लाल खसरा २४५/२ रकबा १.२५ हेक्टेयर "
            "जमाबंदी साल संवत २०८० पटवारी हस्ताक्षर मोहर तहसीलदार",

            "REVENUE DEPARTMENT SUB-REGISTRAR OFFICE SALE DEED CONVEYANCE REGISTER "
            "Vendor Transferor Seller Transferee Buyer Vendee Land Parcel Survey No 402/1 "
            "Total Area 2.50 Acre Stamp Duty Paid Sub-Registrar Ghaziabad Uttar Pradesh",
        ]

        non_land_records = [
            "TAX INVOICE Invoice No INV-2024-8891 Date 15/03/2024 "
            "Bill To Acme Corporation 123 Tech Park Shipping Address Same as Billing "
            "GSTIN 07AAAAA0000A1Z5 Subtotal 4500.00 CGST 9% SGST 9% Total Amount 5310.00 "
            "Payment Terms Net 30 Days Due Date 15/04/2024 Unit Price Qty 10",

            "RETAIL CASH RECEIPT Supermart Store Receipt # 90422 "
            "Items: Milk Bread Butter Eggs Soap Shampoo Total Items 6 "
            "Subtotal $42.50 Tax 8% $3.40 Grand Total $45.90 "
            "Paid by Credit Card Visa ending 4412 Thank you for shopping with us",

            "CURRICULUM VITAE / RESUME "
            "John Doe Senior Software Engineer Email john.doe@email.com LinkedIn linkedin.com/in/johndoe "
            "Professional Experience: 5 years at Tech Solutions Inc developing Python backend APIs "
            "Education: Bachelor of Technology in Computer Science Skills: Python FastAPI Docker SQL",

            "MEDICAL DIAGNOSIS & PRESCRIPTION SLIP "
            "Apollo Hospital Outpatient Department Patient Name Rajesh Verma Age 42 Gender Male "
            "Diagnosis Acute Bronchitis Rx Tab Azithromycin 500mg once daily for 5 days "
            "Paracetamol 650mg SOS Doctor Signature Dr. S. Mehta MD Reg No 44812",

            "RESEARCH PAPER PROCEEDING ABSTRACT "
            "A Comprehensive Survey on Deep Learning Architectures for Natural Language Processing "
            "Abstract: In this paper we analyze convolutional and transformer architectures. "
            "Introduction: Deep neural networks have revolutionized the field of AI. References cited.",

            "RESTAURANT DINE-IN ORDER BILL "
            "Green Leaf Bistro Table 4 Server Alex "
            "1x Paneer Butter Masala 280 2x Butter Naan 90 1x Jeera Rice 150 "
            "Food Total 520 Service Charge 5% 26 CGST 2.5% SGST 2.5% Final Bill Amount 572",

            "BREAKING NEWS DAILY BULLETIN "
            "Weather Forecast for Capital City: Sunny skies expected throughout the weekend. "
            "Sports Update: Local football tournament enters semi-final round. Movie box office review.",

            "GENERIC TEXT DOCUMENT LOREM IPSUM "
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt "
            "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
        ]

        texts = land_records + non_land_records
        labels = [1] * len(land_records) + [0] * len(non_land_records)
        return texts, labels

    def classify_text(self, text: str, document_name: Optional[str] = None) -> ClassificationResult:
        """
        Classifies extracted OCR text into Land Record vs Non-Land Record.
        Returns detailed ClassificationResult with explainable reasons.
        """
        if not text or len(text.strip()) < 15:
            return ClassificationResult(
                is_land_record=False,
                document_type="unrecognized_or_empty_document",
                confidence=0.95,
                reasons=[
                    "Document contains insufficient readable text (fewer than 15 characters).",
                    "No legal revenue keywords, parcel numbers, or cadastral attributes detected.",
                ],
                warning_message=(
                    "The uploaded file does not contain sufficient legible text to be recognized "
                    "as an authentic land record. Please verify the document is right-side up, "
                    "unobscured, and in high resolution."
                ),
            )

        clean_text = text.lower()
        detected_keywords = []

        # 1. Match Positive Land Record Keywords
        matched_types: Dict[str, int] = {}
        for doc_type, patterns in self.LAND_RECORD_KEYWORDS.items():
            count = 0
            for pat in patterns:
                matches = re.findall(pat, clean_text, re.IGNORECASE)
                if matches:
                    count += len(matches)
                    detected_keywords.append(pat.replace(r"\s*", " ").replace(r"\-", "-"))
            if count > 0:
                matched_types[doc_type] = count

        # 2. Match Cadastral & Administrative Indicators
        cadastral_count = 0
        for pat in self.CADASTRAL_TERMS:
            if re.search(pat, clean_text, re.IGNORECASE):
                cadastral_count += 1

        # 3. Match Structural Identifiers (Khasra pattern, area pattern, date)
        has_khasra_pattern = bool(
            re.search(r"\b(\d{1,4}\s*[\/\-]\s*\d{1,3}[A-Za-z\u0900-\u097F]?|[\u0966-\u096F]{1,4}\s*[\/\-]\s*[\u0966-\u096F]{1,3})\b", text)
        )
        has_area_pattern = bool(
            re.search(r"(\d+(?:\.\d+)?|[\u0966-\u096F]+(?:\.[\u0966-\u096F]+)?)\s*(?:hectare|हेक्टेयर|bigha|बीघा|acre|एकड़|sq\.?\s*m|वर्ग\s*मीटर)", text, re.I)
        )
        has_revenue_heading = bool(
            re.search(r"government|revenue\s*department|राजस्व\s*विभाग|अधिकार\s*अभिलेख|जमाबंदी|e\-stamp|conveyance|भूलेख", clean_text)
        )

        # 4. Match Negative Non-Land Indicators
        non_land_matches: Dict[str, int] = {}
        for non_type, patterns in self.NON_LAND_PATTERNS.items():
            count = 0
            for pat in patterns:
                m = re.findall(pat, clean_text, re.IGNORECASE)
                if m:
                    count += len(m)
            if count > 0:
                non_land_matches[non_type] = count

        total_land_keywords = sum(matched_types.values())
        total_non_land_keywords = sum(non_land_matches.values())

        # 5. ML Model Inference
        ml_prob = 0.5
        if self.ml_model is not None and self.vectorizer is not None:
            try:
                X_vec = self.vectorizer.transform([text])
                probs = self.ml_model.predict_proba(X_vec)[0]
                # Class 1 is Land Record, Class 0 is Non-Land Record
                ml_prob = float(probs[1]) if len(probs) > 1 else 0.5
            except Exception:
                ml_prob = 0.5

        # 6. Ensemble Decision Engine
        friendly_non_land_names = {
            "invoice_or_billing": "Commercial Tax Invoice / Bill",
            "resume_or_curriculum_vitae": "Curriculum Vitae / Resume",
            "medical_or_clinical": "Medical Prescription / Clinical Report",
            "academic_or_article": "Academic Paper / General Article",
            "financial_or_banking": "Banking / Financial Statement",
            "utility_bill": "Electricity / Utility Bill",
            "identity_document": "Identity / Civil ID Document",
            "generic_non_land_document": "Generic Non-Land Document",
        }

        # Case A: Strong Non-Land Document Markers Detected
        is_non_land_dominant = (
            (total_non_land_keywords >= 1 and total_land_keywords == 0 and not has_revenue_heading) or
            (total_non_land_keywords >= 2 and total_non_land_keywords >= total_land_keywords and not has_revenue_heading)
        )
        if is_non_land_dominant and non_land_matches:
            top_non_type = max(non_land_matches.items(), key=lambda x: x[1])[0]
            display_type = friendly_non_land_names.get(top_non_type, "Unrelated Document")
            reasons = [
                f"Identified strong markers for '{display_type}' (found {total_non_land_keywords} matching keywords).",
                "Lacks statutory land revenue headers (Government Revenue Department, Record of Rights, Jamabandi).",
            ]
            if has_khasra_pattern:
                reasons.append("Numeric pattern present but lacks legal cadastral land registry context.")
            else:
                reasons.append("No agricultural Khasra parcel numbers, Khata numbers, or land area measurements present.")

            warning_msg = (
                f"The uploaded document is recognized as a '{display_type}', NOT an authentic land revenue record. "
                "LandLens AI only digitizes genuine land records (e.g. RoR, Jamabandi, Khasra, Khatauni, e-Stamp Conveyance Deeds). "
                "Please upload a valid land document."
            )
            conf = min(0.99, max(0.88, 0.60 + 0.08 * total_non_land_keywords))
            return ClassificationResult(
                is_land_record=False,
                document_type=top_non_type,
                confidence=conf,
                reasons=reasons,
                warning_message=warning_msg,
            )

        # Case B: Document with zero land keywords and no statutory revenue heading
        # NOTE: A document with zero land keywords and no revenue heading CANNOT be an authentic land record,
        # even if an isolated fraction, date, or address number happens to match the khasra regex.
        if total_land_keywords == 0 and not has_revenue_heading:
            reasons = [
                "No Indian land revenue terminology detected (e.g., Jamabandi, Khasra, Khata, Tehsil, RoR).",
                "Missing legal land parcel indicators, survey plots, and cadastral hectare/bigha specifications.",
            ]
            if has_khasra_pattern:
                reasons.append("Detected numeric slash/format, but without any land revenue context or keywords.")
            reasons.append(f"Machine learning land-record confidence is extremely low ({ml_prob * 100:.1f}%).")
            warning_msg = (
                "The uploaded document does not appear to be a recognized land record (such as Jamabandi, "
                "Khasra, Khatauni, or e-Stamp deed). Information extracted may be invalid or irrelevant."
            )
            conf = min(0.98, max(0.85, 1.0 - ml_prob))
            return ClassificationResult(
                is_land_record=False,
                document_type="generic_non_land_document",
                confidence=conf,
                reasons=reasons,
                warning_message=warning_msg,
            )

        # Case C: Genuine Land Record Verified
        # Determine specific land record sub-type
        best_type = "jamabandi_ror"
        if matched_types:
            best_type = max(matched_types.items(), key=lambda x: x[1])[0]
        elif "e-stamp" in clean_text or "conveyance" in clean_text:
            best_type = "estamp_conveyance_deed"
        elif has_khasra_pattern:
            best_type = "khasra_khatauni"

        type_labels = {
            "jamabandi_ror": "Record of Rights / Jamabandi (अधिकार अभिलेख)",
            "khasra_khatauni": "Khasra / Khatauni Nakal (खसरा खतौनी नकल)",
            "estamp_conveyance_deed": "Uttar Pradesh e-Stamp Conveyance Deed (विलेख)",
            "mutation_register": "Mutation Register (नामांतरण पंजी)",
        }
        friendly_type = type_labels.get(best_type, "Authentic Revenue Record")

        reasons = [
            f"Classified as '{friendly_type}' with {total_land_keywords} matched statutory revenue keywords.",
        ]
        if has_khasra_pattern:
            reasons.append("Identified valid cadastral parcel identifier (Khasra/Khata pattern).")
        if has_area_pattern:
            reasons.append("Identified standard agricultural/urban parcel area specification.")
        if cadastral_count >= 2:
            reasons.append(f"Matched {cadastral_count} administrative geo-hierarchy entities (Village/Tehsil/District/State).")

        # Confidence calculation
        score = 0.88
        if has_revenue_heading:
            score += 0.04
        if has_khasra_pattern:
            score += 0.03
        if has_area_pattern:
            score += 0.02
        if total_land_keywords >= 3:
            score += 0.02
        if ml_prob > 0.6:
            score = max(score, ml_prob)

        conf = min(0.99, max(0.90, score))

        is_hw = bool(
            re.search(r"[\u0966-\u096F]|हस्तलिखित|हाथ\s*से|पटवारी\s*हल्का", clean_text)
            or (document_name and "handwritten" in document_name.lower())
            or "handwritten" in clean_text.lower()
        )

        return ClassificationResult(
            is_land_record=True,
            document_type=best_type,
            confidence=conf,
            reasons=reasons,
            detected_keywords=list(set(detected_keywords))[:10],
            is_handwritten=is_hw,
        )

    def classify_document(
        self,
        raw_text: str,
        file_path: Optional[str] = None,
        document_name: Optional[str] = None,
    ) -> ClassificationResult:
        """
        High-level orchestrator: inspects text and (optional) image features to classify document.
        """
        # 1. Text-based classification
        text_result = self.classify_text(raw_text, document_name=document_name)

        # 2. Check if file is an image without any discernible document layout
        if not text_result.is_land_record and file_path and os.path.exists(file_path):
            try:
                import cv2
                img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Check text-like edge density
                    edges = cv2.Canny(img, 100, 200)
                    edge_density = float(edges.sum() / 255) / float(img.size)
                    if edge_density < 0.01:
                        # Very few edges -> likely a blank image or non-document photo
                        return ClassificationResult(
                            is_land_record=False,
                            document_type="non_document_image",
                            confidence=0.98,
                            reasons=[
                                "Image edge density is below 1% (no document, table, or text lines detected).",
                                "Uploaded file appears to be a blank page or a non-document photograph.",
                            ],
                            warning_message=(
                                "The uploaded image does not contain readable document text or table grids. "
                                "Please upload a clear scanned land record."
                            ),
                        )
            except Exception:
                pass

        return text_result

    def adapt_realtime(self, text: str, is_land_record: bool = True, doc_type: str = "land_record"):
        """
        Real-time continuous adaptation hook: incrementally calibrates discriminator
        when user verifies or corrects documents using persistent exemplar memory replay.
        """
        if not text or len(text.strip()) < 20:
            return

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            import joblib

            exemplars = self._load_memory()
            exemplars.append({
                "text": text,
                "is_land_record": is_land_record,
                "doc_type": doc_type,
                "adapted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            if len(exemplars) > 100:
                exemplars.pop(0)
            self._save_memory(exemplars)

            corpus_data, labels = self._build_training_dataset()
            for ex in exemplars:
                corpus_data.append(ex["text"])
                labels.append(1 if ex.get("is_land_record", True) else 0)

            vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=2500,
                token_pattern=r"(?u)\b[A-Za-z0-9\u0900-\u097F]{2,}\b",
            )
            X = vectorizer.fit_transform(corpus_data)

            clf = LogisticRegression(C=2.0, max_iter=250, random_state=42)
            clf.fit(X, labels)

            self.ml_model = clf
            self.vectorizer = vectorizer

            artifact = {
                "classifier": clf,
                "vectorizer": vectorizer,
                "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "version": "1.2.0",
                "adapted_samples": len(corpus_data),
            }
            temp_path = MODEL_PATH + ".tmp"
            joblib.dump(artifact, temp_path, compress=3)
            os.replace(temp_path, MODEL_PATH)
        except Exception:
            pass


# Singleton instance accessor
_classifier_instance = None


def get_document_classifier() -> DocumentClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DocumentClassifier()
    return _classifier_instance
