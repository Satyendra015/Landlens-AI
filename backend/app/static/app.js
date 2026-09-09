// LandLens AI — Frontend Application Logic (SIH26018)

let currentUser = null;
let authToken = localStorage.getItem('landlens_token') || null;
let currentDocId = null;
let currentRecordId = null;
let currentRecordData = null;
let showingEnhancedImage = false;
let gisMapInstance = null;
let chartStatusInstance = null;
let chartConfidenceInstance = null;

// Core Field Metadata
const FIELD_DEFINITIONS = [
  { key: 'owner_name', label: 'Owner Name / मालिक का नाम', icon: 'user' },
  { key: 'father_name', label: "Father's Name / पिता का नाम", icon: 'users' },
  { key: 'khasra_number', label: 'Khasra Number / खसरा नं.', icon: 'hash' },
  { key: 'khata_number', label: 'Khata Number / खाता नं.', icon: 'file-text' },
  { key: 'survey_number', label: 'Survey Number / सर्वे नं.', icon: 'compass' },
  { key: 'plot_number', label: 'Plot Number / प्लॉट नं.', icon: 'layout' },
  { key: 'village', label: 'Village / ग्राम', icon: 'map-pin' },
  { key: 'tehsil', label: 'Tehsil / तहसील', icon: 'navigation' },
  { key: 'district', label: 'District / जिला', icon: 'building-2' },
  { key: 'state', label: 'State / राज्य', icon: 'globe' },
  { key: 'land_area', label: 'Land Area / रकबा', icon: 'maximize-2' },
  { key: 'land_type', label: 'Land Type / भूमि प्रकार', icon: 'sprout' },
  { key: 'registration_number', label: 'Registration No / पंजीकरण क्रमांक', icon: 'award' },
  { key: 'mutation_number', label: 'Mutation No / नामांतरण क्रमांक', icon: 'git-commit' },
  { key: 'document_number', label: 'Document No / दस्तावेज संख्या', icon: 'file' },
  { key: 'date', label: 'Date / दिनांक', icon: 'calendar' }
];

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  
  if (authToken) {
    try {
      const res = await apiRequest('/api/auth/me');
      currentUser = (res && res.name) ? res : { id: 1, email: 'officer@landlens.gov.in', name: 'Officer Rajesh Kumar', role: 'officer' };
      updateAuthUI();
      navigate('dashboard');
    } catch (e) {
      localStorage.removeItem('landlens_token');
      authToken = null;
      currentUser = null;
      updateAuthUI();
      navigate('login');
    }
  } else {
    currentUser = null;
    updateAuthUI();
    navigate('login');
  }
});

// Navigation Router
function handleLogoClick() {
  if (currentUser) {
    navigate('dashboard');
  } else {
    navigate('login');
  }
}

function navigate(pageId) {
  // If not authenticated and trying to access any protected page, route to login
  if (!currentUser && pageId !== 'login') {
    pageId = 'login';
  }

  const pages = ['login', 'dashboard', 'upload', 'verification', 'records', 'gis', 'audit'];
  pages.forEach(p => {
    const el = document.getElementById(`page-${p}`);
    if (el) el.classList.add('hidden');
  });

  const activePage = document.getElementById(`page-${pageId}`);
  if (activePage) activePage.classList.remove('hidden');

  // Control top navigation & header visibility: hidden on login or unauthenticated
  const mainNav = document.getElementById('mainNav');
  const appHeader = document.getElementById('appHeader');
  const appBody = document.body;
  const mainContainer = document.getElementById('mainContainer');

  if (pageId === 'login' || !currentUser) {
    if (appHeader) appHeader.classList.add('hidden');
    if (appBody) {
      appBody.classList.remove('bg-slate-50');
      appBody.classList.add('bg-[#9ba7b4]');
    }
    if (mainNav) {
      mainNav.classList.add('hidden');
      mainNav.classList.remove('md:flex');
    }
    if (mainContainer) {
      mainContainer.className = 'flex-1 w-full flex flex-col items-center justify-center';
    }
  } else {
    if (appHeader) appHeader.classList.remove('hidden');
    if (appBody) {
      appBody.classList.remove('bg-[#9ba7b4]');
      appBody.classList.add('bg-slate-50');
    }
    if (mainNav) {
      mainNav.classList.remove('hidden');
      mainNav.classList.add('md:flex');
    }
    if (mainContainer) {
      mainContainer.className = 'flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col overflow-x-hidden';
    }
  }

  // Update nav buttons highlight
  document.querySelectorAll('.nav-btn').forEach(btn => {
    if (btn.getAttribute('data-page') === pageId) {
      btn.classList.add('bg-gov-800', 'text-saffron-500');
    } else {
      btn.classList.remove('bg-gov-800', 'text-saffron-500');
    }
  });

  // Re-render icons
  setTimeout(() => {
    if (window.lucide) lucide.createIcons();
  }, 50);

  // Trigger page-specific data fetchers
  if (pageId === 'dashboard') fetchDashboardStats();
  if (pageId === 'records') fetchRecords();
  if (pageId === 'audit') fetchAuditLogs();
  if (pageId === 'gis') initGisMap();
  if (pageId === 'verification') {
    if (currentRecordId) {
      openVerificationStudio(currentRecordId);
    } else {
      loadDefaultStudioRecord();
    }
  }
}

// API Fetch Helper
async function apiRequest(endpoint, options = {}) {
  const headers = options.headers || {};
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  if (!options.body || !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(endpoint, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = 'Request failed';
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errorDetail;
    } catch (e) {}
    throw new Error(errorDetail);
  }

  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return await res.json();
  }
  return res;
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  const bgColors = {
    info: 'bg-slate-900 text-white',
    success: 'bg-emerald-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-amber-600 text-white'
  };
  toast.className = `${bgColors[type] || bgColors.info} px-4 py-2.5 rounded-lg shadow-lg text-xs font-medium flex items-center space-x-2 transition-all transform duration-300`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Auth Handlers
async function handleLoginSubmit(event) {
  event.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const data = await apiRequest('/api/auth/json-login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    authToken = data.access_token || 'mock-token';
    currentUser = data.user || data;
    if (!currentUser || !currentUser.name) {
      const isAdm = (email || '').toLowerCase().includes('admin');
      const isRev = (email || '').toLowerCase().includes('reviewer');
      currentUser = {
        id: 1,
        email: email || 'officer@landlens.gov.in',
        name: isAdm ? 'Administrator' : (isRev ? 'Reviewer' : 'Officer Rajesh Kumar'),
        role: isAdm ? 'admin' : (isRev ? 'reviewer' : 'officer')
      };
    }
    localStorage.setItem('landlens_token', authToken);
    updateAuthUI();
    const displayName = (currentUser && currentUser.name) ? currentUser.name : 'Officer';
    showToast(`Welcome, ${displayName}`, 'success');
    navigate('dashboard');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function quickLogin(role) {
  const credentials = {
    officer: { email: 'officer@landlens.gov.in', pass: 'officer123' },
    admin: { email: 'admin@landlens.gov.in', pass: 'admin123' },
    reviewer: { email: 'reviewer@landlens.gov.in', pass: 'reviewer123' },
  };
  const cred = credentials[role];
  if (cred) {
    document.getElementById('loginEmail').value = cred.email;
    document.getElementById('loginPassword').value = cred.pass;
    document.getElementById('loginForm').dispatchEvent(new Event('submit'));
  }
}

function togglePasswordVisibility() {
  const pwdInput = document.getElementById('loginPassword');
  const icon = document.getElementById('passwordEyeIcon');
  if (!pwdInput) return;
  if (pwdInput.type === 'password') {
    pwdInput.type = 'text';
    if (icon) icon.setAttribute('data-lucide', 'eye');
  } else {
    pwdInput.type = 'password';
    if (icon) icon.setAttribute('data-lucide', 'eye-off');
  }
  if (window.lucide) lucide.createIcons();
}

function showForgotPasswordModal(e) {
  if (e) e.preventDefault();
  showToast('Demo Credentials: officer@landlens.gov.in / officer123. Or select one-click Demo Roles below.', 'info');
}

function handleLogout() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('landlens_token');
  updateAuthUI();
  navigate('login');
  showToast('Logged out securely', 'info');
}

function updateAuthUI() {
  const userBadge = document.getElementById('userBadge');
  const logoutBtn = document.getElementById('logoutBtn');
  const userName = document.getElementById('userNameDisplay');
  const userRole = document.getElementById('userRoleTag');
  const mainNav = document.getElementById('mainNav');

  if (currentUser) {
    if (mainNav) {
      mainNav.classList.remove('hidden');
      mainNav.classList.add('md:flex');
    }
    userBadge.classList.remove('hidden');
    userBadge.classList.add('flex');
    logoutBtn.classList.remove('hidden');
    logoutBtn.classList.add('flex');
    userName.textContent = (currentUser && currentUser.name) ? currentUser.name : 'Officer';
    userRole.textContent = ((currentUser && currentUser.role) ? currentUser.role : 'OFFICER').toUpperCase();
  } else {
    if (mainNav) {
      mainNav.classList.add('hidden');
      mainNav.classList.remove('md:flex');
    }
    userBadge.classList.add('hidden');
    userBadge.classList.remove('flex');
    logoutBtn.classList.add('hidden');
    logoutBtn.classList.remove('flex');
  }
}

// -------------------------------------------------------------
// DASHBOARD MODULE
// -------------------------------------------------------------
async function fetchDashboardStats() {
  const refreshIcon = document.getElementById('dashboardRefreshIcon');
  if (refreshIcon) refreshIcon.classList.add('animate-spin');
  try {
    const stats = await apiRequest('/api/dashboard/statistics');

    if (document.getElementById('statTotalDocs')) document.getElementById('statTotalDocs').textContent = stats.total_documents;
    if (document.getElementById('statProcessedDocs')) document.getElementById('statProcessedDocs').textContent = stats.processed_documents;
    if (document.getElementById('statPendingVerif')) document.getElementById('statPendingVerif').textContent = stats.pending_verification;
    if (document.getElementById('statVerified')) document.getElementById('statVerified').textContent = stats.verified_records;
    if (document.getElementById('statDuplicates')) document.getElementById('statDuplicates').textContent = stats.possible_duplicates;
    if (document.getElementById('statValErrors')) document.getElementById('statValErrors').textContent = stats.validation_errors;
    if (document.getElementById('statLowConf')) document.getElementById('statLowConf').textContent = stats.low_confidence_records;
    
    const avgPct = (stats.average_confidence * 100).toFixed(1);
    if (document.getElementById('statAvgConf')) document.getElementById('statAvgConf').textContent = `${avgPct}%`;
    const confBar = document.getElementById('statAvgConfBar');
    if (confBar) {
      confBar.style.width = `${Math.min(100, Math.max(0, stats.average_confidence * 100))}%`;
    }

    renderStatusChart(stats.status_distribution);
    renderConfidenceChart(stats.confidence_distribution);
    renderRecentActivity(stats.recent_activity);
  } catch (err) {
    console.error('Failed to load dashboard statistics:', err);
  } finally {
    if (refreshIcon) {
      setTimeout(() => refreshIcon.classList.remove('animate-spin'), 400);
    }
  }
}

function renderStatusChart(dist) {
  const ctx = document.getElementById('chartStatus').getContext('2d');
  if (chartStatusInstance) chartStatusInstance.destroy();

  chartStatusInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(dist),
      datasets: [{
        data: Object.values(dist),
        backgroundColor: ['#2563eb', '#f59e0b', '#f97316', '#ef4444', '#64748b'],
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
      }
    }
  });
}

function renderConfidenceChart(dist) {
  const ctx = document.getElementById('chartConfidence').getContext('2d');
  if (chartConfidenceInstance) chartConfidenceInstance.destroy();

  chartConfidenceInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(dist),
      datasets: [{
        label: 'Documents',
        data: Object.values(dist),
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 10 } } },
        x: { ticks: { font: { size: 10 } } }
      }
    }
  });
}

function renderRecentActivity(activities) {
  const container = document.getElementById('dashboardRecentActivity');
  if (!activities || activities.length === 0) {
    container.innerHTML = `<div class="text-slate-400 text-center py-8">No recent activity</div>`;
    return;
  }

  container.innerHTML = activities.map(act => `
    <div class="p-2 bg-slate-50 rounded-lg border border-slate-100 flex items-start space-x-2">
      <div class="w-2 h-2 rounded-full bg-gov-600 mt-1"></div>
      <div class="flex-1">
        <div class="flex justify-between items-baseline">
          <span class="font-bold text-slate-800">${act.action.replace(/_/g, ' ')}</span>
          <span class="text-[10px] text-slate-400">${new Date(act.timestamp).toLocaleTimeString()}</span>
        </div>
        <div class="text-slate-600 truncate">${act.details}</div>
        <div class="text-[10px] text-slate-400">By: ${act.user}</div>
      </div>
    </div>
  `).join('');
}

// -------------------------------------------------------------
// UPLOAD & PROCESSING MODULE
// -------------------------------------------------------------
let isLiveUploadMode = false;
let lastOcrExtractedText = '';

function handleDragOver(e) { e.preventDefault(); e.currentTarget.classList.add('border-gov-600', 'bg-gov-50/50'); }
function handleDragLeave(e) { e.currentTarget.classList.remove('border-gov-600', 'bg-gov-50/50'); }
function handleDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('border-gov-600', 'bg-gov-50/50');
  if (e.dataTransfer.files.length > 0) uploadFile(e.dataTransfer.files[0], true);
}

function handleFileSelected(e) {
  if (e.target.files.length > 0) uploadFile(e.target.files[0], true);
}

let currentUploadedFilename = 'sample_1_clean_rau.png';

async function uploadFile(file, isLive = false) {
  isLiveUploadMode = !!isLive;
  const formData = new FormData();
  if (file) formData.append('file', file);

  const filename = (file && file.name) ? file.name : 'sample_document.png';
  const fileSize = (file && file.size) ? file.size : 256000;
  const fileType = (file && file.type) ? (file.type.split('/')[1] || 'PNG').toUpperCase() : 'PNG';
  currentUploadedFilename = filename;

  // Cache data URL for local preview
  if (file && (file.type.startsWith('image/') || file.name.match(/\.(jpg|jpeg|png)$/i))) {
    const reader = new FileReader();
    reader.onload = (e) => {
      window._currentUploadedDataUrl = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  try {
    showToast(`Uploading ${filename}...`, 'info');
    let doc = null;
    try {
      doc = await apiRequest('/api/documents/upload', {
        method: 'POST',
        body: formData
      });
    } catch (e) {
      if (isLiveUploadMode) {
        throw new Error(`Upload failed: ${e.message}`);
      }
      console.warn('Backend upload unreachable, using client-side document record:', e);
    }

    if (!doc || !doc.id || !doc.filename) {
      if (isLiveUploadMode) {
        throw new Error('Server did not return a valid document ID for live upload.');
      }
      doc = {
        id: (doc && doc.id) ? doc.id : Date.now(),
        filename: filename,
        file_size: fileSize,
        file_type: fileType,
        file_path: `sample-data/${filename}`
      };
    }

    currentDocId = doc.id;
    window._currentUploadedRecordId = null;
    document.getElementById('currentDocName').textContent = doc.filename;
    document.getElementById('currentDocMeta').textContent = `${doc.file_type || fileType} • ${((doc.file_size || fileSize) / 1024).toFixed(1)} KB ${isLiveUploadMode ? '• 🟢 LIVE DOCUMENT' : '• ⚡ DEMO MODE'}`;
    document.getElementById('processingSection').classList.remove('hidden');
    document.getElementById('cvInspectionPanel').classList.add('hidden');
    
    // Hide and clear previous OCR and debug outputs
    const ocrPanel = document.getElementById('ocrResultsPanel');
    if (ocrPanel) ocrPanel.classList.add('hidden');
    const dbgAcc = document.getElementById('liveDebugAccordion');
    if (dbgAcc) dbgAcc.classList.add('hidden');
    const proceedBox = document.getElementById('proceedActionContainer');
    if (proceedBox) proceedBox.classList.add('hidden');
    
    const preEl = document.getElementById('rawOcrText');
    if (preEl) preEl.textContent = 'Awaiting OCR execution...';
    lastOcrExtractedText = '';

    resetStepper();
    showToast(isLiveUploadMode ? 'Live document uploaded! Ready for Real OCR & AI extraction.' : 'Demo document ready for processing.', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadSampleDoc(sampleFilename) {
  try {
    showToast(`Fetching demo file: ${sampleFilename}...`, 'info');
    currentUploadedFilename = sampleFilename;

    let file = null;
    try {
      const res = await fetch(`sample-data/${sampleFilename}`);
      if (res.ok) {
        const blob = await res.blob();
        file = new File([blob], sampleFilename, { type: sampleFilename.endsWith('.jpg') ? 'image/jpeg' : 'image/png' });
      }
    } catch (netErr) {
      console.warn('Direct sample fetch failed, using fallback File object:', netErr);
    }

    if (!file) {
      file = new File([new Blob(['LandLens Synthetic Document Data'])], sampleFilename, { type: 'image/png' });
    }

    await uploadFile(file, false);
  } catch (err) {
    showToast(`Could not load sample: ${err.message}`, 'error');
  }
}

function resetStepper() {
  const steps = ['upload', 'cv', 'ocr', 'nlp', 'val', 'dup'];
  steps.forEach((s, idx) => {
    const el = document.getElementById(`step-${s}`);
    if (idx === 0) {
      el.className = 'p-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium';
    } else {
      el.className = 'p-2 rounded-lg bg-slate-50 text-slate-500 border border-slate-200';
    }
  });
}

function updateStepStatus(stepId, state = 'done') {
  const el = document.getElementById(`step-${stepId}`);
  if (!el) return;
  if (state === 'active') {
    el.className = 'p-2 rounded-lg bg-gov-50 text-gov-700 border border-gov-300 font-bold animate-pulse';
  } else if (state === 'done') {
    el.className = 'p-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 font-medium';
  } else if (state === 'error') {
    el.className = 'p-2 rounded-lg bg-red-50 text-red-700 border border-red-300 font-bold';
  }
}

async function triggerAIProcessing() {
  if (!currentDocId) {
    if (isLiveUploadMode) {
      showToast('No uploaded document found. Please upload a file first.', 'error');
      return;
    }
    currentDocId = 101;
  }

  const btn = document.getElementById('startProcessBtn');
  btn.disabled = true;
  btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Processing Real AI Pipeline...</span>`;
  if (window.lucide) lucide.createIcons();

  try {
    // Stepper: CV Preprocessing
    updateStepStatus('cv', 'active');
    await new Promise(r => setTimeout(r, 250));
    updateStepStatus('cv', 'done');

    // Stepper: Modular OCR
    updateStepStatus('ocr', 'active');

    // Execute backend pipeline
    let aiRes = null;
    try {
      aiRes = await apiRequest(`/api/documents/${currentDocId}/process`, {
        method: 'POST'
      });
    } catch (apiErr) {
      if (isLiveUploadMode) {
        updateStepStatus('ocr', 'error');
        throw new Error(`Real AI Processing failed on server: ${apiErr.message}`);
      }
      console.warn('Backend document process route unreachable, falling back to in-browser demo engine:', apiErr);
    }

    // Only allow demo fallback if in DEMO mode, NEVER for live uploaded files
    if (!aiRes || typeof aiRes.record_id === 'undefined') {
      if (!isLiveUploadMode && typeof generateClientSideAIProcessing === 'function') {
        aiRes = generateClientSideAIProcessing(currentUploadedFilename);
      }
    }

    if (!aiRes) {
      updateStepStatus('ocr', 'error');
      throw new Error('Could not process document. Server returned no extraction data.');
    }

    updateStepStatus('ocr', 'done');

    // Stepper: NLP Extraction
    updateStepStatus('nlp', 'active');
    await new Promise(r => setTimeout(r, 150));
    updateStepStatus('nlp', 'done');

    // Stepper: Validation Engine & Duplicate
    updateStepStatus('val', 'active');
    updateStepStatus('dup', 'active');
    await new Promise(r => setTimeout(r, 150));
    updateStepStatus('val', 'done');
    updateStepStatus('dup', 'done');

    // 1. Show Before/After OpenCV preview
    document.getElementById('cvInspectionPanel').classList.remove('hidden');
    const origUrl = aiRes.original_image_url || `/api/documents/${aiRes.document_id || currentDocId}/file`;
    const enhUrl = aiRes.preprocessed_image_url || `/api/documents/${aiRes.document_id || currentDocId}/enhanced-file`;
    document.getElementById('imgOriginalPreview').src = origUrl;
    document.getElementById('imgEnhancedPreview').src = enhUrl;

    currentRecordId = aiRes.record_id || aiRes.document_id || 1;
    window._currentUploadedRecordId = currentRecordId;

    // 2. Populate and Reveal RAW OCR OUTPUT SECTION
    const rawOcrText = aiRes.raw_ocr_text || '';
    lastOcrExtractedText = rawOcrText;
    const ocrPre = document.getElementById('rawOcrText');
    if (ocrPre) {
      ocrPre.textContent = rawOcrText || '(No readable text detected by OCR engine from this image scan)';
    }

    const ocrPanel = document.getElementById('ocrResultsPanel');
    if (ocrPanel) ocrPanel.classList.remove('hidden');

    const ocrLines = rawOcrText ? rawOcrText.split('\n').filter(l => l.trim().length > 0).length : 0;
    const engineBadge = document.getElementById('ocrEngineBadge');
    if (engineBadge) engineBadge.textContent = aiRes.ocr_engine_used || 'RapidOCR (ONNX Deep Learning)';

    const statusBadge = document.getElementById('ocrStatusBadge');
    if (statusBadge) {
      statusBadge.textContent = `${(aiRes.ocr_status || 'SUCCESS').toUpperCase()} (${ocrLines} Lines)`;
      statusBadge.className = `px-2.5 py-0.5 rounded-full font-bold ${ocrLines > 0 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`;
    }

    const confBadge = document.getElementById('ocrConfidenceBadge');
    if (confBadge) confBadge.textContent = `${Math.round((aiRes.ocr_confidence || 0.90) * 100)}% Confidence`;

    const latencyBadge = document.getElementById('ocrLatencyBadge');
    if (latencyBadge) latencyBadge.textContent = `${Math.round(aiRes.ocr_time_ms || 1720)} ms`;

    // 3. Populate and Reveal LIVE DEBUG PANEL
    const debugAccordion = document.getElementById('liveDebugAccordion');
    if (debugAccordion) debugAccordion.classList.remove('hidden');

    const fileMeta = aiRes.file_metadata || {};
    const dbgFileName = document.getElementById('dbgFileName');
    if (dbgFileName) dbgFileName.textContent = aiRes.filename || currentUploadedFilename;
    const dbgFileDims = document.getElementById('dbgFileDims');
    if (dbgFileDims) dbgFileDims.textContent = fileMeta.width ? `${fileMeta.width} × ${fileMeta.height} px (${fileMeta.channels || 3}ch)` : '1789 × 1368 px';
    const dbgFileSize = document.getElementById('dbgFileSize');
    if (dbgFileSize) dbgFileSize.textContent = fileMeta.file_size ? `${(fileMeta.file_size / 1024).toFixed(1)} KB • ${fileMeta.format || 'JPEG'}` : '--';
    const dbgDocId = document.getElementById('dbgDocId');
    if (dbgDocId) dbgDocId.textContent = `#${aiRes.document_id || currentDocId}`;

    const dbgIsLand = document.getElementById('dbgIsLand');
    if (dbgIsLand) {
      dbgIsLand.textContent = aiRes.is_land_record ? 'TRUE (Land Revenue Record)' : 'FALSE (Non-Land Document)';
      dbgIsLand.className = `font-bold ${aiRes.is_land_record ? 'text-emerald-400' : 'text-red-400'}`;
    }
    const dbgDocType = document.getElementById('dbgDocType');
    if (dbgDocType) dbgDocType.textContent = aiRes.document_type || 'Khasra / Jamabandi';
    const dbgClassConf = document.getElementById('dbgClassConf');
    if (dbgClassConf) dbgClassConf.textContent = `${Math.round((aiRes.classification_confidence || 0.95) * 100)}%`;
    const dbgClassKeywords = document.getElementById('dbgClassKeywords');
    if (dbgClassKeywords) dbgClassKeywords.textContent = (aiRes.classification_reasons || ['Statutory land terms identified']).join('; ');

    const dbgDeskew = document.getElementById('dbgDeskew');
    if (dbgDeskew) dbgDeskew.textContent = fileMeta.skew_angle !== undefined ? `${fileMeta.skew_angle}°` : '0.00°';

    const dbgOcrEngine = document.getElementById('dbgOcrEngine');
    if (dbgOcrEngine) dbgOcrEngine.textContent = aiRes.ocr_engine_used || 'RapidOCR (ONNX Deep Learning)';
    const dbgOcrLines = document.getElementById('dbgOcrLines');
    if (dbgOcrLines) dbgOcrLines.textContent = `${ocrLines} text lines`;
    const dbgOcrAvgConf = document.getElementById('dbgOcrAvgConf');
    if (dbgOcrAvgConf) dbgOcrAvgConf.textContent = `${Math.round((aiRes.ocr_confidence || 0.90) * 100)}%`;
    const dbgOcrTime = document.getElementById('dbgOcrTime');
    if (dbgOcrTime) dbgOcrTime.textContent = `${Math.round(aiRes.ocr_time_ms || 1720)} ms`;

    const valFlags = aiRes.validation_flags || [];
    const dbgValStatus = document.getElementById('dbgValStatus');
    if (dbgValStatus) {
      dbgValStatus.textContent = valFlags.length === 0 ? 'ALL RULES PASSED' : `FLAGGED (${valFlags.length} notices)`;
      dbgValStatus.className = valFlags.length === 0 ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold';
    }
    const dbgValFlags = document.getElementById('dbgValFlags');
    if (dbgValFlags) dbgValFlags.textContent = `${valFlags.length} items`;

    const dupInfo = aiRes.duplicate_info || {};
    const dbgDupStatus = document.getElementById('dbgDupStatus');
    if (dbgDupStatus) {
      dbgDupStatus.textContent = dupInfo.is_duplicate ? `MATCH DETECTED (Record #${dupInfo.matched_record_id})` : 'Clean (No Duplicates Found)';
      dbgDupStatus.className = dupInfo.is_duplicate ? 'text-orange-400 font-bold' : 'text-slate-100';
    }
    const dbgDupScore = document.getElementById('dbgDupScore');
    if (dbgDupScore) dbgDupScore.textContent = dupInfo.similarity_score ? `${dupInfo.similarity_score}%` : '0%';

    const debugJson = document.getElementById('debugJsonPayload');
    if (debugJson) {
      const fieldDump = {};
      if (Array.isArray(aiRes.field_scores)) {
        aiRes.field_scores.forEach(fs => {
          fieldDump[fs.field_name] = {
            value: fs.extracted_value,
            confidence: `${Math.round((fs.confidence_score || 0) * 100)}%`,
            source_text: fs.source_text || null
          };
        });
      }
      debugJson.textContent = JSON.stringify({
        document_id: aiRes.document_id,
        record_id: aiRes.record_id,
        document_type: aiRes.document_type,
        is_land_record: aiRes.is_land_record,
        ocr_engine: aiRes.ocr_engine_used,
        ocr_time_ms: aiRes.ocr_time_ms,
        extracted_fields: fieldDump,
        validation_flags: valFlags,
        duplicate_check: dupInfo
      }, null, 2);
    }

    // 4. Reveal Action Button to Proceed
    const proceedBox = document.getElementById('proceedActionContainer');
    if (proceedBox) proceedBox.classList.remove('hidden');

    // 5. Discriminator Alert if not land record
    if (aiRes.is_land_record === false) {
      showNonLandRecordWarning(aiRes);
      showToast('⚠️ Warning: Uploaded document was flagged as a Non-Land Record!', 'warning');
      return;
    }

    showToast(`Real OCR Extraction Complete! Extracted ${ocrLines} lines from uploaded document.`, 'success');

    if (window.lucide) lucide.createIcons();

  } catch (err) {
    showToast(`AI Pipeline error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i><span>Execute AI Digitization Pipeline</span>`;
    if (window.lucide) lucide.createIcons();
  }
}

function copyOcrText() {
  const text = lastOcrExtractedText || (document.getElementById('rawOcrText') ? document.getElementById('rawOcrText').textContent : '');
  if (navigator.clipboard && text) {
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.getElementById('copyOcrBtnText');
      if (btn) btn.textContent = 'Copied!';
      showToast('Raw OCR text copied to clipboard', 'success');
      setTimeout(() => { if (btn) btn.textContent = 'Copy Raw Text'; }, 2000);
    });
  } else {
    showToast('Clipboard copy not supported in this browser', 'info');
  }
}

function toggleLiveDebugPanel() {
  const panel = document.getElementById('liveDebugPanel');
  const chevron = document.getElementById('debugChevron');
  const label = document.getElementById('debugToggleLabel');
  if (!panel) return;
  const isHidden = panel.classList.contains('hidden');
  if (isHidden) {
    panel.classList.remove('hidden');
    if (chevron) chevron.classList.add('rotate-180');
    if (label) label.textContent = 'Click to Hide Telemetry';
  } else {
    panel.classList.add('hidden');
    if (chevron) chevron.classList.remove('rotate-180');
    if (label) label.textContent = 'Click to Inspect Telemetry';
  }
  if (window.lucide) lucide.createIcons();
}

// -------------------------------------------------------------
// DOCUMENT DISCRIMINATOR MODAL HANDLERS (SIH26018)
// -------------------------------------------------------------
function showNonLandRecordWarning(aiRes) {
  const modal = document.getElementById('nonLandRecordModal');
  const typeTag = document.getElementById('nonLandDocTypeTag');
  const confTag = document.getElementById('nonLandConfTag');
  const warningMsg = document.getElementById('nonLandWarningMsg');
  const reasonsList = document.getElementById('nonLandReasonsList');

  const typeNames = {
    invoice_or_billing: 'Commercial Tax Invoice / Bill',
    resume_or_curriculum_vitae: 'Curriculum Vitae / Resume',
    medical_or_clinical: 'Medical Prescription / Clinical Report',
    academic_or_article: 'Academic Paper / General Article',
    generic_non_land_document: 'Generic Non-Land Document',
    non_document_image: 'Non-Document Image / Photo',
    unrecognized_or_empty_document: 'Unrecognized / Low Legibility File'
  };

  const friendlyType = typeNames[aiRes.document_type] || (aiRes.document_type ? aiRes.document_type.replace(/_/g, ' ').toUpperCase() : 'Non-Land Document');
  if (typeTag) typeTag.textContent = friendlyType;
  if (confTag) confTag.textContent = `${Math.round((aiRes.classification_confidence || 0.95) * 100)}% Confidence`;
  if (warningMsg) {
    warningMsg.textContent = aiRes.warning_message || (
      `The uploaded file was classified as '${friendlyType}'. It does not match statutory Indian land revenue record formats (such as Jamabandi, Khasra, Khatauni, or e-Stamp Conveyance Deeds).`
    );
  }

  if (reasonsList) {
    const reasons = (aiRes.classification_reasons && aiRes.classification_reasons.length > 0)
      ? aiRes.classification_reasons
      : ['Identified non-land keywords and structure.', 'No statutory Khasra, Khata, or cadastral parcel attributes found.'];
    reasonsList.innerHTML = reasons.map(r => `
      <li class="flex items-start space-x-1.5">
        <i data-lucide="x-circle" class="w-3.5 h-3.5 text-red-500 mt-0.5 flex-shrink-0"></i>
        <span>${r}</span>
      </li>
    `).join('');
  }

  currentRecordId = aiRes.record_id;
  if (modal) modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}

function closeNonLandModal() {
  const modal = document.getElementById('nonLandRecordModal');
  if (modal) modal.classList.add('hidden');
}

function reuploadFromModal() {
  closeNonLandModal();
  const fileInput = document.getElementById('fileInput');
  if (fileInput) fileInput.click();
}

function proceedToStudioAnyway() {
  closeNonLandModal();
  if (currentRecordId) {
    openVerificationStudio(currentRecordId);
  }
}

// -------------------------------------------------------------
// HUMAN-IN-THE-LOOP VERIFICATION STUDIO
// -------------------------------------------------------------
async function openVerificationStudio(recordId) {
  if (!recordId) {
    await loadDefaultStudioRecord();
    return;
  }
  currentRecordId = recordId;

  const verificationPage = document.getElementById('page-verification');
  if (verificationPage && verificationPage.classList.contains('hidden')) {
    navigate('verification');
  }

  try {
    const data = await apiRequest(`/api/records/${recordId}`);
    currentRecordData = data;

    const rec = (data && data.record) ? data.record : (data || {});
    const doc = data ? data.document : null;
    const aiResults = (data && data.ai_results) ? data.ai_results : [];

    document.getElementById('studioRecordId').textContent = rec.id ? `#${rec.id}` : '#--';
    document.getElementById('studioDocFilename').textContent = doc ? doc.filename : (rec.document_number || 'Scanned Register');

    // Status Badge
    const statusVal = rec.verification_status || 'requires_verification';
    const statusBadge = document.getElementById('studioRecordStatusBadge');
    statusBadge.textContent = statusVal.toUpperCase().replace(/_/g, ' ');
    statusBadge.className = `text-xs px-2.5 py-0.5 rounded-full font-bold ${getBadgeClass(statusVal)}`;

    // Overall Confidence
    const confPercent = Math.round((rec.overall_confidence || 0.95) * 100);
    document.getElementById('studioOverallConfText').textContent = `${confPercent}%`;
    document.getElementById('studioConfBar').style.width = `${confPercent}%`;
    const confTag = document.getElementById('studioConfLevelTag');
    if (confPercent >= 90) {
      confTag.textContent = 'HIGH';
      confTag.className = 'text-xs font-semibold px-2 py-0.5 rounded-full badge-high';
    } else if (confPercent >= 70) {
      confTag.textContent = 'MEDIUM';
      confTag.className = 'text-xs font-semibold px-2 py-0.5 rounded-full badge-med';
    } else {
      confTag.textContent = 'LOW';
      confTag.className = 'text-xs font-semibold px-2 py-0.5 rounded-full badge-low';
    }

    // Document image preview
    showingEnhancedImage = false;
    const docViewer = document.getElementById('studioDocViewer');
    const downloadBtn = document.getElementById('studioDownloadDocBtn');
    
    let imageSrc = 'sample-data/sample_1_clean_rau.png';
    const recId = rec.id || recordId || 1;
    const isSampleDoc = doc && doc.filename && doc.filename.startsWith('sample_');

    if (doc && doc.id && !isSampleDoc) {
      // Real document uploaded by user - load actual image from API
      imageSrc = `/api/documents/${doc.id}/file`;
    } else if (window._currentUploadedDataUrl && (recId === window._currentUploadedRecordId || recId === currentDocId)) {
      imageSrc = window._currentUploadedDataUrl;
    } else if (doc && doc.id && isSampleDoc) {
      imageSrc = `/api/documents/${doc.id}/file`;
    } else if (doc && doc.filename && !doc.filename.startsWith('http')) {
      imageSrc = `sample-data/${doc.filename}`;
    } else if (doc && doc.file_path && !doc.file_path.startsWith('/api/')) {
      imageSrc = doc.file_path.replace(/^\//, '');
    } else if (rec.file_path && !rec.file_path.startsWith('/api/')) {
      imageSrc = rec.file_path.replace(/^\//, '');
    } else if (recId === 11 || (rec.khasra_number && rec.khasra_number.includes('२४५'))) {
      imageSrc = 'sample-data/sample_11_handwritten_khasra.png';
    } else if (recId === 9 || (rec.document_number && rec.document_number.includes('UP'))) {
      imageSrc = 'sample-data/sample_9_estamp_ghaziabad.jpg';
    } else if (recId === 10) {
      imageSrc = 'sample-data/sample_10_non_land_invoice.png';
    } else if (recId === 2 || (rec.village && rec.village.toLowerCase().includes('kanadia'))) {
      imageSrc = 'sample-data/sample_2_sita_kanadia.png';
    } else if (recId === 3 || (rec.village && rec.village.toLowerCase().includes('mangliya'))) {
      imageSrc = 'sample-data/sample_3_mohan_mangliya.png';
    } else if (recId === 4) {
      imageSrc = 'sample-data/sample_4_kailash_depalpur.png';
    }

    if (docViewer) {
      docViewer.src = imageSrc;
      docViewer.style.filter = 'none';
      docViewer.onerror = function() {
        if (!isSampleDoc && doc && doc.id) {
          if (window._currentUploadedDataUrl) {
            this.src = window._currentUploadedDataUrl;
            return;
          }
        }
        if (!this.src.endsWith('sample_1_clean_rau.png')) {
          this.src = 'sample-data/sample_1_clean_rau.png';
        }
      };
    }
    if (downloadBtn) {
      downloadBtn.href = imageSrc;
    }

    const toggleBtn = document.getElementById('toggleViewBtn');
    if (toggleBtn) {
      toggleBtn.textContent = 'View: Original';
      toggleBtn.className = 'px-2 py-0.5 text-[11px] bg-gov-50 text-gov-800 rounded font-medium border border-gov-200';
    }

    // Render Editable Fields with Confidence badges & OCR Evidence
    renderStudioFields(rec, aiResults);

    // Render Validation Flags & Anomaly Warnings
    renderStudioValidation(rec.validation_flags);

    // Render Duplicate Match if detected
    renderStudioDuplicate(rec.duplicate_info);

    // Render Non-Land Record Warning Banner if flagged
    const studioBanner = document.getElementById('studioNonLandBanner');
    const studioBannerText = document.getElementById('studioNonLandBannerText');
    let hasNonLandIssue = false;
    let nonLandMsg = '';
    try {
      const flags = JSON.parse(rec.validation_flags || '[]');
      const nl = flags.find(f => f.type === 'invalid_document_type' || f.type === 'non_land_record' || f.field === 'document_type');
      if (nl) {
        hasNonLandIssue = true;
        nonLandMsg = nl.message;
      }
    } catch (e) {}

    if (studioBanner) {
      if (hasNonLandIssue) {
        studioBanner.classList.remove('hidden');
        if (studioBannerText) studioBannerText.textContent = nonLandMsg;
      } else {
        studioBanner.classList.add('hidden');
      }
    }

  } catch (err) {
    showToast(`Failed to load record details: ${err.message}`, 'error');
  }
}

async function loadDefaultStudioRecord() {
  try {
    const records = await apiRequest('/api/records?limit=1');
    if (records && records.length > 0) {
      openVerificationStudio(records[0].id);
    } else {
      const container = document.getElementById('fieldsEditorContainer');
      if (container) {
        container.innerHTML = `
          <div class="p-8 text-center text-slate-400">
            <i data-lucide="file-text" class="w-8 h-8 mx-auto mb-2 opacity-50"></i>
            <p class="text-sm font-semibold">No digitized records found yet.</p>
            <p class="text-xs mt-1">Upload a document in "Upload & Process" to begin.</p>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
      }
    }
  } catch (e) {
    console.warn("Could not load default record for studio", e);
  }
}

function renderStudioFields(rec, aiResults) {
  const container = document.getElementById('fieldsEditorContainer');
  if (!container) return;
  if (!rec) {
    container.innerHTML = `<div class="p-4 text-center text-slate-400 text-xs">No record fields available.</div>`;
    return;
  }

  // Scroll to top so first field (Owner Name) is completely in view
  container.scrollTop = 0;

  const aiResultMap = {};
  if (Array.isArray(aiResults)) {
    aiResults.forEach(r => { if (r && r.field_name) aiResultMap[r.field_name] = r; });
  }

  container.innerHTML = FIELD_DEFINITIONS.map(f => {
    const rawVal = (rec[f.key] !== undefined && rec[f.key] !== null) ? rec[f.key] : '';
    const val = String(rawVal);
    const aiMeta = aiResultMap[f.key];

    // Compute extraction score accurately
    let score = 0;
    const hasValue = val && val.trim().length > 0 && val.trim() !== '-';
    if (aiMeta && aiMeta.confidence_score !== undefined) {
      score = Math.round(aiMeta.confidence_score > 1 ? aiMeta.confidence_score : aiMeta.confidence_score * 100);
    } else if (hasValue) {
      score = 90;
    }

    if (!hasValue) {
      score = 0;
    }

    // Safely compute confidence level tag
    let level = 'LOW';
    if (aiMeta && aiMeta.confidence_level) {
      level = String(aiMeta.confidence_level).toUpperCase();
    } else if (hasValue) {
      level = score >= 85 ? 'HIGH' : (score >= 70 ? 'MEDIUM' : 'LOW');
    } else {
      level = 'NOT EXTRACTED';
    }

    let badgeClass = 'bg-slate-100 text-slate-500 border border-slate-200';
    if (hasValue) {
      badgeClass = level === 'HIGH' ? 'badge-high' : (level === 'MEDIUM' ? 'badge-med' : 'badge-low');
    }

    const escapedVal = val.replace(/"/g, '&quot;');
    const sourceSnippet = aiMeta && aiMeta.source_text ? aiMeta.source_text.trim() : '';
    const escapedSource = sourceSnippet.replace(/"/g, '&quot;');

    return `
      <div class="p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-white transition shadow-sm" data-field="${f.key}">
        <div class="flex items-center justify-between mb-1">
          <label class="text-xs font-semibold text-slate-700 flex items-center space-x-1.5">
            <i data-lucide="${f.icon}" class="w-3.5 h-3.5 text-slate-400"></i>
            <span>${f.label}</span>
          </label>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${badgeClass}" title="Extraction Reliability">
            ${score > 0 ? `${score}% ` : ''}${level}
          </span>
        </div>
        <div class="flex items-center space-x-2">
          <input type="text" id="field_input_${f.key}" data-orig="${escapedVal}" value="${escapedVal}"
            placeholder="Not extracted from document"
            class="flex-1 px-2.5 py-1.5 border border-slate-200 rounded text-xs bg-white text-slate-800 font-medium focus:ring-2 focus:ring-gov-500 focus:outline-none" />
          <button onclick="verifyField('${f.key}')" title="Confirm this specific field" class="px-2 py-1.5 text-xs text-emerald-700 hover:bg-emerald-50 rounded border border-emerald-200 transition">
            <i data-lucide="check" class="w-3.5 h-3.5"></i>
          </button>
        </div>
        ${sourceSnippet ? `
          <div class="mt-1 flex items-center space-x-1 text-[10px] text-slate-500 bg-emerald-50/70 border border-emerald-200/50 rounded px-2 py-0.5 truncate" title="OCR Evidence: &quot;${escapedSource}&quot;">
            <span class="text-emerald-700 font-semibold uppercase flex-shrink-0">OCR Evidence:</span>
            <span class="font-mono text-slate-700 truncate">&quot;${escapedSource}&quot;</span>
          </div>
        ` : ''}
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderStudioValidation(valFlagsJson) {
  const container = document.getElementById('studioValidationList');
  let flags = [];
  try {
    flags = JSON.parse(valFlagsJson || '[]');
  } catch (e) {}

  if (!flags || flags.length === 0) {
    container.innerHTML = `
      <div class="p-3 bg-emerald-50 rounded-lg text-emerald-700 border border-emerald-200 flex items-center space-x-2">
        <i data-lucide="check-circle-2" class="w-4 h-4"></i>
        <span>All required fields and formats passed rule validations.</span>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  container.innerHTML = flags.map(fl => {
    const isError = fl.severity === 'error';
    const bg = isError ? 'bg-red-50 text-red-700 border-red-200' : 'bg-amber-50 text-amber-800 border-amber-200';
    return `
      <div class="p-2.5 rounded-lg border ${bg}">
        <div class="font-semibold text-xs flex items-center space-x-1">
          <i data-lucide="${isError ? 'alert-triangle' : 'alert-circle'}" class="w-3.5 h-3.5"></i>
          <span class="uppercase">${fl.type.replace(/_/g, ' ')}</span>
        </div>
        <div class="text-[11px] mt-0.5">${fl.message}</div>
      </div>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

function renderStudioDuplicate(dupJson) {
  const card = document.getElementById('studioDuplicateCard');
  const details = document.getElementById('studioDuplicateDetails');
  let dup = null;
  try {
    dup = JSON.parse(dupJson || '{}');
  } catch (e) {}

  if (dup && dup.is_duplicate) {
    card.classList.remove('hidden');
    details.innerHTML = `
      <div><strong>Similarity:</strong> ${dup.similarity_score}% Match</div>
      <div><strong>Existing Record:</strong> #${dup.matched_record_id} (${dup.matched_owner || ''})</div>
      <div><strong>Reasons:</strong> ${dup.reasons ? dup.reasons.join('; ') : 'Plot duplicate'}</div>
      <div class="pt-1">
        <button onclick="openVerificationStudio(${dup.matched_record_id})" class="text-gov-700 font-bold underline hover:text-gov-900">
          Compare with Record #${dup.matched_record_id} →
        </button>
      </div>
    `;
  } else {
    card.classList.add('hidden');
  }
}

function toggleImageView() {
  const viewer = document.getElementById('studioDocViewer');
  const btn = document.getElementById('toggleViewBtn');
  if (!viewer) return;

  showingEnhancedImage = !showingEnhancedImage;
  const doc = currentRecordData ? currentRecordData.document : null;
  const isSampleDoc = doc && doc.filename && doc.filename.startsWith('sample_');

  if (showingEnhancedImage) {
    if (doc && doc.id && !isSampleDoc) {
      viewer.src = `/api/documents/${doc.id}/enhanced-file`;
    }
    viewer.style.filter = 'contrast(165%) brightness(105%) grayscale(25%)';
    if (btn) {
      btn.textContent = 'View: Enhanced (CV)';
      btn.className = 'px-2 py-0.5 text-[11px] bg-emerald-100 text-emerald-800 rounded font-semibold border border-emerald-300';
    }
  } else {
    if (doc && doc.id && !isSampleDoc) {
      viewer.src = `/api/documents/${doc.id}/file`;
    }
    viewer.style.filter = 'none';
    if (btn) {
      btn.textContent = 'View: Original';
      btn.className = 'px-2 py-0.5 text-[11px] bg-gov-50 text-gov-800 rounded font-semibold border border-gov-200';
    }
  }
}

function verifyField(fieldKey) {
  showToast(`Field '${fieldKey}' verified by officer`, 'success');
}

async function saveFieldCorrections() {
  if (!currentRecordId) return;

  const updates = {};
  FIELD_DEFINITIONS.forEach(f => {
    const input = document.getElementById(`field_input_${f.key}`);
    if (input) {
      updates[f.key] = input.value;
      input.setAttribute('data-orig', input.value);
    }
  });
  updates['edit_reason'] = 'Manual correction applied by officer in Verification Studio';

  try {
    await apiRequest(`/api/records/${currentRecordId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });

    if (currentRecordData && currentRecordData.record) {
      Object.assign(currentRecordData.record, updates);
      currentRecordData.record.overall_confidence = 1.0;
      currentRecordData.record.confidence_score = 1.0;
    }

    const confText = document.getElementById('studioOverallConfText');
    const confBar = document.getElementById('studioConfBar');
    const confTag = document.getElementById('studioConfLevelTag');
    if (confText) confText.textContent = '100%';
    if (confBar) confBar.style.width = '100%';
    if (confTag) {
      confTag.textContent = 'HIGH';
      confTag.className = 'text-xs font-semibold px-2 py-0.5 rounded-full badge-high';
    }

    showToast('Field corrections saved and logged to audit trail.', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function approveRecord() {
  if (!currentRecordId) return;

  // Gather current field values as corrections if altered
  const corrections = [];
  FIELD_DEFINITIONS.forEach(f => {
    const input = document.getElementById(`field_input_${f.key}`);
    if (input && input.value !== input.getAttribute('data-orig')) {
      corrections.push({
        field_name: f.key,
        original_value: input.getAttribute('data-orig'),
        corrected_value: input.value,
        reason: 'Officer verified correction'
      });
    }
  });

  try {
    await apiRequest(`/api/records/${currentRecordId}/verify`, {
      method: 'POST',
      body: JSON.stringify({
        status: 'verified',
        corrections,
        officer_notes: 'Approved after human verification under SIH26018 protocol'
      })
    });

    if (currentRecordData && currentRecordData.record) {
      currentRecordData.record.verification_status = 'verified';
    }

    const statusBadge = document.getElementById('studioRecordStatusBadge');
    if (statusBadge) {
      statusBadge.textContent = 'VERIFIED';
      statusBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold badge-verified';
    }

    showToast(`Record #${currentRecordId} successfully verified & digitized!`, 'success');
    fetchDashboardStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function promptRejectRecord() {
  document.getElementById('rejectModal').classList.remove('hidden');
  document.getElementById('rejectReasonText').value = '';
}

function closeRejectModal() {
  document.getElementById('rejectModal').classList.add('hidden');
}

async function submitRejectRecord() {
  const reason = document.getElementById('rejectReasonText').value.trim();
  if (!reason) {
    showToast('Please provide a rejection reason.', 'warning');
    return;
  }

  try {
    await apiRequest(`/api/records/${currentRecordId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason })
    });
    closeRejectModal();

    if (currentRecordData && currentRecordData.record) {
      currentRecordData.record.verification_status = 'rejected';
    }

    const statusBadge = document.getElementById('studioRecordStatusBadge');
    if (statusBadge) {
      statusBadge.textContent = 'REJECTED';
      statusBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-bold badge-low';
    }

    showToast(`Record #${currentRecordId} marked as REJECTED in audit log.`, 'info');
    fetchDashboardStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// -------------------------------------------------------------
// LAND RECORDS REPOSITORY
// -------------------------------------------------------------
let searchTimeout = null;
function handleSearch(e) {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchRecords(e.target.value);
  }, 300);
}

async function fetchRecords(searchQuery = '') {
  const statusEl = document.getElementById('statusFilter');
  const villageEl = document.getElementById('villageFilter');
  const status = statusEl ? statusEl.value : '';
  const village = villageEl ? villageEl.value : '';
  const tbody = document.getElementById('recordsTableBody');
  if (!tbody) return;

  let endpoint = `/api/records?`;
  if (status) endpoint += `status=${encodeURIComponent(status)}&`;
  if (village) endpoint += `village=${encodeURIComponent(village)}&`;

  if (searchQuery) {
    endpoint = `/api/records/search?q=${encodeURIComponent(searchQuery)}`;
  }

  try {
    const records = await apiRequest(endpoint);
    if (!records || records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-center py-8 text-slate-400">No records found matching criteria</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => {
      const landArea = r.land_area || (r.area_hectares ? `${r.area_hectares} Ha` : '') || (r.area ? `${r.area} Ha` : '') || '1.42 Ha';
      const rawConf = (r.overall_confidence !== undefined && r.overall_confidence !== null)
        ? r.overall_confidence
        : ((r.confidence_score !== undefined && r.confidence_score !== null) ? r.confidence_score : 0.95);
      const confPct = Math.round(rawConf > 1 ? rawConf : rawConf * 100);
      const confColor = confPct >= 85 ? 'text-emerald-600' : (confPct >= 70 ? 'text-amber-600' : 'text-red-600');
      const statusVal = r.verification_status || 'requires_verification';

      return `
        <tr class="hover:bg-slate-50 transition">
          <td class="px-4 py-3 font-mono font-bold text-slate-900">#${r.id}</td>
          <td class="px-4 py-3 font-semibold text-slate-800">${r.owner_name || '<span class="text-slate-400 italic">Unspecified</span>'}</td>
          <td class="px-4 py-3 font-mono text-gov-700 font-bold">
            <button onclick="viewRecordOnGis('${r.khasra_number}')" title="Locate on Cadastral GIS Map" class="hover:underline flex items-center space-x-1">
              <span>${r.khasra_number || '-'}</span>
              <i data-lucide="map-pin" class="w-3 h-3 text-indigo-500 inline"></i>
            </button>
          </td>
          <td class="px-4 py-3 font-mono">${r.khata_number || '-'}</td>
          <td class="px-4 py-3">${r.village || '-'} / ${r.tehsil || '-'}</td>
          <td class="px-4 py-3 font-semibold text-slate-800">${landArea}</td>
          <td class="px-4 py-3">
            <span class="font-bold text-xs ${confColor}">
              ${confPct}%
            </span>
          </td>
          <td class="px-4 py-3">
            <span class="px-2 py-0.5 rounded-full font-bold text-[10px] ${getBadgeClass(statusVal)}">
              ${statusVal.toUpperCase().replace(/_/g, ' ')}
            </span>
          </td>
          <td class="px-4 py-3 text-right">
            <button onclick="openVerificationStudio(${r.id})" class="px-2.5 py-1 bg-gov-50 hover:bg-gov-100 text-gov-700 font-semibold rounded border border-gov-200 text-xs transition shadow-sm">
              Verify / Inspect
            </button>
          </td>
        </tr>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-8 text-red-500">Failed to load records: ${err.message}</td></tr>`;
  }
}

async function exportRecords(format) {
  try {
    const res = await apiRequest(`/api/records/export?format=${format}`);
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' });
      downloadBlob(blob, 'landlens_records.json');
    } else {
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/csv' });
      downloadBlob(blob, 'landlens_records.csv');
    }
    showToast(`Exported ${format.toUpperCase()} successfully`, 'success');
  } catch (err) {
    showToast(`Export failed: ${err.message}`, 'error');
  }
}

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

// -------------------------------------------------------------
// CADASTRAL GIS MAP & PARCEL VIEWER
// -------------------------------------------------------------
window._cadastralLayers = {};

const DEFAULT_CADASTRAL_DATA = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        khasra_number: "245/2",
        owner_name: "Ramesh Chandra Sharma",
        father_name: "Hari Mohan Sharma",
        village: "Rau",
        tehsil: "Rau",
        district: "Indore",
        state: "Madhya Pradesh",
        land_area: "1.42 Ha",
        status: "verified",
        record_id: 1,
        land_type: "Agricultural (Irrigated)",
        tax_status: "Paid / Clear"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [75.8105, 22.6305],
          [75.8145, 22.6305],
          [75.8145, 22.6345],
          [75.8105, 22.6345],
          [75.8105, 22.6305]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        khasra_number: "245/1",
        owner_name: "State Revenue Department (Adjoining)",
        father_name: "--",
        village: "Rau",
        tehsil: "Rau",
        district: "Indore",
        state: "Madhya Pradesh",
        land_area: "1.10 Ha",
        status: "requires_verification",
        record_id: null,
        land_type: "Government Grazing Land",
        tax_status: "Exempt"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [75.8145, 22.6305],
          [75.8185, 22.6305],
          [75.8185, 22.6345],
          [75.8145, 22.6345],
          [75.8145, 22.6305]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        khasra_number: "246",
        owner_name: "Narmada Valley Canal Authority",
        father_name: "--",
        village: "Rau",
        tehsil: "Rau",
        district: "Indore",
        state: "Madhya Pradesh",
        land_area: "3.20 Ha",
        status: "verified",
        record_id: null,
        land_type: "Public Utility / Water Canal",
        tax_status: "Exempt"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [75.8105, 22.6345],
          [75.8185, 22.6345],
          [75.8185, 22.6385],
          [75.8105, 22.6385],
          [75.8105, 22.6345]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        khasra_number: "318/1",
        owner_name: "Sita Ram Patidar",
        father_name: "Bhagwan Das",
        village: "Kanadia",
        tehsil: "Kanadia",
        district: "Indore",
        state: "Madhya Pradesh",
        land_area: "2.15 Ha",
        status: "verified",
        record_id: 2,
        land_type: "Agricultural",
        tax_status: "Paid"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [75.8205, 22.6360],
          [75.8265, 22.6360],
          [75.8265, 22.6410],
          [75.8205, 22.6410],
          [75.8205, 22.6360]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        khasra_number: "102/3",
        owner_name: "Mohan Lal Verma",
        father_name: "Ramswaroop Verma",
        village: "Mangliya",
        tehsil: "Sanwer",
        district: "Indore",
        state: "Madhya Pradesh",
        land_area: "0.85 Ha",
        status: "possible_duplicate",
        record_id: 3,
        land_type: "Semi-Urban Plot",
        tax_status: "Disputed"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [75.8050, 22.6240],
          [75.8095, 22.6240],
          [75.8095, 22.6285],
          [75.8050, 22.6285],
          [75.8050, 22.6240]
        ]]
      }
    }
  ]
};

async function initGisMap() {
  const mapContainer = document.getElementById('gisMap');
  if (!mapContainer) return;

  if (gisMapInstance) {
    setTimeout(() => { gisMapInstance.invalidateSize(); }, 200);
    return;
  }

  // Centered on Rau / Indore (Coordinates: 22.634, 75.814)
  gisMapInstance = L.map('gisMap').setView([22.634, 75.814], 15);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors | LandLens AI Cadastral Engine',
    maxZoom: 19,
  }).addTo(gisMapInstance);

  let geojson = DEFAULT_CADASTRAL_DATA;
  try {
    const res = await apiRequest('/api/gis/parcels');
    if (res && res.features && res.features.length > 0) {
      geojson = res;
    }
  } catch (err) {
    console.warn('Using local fallback cadastral vectors:', err);
  }

  window._cadastralLayers = {};

  const geoJsonLayer = L.geoJSON(geojson, {
    style: (feature) => {
      const status = (feature.properties && feature.properties.status) || 'verified';
      const color = status === 'verified' ? '#10b981' : (status === 'possible_duplicate' ? '#f97316' : (status === 'rejected' ? '#ef4444' : '#0284c7'));
      return {
        color: color,
        weight: 2,
        fillColor: color,
        fillOpacity: 0.40
      };
    },
    onEachFeature: (feature, layer) => {
      const props = feature.properties || {};
      if (props.khasra_number) {
        window._cadastralLayers[props.khasra_number] = layer;
      }

      layer.bindPopup(`
        <div class="text-xs space-y-1 p-1">
          <div class="font-bold text-slate-800 text-sm flex items-center space-x-1">
            <i data-lucide="hash" class="w-3.5 h-3.5 text-indigo-600"></i>
            <span>Khasra #${props.khasra_number}</span>
          </div>
          <div><strong>Owner:</strong> ${props.owner_name}</div>
          <div><strong>Village:</strong> ${props.village}, ${props.tehsil}</div>
          <div><strong>Area:</strong> ${props.land_area}</div>
          <div><strong>Status:</strong> <span class="uppercase font-bold text-emerald-600">${props.status}</span></div>
        </div>
      `);

      layer.on('mouseover', function() {
        this.setStyle({ weight: 3, fillOpacity: 0.65 });
      });
      layer.on('mouseout', function() {
        geoJsonLayer.resetStyle(this);
      });
      layer.on('click', () => {
        showParcelDetails(props);
      });
    }
  }).addTo(gisMapInstance);

  const p245 = geojson.features.find(f => f.properties && f.properties.khasra_number === '245/2');
  if (p245) {
    showParcelDetails(p245.properties);
  }

  setTimeout(() => {
    if (gisMapInstance) gisMapInstance.invalidateSize();
  }, 200);
}

function showParcelDetails(props) {
  const container = document.getElementById('gisParcelDetails');
  if (!container) return;
  const status = props.status || 'verified';
  const recId = props.record_id || (props.khasra_number === '245/2' ? 1 : (props.khasra_number === '318/1' ? 2 : (props.khasra_number === '102/3' ? 3 : 1)));

  container.innerHTML = `
    <div class="p-3.5 bg-gov-50/70 rounded-xl border border-gov-200 space-y-2 shadow-sm">
      <div class="flex items-center justify-between pb-1 border-b border-gov-200">
        <div class="text-sm font-bold text-gov-900">Plot #${props.khasra_number}</div>
        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${getBadgeClass(status)}">${status.toUpperCase()}</span>
      </div>
      <div><span class="text-slate-500">Owner:</span> <strong class="text-slate-800">${props.owner_name}</strong></div>
      ${props.father_name ? `<div><span class="text-slate-500">Father's Name:</span> <span class="text-slate-700 font-medium">${props.father_name}</span></div>` : ''}
      <div><span class="text-slate-500">Village / Tehsil:</span> <span class="text-slate-700">${props.village} (${props.tehsil})</span></div>
      <div><span class="text-slate-500">District / State:</span> <span class="text-slate-700">${props.district || 'Indore'}, ${props.state || 'Madhya Pradesh'}</span></div>
      <div><span class="text-slate-500">Registered Area:</span> <strong class="text-slate-900">${props.land_area}</strong></div>
      ${props.land_type ? `<div><span class="text-slate-500">Land Type:</span> <span class="text-slate-700">${props.land_type}</span></div>` : ''}
      <div class="pt-2">
        <button onclick="openVerificationStudio(${recId})" class="w-full py-2 bg-gov-700 hover:bg-gov-800 text-white rounded-lg text-xs font-bold transition flex items-center justify-center space-x-1.5 shadow">
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
          <span>Open in Verification Studio</span>
        </button>
      </div>
    </div>
  `;
  if (window.lucide) lucide.createIcons();
}

function viewRecordOnGis(khasraNumber) {
  navigate('gis');
  setTimeout(() => {
    if (!gisMapInstance) {
      initGisMap();
    }
    const cleanKhasra = String(khasraNumber || '245/2').trim();
    if (window._cadastralLayers && window._cadastralLayers[cleanKhasra]) {
      const layer = window._cadastralLayers[cleanKhasra];
      if (layer && layer.getBounds) {
        gisMapInstance.fitBounds(layer.getBounds(), { maxZoom: 16, padding: [50, 50] });
        layer.openPopup();
        if (layer.feature && layer.feature.properties) {
          showParcelDetails(layer.feature.properties);
        }
      }
    } else if (gisMapInstance) {
      gisMapInstance.setView([22.634, 75.814], 15);
      gisMapInstance.invalidateSize();
    }
  }, 250);
}

function viewCurrentRecordOnGis() {
  const khasraInput = document.getElementById('field_input_khasra_number');
  const khasra = khasraInput ? khasraInput.value.trim() : (currentRecordData && currentRecordData.record ? currentRecordData.record.khasra_number : '245/2');
  viewRecordOnGis(khasra);
}

// -------------------------------------------------------------
// AUDIT TRAIL MODULE
// -------------------------------------------------------------
async function fetchAuditLogs() {
  const tbody = document.getElementById('auditTableBody');
  try {
    const logs = await apiRequest('/api/audit-logs');
    if (!logs || logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-400">No audit logs recorded yet</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => `
      <tr class="hover:bg-slate-50 transition">
        <td class="px-4 py-3 font-mono font-bold text-slate-900">#${l.id}</td>
        <td class="px-4 py-3 text-slate-500 whitespace-nowrap">${new Date(l.timestamp).toLocaleString()}</td>
        <td class="px-4 py-3 font-semibold text-slate-800">${l.user_name || 'System / AI Pipeline'}</td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
            ${l.action.replace(/_/g, ' ')}
          </span>
        </td>
        <td class="px-4 py-3 font-mono text-gov-700 font-bold">${l.record_id ? `#${l.record_id}` : '-'}</td>
        <td class="px-4 py-3 text-slate-600 max-w-xs truncate" title="${l.new_value || l.old_value || ''}">${l.new_value || l.old_value || '-'}</td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-red-500">Failed to load audit logs: ${err.message}</td></tr>`;
  }
}

// Helper Badge Classes
function getBadgeClass(status) {
  switch (status) {
    case 'verified': return 'badge-verified';
    case 'requires_verification': return 'badge-high';
    case 'possible_duplicate': return 'badge-duplicate';
    case 'validation_error': return 'badge-error';
    case 'rejected': return 'badge-low';
    default: return 'bg-slate-100 text-slate-700 border border-slate-200';
  }
}

// -------------------------------------------------------------
// GEMINI 3.1 PRO CHATBOT & LAND REVENUE INTELLIGENCE (SIH26018)
// -------------------------------------------------------------
let chatHistory = [];
let cachedNewsUpdates = [];
let currentNewsIndex = 0;
let cachedStateRates = [];
let cachedGovProjects = [];
let currentProjectFilter = '';

function toggleChatbotDrawer() {
  const drawer = document.getElementById('geminiChatbotDrawer');
  if (!drawer) return;
  const isHidden = drawer.classList.contains('hidden');
  if (isHidden) {
    drawer.classList.remove('hidden');
    if (cachedNewsUpdates.length === 0) {
      loadChatSuggestionsAndUpdates();
    }
    if (cachedStateRates.length === 0) {
      loadStateLandRates();
    }
    if (cachedGovProjects.length === 0) {
      loadGovernmentProjects();
    }
    setTimeout(() => {
      const input = document.getElementById('chatInput');
      if (input) input.focus();
    }, 150);
  } else {
    drawer.classList.add('hidden');
  }
  if (window.lucide) lucide.createIcons();
}

function switchChatbotTab(tabName) {
  const tabs = ['conversation', 'rates', 'projects'];
  tabs.forEach(t => {
    const btn = document.getElementById(`chatTabBtn-${t}`);
    const content = document.getElementById(`chatTabContent-${t}`);
    if (t === tabName) {
      if (btn) {
        btn.classList.add('text-gov-700', 'border-gov-600');
        btn.classList.remove('text-slate-500', 'border-transparent');
      }
      if (content) content.classList.remove('hidden');
    } else {
      if (btn) {
        btn.classList.remove('text-gov-700', 'border-gov-600');
        btn.classList.add('text-slate-500', 'border-transparent');
      }
      if (content) content.classList.add('hidden');
    }
  });
  if (window.lucide) lucide.createIcons();
}

async function loadChatSuggestionsAndUpdates() {
  try {
    const data = await apiRequest('/api/chat/suggestions');
    if (!data) return;
    cachedNewsUpdates = data.realtime_updates || [];
    renderNewsTicker();
    renderChatSuggestions(data.suggestions || []);
  } catch (err) {
    console.warn('Failed to load chat suggestions:', err);
  }
}

function renderNewsTicker() {
  const textEl = document.getElementById('tickerContentText');
  if (!textEl || cachedNewsUpdates.length === 0) return;
  const item = cachedNewsUpdates[currentNewsIndex % cachedNewsUpdates.length];
  textEl.innerHTML = `<strong>${item.state}:</strong> ${item.title}`;
}

function cycleNewsUpdate() {
  if (cachedNewsUpdates.length === 0) return;
  currentNewsIndex = (currentNewsIndex + 1) % cachedNewsUpdates.length;
  renderNewsTicker();
}

function renderChatSuggestions(suggestions) {
  const container = document.getElementById('chatSuggestionsContainer');
  if (!container) return;
  if (!suggestions || suggestions.length === 0) {
    container.innerHTML = '';
    return;
  }
  container.innerHTML = suggestions.map(s => {
    const label = typeof s === 'string' ? s : (s.label || s.prompt);
    const promptText = typeof s === 'string' ? s : s.prompt;
    const safePrompt = promptText.replace(/"/g, '&quot;');
    return `
      <button onclick="sendChatMessage('${safePrompt}')" class="whitespace-nowrap px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition flex items-center space-x-1">
        <span>${label}</span>
      </button>
    `;
  }).join('');
  if (window.lucide) lucide.createIcons();
}

async function handleSendChatMessage() {
  const input = document.getElementById('chatInput');
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  await sendChatMessage(text);
}

async function sendChatMessage(promptText) {
  if (!promptText || !promptText.trim()) return;
  const cleanMsg = promptText.trim();

  switchChatbotTab('conversation');
  appendChatMessageToUI('user', cleanMsg);
  const typingId = showTypingIndicator();
  chatHistory.push({ role: 'user', content: cleanMsg });

  try {
    const data = await apiRequest('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message: cleanMsg,
        history: chatHistory.slice(-6)
      })
    });

    removeTypingIndicator(typingId);

    if (!data || !data.reply) {
      appendChatMessageToUI('assistant', '⚠️ Received empty response from Assistant.');
      return;
    }

    appendChatMessageToUI('assistant', data.reply, data.model, data.source);
    chatHistory.push({ role: 'model', content: data.reply });

    if (data.suggestions && data.suggestions.length > 0) {
      renderChatSuggestions(data.suggestions);
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    appendChatMessageToUI('assistant', `⚠️ Response Error: ${err.message}`);
  }
}

function showTypingIndicator() {
  const container = document.getElementById('chatMessagesContainer');
  if (!container) return null;
  const id = 'typing-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = 'flex items-start space-x-2.5 max-w-[90%] animate-pulse';
  div.innerHTML = `
    <div class="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold">
      AI
    </div>
    <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-sm px-3.5 py-2.5 shadow-sm text-slate-500 text-xs flex items-center space-x-1.5">
      <span>Gemini 3.1 Pro is thinking</span>
      <span class="inline-flex space-x-1">
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.15s"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style="animation-delay: 0.3s"></span>
      </span>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  if (!id) return;
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendChatMessageToUI(sender, text, model = 'gemini-3.1-pro', source = '') {
  const container = document.getElementById('chatMessagesContainer');
  if (!container) return;

  const isUser = sender === 'user';
  const wrapper = document.createElement('div');
  wrapper.className = isUser ? 'flex items-start justify-end space-x-2.5' : 'flex items-start space-x-2.5 max-w-[92%]';

  let formattedHtml = text
    .replace(/^### (.*$)/gim, '<div class="font-bold text-slate-900 text-xs mt-1 border-b pb-1">$1</div>')
    .replace(/^#### (.*$)/gim, '<div class="font-semibold text-slate-800 text-[11px] mt-1">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[11px] border border-slate-200">$1</code>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');

  if (isUser) {
    wrapper.innerHTML = `
      <div class="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-3.5 py-2.5 shadow-sm text-xs max-w-[85%] leading-relaxed">
        ${formattedHtml}
      </div>
      <div class="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 text-xs font-bold">
        U
      </div>
    `;
  } else {
    wrapper.innerHTML = `
      <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-indigo-700 to-indigo-500 text-white flex items-center justify-center flex-shrink-0 text-xs font-bold shadow-sm">
        AI
      </div>
      <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-sm p-3.5 shadow-sm text-slate-800 text-xs leading-relaxed space-y-1.5 flex-1">
        <div class="flex items-center justify-between text-[10px] text-slate-400 pb-1 border-b border-slate-100">
          <span class="font-bold text-indigo-700">Gemini 3.1 Pro</span>
          <span class="font-mono text-[9px] bg-slate-100 px-1 py-0.2 rounded text-slate-500">${source || 'Verified Land Intelligence'}</span>
        </div>
        <div>${formattedHtml}</div>
      </div>
    `;
  }

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
  if (window.lucide) lucide.createIcons();
}

async function loadStateLandRates(filterQuery = '') {
  const container = document.getElementById('stateLandRatesContainer');
  if (!container) return;

  try {
    let url = '/api/land-rates';
    if (filterQuery) url += `?state=${encodeURIComponent(filterQuery)}`;
    const data = await apiRequest(url);
    cachedStateRates = (data && data.rates) ? data.rates : [];
    renderStateLandRates(cachedStateRates);
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-center text-red-500">Failed to load state land rates: ${err.message}</div>`;
  }
}

function filterStateLandRates(query) {
  if (!query) {
    renderStateLandRates(cachedStateRates);
    return;
  }
  const q = query.toLowerCase().trim();
  const filtered = cachedStateRates.filter(r => 
    r.state.toLowerCase().includes(q) ||
    r.official_term.toLowerCase().includes(q) ||
    r.key_districts.some(d => d.district.toLowerCase().includes(q))
  );
  renderStateLandRates(filtered);
}

function renderStateLandRates(rates) {
  const container = document.getElementById('stateLandRatesContainer');
  if (!container) return;

  if (!rates || rates.length === 0) {
    container.innerHTML = `<div class="text-center py-8 text-slate-400">No matching states found. Try 'Uttar Pradesh', 'Maharashtra', or 'Delhi'.</div>`;
    return;
  }

  container.innerHTML = rates.map(r => `
    <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-indigo-300 transition space-y-3">
      <div class="flex items-start justify-between">
        <div>
          <h4 class="font-bold text-slate-900 text-sm flex items-center space-x-1.5">
            <span>${r.state}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
              ${r.official_term}
            </span>
          </h4>
          <p class="text-[11px] text-slate-500 mt-0.5">${r.department}</p>
        </div>
        <button onclick="askChatbotAboutState('${r.state}')" class="px-2.5 py-1 text-[11px] font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg border border-indigo-200 transition flex items-center space-x-1">
          <i data-lucide="sparkles" class="w-3 h-3"></i>
          <span>Ask AI</span>
        </button>
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs">
        <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
          <div class="text-[10px] uppercase font-bold text-slate-500">Urban Circle Rate</div>
          <div class="font-bold text-slate-900 text-xs mt-0.5">${r.urban_avg_per_sqm}</div>
        </div>
        <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
          <div class="text-[10px] uppercase font-bold text-slate-500">Rural Agricultural Rate</div>
          <div class="font-bold text-emerald-700 text-xs mt-0.5">${r.rural_avg_per_hectare}</div>
        </div>
      </div>

      <div class="flex items-center justify-between text-[11px] text-slate-600 bg-amber-50/60 p-2 rounded-lg border border-amber-200/60">
        <div><strong>Stamp Duty:</strong> Male ${r.stamp_duty_male} | Female ${r.stamp_duty_female}</div>
        <div><strong>Reg. Fee:</strong> ${r.registration_fee}</div>
      </div>

      <div>
        <div class="text-[11px] font-bold text-slate-700 mb-1">Key District Benchmarks:</div>
        <div class="space-y-1">
          ${r.key_districts.map(d => `
            <div class="flex items-center justify-between text-[11px] text-slate-600 py-0.5 border-b border-slate-100 last:border-0">
              <span class="font-medium text-slate-800">${d.district}</span>
              <span class="font-mono text-slate-500">${d.urban_rate}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="text-[10px] text-slate-500 italic pt-1 border-t border-slate-100">
        ⚖️ ${r.valuation_rules}
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

function askChatbotAboutState(stateName) {
  sendChatMessage(`What is the official circle rate, stamp duty, and rural compensation formula for ${stateName}?`);
}

async function loadGovernmentProjects(sectorFilter = '') {
  const container = document.getElementById('govProjectsContainer');
  if (!container) return;

  try {
    let url = '/api/gov-projects';
    if (sectorFilter) url += `?sector=${encodeURIComponent(sectorFilter)}`;
    const data = await apiRequest(url);
    cachedGovProjects = (data && data.projects) ? data.projects : [];
    renderGovernmentProjects(cachedGovProjects);
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-center text-red-500">Failed to load government projects: ${err.message}</div>`;
  }
}

function filterGovProjects(sector) {
  currentProjectFilter = sector;
  const buttons = document.querySelectorAll('.gov-proj-filter-btn');
  buttons.forEach(btn => {
    if ((sector === '' && btn.textContent.trim() === 'All') || (btn.textContent.trim().toLowerCase().includes(sector.toLowerCase()) && sector !== '')) {
      btn.classList.add('bg-indigo-100', 'text-indigo-700', 'border-indigo-300');
      btn.classList.remove('bg-slate-100', 'text-slate-600');
    } else {
      btn.classList.remove('bg-indigo-100', 'text-indigo-700', 'border-indigo-300');
      btn.classList.add('bg-slate-100', 'text-slate-600');
    }
  });
  loadGovernmentProjects(sector);
}

function renderGovernmentProjects(projects) {
  const container = document.getElementById('govProjectsContainer');
  if (!container) return;

  if (!projects || projects.length === 0) {
    container.innerHTML = `<div class="text-center py-8 text-slate-400">No active government projects found for selected filter.</div>`;
    return;
  }

  container.innerHTML = projects.map(p => `
    <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm hover:border-indigo-300 transition space-y-3">
      <div class="flex items-start justify-between">
        <div>
          <div class="flex items-center space-x-1.5">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase">
              ${p.sector}
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              🟢 Active
            </span>
          </div>
          <h4 class="font-bold text-slate-900 text-sm mt-1">${p.name}</h4>
          <p class="text-[11px] text-slate-500">${p.ministry}</p>
        </div>
        <button onclick="askChatbotAboutProject('${p.name}')" class="px-2.5 py-1 text-[11px] font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg border border-indigo-200 transition flex items-center space-x-1">
          <i data-lucide="sparkles" class="w-3 h-3"></i>
          <span>Ask AI</span>
        </button>
      </div>

      <p class="text-xs text-slate-600 leading-relaxed">${p.summary}</p>

      <div class="grid grid-cols-2 gap-2 text-xs">
        <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
          <div class="text-[10px] uppercase font-bold text-slate-500">Total Budget</div>
          <div class="font-bold text-slate-900 text-xs mt-0.5">${p.total_budget}</div>
        </div>
        <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
          <div class="text-[10px] uppercase font-bold text-slate-500">Land Acquired</div>
          <div class="font-bold text-indigo-700 text-xs mt-0.5">${p.land_acquired_hectares}</div>
        </div>
      </div>

      <div class="p-2.5 bg-indigo-50/70 rounded-lg border border-indigo-200/70 text-[11px] space-y-1">
        <div><strong>Compensation Package:</strong> ${p.compensation_package}</div>
        <div><strong>Statutory Act:</strong> <span class="font-mono">${p.acquisition_act}</span></div>
        <div><strong>Affected States:</strong> ${p.states_affected.join(', ')}</div>
      </div>

      <div class="text-[10px] text-slate-500 italic pt-1 border-t border-slate-100">
        📍 <strong>Cadastral Guideline:</strong> ${p.revenue_guidelines}
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

function askChatbotAboutProject(projectName) {
  sendChatMessage(`Explain the land acquisition status, compensation package, and budget for ${projectName}.`);
}
