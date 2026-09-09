import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def generate_synthetic_documents():
    """
    Generates realistic synthetic Indian Land Record documents (PNG images + metadata)
    tailored for testing and demonstrating SIH26018 LandLens AI capabilities.
    """
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
    records_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_records"))

    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(records_dir, exist_ok=True)

    samples = [
        {
            "filename": "sample_1_clean_rau.png",
            "title": "RECORD OF RIGHTS / अधिकार अभिलेख",
            "faded": False,
            "fields": {
                "owner_name": "Ram Kumar",
                "father_name": "Shyam Lal",
                "khasra_number": "245/2",
                "khata_number": "112",
                "survey_number": "SN-882",
                "plot_number": "P-12",
                "village": "Rau",
                "tehsil": "Rau",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "1.25 Hectare",
                "land_type": "Agricultural (Irrigated)",
                "registration_number": "MP-IND-2023-9901",
                "mutation_number": "MUT-441",
                "document_number": "DOC-JAMABANDI-01",
                "date": "14/08/2023",
            },
            "description": "Standard high-confidence bilingual Jamabandi record (Rau Village)",
        },
        {
            "filename": "sample_2_sita_kanadia.png",
            "title": "KHATONI NAKAL / खतौनी नकल",
            "faded": False,
            "fields": {
                "owner_name": "Sita Sharma",
                "father_name": "Rameshwar Sharma",
                "khasra_number": "318/1",
                "khata_number": "207",
                "survey_number": "SN-402",
                "plot_number": "P-04",
                "village": "Kanadia",
                "tehsil": "Kanadia",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "2.10 Hectare",
                "land_type": "Agricultural (Non-Irrigated)",
                "registration_number": "MP-IND-2022-8104",
                "mutation_number": "MUT-129",
                "document_number": "DOC-JAMABANDI-02",
                "date": "05/11/2022",
            },
            "description": "Bilingual land register for Sita Sharma (Kanadia Village)",
        },
        {
            "filename": "sample_3_mohan_mangliya.png",
            "title": "KHASRA PANCHSALA / खसरा पंचसाला",
            "faded": False,
            "fields": {
                "owner_name": "Mohan Singh",
                "father_name": "Pratap Singh",
                "khasra_number": "102/3",
                "khata_number": "89",
                "survey_number": "SN-109",
                "plot_number": "P-33",
                "village": "Mangliya",
                "tehsil": "Sanwer",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "0.85 Hectare",
                "land_type": "Agricultural (Irrigated)",
                "registration_number": "MP-IND-2021-3329",
                "mutation_number": "MUT-884",
                "document_number": "DOC-JAMABANDI-03",
                "date": "22/01/2021",
            },
            "description": "Mohan Singh record (Mangliya Village)",
        },
        {
            "filename": "sample_4_faded_khata_low_confidence.png",
            "title": "LEGACY RECORD / पुराना भू-अभिलेख",
            "faded": True,  # Simulated faded ink triggering low confidence
            "fields": {
                "owner_name": "Gopal Das",
                "father_name": "Narayan Das",
                "khasra_number": "512/4",
                "khata_number": "39",  # Deliberately degraded in rendering
                "survey_number": "SN-771",
                "plot_number": "P-09",
                "village": "Rau",
                "tehsil": "Rau",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "1.80 Hectare",
                "land_type": "Agricultural",
                "registration_number": "MP-IND-2018-4421",
                "mutation_number": "MUT-302",
                "document_number": "DOC-JAMABANDI-04",
                "date": "10/04/2018",
            },
            "description": "Faded historical document triggering low confidence and human verification",
        },
        {
            "filename": "sample_5_duplicate_ramkumar.png",
            "title": "MUTATION REGISTER / नामांतरण पंजी",
            "faded": False,
            "fields": {
                "owner_name": "Ramkumar",  # Fuzzy duplicate of Ram Kumar
                "father_name": "Shyam Lal",
                "khasra_number": "245/2",  # Same Khasra in Rau
                "khata_number": "112",
                "survey_number": "SN-882",
                "plot_number": "P-12",
                "village": "Rau",
                "tehsil": "Rau",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "1.25 Hectare",
                "land_type": "Agricultural",
                "registration_number": "MP-IND-2024-1188",
                "mutation_number": "MUT-992",
                "document_number": "DOC-MUT-05",
                "date": "12/02/2024",
            },
            "description": "Overlapping record with same Khasra 245/2 triggering Fuzzy Duplicate Warning",
        },
        {
            "filename": "sample_6_anomaly_unusual_area.png",
            "title": "LAND REGISTRY / भूमि पंजीयन",
            "faded": False,
            "fields": {
                "owner_name": "Kailash Chand",
                "father_name": "Deepak Chand",
                "khasra_number": "409/1",
                "khata_number": "601",
                "survey_number": "SN-339",
                "plot_number": "P-88",
                "village": "Kanadia",
                "tehsil": "Kanadia",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "150.0 Hectare",  # Anomaly: Exceeds 50 Ha threshold
                "land_type": "Commercial / Mixed",
                "registration_number": "MP-IND-2023-5512",
                "mutation_number": "MUT-761",
                "document_number": "DOC-REG-06",
                "date": "19/09/2023",
            },
            "description": "Record with unusual land area (150 Ha) triggering Range Anomaly Warning",
        },
        {
            "filename": "sample_7_missing_khasra.png",
            "title": "INCOMPLETE APPLICATION / अपूर्ण भू-अभिलेख",
            "faded": False,
            "fields": {
                "owner_name": "Vikram Sethi",
                "father_name": "Harish Sethi",
                "khasra_number": "",  # Missing Required Field
                "khata_number": "415",
                "survey_number": "",
                "plot_number": "P-19",
                "village": "Mangliya",
                "tehsil": "Sanwer",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "land_area": "0.95 Hectare",
                "land_type": "Agricultural",
                "registration_number": "MP-IND-2023-8871",
                "mutation_number": "",
                "document_number": "DOC-INC-07",
                "date": "08/03/2023",
            },
            "description": "Incomplete document with missing Khasra number triggering Missing Field Error",
        },
    ]

    for item in samples:
        img_path = os.path.join(docs_dir, item["filename"])
        _render_document_image(item, img_path)

        # Save sidecar ground truth text for automated benchmarking and testing
        txt_path = os.path.splitext(img_path)[0] + "_ground_truth.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            for k, v in item["fields"].items():
                f.write(f"{k}: {v}\n")

        # Save metadata json
        json_path = os.path.join(records_dir, os.path.splitext(item["filename"])[0] + ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2)

    print(f">> Successfully generated {len(samples)} synthetic land record documents in {docs_dir}")


def _render_document_image(data: dict, output_path: str):
    """Renders high-resolution synthetic Indian land record register image with border and stamp."""
    width, height = 1000, 1400
    bg_color = (250, 248, 240) if data.get("faded") else (255, 255, 255)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Outer decorative border
    draw.rectangle([25, 25, width - 25, height - 25], outline=(40, 50, 60), width=3)
    draw.rectangle([35, 35, width - 35, height - 35], outline=(100, 110, 120), width=1)

    # Header section
    draw.text((width // 2 - 190, 60), "GOVERNMENT OF MADHYA PRADESH", fill=(20, 30, 40))
    draw.text((width // 2 - 150, 85), "REVENUE DEPARTMENT / राजस्व विभाग", fill=(30, 40, 50))
    draw.text((width // 2 - 180, 120), data["title"], fill=(150, 30, 30))
    draw.line([50, 155, width - 50, 155], fill=(40, 50, 60), width=2)

    # Form Fields Table
    y = 180
    field_labels = [
        ("Owner Name / मालिक का नाम", "owner_name"),
        ("Father's Name / पिता का नाम", "father_name"),
        ("Khasra Number / खसरा नं.", "khasra_number"),
        ("Khata Number / खाता नं.", "khata_number"),
        ("Survey Number / सर्वे नं.", "survey_number"),
        ("Plot Number / प्लॉट नं.", "plot_number"),
        ("Village / ग्राम", "village"),
        ("Tehsil / तहसील", "tehsil"),
        ("District / जिला", "district"),
        ("State / राज्य", "state"),
        ("Land Area / रकबा", "land_area"),
        ("Land Type / भूमि प्रकार", "land_type"),
        ("Registration No / पंजीकरण क्रमांक", "registration_number"),
        ("Mutation No / नामांतरण क्रमांक", "mutation_number"),
        ("Document No / दस्तावेज संख्या", "document_number"),
        ("Date / दिनांक", "date"),
    ]

    for label, key in field_labels:
        val = data["fields"].get(key, "")
        text_color = (70, 70, 70)
        if data.get("faded") and key == "khata_number":
            # Simulate faded text
            text_color = (215, 215, 215)

        draw.text((60, y), f"{label} :", fill=(30, 40, 60))
        draw.text((450, y), str(val), fill=text_color)
        draw.line([50, y + 30, width - 50, y + 30], fill=(220, 220, 220), width=1)
        y += 50

    # Official Seal / Watermark
    seal_x, seal_y = width - 250, height - 250
    draw.ellipse([seal_x, seal_y, seal_x + 180, seal_y + 180], outline=(180, 40, 40), width=3)
    draw.ellipse([seal_x + 10, seal_y + 10, seal_x + 170, seal_y + 170], outline=(180, 40, 40), width=1)
    draw.text((seal_x + 35, seal_y + 55), "TEHSILDAR", fill=(180, 40, 40))
    draw.text((seal_x + 30, seal_y + 80), "DIST. INDORE", fill=(180, 40, 40))
    draw.text((seal_x + 40, seal_y + 105), "SEAL / मोहर", fill=(180, 40, 40))

    # Officer Signature
    draw.text((100, height - 120), "Verified & Digitized under SIH26018", fill=(100, 100, 100))
    draw.line([100, height - 140, 300, height - 140], fill=(60, 60, 60), width=1)
    draw.text((100, height - 165), "Signature of Revenue Officer", fill=(50, 50, 50))

    # Synthetic noise if faded
    if data.get("faded"):
        arr = np.array(img)
        noise = np.random.normal(0, 8, arr.shape).astype(np.int16)
        noisy_arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(noisy_arr)

    img.save(output_path)


def _render_invoice_image(output_path: str):
    """Renders a realistic commercial Tax Invoice image to test discriminator rejection."""
    width, height = 1000, 1400
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Clean corporate border
    draw.rectangle([30, 30, width - 30, height - 30], outline=(180, 190, 200), width=2)

    # Company Header
    draw.text((60, 55), "ACME ENTERPRISES PRIVATE LIMITED", fill=(20, 35, 60))
    draw.text((60, 80), "Plot 45, Okhla Industrial Area, Phase III, New Delhi - 110020", fill=(100, 110, 120))
    draw.text((60, 100), "GSTIN: 07AAAAA0000A1Z5 | PAN: AAAAA0000A | CIN: U72200DL2018PTC334101", fill=(100, 110, 120))

    # Big Tax Invoice Header
    draw.rectangle([width - 320, 50, width - 50, 115], fill=(240, 245, 250), outline=(200, 215, 230))
    draw.text((width - 300, 65), "TAX INVOICE / बिल", fill=(25, 45, 80))
    draw.text((width - 300, 90), "ORIGINAL FOR RECIPIENT", fill=(120, 130, 140))

    draw.line([50, 135, width - 50, 135], fill=(210, 220, 230), width=2)

    # Billing and Invoice Meta
    y = 155
    draw.text((60, y), "BILL TO / INVOICE RECIPIENT:", fill=(30, 40, 50))
    draw.text((60, y + 25), "Tech Global Solutions LLP", fill=(50, 60, 70))
    draw.text((60, y + 45), "Cyber City, Tower B, 8th Floor, Gurugram, HR", fill=(90, 100, 110))
    draw.text((60, y + 65), "GSTIN: 06BBBBB1111B2Z6", fill=(90, 100, 110))

    draw.text((550, y), "Invoice Number : INV-2024-8891", fill=(30, 40, 50))
    draw.text((550, y + 25), "Invoice Date   : 15/03/2024", fill=(50, 60, 70))
    draw.text((550, y + 45), "Payment Terms  : Net 30 Days", fill=(90, 100, 110))
    draw.text((550, y + 65), "Due Date       : 15/04/2024", fill=(90, 100, 110))

    # Line Item Table
    table_y = 265
    draw.rectangle([50, table_y, width - 50, table_y + 35], fill=(40, 60, 90))
    draw.text((65, table_y + 10), "#", fill=(255, 255, 255))
    draw.text((110, table_y + 10), "ITEM & SERVICE DESCRIPTION", fill=(255, 255, 255))
    draw.text((550, table_y + 10), "HSN/SAC", fill=(255, 255, 255))
    draw.text((660, table_y + 10), "QTY", fill=(255, 255, 255))
    draw.text((740, table_y + 10), "RATE (INR)", fill=(255, 255, 255))
    draw.text((860, table_y + 10), "AMOUNT (INR)", fill=(255, 255, 255))

    row_y = table_y + 50
    items = [
        ("1", "Enterprise Cloud Hosting & Database Subscription", "998313", "1", "3,500.00", "3,500.00"),
        ("2", "Managed API Gateway Routing & SSL Support", "998314", "1", "1,000.00", "1,000.00"),
    ]
    for num, desc, hsn, qty, rate, amt in items:
        draw.text((65, row_y), num, fill=(60, 70, 80))
        draw.text((110, row_y), desc, fill=(30, 40, 50))
        draw.text((550, row_y), hsn, fill=(80, 90, 100))
        draw.text((670, row_y), qty, fill=(80, 90, 100))
        draw.text((740, row_y), rate, fill=(80, 90, 100))
        draw.text((860, row_y), amt, fill=(30, 40, 50))
        draw.line([50, row_y + 30, width - 50, row_y + 30], fill=(235, 240, 245), width=1)
        row_y += 45

    # Summary Totals Box
    sum_y = row_y + 30
    draw.line([500, sum_y, width - 50, sum_y], fill=(180, 190, 200), width=1)
    draw.text((550, sum_y + 10), "Subtotal:", fill=(80, 90, 100))
    draw.text((860, sum_y + 10), "Rs. 4,500.00", fill=(40, 50, 60))

    draw.text((550, sum_y + 35), "CGST (9.0%):", fill=(80, 90, 100))
    draw.text((860, sum_y + 35), "Rs. 405.00", fill=(40, 50, 60))

    draw.text((550, sum_y + 60), "SGST (9.0%):", fill=(80, 90, 100))
    draw.text((860, sum_y + 60), "Rs. 405.00", fill=(40, 50, 60))

    draw.rectangle([500, sum_y + 90, width - 50, sum_y + 135], fill=(245, 250, 255), outline=(180, 205, 230))
    draw.text((520, sum_y + 103), "Total Amount Due:", fill=(20, 35, 70))
    draw.text((840, sum_y + 103), "Rs. 5,310.00", fill=(20, 35, 70))

    # Bank Details & Signature
    draw.text((60, height - 260), "Bank Name      : HDFC Bank Limited", fill=(100, 110, 120))
    draw.text((60, height - 240), "Account No     : 50200049281729", fill=(100, 110, 120))
    draw.text((60, height - 220), "IFSC Code      : HDFC0001204", fill=(100, 110, 120))

    draw.text((width - 320, height - 200), "For Acme Enterprises Pvt Ltd", fill=(60, 70, 80))
    draw.line([width - 320, height - 140, width - 80, height - 140], fill=(100, 110, 120), width=1)
    draw.text((width - 300, height - 130), "Authorized Signatory", fill=(100, 110, 120))

    img.save(output_path)


def _render_handwritten_khasra_image(output_path: str):
    """Renders a realistic handwritten-style Devanagari Khasra revenue register."""
    width, height = 1000, 1400
    # Antique register paper background
    img = Image.new("RGB", (width, height), color=(248, 245, 235))
    draw = ImageDraw.Draw(img)

    # Ruled register notebook lines
    for line_y in range(150, height - 100, 35):
        draw.line([40, line_y, width - 40, line_y], fill=(225, 235, 240), width=1)

    # Double ledger margins
    draw.line([120, 40, 120, height - 40], fill=(240, 190, 190), width=1)
    draw.line([125, 40, 125, height - 40], fill=(240, 190, 190), width=1)

    # Header in traditional Devanagari ink
    draw.text((width // 2 - 180, 50), "मध्य प्रदेश शासन - राजस्व विभाग", fill=(20, 30, 60))
    draw.text((width // 2 - 200, 80), "अधिकार अभिलेख (हस्तलिखित खसरा पंजी)", fill=(30, 40, 70))
    draw.line([60, 120, width - 60, 120], fill=(80, 60, 40), width=2)

    # Handwritten register entries (dark ink blue)
    ink_color = (25, 40, 95)
    entries = [
        ("मालिक का नाम / Owner Name", "राम कुमार (Ram Kumar)"),
        ("पिता का नाम / Father's Name", "श्याम लाल (Shyam Lal)"),
        ("खसरा नं. / Khasra Number", "२४५/२ (245/2)"),
        ("खाता नं. / Khata Number", "११२ (112)"),
        ("सर्वे नं. / Survey Number", "८८२ (SN-882)"),
        ("प्लॉट नं. / Plot Number", "१२ (P-12)"),
        ("ग्राम / Village", "राऊ (Rau)"),
        ("तहसील / Tehsil", "राऊ (Rau)"),
        ("जिला / District", "इंदौर (Indore)"),
        ("राज्य / State", "मध्य प्रदेश (Madhya Pradesh)"),
        ("रकबा / Land Area", "१.२५ हेक्टेयर (1.25 Hectare)"),
        ("भूमि प्रकार / Land Type", "कृषि सिंचित (Agricultural)"),
        ("पंजीकरण क्रमांक / Reg No", "MP-IND-2023-9901"),
        ("नामांतरण क्रमांक / Mutation No", "४४१ (MUT-441)"),
        ("दस्तावेज संख्या / Doc No", "DOC-HANDWRITTEN-11"),
        ("दिनांक / Date", "१४/०८/२०२३ (14/08/2023)"),
    ]

    y = 150
    for label, val in entries:
        draw.text((140, y + 8), f"{label} :", fill=(60, 50, 40))
        draw.text((500, y + 8), val, fill=ink_color)
        y += 45

    # Circular revenue seal in violet/purple ink
    seal_x, seal_y = width - 260, height - 280
    draw.ellipse([seal_x, seal_y, seal_x + 160, seal_y + 160], outline=(110, 40, 140), width=3)
    draw.ellipse([seal_x + 8, seal_y + 8, seal_x + 152, seal_y + 152], outline=(110, 40, 140), width=1)
    draw.text((seal_x + 35, seal_y + 45), "तहसीलदार", fill=(110, 40, 140))
    draw.text((seal_x + 30, seal_y + 70), "जिला इंदौर", fill=(110, 40, 140))
    draw.text((seal_x + 40, seal_y + 95), "राजस्व मोहर", fill=(110, 40, 140))

    # Patwari manual signature
    draw.text((150, height - 120), "हस्ताक्षर पटवारी हल्का राऊ (Patwari Sign)", fill=ink_color)
    draw.line([150, height - 130, 380, height - 130], fill=ink_color, width=1)

    # Organic aging noise
    arr = np.array(img)
    noise = np.random.normal(0, 5, arr.shape).astype(np.int16)
    noisy_arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(noisy_arr)

    img.save(output_path)


if __name__ == "__main__":
    generate_synthetic_documents()
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_documents"))
    _render_invoice_image(os.path.join(docs_dir, "sample_10_non_land_invoice.png"))
    _render_handwritten_khasra_image(os.path.join(docs_dir, "sample_11_handwritten_khasra.png"))
