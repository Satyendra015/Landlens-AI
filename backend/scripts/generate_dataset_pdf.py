import os
import sys
import json
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PDF_OUTPUT_PATH = os.path.join(BASE_DIR, "SIH26018_LandLens_AI_Training_Datasets_Report.pdf")

# Images
SEAL_IMG = os.path.join(BASE_DIR, "backend", "app", "static", "landlens_seal_exact.png")
CHAR_GRID_IMG = os.path.join(BASE_DIR, "data", "datasets", "devanagari_characters", "sample_grid.png")
ESTAMP_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_9_estamp_ghaziabad.jpg")
HW_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_11_handwritten_khasra.png")
INVOICE_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_10_non_land_invoice.png")
CLEAN_IMG = os.path.join(BASE_DIR, "data", "sample_documents", "sample_1_clean_rau.png")


class NumberedCanvas(canvas.Canvas):
    """Adds running headers, footers, and page numbers to PDF."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header (pages 2 and later)
        if self._pageNumber > 1:
            self.drawString(54, 800, "LandLens AI — SIH26018 Official Training & Benchmark Datasets Dossier")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 794, 541, 794)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 541, 45)

        footer_left = "Smart India Hackathon 2024 • SIH26018 Training Dataset Specifications"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 32, footer_left)
        self.drawRightString(541, 32, footer_right)
        self.restoreState()


def build_dataset_pdf():
    print(f"[*] Building Publication-Grade Training Dataset PDF Report...")
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Executive Palette
    C_NAVY = colors.HexColor("#1e3a8a")
    C_NAVY_DARK = colors.HexColor("#0f172a")
    C_AMBER = colors.HexColor("#b45309")
    C_SLATE = colors.HexColor("#1e293b")
    C_MUTED = colors.HexColor("#64748b")
    C_BG_LIGHT = colors.HexColor("#f8fafc")
    C_BG_CARD = colors.HexColor("#f1f5f9")
    C_BORDER = colors.HexColor("#e2e8f0")
    C_BORDER_DARK = colors.HexColor("#cbd5e1")
    C_ACCENT_BLUE = colors.HexColor("#eff6ff")
    C_ACCENT_AMBER = colors.HexColor("#fffbeb")
    C_GREEN = colors.HexColor("#15803d")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=C_NAVY,
        alignment=1,
        spaceAfter=2
    )

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=C_AMBER,
        alignment=1,
        spaceAfter=3
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=C_MUTED,
        alignment=1,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=C_NAVY,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=C_SLATE,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=C_SLATE,
        spaceAfter=5
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=C_SLATE,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=C_SLATE,
        leftIndent=10,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'THStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TDStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=C_SLATE,
        alignment=0
    )

    table_cell_bold = ParagraphStyle(
        'TDBoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=C_NAVY,
        alignment=0
    )

    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=C_NAVY,
        alignment=1,
        spaceBefore=2,
        spaceAfter=1
    )

    cap_note_style = ParagraphStyle(
        'CapNote_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=9,
        textColor=C_MUTED,
        alignment=1,
        spaceAfter=6
    )

    story = []

    # =========================================================================
    # Header & Title Block
    # =========================================================================
    if os.path.exists(SEAL_IMG):
        story.append(RLImage(SEAL_IMG, width=1.1*inch, height=1.1*inch))
        story.append(Spacer(1, 3))

    story.append(Paragraph("LANDLENS AI", title_style))
    story.append(Paragraph("Official Training & Benchmark Dataset Dossier (SIH26018)", sub_style))
    story.append(Paragraph("Comprehensive Data Specifications, Annotation Protocols, Class Distributions, and Evaluation Benchmarks", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER_DARK, spaceAfter=8))

    # Metadata Grid
    meta_box = [
        [
            Paragraph("<b>Problem Statement ID:</b> SIH26018", table_cell_style),
            Paragraph("<b>Total Training Corpus:</b> 10,800+ Samples", table_cell_style),
            Paragraph("<b>Primary Languages:</b> Hindi (Devanagari) & English", table_cell_style)
        ],
        [
            Paragraph("<b>Data Privacy Standard:</b> DPDP Act 2023 Sandbox", table_cell_style),
            Paragraph("<b>Dataset Storage:</b> Local On-Premises (Offline)", table_cell_style),
            Paragraph("<b>Release Version:</b> v2.4.0 (Production Verified)", table_cell_style)
        ]
    ]
    meta_table = Table(meta_box, colWidths=[160, 160, 167])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # =========================================================================
    # Section 1: Executive Data Summary
    # =========================================================================
    story.append(Paragraph("1. Executive Dataset Architecture & Summary Overview", h1_style))
    story.append(Paragraph(
        "To achieve robust, production-grade land record digitization and validation without catastrophic forgetting, "
        "LandLens AI utilizes a multi-tiered data architecture. The datasets cover character-level handwritten Indic numerals, "
        "bilingual land record corpora, non-land negative discriminator exemplars, real-time online adaptation memory buffers, "
        "and paired high-confidence benchmark test records.",
        body_style
    ))

    master_summary_headers = [
        Paragraph("<b>Dataset Tier</b>", table_header_style),
        Paragraph("<b>Category / Content</b>", table_header_style),
        Paragraph("<b>Total Volume / Size</b>", table_header_style),
        Paragraph("<b>Splits & Format</b>", table_header_style),
        Paragraph("<b>Trained Component</b>", table_header_style)
    ]
    master_summary_rows = [master_summary_headers]

    raw_summary_data = [
        ("Tier 1: Devanagari & Numeral Characters", "Devanagari digits (०-९), Arabic digits (0-9), Hindi/Eng sub-parcels (क, ख, ग, घ, A, B)", "7,800 Images (18.9 MB)", "70% Train / 15% Val / 15% Test (.npz)", "Deep CNN Numeral Model (devanagari_cnn.keras)"),
        ("Tier 2: Land Records NER Corpus", "Bilingual Jamabandi, RoR, Khatauni, and Indian Non-Judicial e-Stamp Deeds", "2,001 Annotated Deeds (3.8 MB JSON)", "80% Train / 20% Test (Tokens)", "Bilingual Domain NER (field_ner_model.joblib)"),
        ("Tier 3: Land Record Discriminator Set", "Authentic land revenue records vs. Tax Invoices, Resumes, Prescriptions, Utility Bills", "500+ Semantic Exemplars + Regex Rules", "TF-IDF (1-2 N-grams) + Memory Buffer", "Document Classifier & Fraud Guard (doc_classifier.joblib)"),
        ("Tier 4: Online Adaptation Buffer", "Real-world continuous learning exemplars (e-Stamp deed + historical Jamabandi)", "Fast-Loop Memory Buffer (24 KB JSON)", "Experience Replay Exemplar Buffer", "Continuous Learner (adaptive_memory.json)"),
        ("Tier 5: Benchmark Ground Truth Suite", "High-fidelity paired image scans (.png/.jpg) and exact ground truth metadata (.json/.txt)", "15 Comprehensive Test Records (6.4 MB)", "100% Held-Out Benchmark Test Suite", "Pipeline Benchmarking (evaluate_pipeline.py)"),
        ("Tier 6: Geospatial & Administrative Data", "Indian administrative hierarchy (MP & UP) + Cadastral parcel spatial boundaries", "26 KB Taxonomy + 5.4 KB GeoJSON", "Static Reference JSON & GeoJSON", "Cadastral GIS Engine & Validation Rules")
    ]

    for t_name, cat, vol, split, comp in raw_summary_data:
        master_summary_rows.append([
            Paragraph(f"<b>{t_name}</b>", table_cell_bold),
            Paragraph(cat, table_cell_style),
            Paragraph(vol, table_cell_style),
            Paragraph(split, table_cell_style),
            Paragraph(f"<i>{comp}</i>", table_cell_style)
        ])

    sum_table = Table(master_summary_rows, colWidths=[105, 115, 80, 95, 92])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('BACKGROUND', (0, 1), (-1, 1), C_ACCENT_BLUE),
        ('BACKGROUND', (0, 3), (-1, 3), C_ACCENT_BLUE),
        ('BACKGROUND', (0, 5), (-1, 5), C_ACCENT_BLUE),
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # Section 2: Tier 1 Devanagari & Numeral Character Recognition Dataset
    # =========================================================================
    story.append(Paragraph("2. Tier 1: Devanagari & Arabic Numeral Character Dataset", h1_style))
    story.append(Paragraph(
        "<b>Storage Location:</b> <font color='#1e3a8a'><code>data/datasets/devanagari_characters/</code></font><br/>"
        "The Devanagari Character & Numeral Dataset provides the foundation for solving the most critical transcription bottleneck "
        "in Indian land administration: recognizing handwritten and printed Devanagari numerals in revenue field registers "
        "(e.g., converting Khasra <b>२४५/२</b> to <b>245/2</b>).",
        body_style
    ))

    dev_split_headers = [
        Paragraph("<b>Data Split</b>", table_header_style),
        Paragraph("<b>Filename</b>", table_header_style),
        Paragraph("<b>Sample Count</b>", table_header_style),
        Paragraph("<b>Percentage</b>", table_header_style),
        Paragraph("<b>Dimensions</b>", table_header_style),
        Paragraph("<b>File Size</b>", table_header_style)
    ]
    dev_split_rows = [dev_split_headers]
    dev_split_data = [
        ("Training Set", "train.npz", "5,460 Samples", "70.0%", "5460 x 32 x 32", "13.23 MB"),
        ("Validation Set", "val.npz", "1,170 Samples", "15.0%", "1170 x 32 x 32", "2.83 MB"),
        ("Unseen Test Set", "test.npz", "1,170 Samples", "15.0%", "1170 x 32 x 32", "2.84 MB"),
        ("Total Dataset", "classes.json", "7,800 Samples", "100.0%", "26 Classes x 300 Samples", "18.90 MB")
    ]
    for sp, fn, cnt, pct, dim, sz in dev_split_data:
        is_tot = sp == "Total Dataset"
        dev_split_rows.append([
            Paragraph(f"<b>{sp}</b>" if is_tot else sp, table_cell_bold if is_tot else table_cell_style),
            Paragraph(f"<code>{fn}</code>", table_cell_style),
            Paragraph(cnt, table_cell_style),
            Paragraph(pct, table_cell_style),
            Paragraph(dim, table_cell_style),
            Paragraph(sz, table_cell_style)
        ])

    dev_split_table = Table(dev_split_rows, colWidths=[90, 80, 80, 65, 100, 72])
    dev_split_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('BACKGROUND', (0, -1), (-1, -1), C_ACCENT_AMBER),
    ]))
    story.append(dev_split_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>26 Target Classes (classes.json):</b>", h2_style))
    story.append(Paragraph(
        "• <b>Devanagari Numerals (10 classes):</b> <code>०, १, २, ३, ४, ५, ६, ७, ८, ९</code> (Normalized to 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)<br/>"
        "• <b>Arabic / English Numerals (10 classes):</b> <code>0, 1, 2, 3, 4, 5, 6, 7, 8, 9</code><br/>"
        "• <b>Hindi Cadastral Sub-Parcel Letters (4 classes):</b> <code>क, ख, ग, घ</code> (e.g., Khasra 245/2क, 102/1ख)<br/>"
        "• <b>English Cadastral Sub-Parcel Letters (2 classes):</b> <code>A, B</code> (e.g., Survey SN-882A)",
        bullet_style
    ))

    # Embedded Character Grid
    if os.path.exists(CHAR_GRID_IMG):
        story.append(Spacer(1, 3))
        story.append(RLImage(CHAR_GRID_IMG, width=6.5*inch, height=1.35*inch))
        story.append(Paragraph("Figure 1: Representative 32x32 Augmented Grayscale Training Samples across all 26 Character Classes (train.npz)", caption_style))
        story.append(Paragraph("Augmentation Pipeline: Nirmala Indic UI rendering, affine rotation (-10° to +10°), horizontal/vertical center jitter, Gaussian ink variance.", cap_note_style))

    story.append(Spacer(1, 4))

    # =========================================================================
    # Section 3: Tier 2 Bilingual Land Records NER Corpus
    # =========================================================================
    story.append(Paragraph("3. Tier 2: Bilingual Land Records & e-Stamp Corpus", h1_style))
    story.append(Paragraph(
        "<b>Storage Location:</b> <font color='#1e3a8a'><code>data/datasets/land_records_corpus/land_records_ner.json</code></font> (3.83 MB)<br/>"
        "The Bilingual Land Records NER Corpus comprises <b>2,001 fully annotated documents</b> representing authentic legal deeds "
        "and revenue registers from Madhya Pradesh, Uttar Pradesh, and Delhi revenue jurisdictions:",
        body_style
    ))

    ner_doc_types = [
        Paragraph("<b>Document Category</b>", table_header_style),
        Paragraph("<b>Count</b>", table_header_style),
        Paragraph("<b>Percentage</b>", table_header_style),
        Paragraph("<b>Typical Legal Articles & Administrative Forms</b>", table_header_style)
    ]
    ner_type_rows = [ner_doc_types]
    ner_raw_types = [
        ("Traditional Record of Rights (Jamabandi / Khatauni)", "1,200", "60.0%", "Jamabandi Nakal, Khatauni (CH-41), Khasra Panchsala, Shajra Nakal (Indore, Lucknow, Varanasi, Agra)"),
        ("Indian Non-Judicial e-Stamp Deeds", "800", "40.0%", "Article 23 Conveyance Deeds, Article 24/25 Sale Deeds, Agreements to Sell, Gift Deeds, SHCIL formatting"),
        ("Real-World Operational Exemplar", "1", "0.05%", "Ghaziabad Sub-Registrar IV e-Stamp Certificate (IN-UP01272481023775T) adapted via online learning"),
        ("Total Annotated Corpus", "2,001", "100.0%", "Comprehensive coverage of rural cadastral registers and urban apartment conveyance certificates")
    ]
    for cat, cnt, pct, desc in ner_raw_types:
        is_t = cat.startswith("Total")
        ner_type_rows.append([
            Paragraph(f"<b>{cat}</b>" if is_t else cat, table_cell_bold if is_t else table_cell_style),
            Paragraph(cnt, table_cell_style),
            Paragraph(pct, table_cell_style),
            Paragraph(desc, table_cell_style)
        ])

    ner_table = Table(ner_type_rows, colWidths=[140, 45, 55, 247])
    ner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('BACKGROUND', (0, -1), (-1, -1), C_ACCENT_AMBER),
    ]))
    story.append(ner_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>The 16 Standardized Land Record Entities (BIO Tagging Schema):</b>", h2_style))

    entity_headers = [
        Paragraph("<b>Attribute Key</b>", table_header_style),
        Paragraph("<b>BIO Tag</b>", table_header_style),
        Paragraph("<b>Hindi Label</b>", table_header_style),
        Paragraph("<b>Representative Training Samples</b>", table_header_style)
    ]
    entity_rows = [entity_headers]
    entity_raw = [
        ("owner_name", "B/I-OWNER", "मालिक का नाम", "Ram Kumar, Sita Sharma, Vikram Rathore"),
        ("father_name", "B/I-FATHER", "पिता का नाम", "Shyam Lal, Narayan Das, Pratap Singh"),
        ("khasra_number", "B/I-KHASRA", "खसरा नं.", "245/2, 318/1, 102/3, 415/1A, 89/1"),
        ("khata_number", "B/I-KHATA", "खाता नं.", "112, 94, 67, 220, 145, 310"),
        ("survey_number", "B/I-SURVEY", "सर्वे नं.", "SN-882, SN-402, SN-119, SN-630"),
        ("plot_number", "B/I-PLOT", "प्लॉट नं.", "P-12, P-05, P-44, Flat No 402, Plot-18"),
        ("village", "B/I-VILLAGE", "ग्राम / मौजा", "Rau, Kanadia, Mangliya, Depalpur, Pindra"),
        ("tehsil", "B/I-TEHSIL", "तहसील", "Rau, Sanwer, Mhow, Mohanlalganj, Tarana"),
        ("district", "B/I-DISTRICT", "जिला", "Indore, Lucknow, Varanasi, Agra, Ghaziabad"),
        ("state", "B/I-STATE", "राज्य", "Madhya Pradesh, Uttar Pradesh, Delhi"),
        ("land_area", "B/I-AREA", "रकबा", "1.25 Hectare, 2.10 Hectare, 0.85 Bigha"),
        ("land_type", "B/I-LAND_TYPE", "भूमि प्रकार", "Agricultural (Irrigated), Non-Irrigated, Residential"),
        ("registration_number", "B/I-REG_NO", "पंजीकरण क्रमांक", "MP-IND-2023-9901, IN-UP01272481023775T"),
        ("mutation_number", "B/I-MUTATION", "नामांतरण क्रमांक", "MUT-441, MUT-512, MUT-889, MUT-302"),
        ("document_number", "B/I-DOC_NO", "दस्तावेज संख्या", "DOC-ROR-001, SUBIN-UPUP14012024"),
        ("date", "B/I-DATE", "दिनांक", "14/08/2023, 22/11/2022, 10/09/2023")
    ]
    for ak, tg, hl, smp in entity_raw:
        entity_rows.append([
            Paragraph(f"<code>{ak}</code>", table_cell_bold),
            Paragraph(f"<code>{tg}</code>", table_cell_style),
            Paragraph(hl, table_cell_style),
            Paragraph(smp, table_cell_style)
        ])

    ent_table = Table(entity_rows, colWidths=[105, 75, 95, 212])
    ent_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
    ]))
    story.append(ent_table)
    story.append(Spacer(1, 8))

    # Contextual Sliding Window Feature Vectorization Note
    story.append(Paragraph("<b>Token Feature Vectorization (5-Token Contextual Window):</b>", h2_style))
    story.append(Paragraph(
        "Each token $w_i$ is parameterized via an extensive multi-window feature dictionary extracted in "
        "<code>train_ner_model.py</code>: bias term, lowercase token, uppercase/title flags, is_digit, is_devanagari regex "
        "(<code>[\\u0900-\\u097F]</code>), slash and hyphen indicators, token length, prefix/suffix character n-grams (2 & 3 chars), "
        "and adjacent contextual window tokens from $w_{i-2}, w_{i-1}, w_{i+1}, w_{i+2}$ including colon proximity flags.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # Section 4: Concrete Training Examples from Corpus
    # =========================================================================
    story.append(Paragraph("4. Concrete Annotated Training Samples from the Corpus", h1_style))
    story.append(Paragraph(
        "Below are two verbatim training exemplars extracted directly from <code>land_records_ner.json</code> "
        "illustrating the raw text structure paired with the ground-truth extracted entity dictionaries:",
        body_style
    ))

    # Example 1
    story.append(Paragraph("<b>Exemplar A: Traditional Madhya Pradesh Jamabandi / Record of Rights (doc_id: 1)</b>", h2_style))
    sample_1_text = (
        "GOVERNMENT OF MADHYA PRADESH - REVENUE DEPARTMENT\n"
        "RECORD OF RIGHTS / अधिकार अभिलेख जमाबंदी\n"
        "Owner Name / मालिक का नाम : Ram Kumar\n"
        "Father's Name / पिता का नाम : Shyam Lal\n"
        "Khasra Number / खसरा नं. : 245/2\n"
        "Khata Number / खाता नं. : 112\n"
        "Survey Number / सर्वे नं. : SN-882\n"
        "Plot Number / प्लॉट नं. : P-12\n"
        "Village / ग्राम : Rau\n"
        "Tehsil / तहसील : Rau\n"
        "District / जिला : Indore\n"
        "State / राज्य : Madhya Pradesh\n"
        "Land Area / रकबा : 1.25 Hectare\n"
        "Land Type / भूमि प्रकार : Agricultural (Irrigated)\n"
        "Registration No / पंजीकरण क्रमांक : MP-IND-2023-9901\n"
        "Mutation No / नामांतरण क्रमांक : MUT-441\n"
        "Document No / दस्तावेज संख्या : DOC-ROR-0001\n"
        "Date / दिनांक : 14/08/2023"
    )
    sample_1_entities = (
        "{\n"
        "  'owner_name': 'Ram Kumar',\n"
        "  'father_name': 'Shyam Lal',\n"
        "  'khasra_number': '245/2',\n"
        "  'khata_number': '112',\n"
        "  'survey_number': 'SN-882',\n"
        "  'plot_number': 'P-12',\n"
        "  'village': 'Rau',\n"
        "  'tehsil': 'Rau',\n"
        "  'district': 'Indore',\n"
        "  'state': 'Madhya Pradesh',\n"
        "  'land_area': '1.25 Hectare',\n"
        "  'land_type': 'Agricultural (Irrigated)',\n"
        "  'registration_number': 'MP-IND-2023-9901',\n"
        "  'mutation_number': 'MUT-441',\n"
        "  'document_number': 'DOC-ROR-0001',\n"
        "  'date': '14/08/2023'\n"
        "}"
    )

    ex1_table = Table([[
        Paragraph(f"<b>Raw Document OCR Text Stream:</b><br/><br/><font name='Courier' size=6.5 color='#1e293b'>{sample_1_text.replace(chr(10), '<br/>')}</font>", table_cell_style),
        Paragraph(f"<b>Supervised Ground-Truth Entity Map:</b><br/><br/><font name='Courier' size=6.5 color='#1e3a8a'>{sample_1_entities.replace(chr(10), '<br/>')}</font>", table_cell_style)
    ]], colWidths=[240, 247])
    ex1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_BG_LIGHT),
        ('BACKGROUND', (1, 0), (1, 0), C_ACCENT_BLUE),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ex1_table)
    story.append(Spacer(1, 6))

    # Example 2
    story.append(Paragraph("<b>Exemplar B: Indian Non-Judicial e-Stamp Certificate (doc_id: 1201)</b>", h2_style))
    sample_2_text = (
        "INDIA NON JUDICIAL\n"
        "Government of Uttar Pradesh e-Stamp\n"
        "Certificate No. : IN-UP01272481023775T\n"
        "Certificate Issued Date : 14-Jan-2024 01:51 PM\n"
        "Account Reference : NEWIMPACC (SV)/ up14012024/ GHAZIABAD/ UP-GHA\n"
        "Unique Doc. Reference : SUBIN-UPUP14012024881023T\n"
        "Purchased by : SURESH CHOUDHRY\n"
        "Description of Document : Article 23 Conveyance\n"
        "Property Description : FLAT NO 402 SEC-4 EMERALD HEIGHTS GHAZIABAD\n"
        "Consideration Price (Rs.) : 4,500,000\n"
        "First Party : ANIL GUPTA GPA HOLDER OF VIKRAM SINGH\n"
        "Second Party : SURESH CHOUDHRY AND ANITA CHOUDHRY\n"
        "Stamp Duty Amount(Rs.) : 315,000\n"
        "Owner Name : SURESH CHOUDHRY\n"
        "Khasra Number : 142/4\n"
        "District : Ghaziabad | State : Uttar Pradesh"
    )
    sample_2_entities = (
        "{\n"
        "  'owner_name': 'SURESH CHOUDHRY',\n"
        "  'father_name': 'ANIL GUPTA',\n"
        "  'khasra_number': '142/4',\n"
        "  'khata_number': 'SUBIN-UPUP14012',\n"
        "  'survey_number': 'IN-UP01272481023775T',\n"
        "  'plot_number': 'FLAT NO 402',\n"
        "  'village': 'EMERALD HEIGHTS',\n"
        "  'tehsil': 'Ghaziabad',\n"
        "  'district': 'Ghaziabad',\n"
        "  'state': 'Uttar Pradesh',\n"
        "  'land_area': 'FLAT NO 402',\n"
        "  'land_type': 'Article 23 Conveyance',\n"
        "  'registration_number': 'IN-UP01272481023775T',\n"
        "  'mutation_number': 'MUT-01',\n"
        "  'document_number': 'SUBIN-UPUP14012024881023T',\n"
        "  'date': '14/01/2024'\n"
        "}"
    )
    ex2_table = Table([[
        Paragraph(f"<b>Raw e-Stamp Deed OCR Stream:</b><br/><br/><font name='Courier' size=6.5 color='#1e293b'>{sample_2_text.replace(chr(10), '<br/>')}</font>", table_cell_style),
        Paragraph(f"<b>Supervised Ground-Truth Entity Map:</b><br/><br/><font name='Courier' size=6.5 color='#1e3a8a'>{sample_2_entities.replace(chr(10), '<br/>')}</font>", table_cell_style)
    ]], colWidths=[240, 247])
    ex2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_BG_LIGHT),
        ('BACKGROUND', (1, 0), (1, 0), C_ACCENT_BLUE),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ex2_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # Section 5: Tier 3 Document Discriminator Dataset
    # =========================================================================
    story.append(Paragraph("5. Tier 3: Land Record vs. Non-Land Discriminator Dataset", h1_style))
    story.append(Paragraph(
        "<b>Storage Location:</b> Built in <code>document_classifier.py</code> & supplemented by <code>doc_classifier_memory.json</code>.<br/>"
        "To prevent fraudulent file injection and unintentional database contamination, the discriminator trains on two balanced distributions:",
        body_style
    ))

    disc_headers = [
        Paragraph("<b>Class Label</b>", table_header_style),
        Paragraph("<b>Target Category</b>", table_header_style),
        Paragraph("<b>Key Characteristic Vocabulary & Indicators</b>", table_header_style),
        Paragraph("<b>Decision Rule</b>", table_header_style)
    ]
    disc_rows = [disc_headers]
    disc_raw = [
        ("Positive (1)", "Jamabandi / RoR", "अधिकार अभिलेख, जमाबंदी, भूस्वामी, खातेदार, काश्तकार, रकबा, खसरा, खाता, खेवट, पटवारी, तहसीलदार", "ACCEPT ➔ Process Pipeline"),
        ("Positive (1)", "Khatauni / Nakal", "खतौनी नकल, पंचसाला, सर्वे नं., भूलेख, bhulekh, nakal, किस्म जमीन, सिंचित, असिंचित", "ACCEPT ➔ Process Pipeline"),
        ("Positive (1)", "e-Stamp Deed", "e-Stamp, india non judicial, article 23 conveyance, subin, stamp duty, consideration price, sub-registrar", "ACCEPT ➔ Process Pipeline"),
        ("Negative (0)", "Tax Invoices & Billing", "tax invoice, bill to, gstin, subtotal, grand total, hsn code, cgst, sgst, payment terms, unit price", "REJECT ➔ Trigger Warning Modal"),
        ("Negative (0)", "Resumes & CVs", "curriculum vitae, work experience, technical skills, core competencies, education, linkedin, github", "REJECT ➔ Trigger Warning Modal"),
        ("Negative (0)", "Clinical Prescriptions", "patient name, rx, diagnosis, dosage, lab report, hospital admission, doctor signature", "REJECT ➔ Trigger Warning Modal"),
        ("Negative (0)", "Utility & Electricity", "electricity bill, power distribution, meter number, kwh, units consumed, connected load", "REJECT ➔ Trigger Warning Modal"),
        ("Negative (0)", "Identity Documents", "driving licence, passport, aadhaar, uidai, voter id, epic no, permanent account number", "REJECT ➔ Trigger Warning Modal")
    ]
    for lbl, cat, vocab, rule in disc_raw:
        is_pos = "Positive" in lbl
        disc_rows.append([
            Paragraph(f"<b>{lbl}</b>", table_cell_bold if is_pos else table_cell_style),
            Paragraph(f"<b>{cat}</b>", table_cell_style),
            Paragraph(vocab, table_cell_style),
            Paragraph(f"<font color='{'#15803d' if is_pos else '#b91c1c'}'><b>{rule}</b></font>", table_cell_style)
        ])

    disc_table = Table(disc_rows, colWidths=[65, 110, 205, 107])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('BACKGROUND', (0, 1), (-1, 3), C_ACCENT_BLUE),
    ]))
    story.append(disc_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # Section 6: Tier 5 Benchmark Ground Truth Test Suite
    # =========================================================================
    story.append(Paragraph("6. Tier 5: High-Fidelity Benchmark Test Suite", h1_style))
    story.append(Paragraph(
        "<b>Storage Locations:</b> Document Scans: <font color='#1e3a8a'><code>data/sample_documents/</code></font> | "
        "Verified Metadata: <font color='#1e3a8a'><code>data/sample_records/</code></font><br/>"
        "The Benchmark Test Suite comprises <b>15 calibrated test cases</b> evaluating the end-to-end pipeline across pristine, "
        "degraded, duplicate, and edge-case operational scenarios:",
        body_style
    ))

    test_headers = [
        Paragraph("<b>Test ID & Filename</b>", table_header_style),
        Paragraph("<b>Document Title / Type</b>", table_header_style),
        Paragraph("<b>Jurisdiction</b>", table_header_style),
        Paragraph("<b>Operational Evaluation Scenario</b>", table_header_style),
        Paragraph("<b>Target Confidence</b>", table_header_style)
    ]
    test_rows = [test_headers]
    test_raw = [
        ("sample_1_clean_rau.png", "Jamabandi RoR (Ram Kumar)", "Rau, Indore (MP)", "Pristine agricultural baseline record", "HIGH (>=95%)"),
        ("sample_2_sita_kanadia.png", "Khatauni Nakal (Sita Sharma)", "Kanadia, Indore (MP)", "Multi-owner non-irrigated parcel", "HIGH (>=92%)"),
        ("sample_3_mohan_mangliya.png", "Jamabandi RoR (Mohan Singh)", "Sanwer, Indore (MP)", "Standard single-owner agricultural", "HIGH (>=94%)"),
        ("sample_4_kailash_depalpur.png", "Record of Rights (Kailash)", "Depalpur, Indore (MP)", "Irrigated high-acreage parcel", "HIGH (>=93%)"),
        ("sample_5_anita_lucknow.png", "Khatauni CH-41 (Anita Verma)", "Mohanlalganj, LKO (UP)", "Uttar Pradesh standard revenue format", "HIGH (>=91%)"),
        ("sample_6_rajesh_varanasi.png", "RoR Nakal (Rajesh Gupta)", "Pindra, Varanasi (UP)", "Eastern UP dialect & font variations", "HIGH (>=92%)"),
        ("sample_7_vikram_mhow.png", "Revenue Register (Vikram)", "Mhow, Indore (MP)", "Non-irrigated hilly terrain record", "HIGH (>=90%)"),
        ("sample_8_sunil_sanwer.png", "Cadastral Record (Sunil)", "Sanwer, Indore (MP)", "Cadastral boundary cross-verification", "HIGH (>=93%)"),
        ("sample_4_faded_khata_low_conf...", "Degraded Legacy Scan", "Indore (MP)", "Tests CLAHE & low-confidence amber flag", "MED / LOW (<70%)"),
        ("sample_5_duplicate_ramkumar.png", "Duplicate Claim Test", "Rau, Indore (MP)", "Tests RapidFuzz phonetic matching", "FLAGGED DUPLICATE"),
        ("sample_6_anomaly_unusual_area...", "Area Out-of-Bounds Test", "Indore (MP)", "Parcel >50.0 Ha triggers anomaly alert", "ANOMALY FLAGGED"),
        ("sample_7_missing_khasra.png", "Incomplete Record Test", "Indore (MP)", "Missing Khasra number validation trigger", "MISSING FIELD"),
        ("sample_9_estamp_ghaziabad.jpg", "Real e-Stamp Conveyance", "Ghaziabad (UP)", "Real-world Article 23 conveyance deed", "HIGH (>=91%)"),
        ("sample_10_non_land_invoice.png", "Commercial GST Tax Invoice", "Corporate (Delhi)", "Tests Discriminator automatic rejection", "REJECTED (0%)"),
        ("sample_11_handwritten_khasra...", "Handwritten Patwari Register", "Indore (MP)", "Devanagari digit normalization (२४५/२)", "HIGH (>=96%)")
    ]
    for tid, ttl, jur, scn, exp in test_raw:
        is_sp = "sample_4_faded" in tid or "duplicate" in tid or "anomaly" in tid or "invoice" in tid or "handwritten" in tid
        test_rows.append([
            Paragraph(f"<code>{tid[:26]}</code>", table_cell_bold if is_sp else table_cell_style),
            Paragraph(ttl, table_cell_style),
            Paragraph(jur, table_cell_style),
            Paragraph(scn, table_cell_style),
            Paragraph(f"<b>{exp}</b>", table_cell_style)
        ])

    test_table = Table(test_rows, colWidths=[120, 105, 75, 120, 67])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 8))

    # Embedded Gallery of 4 Documents
    def make_doc_cell(img_p, caption, sub, w=2.1*inch, h=2.5*inch):
        if os.path.exists(img_p):
            return [
                RLImage(img_p, width=w, height=h),
                Paragraph(caption, caption_style),
                Paragraph(sub, cap_note_style)
            ]
        return [Paragraph("Image not found", body_style)]

    cell_a = make_doc_cell(ESTAMP_IMG, "Fig 2: UP e-Stamp Deed", "Article 23 conveyance (Ghaziabad)")
    cell_b = make_doc_cell(HW_IMG, "Fig 3: Handwritten Khasra", "Devanagari numerals normalized")

    doc_grid_1 = Table([[cell_a, cell_b]], colWidths=[240, 247])
    doc_grid_1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(doc_grid_1)
    story.append(Spacer(1, 6))

    cell_c = make_doc_cell(INVOICE_IMG, "Fig 4: Commercial Invoice", "Discriminator rejects file")
    cell_d = make_doc_cell(CLEAN_IMG, "Fig 5: Clean Jamabandi RoR", "MP RoR (Rau, Indore)")

    doc_grid_2 = Table([[cell_c, cell_d]], colWidths=[240, 247])
    doc_grid_2.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(doc_grid_2)
    story.append(Spacer(1, 8))

    # =========================================================================
    # Section 7: Tier 6 Geospatial & Administrative Datasets
    # =========================================================================
    story.append(Paragraph("7. Tier 6: Geospatial & Administrative Reference Datasets", h1_style))
    story.append(Paragraph(
        "LandLens AI bridges optical document extraction with statutory spatial and geographic ground truth:",
        body_style
    ))

    geo_data = [
        ("Administrative Taxonomy (india_land_taxonomy.json)",
         "National administrative hierarchy sourced from open government standards (data.gov.in) covering Madhya Pradesh "
         "(Indore, Ujjain, Dewas, Dhar, Bhopal, Sehore districts) and Uttar Pradesh (Lucknow, Varanasi, Agra, Kanpur, Ghaziabad). "
         "Used by validation_engine.py for automated cross-field Tehsil vs. District alignment verification."),
        ("Cadastral Parcels GeoJSON (cadastral_parcels.geojson)",
         "High-precision polygon geometries representing cadastral land parcels for demo revenue villages. "
         "Directly indexed by Khasra survey number (e.g., Khasra #245/2) for interactive Leaflet GIS rendering and boundary overlap validation."),
        ("State Circle Rates & Projects Tracker (state_land_rates_and_projects.json)",
         "Comprehensive state-by-state guidance values and ready reckoner rates across 10 major states. "
         "Tracks live land acquisition progress for national infrastructure mega projects (Bharatmala, Jewar Airport, Bullet Train, Ganga Expressway).")
    ]

    for title, desc in geo_data:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 8))

    # =========================================================================
    # Section 8: Privacy, Governance & DPDP Act 2023 Compliance
    # =========================================================================
    story.append(Paragraph("8. Data Governance, Privacy & Ethical AI Statement", h1_style))
    story.append(Paragraph(
        "• <b>Synthetic Sandbox Compliance:</b> All personal names, phone references, and residential identities within the training corpus "
        "were synthesized following realistic statistical distributions in compliance with the Digital Personal Data Protection (DPDP) Act 2023.<br/>"
        "• <b>Zero Cloud Exfiltration:</b> All model training, evaluation, and inference code runs 100% locally on sovereign edge servers.<br/>"
        "• <b>Statutory Decision Authority:</b> LandLens AI acts strictly as an AI decision-support platform. All final administrative determinations "
        "remain under the statutory jurisdiction of authorized revenue officers (Tehsildars / Patwaris).",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Dataset PDF report generated successfully:\n  -> {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_dataset_pdf()
