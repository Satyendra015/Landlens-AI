import os
import sys

# Reconfigure stdout for utf-8 on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Ensure workspace root is in python search path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import json
import time
from typing import Dict, Any, List

from backend.app.ai.ocr_engine import ModularOCREngine
from backend.app.ai.field_extractor import IntelligentFieldExtractor
from backend.app.ai.duplicate_detector import DuplicateDetector
from backend.app.database.session import SessionLocal
from backend.app.models.models import LandRecord


def evaluate_pipeline():
    """
    Evaluates the LandLens AI Digitization & Validation Pipeline against synthetic ground truth.
    Measures Precision, Recall, F1-Score, Duplicate Detection Accuracy, and Latency.
    """
    sample_docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
    sample_records_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_records"))

    ocr_engine = ModularOCREngine()
    db = SessionLocal()

    total_fields = 0
    correct_extractions = 0
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    total_latency = 0.0
    doc_count = 0
    all_document_confidences = []

    print("=" * 70)
    print("LANDLENS AI — PIPELINE EVALUATION BENCHMARK (SIH26018)")
    print("=" * 70)

    for meta_file in sorted(os.listdir(sample_records_dir)):
        if not meta_file.endswith(".json"):
            continue

        json_path = os.path.join(sample_records_dir, meta_file)
        with open(json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        img_path = os.path.join(sample_docs_dir, meta["filename"])
        if not os.path.exists(img_path):
            continue

        doc_count += 1
        start_time = time.time()

        # Step 1: OCR
        ocr_res = ocr_engine.process_document(img_path, document_name=meta["filename"])

        # Step 2: Field Extraction
        extracted = IntelligentFieldExtractor.extract_all_fields(
            ocr_res.raw_text, base_ocr_conf=ocr_res.average_confidence
        )

        elapsed = time.time() - start_time
        total_latency += elapsed

        # Compute document AI confidence score
        doc_confs = []
        gt_fields = meta.get("fields", {})
        for field, expected_val in gt_fields.items():
            total_fields += 1
            f_obj = extracted.get(field)
            pred_val = f_obj.value if f_obj else ""

            is_match = (expected_val.strip().lower() == pred_val.strip().lower())
            if is_match:
                correct_extractions += 1

            if expected_val and pred_val and is_match:
                tp += 1
            elif pred_val and not is_match:
                fp += 1
            elif expected_val and not is_match:
                fn += 1
            elif not expected_val and not pred_val:
                tn += 1

            if f_obj and f_obj.value:
                doc_confs.append(f_obj.confidence)

        doc_ai_confidence = sum(doc_confs) / max(len(doc_confs), 1) if doc_confs else 0.0
        all_document_confidences.append(doc_ai_confidence)

        print(f"[*] Document: {meta['filename']:<32} | Latency: {elapsed:.3f}s | AI Confidence: {doc_ai_confidence*100:.1f}% ({'HIGH' if doc_ai_confidence>=0.90 else 'MED'})")

    # Metrics computation
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = (2 * precision * recall) / max(precision + recall, 1e-6)
    accuracy = correct_extractions / max(total_fields, 1)
    avg_latency = total_latency / max(doc_count, 1)
    mean_ai_confidence = sum(all_document_confidences) / max(len(all_document_confidences), 1)

    print("-" * 70)
    print("PIPELINE PERFORMANCE & CONFIDENCE BENCHMARK:")
    print(f"  Total Evaluated Documents   : {doc_count}")
    print(f"  Total Ground Truth Fields   : {total_fields}")
    print(f"  Field Extraction Accuracy   : {accuracy * 100:.2f}%")
    print(f"  Precision                   : {precision * 100:.2f}%")
    print(f"  Recall                      : {recall * 100:.2f}%")
    print(f"  F1-Score                    : {f1 * 100:.2f}%")
    print(f"  OVERALL MEAN AI CONFIDENCE  : {mean_ai_confidence * 100:.2f}% (Target > 90%)")
    print(f"  Average Processing Latency  : {avg_latency:.3f} seconds / document")
    print("-" * 70)

    # Duplicate detection benchmark
    print("[*] Testing Fuzzy Duplicate Detection Engine...")
    dup_test = DuplicateDetector.check_duplicate(
        {"khasra_number": "245/2", "village": "Rau", "owner_name": "Ramkumar"},
        db=db,
    )
    print(f"  Target: 'Ramkumar' vs 'Ram Kumar' (Khasra 245/2, Rau)")
    print(f"  Detected As Duplicate       : {dup_test['is_duplicate']}")
    print(f"  Similarity Match Score      : {dup_test['similarity_score']}%")
    print(f"  Match Justification         : {', '.join(dup_test['reasons'])}")
    print("=" * 70)

    db.close()


if __name__ == "__main__":
    evaluate_pipeline()
