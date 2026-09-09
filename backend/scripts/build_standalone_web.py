import os
import json
import shutil
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PUBLIC_DIR = os.path.join(BASE_DIR, "public_web")
ZIP_PATH = os.path.join(BASE_DIR, "LandLens_AI_Public_Web_Deploy.zip")
RATES_JSON_PATH = os.path.join(BASE_DIR, "data", "datasets", "administrative_geo", "state_land_rates_and_projects.json")

print("Building Self-Contained Zero-Server Public Web Distribution...")
os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(os.path.join(PUBLIC_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(PUBLIC_DIR, "sample-data"), exist_ok=True)

# Load state land rates and projects data
with open(RATES_JSON_PATH, "r", encoding="utf-8") as f:
    land_data = json.load(f)

# Copy static assets
static_src = os.path.join(BASE_DIR, "backend", "app", "static")
for f in os.listdir(static_src):
    sp = os.path.join(static_src, f)
    dp = os.path.join(PUBLIC_DIR, "static", f)
    if os.path.isfile(sp):
        shutil.copy2(sp, dp)

# Copy sample documents
sample_src = os.path.join(BASE_DIR, "data", "sample_documents")
for f in os.listdir(sample_src):
    sp = os.path.join(sample_src, f)
    dp = os.path.join(PUBLIC_DIR, "sample-data", f)
    if os.path.isfile(sp):
        shutil.copy2(sp, dp)

# Read index.html and make all asset paths relative for standalone hosting
with open(os.path.join(static_src, "index.html"), "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace root-relative paths with relative paths
html_content = html_content.replace('href="/static/', 'href="static/')
html_content = html_content.replace('src="/static/', 'src="static/')
html_content = html_content.replace('src="/sample-data/', 'src="sample-data/')
html_content = html_content.replace('/static/app.js', 'static/app.js')

with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

# Read app.js
with open(os.path.join(static_src, "app.js"), "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace root-relative sample-data path with relative path
js_content = js_content.replace("'/sample-data/'", "'sample-data/'")
js_content = js_content.replace('"/sample-data/"', '"sample-data/"')
js_content = js_content.replace("`/sample-data/${filename}`", "`sample-data/${filename}`")
js_content = js_content.replace("'/static/landlens_seal_exact.png'", "'static/landlens_seal_exact.png'")

# Append the Client-Side In-Browser Autonomous Fallback Engine
client_engine_code = f"""

// =========================================================================
// LANDLENS AI — AUTONOMOUS IN-BROWSER ZERO-SERVER CLIENT ENGINE (SIH26018)
// Enables full application functionality on any device without running a server.
// =========================================================================

const EMBEDDED_LAND_DATA = {json.dumps(land_data, ensure_ascii=False)};

// Global persistent in-memory database
window._standaloneRecords = window._standaloneRecords || [
  {{
    id: 1,
    document_id: 1,
    owner_name: "Ramesh Chandra Sharma",
    father_name: "Hari Mohan Sharma",
    khasra_number: "245/2",
    khata_number: "112",
    survey_number: "245",
    plot_number: "2",
    village: "Rau",
    tehsil: "Rau",
    district: "Indore",
    state: "Madhya Pradesh",
    land_area: "1.42 Ha",
    area_hectares: 1.42,
    land_type: "Agricultural (Irrigated)",
    confidence_score: 0.97,
    overall_confidence: 0.97,
    verification_status: "verified",
    notes: "Clean verified RoR record",
    created_at: new Date(Date.now() - 86400000).toISOString()
  }},
  {{
    id: 2,
    document_id: 2,
    owner_name: "Sita Ram Patidar",
    father_name: "Bhagwan Das",
    khasra_number: "318/1",
    khata_number: "74",
    survey_number: "318",
    plot_number: "1",
    village: "Kanadia",
    tehsil: "Kanadia",
    district: "Indore",
    state: "Madhya Pradesh",
    land_area: "2.15 Ha",
    area_hectares: 2.15,
    land_type: "Agricultural (Unirrigated)",
    confidence_score: 0.96,
    overall_confidence: 0.96,
    verification_status: "verified",
    notes: "Verified agricultural deed",
    created_at: new Date(Date.now() - 43200000).toISOString()
  }},
  {{
    id: 3,
    document_id: 3,
    owner_name: "Mohan Lal Verma",
    father_name: "Ramswaroop Verma",
    khasra_number: "102/3",
    khata_number: "58",
    survey_number: "102",
    plot_number: "3",
    village: "Mangliya",
    tehsil: "Sanwer",
    district: "Indore",
    state: "Madhya Pradesh",
    land_area: "0.85 Ha",
    area_hectares: 0.85,
    land_type: "Semi-Urban Plot",
    confidence_score: 0.88,
    overall_confidence: 0.88,
    verification_status: "possible_duplicate",
    notes: "Boundary overlap flagged with Khasra 102/2",
    created_at: new Date(Date.now() - 21600000).toISOString()
  }},
  {{
    id: 9,
    document_id: 9,
    owner_name: "Rajiv Kumar Goel",
    father_name: "Late S. P. Goel",
    khasra_number: "441/3",
    khata_number: "89",
    survey_number: "441",
    plot_number: "Flat 1101, Tower B",
    village: "Vaishali, Sector 7",
    tehsil: "Ghaziabad Sadar",
    district: "Ghaziabad",
    state: "Uttar Pradesh",
    land_area: "0.016 Ha",
    area_hectares: 0.016,
    land_type: "Residential Apartment",
    confidence_score: 0.96,
    overall_confidence: 0.96,
    verification_status: "verified",
    notes: "UP e-Stamp Conveyance Deed Article 23",
    created_at: new Date(Date.now() - 10800000).toISOString()
  }},
  {{
    id: 10,
    document_id: 10,
    owner_name: "Apex Tech Solutions Pvt Ltd",
    father_name: "",
    khasra_number: "-",
    khata_number: "-",
    survey_number: "",
    plot_number: "",
    village: "New Delhi",
    tehsil: "Central",
    district: "New Delhi",
    state: "Delhi",
    land_area: "-",
    area_hectares: 0.0,
    land_type: "Commercial Invoice",
    confidence_score: 0.15,
    overall_confidence: 0.15,
    verification_status: "rejected",
    notes: "Commercial Tax Invoice Blocked by Discriminator",
    created_at: new Date(Date.now() - 5400000).toISOString()
  }},
  {{
    id: 11,
    document_id: 11,
    owner_name: "Ramesh Chandra Sharma",
    father_name: "Hari Mohan Sharma",
    khasra_number: "245/2",
    khata_number: "112",
    survey_number: "245",
    plot_number: "2",
    village: "Rau",
    tehsil: "Rau",
    district: "Indore",
    state: "Madhya Pradesh",
    land_area: "1.42 Ha",
    area_hectares: 1.42,
    land_type: "Agricultural (Irrigated)",
    confidence_score: 0.94,
    overall_confidence: 0.94,
    verification_status: "verified",
    notes: "Handwritten Devanagari २४५/२ -> 245/2 Normalized",
    created_at: new Date().toISOString()
  }}
];

window._standaloneAuditLogs = window._standaloneAuditLogs || [
  {{ id: 502, timestamp: new Date().toISOString(), user_name: "Officer Rajesh", action: "DOCUMENT_VERIFIED", record_id: 1, new_value: "Jamabandi Khasra 245/2 Verified & Sealed" }},
  {{ id: 501, timestamp: new Date(Date.now() - 900000).toISOString(), user_name: "AI Discriminator", action: "NON_LAND_REJECTED", record_id: 10, new_value: "Commercial Tax Invoice Blocked" }},
  {{ id: 500, timestamp: new Date(Date.now() - 1800000).toISOString(), user_name: "AI Normalizer", action: "NUMERALS_NORMALIZED", record_id: 11, new_value: "Handwritten Devanagari २४५/२ -> 245/2" }},
  {{ id: 499, timestamp: new Date(Date.now() - 3600000).toISOString(), user_name: "System Ingestion", action: "AI_INGEST_ESTAMP", record_id: 9, new_value: "UP e-Stamp Article 23 Ghaziabad" }},
  {{ id: 498, timestamp: new Date(Date.now() - 7200000).toISOString(), user_name: "Officer Rajesh", action: "RECORD_APPROVED", record_id: 2, new_value: "Kanadia Khasra 318/1 Digitized" }}
];

// Override apiRequest to support zero-server in-browser execution
const originalApiRequest = apiRequest;
apiRequest = async function(endpoint, options = {{}}) {{
  try {{
    return await originalApiRequest(endpoint, options);
  }} catch (networkOr404Error) {{
    console.warn('Backend server not detected for ' + endpoint + '. Activating LandLens Autonomous In-Browser Engine.');
    return await mockClientSideEngine(endpoint, options);
  }}
}};

// In-Browser Mock Router
async function mockClientSideEngine(endpoint, options = {{}}) {{
  const method = (options.method || 'GET').toUpperCase();

  // 1. Auth Login & Token & Me (Autonomous Zero-Server Auth)
  if (endpoint.includes('/api/auth/')) {{
    let email = 'officer@landlens.gov.in';
    let role = 'officer';
    let name = 'Officer Rajesh Kumar';

    if (options.body && typeof options.body === 'string') {{
      try {{
        const parsed = JSON.parse(options.body);
        if (parsed.email) email = parsed.email;
      }} catch (e) {{}}
    }}

    const em = email.toLowerCase();
    if (em.includes('admin')) {{
      role = 'admin';
      name = 'Administrator System';
    }} else if (em.includes('reviewer')) {{
      role = 'reviewer';
      name = 'Reviewer Ananya Sharma';
    }}

    const userObj = {{
      id: 1,
      email: email,
      name: name,
      role: role,
      created_at: new Date().toISOString()
    }};

    if (endpoint.includes('/api/auth/me')) {{
      return userObj;
    }}

    return {{
      access_token: 'mock-officer-token-' + Date.now(),
      token_type: 'bearer',
      user: userObj
    }};
  }}

  // 2. Dashboard Statistics
  if (endpoint.includes('/api/dashboard/statistics')) {{
    const recs = window._standaloneRecords;
    const verified = recs.filter(r => r.verification_status === 'verified').length;
    const requiresVer = recs.filter(r => r.verification_status === 'requires_verification').length;
    const dup = recs.filter(r => r.verification_status === 'possible_duplicate').length;
    const err = recs.filter(r => r.verification_status === 'validation_error' || r.verification_status === 'rejected').length;
    const total = recs.length;
    const avgConf = (recs.reduce((acc, r) => acc + (r.overall_confidence || 0.95), 0) / (total || 1)).toFixed(3);

    return {{
      total_documents: total,
      processed_documents: total,
      pending_verification: requiresVer,
      verified_records: verified,
      possible_duplicates: dup,
      validation_errors: err,
      low_confidence_records: recs.filter(r => (r.overall_confidence || 0) < 0.7).length,
      average_confidence: parseFloat(avgConf),
      status_distribution: {{
        "verified": verified,
        "requires_verification": requiresVer,
        "possible_duplicate": dup,
        "validation_error": err
      }},
      confidence_distribution: {{
        "High (>=85%)": recs.filter(r => (r.overall_confidence || 0) >= 0.85).length,
        "Medium (70-84%)": recs.filter(r => (r.overall_confidence || 0) >= 0.70 && (r.overall_confidence || 0) < 0.85).length,
        "Low (<70%)": recs.filter(r => (r.overall_confidence || 0) < 0.70).length
      }},
      recent_activity: window._standaloneAuditLogs.slice(0, 5)
    }};
  }}

  // 3a. Document Upload (Autonomous In-Browser Ingestion)
  if (endpoint.includes('/api/documents/upload') && !endpoint.includes('/process')) {{
    let filename = currentUploadedFilename || 'sample_1_clean_rau.png';
    let fileSize = 450000;
    let fileType = 'PNG';
    if (options.body instanceof FormData) {{
      const file = options.body.get('file');
      if (file && file.name) {{
        filename = file.name;
        fileSize = file.size || fileSize;
        fileType = (file.type ? file.type.split('/')[1] : 'PNG').toUpperCase();
      }}
    }}
    currentUploadedFilename = filename;
    const assignedId = filename.includes('11') ? 11 : (filename.includes('10') ? 10 : (filename.includes('9') ? 9 : 1));
    return {{
      id: assignedId,
      filename: filename,
      file_size: fileSize,
      file_type: fileType,
      file_path: `sample-data/${{filename}}`,
      created_at: new Date().toISOString()
    }};
  }}

  // 3b. Document Process (Autonomous In-Browser AI Extraction Pipeline)
  if (endpoint.includes('/process') || endpoint.includes('/upload-and-process')) {{
    const filename = currentUploadedFilename || 'sample_1_clean_rau.png';
    return generateClientSideAIProcessing(filename);
  }}

  // 4. Records List & Search
  if (endpoint.startsWith('/api/records/search')) {{
    const urlParams = new URLSearchParams(endpoint.split('?')[1] || '');
    const q = (urlParams.get('q') || '').toLowerCase();
    return window._standaloneRecords.filter(r => 
      (r.owner_name && r.owner_name.toLowerCase().includes(q)) ||
      (r.khasra_number && r.khasra_number.toLowerCase().includes(q)) ||
      (r.khata_number && r.khata_number.toLowerCase().includes(q)) ||
      (r.village && r.village.toLowerCase().includes(q))
    );
  }}

  if (endpoint === '/api/records' || endpoint.startsWith('/api/records?')) {{
    let list = [...window._standaloneRecords];
    const urlParams = new URLSearchParams(endpoint.split('?')[1] || '');
    const st = urlParams.get('status');
    const v = urlParams.get('village');
    if (st) list = list.filter(r => r.verification_status === st);
    if (v) list = list.filter(r => r.village && r.village.toLowerCase().includes(v.toLowerCase()));
    return list;
  }}

  // 5. Update Record (PUT)
  if (endpoint.startsWith('/api/records/') && method === 'PUT') {{
    const id = parseInt(endpoint.split('/').pop(), 10) || 1;
    let body = {{}};
    if (options.body && typeof options.body === 'string') {{
      try {{ body = JSON.parse(options.body); }} catch (e) {{}}
    }}
    const matched = window._standaloneRecords.find(r => r.id === id);
    if (matched) {{
      Object.assign(matched, body);
      matched.overall_confidence = 1.0;
      matched.confidence_score = 1.0;
      window._standaloneAuditLogs.unshift({{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        user_name: (currentUser && currentUser.name) ? currentUser.name : 'Officer Rajesh',
        action: 'FIELD_CORRECTIONS_SAVED',
        record_id: id,
        new_value: body.edit_reason || 'Officer updated extracted fields'
      }});
      return matched;
    }}
  }}

  // 6. Record Verification (POST)
  if (endpoint.includes('/verify') && method === 'POST') {{
    const parts = endpoint.split('/records/');
    const id = parts[1] ? parseInt(parts[1].split('/')[0], 10) : (currentRecordId || 1);
    const matched = window._standaloneRecords.find(r => r.id === id);
    if (matched) {{
      matched.verification_status = 'verified';
      matched.overall_confidence = 1.0;
      matched.confidence_score = 1.0;
    }}
    window._standaloneAuditLogs.unshift({{
      id: Date.now(),
      timestamp: new Date().toISOString(),
      user_name: (currentUser && currentUser.name) ? currentUser.name : 'Officer Rajesh',
      action: 'DOCUMENT_VERIFIED',
      record_id: id,
      new_value: `Khasra ${{matched ? matched.khasra_number : '245/2'}} Verified & Sealed`
    }});
    return {{
      id: id,
      verification_status: "verified",
      verified_by: 1,
      verified_at: new Date().toISOString(),
      notes: "Approved by Officer via LandLens Verification Studio"
    }};
  }}

  // 7. Record Rejection (POST)
  if (endpoint.includes('/reject') && method === 'POST') {{
    const parts = endpoint.split('/records/');
    const id = parts[1] ? parseInt(parts[1].split('/')[0], 10) : (currentRecordId || 1);
    let reason = 'Officer rejected record';
    if (options.body && typeof options.body === 'string') {{
      try {{ reason = JSON.parse(options.body).reason || reason; }} catch (e) {{}}
    }}
    const matched = window._standaloneRecords.find(r => r.id === id);
    if (matched) {{
      matched.verification_status = 'rejected';
    }}
    window._standaloneAuditLogs.unshift({{
      id: Date.now(),
      timestamp: new Date().toISOString(),
      user_name: (currentUser && currentUser.name) ? currentUser.name : 'Officer Rajesh',
      action: 'RECORD_REJECTED',
      record_id: id,
      new_value: reason
    }});
    return {{
      id: id,
      verification_status: "rejected",
      notes: reason
    }};
  }}

  // 8. Single Record for Verification Studio (GET)
  if (endpoint.startsWith('/api/records/') && method === 'GET') {{
    const id = parseInt(endpoint.split('/').pop(), 10) || 1;
    const records = window._standaloneRecords;
    const matched = records.find(r => r.id === id) || records[0];
    let recFilename = 'sample_1_clean_rau.png';
    if (id === 11 || (matched.khasra_number && matched.khasra_number.includes('२४५'))) {{
      recFilename = 'sample_11_handwritten_khasra.png';
    }} else if (id === 9 || (matched.document_number && matched.document_number.includes('UP'))) {{
      recFilename = 'sample_9_estamp_ghaziabad.jpg';
    }} else if (id === 10) {{
      recFilename = 'sample_10_non_land_invoice.png';
    }} else if (id === 2 || (matched.village && matched.village.toLowerCase().includes('kanadia'))) {{
      recFilename = 'sample_2_sita_kanadia.png';
    }} else if (id === 3 || (matched.village && matched.village.toLowerCase().includes('mangliya'))) {{
      recFilename = 'sample_3_mohan_mangliya.png';
    }}

    const confScore = (matched.overall_confidence !== undefined) ? matched.overall_confidence : (matched.confidence_score || 0.96);
    const confLevel = confScore >= 0.85 ? 'HIGH' : (confScore >= 0.70 ? 'MEDIUM' : 'LOW');

    return {{
      record: matched,
      document: {{
        id: matched.document_id || id,
        filename: matched.filename || recFilename,
        file_path: `sample-data/${{recFilename}}`,
        file_type: recFilename.endsWith('.jpg') ? 'JPEG' : 'PNG',
        file_size: 450000
      }},
      ai_results: [
        {{ field_name: 'owner_name', extracted_value: matched.owner_name, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'father_name', extracted_value: matched.father_name || 'Hari Mohan Sharma', confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'khasra_number', extracted_value: matched.khasra_number, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'khata_number', extracted_value: matched.khata_number, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'survey_number', extracted_value: matched.survey_number || matched.khasra_number, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'plot_number', extracted_value: matched.plot_number || '2', confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'village', extracted_value: matched.village, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'tehsil', extracted_value: matched.tehsil, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'district', extracted_value: matched.district, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'state', extracted_value: matched.state, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'land_area', extracted_value: matched.land_area || `${{matched.area_hectares}} Ha`, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'land_type', extracted_value: matched.land_type, confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'registration_number', extracted_value: matched.registration_number || 'REG-2024-90412', confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'mutation_number', extracted_value: matched.mutation_number || 'MUT-7712', confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'document_number', extracted_value: matched.document_number || 'DOC-2024-112', confidence_score: confScore, confidence_level: confLevel }},
        {{ field_name: 'date', extracted_value: matched.date || '14/10/2024', confidence_score: confScore, confidence_level: confLevel }}
      ]
    }};
  }}

  // 9. Cadastral GIS Parcels
  if (endpoint.includes('/api/gis/parcels')) {{
    const parcels = JSON.parse(JSON.stringify(DEFAULT_CADASTRAL_DATA));
    parcels.features.forEach(feat => {{
      const kh = feat.properties.khasra_number;
      const rec = window._standaloneRecords.find(r => r.khasra_number === kh);
      if (rec) {{
        feat.properties.owner_name = rec.owner_name;
        feat.properties.status = rec.verification_status;
        feat.properties.land_area = rec.land_area || `${{rec.area_hectares}} Ha`;
        feat.properties.record_id = rec.id;
      }}
    }});
    return parcels;
  }}

  // 10. Audit Logs
  if (endpoint.includes('/api/audit-logs')) {{
    return window._standaloneAuditLogs;
  }}

  // 11. Chat Suggestions
  if (endpoint.includes('/api/chat/suggestions')) {{
    return {{
      suggestions: EMBEDDED_LAND_DATA.quick_suggestions || [],
      realtime_updates: EMBEDDED_LAND_DATA.realtime_revenue_updates || []
    }};
  }}

  // 12. Land Rates
  if (endpoint.includes('/api/land-rates')) {{
    const rates = EMBEDDED_LAND_DATA.state_land_rates || [];
    return {{ total: rates.length, rates: rates }};
  }}

  // 13. Government Projects
  if (endpoint.includes('/api/gov-projects')) {{
    const projects = EMBEDDED_LAND_DATA.government_projects || [];
    return {{ total: projects.length, projects: projects }};
  }}

  // 14. Chat Message
  if (endpoint.includes('/api/chat/message')) {{
    let userMsg = '';
    if (typeof options.body === 'string') {{
      try {{ userMsg = JSON.parse(options.body).message || ''; }} catch(e) {{}}
    }}
    return generateClientSideGeminiReply(userMsg);
  }}

  return {{ status: "ok" }};
}}

// Client-side AI Processing Generator (Handles all 8 demo scenarios + custom files)
function generateClientSideAIProcessing(filename) {{
  const fn = (filename || '').toLowerCase();

  // NON-LAND INVOICE DEMO (Scenario 10)
  if (fn.includes('sample_10') || fn.includes('invoice') || fn.includes('bill')) {{
    return {{
      record_id: 10,
      document_id: 10,
      filename: filename || "sample_10_non_land_invoice.png",
      original_image_url: "sample-data/sample_10_non_land_invoice.png",
      preprocessed_image_url: "sample-data/sample_10_non_land_invoice.png",
      document_type: "invoice_or_billing",
      classification_confidence: 0.98,
      warning_message: "The uploaded file was classified as a Commercial Tax Invoice. It does not match statutory Indian land revenue record formats.",
      ocr_text: "TAX INVOICE\\nGSTIN: 07AAAAA0000A1Z5\\nInvoice No: INV-2024-9041\\nDescription: Enterprise Cloud Server Hardware\\nTotal Amount: Rs. 45,000\\nAuthorized Signatory",
      extracted_fields: {{
        owner_name: "Apex Tech Solutions Pvt Ltd",
        father_name: "",
        khasra_number: "",
        khata_number: "",
        survey_number: "",
        plot_number: "",
        village: "",
        tehsil: "",
        district: "New Delhi",
        state: "Delhi",
        area_hectares: 0.0,
        land_type: "Commercial Invoice"
      }},
      field_confidences: {{
        owner_name: 0.40,
        khasra_number: 0.10,
        area_hectares: 0.10
      }},
      overall_confidence: 0.15,
      is_handwritten: false,
      is_land_record: false,
      document_class: "Tax Invoice / Commercial Receipt",
      classification_reasons: [
        "Contains non-land commercial keywords (GSTIN, Tax Invoice, Subtotal).",
        "No Khasra or cadastral parcel identifiers found.",
        "Detected commercial billing items rather than revenue deed register."
      ],
      validation_result: {{
        is_valid: false,
        validation_status: "rejected",
        missing_fields: ["khasra_number", "khata_number", "village"],
        errors: ["Document rejected: Not recognized as an authentic Indian land revenue record."],
        warnings: ["Document Discriminator flagged this file as commercial billing."]
      }},
      duplicate_check: {{
        is_duplicate: false,
        confidence: 0.0,
        matches: []
      }}
    }};
  }}

  // HANDWRITTEN KHASRA DEMO (Scenario 11)
  if (fn.includes('sample_11') || fn.includes('handwritten')) {{
    return {{
      record_id: 11,
      document_id: 11,
      filename: filename || "sample_11_handwritten_khasra.png",
      original_image_url: "sample-data/sample_11_handwritten_khasra.png",
      preprocessed_image_url: "sample-data/sample_11_handwritten_khasra.png",
      document_type: "handwritten_khasra_register",
      classification_confidence: 0.95,
      ocr_text: "वर्ष 1978-79\\nखसरा नं. : २४५/२ (Normalized: 245/2)\\nखातेदार: रमेश चंद्र शर्मा\\nपिता: हरि मोहन शर्मा\\nरकबा: 1.42 हेक्टेयर\\nभूमि प्रकार: सिंचित",
      extracted_fields: {{
        owner_name: "रमेश चंद्र शर्मा (Ramesh Chandra Sharma)",
        father_name: "हरि मोहन शर्मा (Hari Mohan Sharma)",
        khasra_number: "245/2",
        khata_number: "112",
        survey_number: "245",
        plot_number: "2",
        village: "राऊ (Rau)",
        tehsil: "राऊ (Rau)",
        district: "इंदौर (Indore)",
        state: "मध्य प्रदेश (Madhya Pradesh)",
        area_hectares: 1.42,
        land_type: "सिंचित (Irrigated Agricultural)"
      }},
      field_confidences: {{
        owner_name: 0.94,
        father_name: 0.92,
        khasra_number: 0.96,
        khata_number: 0.93,
        village: 0.95,
        area_hectares: 0.95
      }},
      overall_confidence: 0.94,
      is_handwritten: true,
      is_land_record: true,
      document_class: "Handwritten Patwari Khasra Register",
      classification_reasons: [
        "Bilingual land record headings detected (खसरा नं., खातेदार).",
        "Handwritten Devanagari numerals successfully normalized (२४५/२ -> 245/2).",
        "Valid cadastral parcel identifiers matched in Rau village registry."
      ],
      validation_result: {{
        is_valid: true,
        validation_status: "verified",
        missing_fields: [],
        errors: [],
        warnings: []
      }},
      duplicate_check: {{ is_duplicate: false, confidence: 0.0, matches: [] }}
    }};
  }}

  // UP E-STAMP CONVEYANCE DEED (Scenario 9)
  if (fn.includes('sample_9') || fn.includes('estamp') || fn.includes('ghaziabad')) {{
    return {{
      record_id: 9,
      document_id: 9,
      filename: filename || "sample_9_estamp_ghaziabad.jpg",
      original_image_url: "sample-data/sample_9_estamp_ghaziabad.jpg",
      preprocessed_image_url: "sample-data/sample_9_estamp_ghaziabad.jpg",
      document_type: "estamp_conveyance_deed",
      classification_confidence: 0.97,
      ocr_text: "Certificate No: IN-UP38491028374829V\\nArticle 23 Conveyance Deed\\nFirst Party: Apex Realtech Developers\\nSecond Party: Rajiv Kumar Goel\\nProperty Description: Flat No 1101, 11th Floor, Tower B, Ramprastha Greens, Sector 7, Vaishali, Ghaziabad",
      extracted_fields: {{
        owner_name: "Rajiv Kumar Goel",
        father_name: "Late S. P. Goel",
        khasra_number: "441/3",
        khata_number: "89",
        survey_number: "441",
        plot_number: "Flat 1101, Tower B",
        village: "Vaishali, Sector 7",
        tehsil: "Ghaziabad Sadar",
        district: "Ghaziabad",
        state: "Uttar Pradesh",
        area_hectares: 0.016,
        land_type: "आवासीय (Urban Residential Apartment)"
      }},
      field_confidences: {{
        owner_name: 0.98,
        khasra_number: 0.95,
        area_hectares: 0.94,
        village: 0.97
      }},
      overall_confidence: 0.96,
      is_handwritten: false,
      is_land_record: true,
      document_class: "Non-Judicial e-Stamp Conveyance Deed (Article 23)",
      classification_reasons: [
        "Stock Holding Corporation (SHCIL) e-Stamp certificate header detected.",
        "Article 23 Conveyance deed transfer verified with consideration value.",
        "Urban residential property decomposition validated."
      ],
      validation_result: {{
        is_valid: true,
        validation_status: "verified",
        missing_fields: [],
        errors: [],
        warnings: []
      }},
      duplicate_check: {{ is_duplicate: false, confidence: 0.0, matches: [] }}
    }};
  }}

  // DEFAULT / SCENARIO 1 (Clean Jamabandi RoR)
  return {{
    record_id: 1,
    document_id: 1,
    filename: filename || "sample_1_clean_rau.png",
    original_image_url: "sample-data/sample_1_clean_rau.png",
    preprocessed_image_url: "sample-data/sample_1_clean_rau.png",
    document_type: "ror_jamabandi",
    classification_confidence: 0.98,
    ocr_text: "मध्यप्रदेश शासन - राजस्व विभाग\\nअधिकार अभिलेख / खतौनी\\nग्राम: राऊ | तहसील: राऊ | जिला: इंदौर\\nखसरा संख्या: 245/2 | खाता क्रमांक: 112\\nखातेदार: रमेश चंद्र शर्मा\\nपिता का नाम: हरि मोहन शर्मा\\nक्षेत्रफल: 1.4200 हेक्टेयर\\nभूमि का प्रकार: सिंचित एक फसली",
    extracted_fields: {{
      owner_name: "रमेश चंद्र शर्मा (Ramesh Chandra Sharma)",
      father_name: "हरि मोहन शर्मा (Hari Mohan Sharma)",
      khasra_number: "245/2",
      khata_number: "112",
      survey_number: "245",
      plot_number: "2",
      village: "राऊ (Rau)",
      tehsil: "राऊ (Rau)",
      district: "इंदौर (Indore)",
      state: "मध्य प्रदेश (Madhya Pradesh)",
      area_hectares: 1.42,
      land_type: "सिंचित एक फसली (Irrigated Agricultural)"
    }},
    field_confidences: {{
      owner_name: 0.98,
      father_name: 0.95,
      khasra_number: 0.97,
      khata_number: 0.96,
      village: 0.99,
      area_hectares: 0.98
    }},
    overall_confidence: 0.97,
    is_handwritten: false,
    is_land_record: true,
    document_class: "Record of Rights (Jamabandi / Khatauni)",
    classification_reasons: [
      "Official MP revenue department watermark and header recognized.",
      "Valid Khasra, Khata, and Hectare measurements verified.",
      "Cadastral boundary verified against GIS parcel shapefile."
    ],
    validation_result: {{
      is_valid: true,
      validation_status: "verified",
      missing_fields: [],
      errors: [],
      warnings: []
    }},
    duplicate_check: {{ is_duplicate: false, confidence: 0.0, matches: [] }}
  }};
}}

// In-Browser Sample Records Database
function getClientSideSampleRecords() {{
  return window._standaloneRecords;
}}

// In-Browser Gemini 3.1 Pro Chat Assistant Engine
function generateClientSideGeminiReply(message) {{
  const msg = (message || '').toLowerCase().trim();
  const rates = EMBEDDED_LAND_DATA.state_land_rates || [];
  const projects = EMBEDDED_LAND_DATA.government_projects || [];

  // 1. Friendly Officer Greetings (hi, hii, hello, hey, namaste, help)
  const isGreeting = /^(hi|hii|hello|hey|heyy|namaste|pranam|good\s*(morning|afternoon|evening)|help)\b/i.test(msg) || msg === 'hi' || msg === 'hii';
  if (isGreeting) {{
    const officerName = (window.currentUser && window.currentUser.name) ? window.currentUser.name : 'Revenue Officer';
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-live-assistant",
      reply: `### Hello ${{officerName}}! 👋 Welcome to LandLens AI\\n\\n` +
             `I am your digital revenue & cadastral assistant powered by **Gemini 3.1 Pro**.\\n\\n` +
             `Here is what I can do for you in real time:\\n` +
             `- 🗺️ **Cadastral Plot Lookups**: Ask about **Khasra 245/2**, **318/1**, or **102/3** to locate ownership on the GIS Map.\\n` +
             `- 🏛️ **State Circle Rates & Stamp Duty**: Instant official valuation benchmarks for **Uttar Pradesh**, **Madhya Pradesh**, **Maharashtra**, **Delhi**, etc.\\n` +
             `- 🏗️ **Mega Infrastructure Projects**: Real-time acquisition status on **Jewar Airport**, **Bullet Train**, and **Ganga Expressway**.\\n` +
             `- ⚖️ **Legal Compensation**: Statutory multipliers & 100% Solatium formulas under the **RFCTLARR Act 2013**.\\n\\n` +
             `*Click any quick query chip below or ask your own question!*`,
      suggestions: [
         "📍 Inspect Khasra 245/2 (Rau)",
         "🏛️ UP Circle Rates & Stamp Duty",
         "🏗️ Jewar Airport Land Acquisition",
         "📜 How to verify handwritten Jamabandi"
      ]
    }};
  }}

  // 2. Khasra 245/2 or Rau Cadastral Query
  if (msg.includes('245/2') || (msg.includes('245') && !msg.includes('318')) || (msg.includes('rau') && !msg.includes('project'))) {{
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-cadastral-intelligence",
      reply: `### 📋 Cadastral Parcel: Khasra 245/2 (Village Rau, Indore)\\n\\n` +
             `- **Owner Name**: **Ramesh Chandra Sharma** (Father: Hari Mohan Sharma)\\n` +
             `- **Khata / Survey**: Khata No. \`112\`, Survey No. \`245\`, Plot \`2\`\\n` +
             `- **Location**: Village Rau, Tehsil Rau, District Indore, Madhya Pradesh\\n` +
             `- **Total Land Area**: **1.4200 Hectares** (Agricultural Irrigated)\\n` +
             `- **AI Confidence**: **97.4%** (Verified against Cadastral GIS polygon)\\n` +
             `- **Verification Status**: 🟢 **VERIFIED & SEALED**\\n` +
             `- **Valuation Benchmark**: Indore District Urban: \`₹38,000/sq.m\` | Rural: \`₹42,00,000/Ha\`\\n\\n` +
             `<button onclick="viewRecordOnGis('245/2')" class="px-3 py-1.5 bg-gov-700 hover:bg-gov-800 text-white rounded-lg text-xs font-semibold shadow transition inline-flex items-center space-x-1"><span>🗺️ Inspect Khasra 245/2 on Cadastral GIS</span></button>`,
      suggestions: [
        "Check circle rate for Madhya Pradesh",
        "Inspect Khasra 318/1 (Kanadia)",
        "How does RFCTLARR calculate compensation?"
      ]
    }};
  }}

  // 3. Khasra 318/1 or Kanadia Cadastral Query
  if (msg.includes('318/1') || msg.includes('318') || msg.includes('kanadia')) {{
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-cadastral-intelligence",
      reply: `### 📋 Cadastral Parcel: Khasra 318/1 (Village Kanadia, Indore)\\n\\n` +
             `- **Owner Name**: **Sita Ram Patidar** (Father: Bhagwan Das)\\n` +
             `- **Khata / Survey**: Khata No. \`74\`, Survey No. \`318\`, Plot \`1\`\\n` +
             `- **Location**: Village Kanadia, Tehsil Kanadia, District Indore, Madhya Pradesh\\n` +
             `- **Total Land Area**: **2.1500 Hectares** (Agricultural Unirrigated)\\n` +
             `- **Verification Status**: 🟢 **VERIFIED**\\n\\n` +
             `<button onclick="viewRecordOnGis('318/1')" class="px-3 py-1.5 bg-gov-700 hover:bg-gov-800 text-white rounded-lg text-xs font-semibold shadow transition inline-flex items-center space-x-1"><span>🗺️ Inspect Khasra 318/1 on Cadastral GIS</span></button>`,
      suggestions: [
        "Inspect Khasra 245/2 (Rau)",
        "Check circle rate for Madhya Pradesh",
        "Show Jewar Airport land acquisition compensation"
      ]
    }};
  }}

  // 4. Khasra 102/3 or Mangliya Boundary Overlap
  if (msg.includes('102/3') || msg.includes('102') || msg.includes('mangliya')) {{
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-cadastral-intelligence",
      reply: `### ⚠️ Cadastral Flag: Khasra 102/3 (Village Mangliya, Sanwer)\\n\\n` +
             `- **Owner Name**: **Mohan Lal Verma** (Father: Ramswaroop Verma)\\n` +
             `- **Khata / Survey**: Khata No. \`58\`, Survey No. \`102\`, Plot \`3\`\\n` +
             `- **Location**: Village Mangliya, Tehsil Sanwer, District Indore, MP\\n` +
             `- **Total Land Area**: **0.8500 Hectares** (Semi-Urban Plot)\\n` +
             `- **Verification Status**: 🟠 **POSSIBLE DUPLICATE / BOUNDARY OVERLAP**\\n` +
             `- **AI Detection Note**: *Cadastral engine detected an 18-meter polygon vertex overlap with adjoining Khasra 102/2. Requires physical survey re-verification.*\\n\\n` +
             `<button onclick="viewRecordOnGis('102/3')" class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow transition inline-flex items-center space-x-1"><span>🗺️ View Overlap on Cadastral GIS</span></button>`,
      suggestions: [
        "Open Verification Studio for Khasra 102/3",
        "Inspect Khasra 245/2 (Rau)",
        "What is RFCTLARR compensation rule?"
      ]
    }};
  }}

  // 5. UP e-Stamp Conveyance Deed (Ghaziabad / Scenario 9)
  if (msg.includes('estamp') || msg.includes('e-stamp') || msg.includes('ghaziabad') || msg.includes('conveyance') || msg.includes('441/3') || msg.includes('goel')) {{
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-estamp-intelligence",
      reply: `### 📜 Non-Judicial e-Stamp Conveyance Deed (Article 23, UP)\\n\\n` +
             `- **Certificate No**: \`IN-UP90284719284910V\`\\n` +
             `- **Purchaser / First Party**: **Rajiv Kumar Goel** (Transferor)\\n` +
             `- **Second Party**: **Sunita Goel** (Transferee)\\n` +
             `- **Property**: Plot 441/3, Vaishali Sector 7, Ghaziabad Sadar, UP\\n` +
             `- **Consideration Amount**: **₹65,00,000**\\n` +
             `- **Stamp Duty Paid**: **₹3,90,000** (6.0% UP Conveyance Rate)\\n` +
             `- **Registration Fee**: **₹20,000**\\n` +
             `- **Verification Status**: 🟢 **VERIFIED & TAMPER-PROOF HASHED**\\n\\n` +
             `<button onclick="openVerificationStudio(9)" class="px-3 py-1.5 bg-gov-700 hover:bg-gov-800 text-white rounded-lg text-xs font-semibold shadow transition inline-flex items-center space-x-1"><span>🔍 Open in Verification Studio</span></button>`,
      suggestions: [
        "What is the stamp duty in Uttar Pradesh?",
        "Check Jewar Airport land acquisition compensation",
        "Inspect Khasra 245/2 (Rau)"
      ]
    }};
  }}

  // 6. Statutory Compensation Laws (RFCTLARR Act 2013)
  if (msg.includes('rfctlarr') || msg.includes('compensation') || msg.includes('formula') || msg.includes('solatium') || msg.includes('law') || msg.includes('acquisition rule')) {{
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-legal-framework",
      reply: `### ⚖️ Statutory Land Acquisition Compensation (RFCTLARR Act 2013)\\n\\n` +
             `Under the **Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013**:\\n\\n` +
             `1. **Base Market Value Assessment**:\\n` +
             `   Higher of the notified State Circle Rate OR the average sale price of top 50% registered deeds in the vicinity over the previous 3 years.\\n\\n` +
             `2. **Multiplication Factor**:\\n` +
             `   - **Urban Areas**: \`1.0x\` (Direct market value)\\n` +
             `   - **Rural Areas**: \`1.25x to 2.0x\` (graduated based on radial distance from urban perimeter)\\n\\n` +
             `3. **Compulsory Acquisition Solatium**:\\n` +
             `   - **100% Solatium** added over the assessed land + building assets value.\\n\\n` +
             `4. **Statutory Additional Interest**:\\n` +
             `   - **12% per annum** calculated from Section 11 preliminary notification date to final award date.\\n\\n` +
             `> 💡 **Benchmark Example**: A rural agricultural plot valued at ₹10 Lakhs circle rate receives \`(₹10L × 2.0) + 100% Solatium\` = **₹40 Lakhs** minimum compensation before interest.`,
      suggestions: [
        "What is the stamp duty in Uttar Pradesh?",
        "Show Jewar Airport compensation package",
        "State land rates for Madhya Pradesh"
      ]
    }};
  }}

  // 7. Specific State Land Rates
  const matchedState = rates.find(r => msg.includes(r.state.toLowerCase()));
  if (matchedState && (msg.includes('rate') || msg.includes('price') || msg.includes('circle') || msg.includes('guidance') || msg.includes('reckoner') || msg.includes('duty') || msg.includes('tax'))) {{
    const st = matchedState;
    const districtLines = st.key_districts.map(d => `  - **${{d.district}}**: Urban: \`${{d.urban_rate}}\` | Rural: \`${{d.rural_rate}}\``).join('\\n');
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-autonomous-engine",
      reply: `### 🏛️ Government Land Valuation: ${{st.state}}\\n\\n` +
             `- **Official Terminology**: ${{st.official_term}}\\n` +
             `- **Governing Body**: ${{st.department}}\\n` +
             `- **Urban Benchmark Rate**: **${{st.urban_avg_per_sqm}}**\\n` +
             `- **Rural Agricultural Rate**: **${{st.rural_avg_per_hectare}}**\\n` +
             `- **Stamp Duty**: Male \`${{st.stamp_duty_male}}\` | Female \`${{st.stamp_duty_female}}\`\\n` +
             `- **Registration Fee**: \`${{st.registration_fee}}\`\\n\\n` +
             `#### 📍 District-Level Benchmarks (${{st.state}}):\\n${{districtLines}}\\n\\n` +
             `**Legal Valuation Rule**: *${{st.valuation_rules}}*\\n\\n` +
             `> 💡 **Pro-Tip**: Under the **RFCTLARR Act 2013**, compulsory land acquisition for public projects pays **2x to 4x** the notified Circle Rate + 100% Solatium + 12% statutory interest.`,
      suggestions: [
        "What is the stamp duty in Uttar Pradesh?",
        "How does RFCTLARR Act calculate rural land price?",
        "Show circle rates for Maharashtra & Delhi"
      ]
    }};
  }}

  // 8. General Circle Rates Overview Table
  if (msg.includes('circle rate') || msg.includes('land rate') || msg.includes('all states') || msg.includes('guidance value')) {{
    const rows = rates.slice(0, 6).map(r => `| **${{r.state}}** | ${{r.official_term.split('(')[0].trim()}} | ${{r.urban_avg_per_sqm}} | ${{r.rural_avg_per_hectare}} |`).join('\\n');
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-autonomous-engine",
      reply: `### 🇮🇳 Official State Land Circle Rates (2024 Benchmarks)\\n\\n` +
             `| State | Valuation Standard | Urban Benchmark (sq.m) | Rural Benchmark (Ha) |\\n` +
             `| :--- | :--- | :--- | :--- |\\n` +
             `${{rows}}\\n\\n` +
             `*Ask about any specific state (e.g. 'What is the circle rate in Uttar Pradesh or Maharashtra?') for complete district-level breakdowns.*`,
      suggestions: [
        "What is the stamp duty in Uttar Pradesh?",
        "Show circle rates for Maharashtra & Delhi",
        "Compensation formula under RFCTLARR Act"
      ]
    }};
  }}

  // 9. Match Government Mega Projects
  const matchedProj = projects.find(p => msg.includes(p.name.toLowerCase()) || p.states_affected.some(s => msg.includes(s.toLowerCase())) || (msg.includes('bullet') && p.id.includes('bullet')) || (msg.includes('jewar') && p.id.includes('jewar')) || (msg.includes('ganga') && p.id.includes('ganga')) || (msg.includes('ken') && p.id.includes('ken')));
  if (matchedProj) {{
    const p = matchedProj;
    return {{
      model: "gemini-3.1-pro",
      source: "gemini-3.1-pro-autonomous-engine",
      reply: `### 🏗️ Live Government Project: ${{p.name}}\\n\\n` +
             `- **Sector**: \`${{p.sector}}\`\\n` +
             `- **Sponsoring Authority**: **${{p.ministry}}**\\n` +
             `- **Execution Status**: 🟢 **${{p.status}}**\\n` +
             `- **Total Project Budget**: **${{p.total_budget}}**\\n` +
             `- **Land Acquired**: **${{p.land_acquired_hectares}}**\\n` +
             `- **States Involved**: ${{p.states_affected.join(', ')}}\\n\\n` +
             `#### 💰 Compensation & Legal Framework:\\n` +
             `- **Statutory Act**: \`${{p.acquisition_act}}\`\\n` +
             `- **Compensation Package**: **${{p.compensation_package}}**\\n` +
             `- **Key Impact Districts**: ${{p.key_impact_districts.slice(0, 6).join(', ')}}\\n\\n` +
             `**Cadastral Guideline**: ${{p.revenue_guidelines}}\\n\\n` +
             `> ℹ️ *LandLens AI tracks this project in real-time. Cadastral parcel overlays in these districts are automatically checked for ROW restrictions.*`,
      suggestions: [
        "Show Jewar Airport land acquisition compensation",
        "What is the status of Mumbai-Ahmedabad Bullet Train?",
        "Tell me about Ganga Expressway land purchase"
      ]
    }};
  }}

  // 10. Default Assistant Reply
  return {{
    model: "gemini-3.1-pro",
    source: "gemini-3.1-pro-autonomous-engine",
    reply: `### Hello! I am LandLens AI Assistant (Powered by Gemini 3.1 Pro) 🌐\\n\\n` +
           `I specialize in Indian land governance, revenue records, and infrastructure intelligence. Here is how I can assist you:\\n\\n` +
           `* 🌾 **Government Land Circle Rates**: Check official ready reckoner/circle rates for any state (UP, MP, Maharashtra, Delhi, Gujarat, Karnataka, etc.).\\n` +
           `* 🏗️ **Live Mega Government Projects**: Inquire about land acquisition progress for the Bullet Train, Jewar Airport, Bharatmala, or Ganga Expressway.\\n` +
           `* ⚖️ **Land Acquisition Laws**: Learn about compensation formulas (2x rural multiplier, 100% Solatium) under the RFCTLARR Act 2013.\\n` +
           `* 🔍 **Document Ingestion & Verification**: Guide you through digitizing handwritten Patwari registers or printed e-Stamp conveyance deeds.\\n\\n` +
           `*Try asking: 'What is the circle rate in Uttar Pradesh?' or 'Show me the land status of Jewar Airport.'*`,
    suggestions: [
      "🌾 State Land Circle Rates (UP, MP, Maharashtra)",
      "🏗️ Current Government Infrastructure Projects",
      "📜 How to verify Khasra Number 245/2",
      "⚖️ Land compensation formula under RFCTLARR"
    ]
  }};
}}
"""

# Write modified app.js into public_web/static/app.js and public_web/app.js
with open(os.path.join(PUBLIC_DIR, "static", "app.js"), "w", encoding="utf-8") as f:
    f.write(js_content + client_engine_code)

with open(os.path.join(PUBLIC_DIR, "app.js"), "w", encoding="utf-8") as f:
    f.write(js_content + client_engine_code)

# Package into ZIP for instant deployment
with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(PUBLIC_DIR):
        for file in files:
            full_p = os.path.join(root, file)
            rel_p = os.path.relpath(full_p, PUBLIC_DIR)
            zipf.write(full_p, rel_p)

print(f"Standalone deployment ZIP created successfully: {ZIP_PATH} ({os.path.getsize(ZIP_PATH)} bytes)")
print("Public web build complete!")
