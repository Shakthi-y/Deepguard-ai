(() => {
  "use strict";

  const API_BASE = window.location.origin.includes("null") || window.location.protocol === "file:"
    ? "http://localhost:8000"
    : "";

  const AGENTS = [
    { name: "AI Orchestrator", desc: "Coordinates the full pipeline and assembles the final report." },
    { name: "Image Validation Agent", desc: "Checks file type, size, MIME and image integrity." },
    { name: "Deepfake Detection Agent", desc: "Runs model2_skincare.h5 inference at 224×224." },
    { name: "Forensic Analysis Agent", desc: "Inspects metadata, compression, and dimensions." },
    { name: "Verification Agent", desc: "Cross-checks model output against forensic evidence." },
    { name: "Confidence Agent", desc: "Separates model confidence from system confidence." },
    { name: "Explanation Agent", desc: "Generates a grounded, plain-language explanation." },
  ];

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  let selectedFile = null;
  let currentAnalysis = null;
  let zoomLevel = 1;

  // ---------- NAV ----------
  function showView(name) {
    $$(".view").forEach(v => v.classList.add("hidden"));
    const el = document.getElementById(`view-${name}`);
    if (el) el.classList.remove("hidden");
    $$(".nav-link").forEach(b => b.classList.toggle("active", b.dataset.nav === name));
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (name === "history") renderHistory();
  }

  $$("[data-nav]").forEach(el => {
    el.addEventListener("click", () => showView(el.dataset.nav));
  });

  $("#scrollPipelineBtn").addEventListener("click", () => {
    document.getElementById("pipelineSection").scrollIntoView({ behavior: "smooth" });
  });

  // ---------- LANDING AGENT FLOW ----------
  function renderLandingFlow() {
    const container = $("#landingAgentFlow");
    container.innerHTML = AGENTS.map((a, i) => `
      <div class="agent-node">
        <span class="idx">0${i}</span>
        <div class="name">${a.name}</div>
        <div class="desc">${a.desc}</div>
      </div>
    `).join("");
  }
  renderLandingFlow();

  // ---------- MODEL HEALTH ----------
  async function checkHealth() {
    const pill = $("#modelStatusPill");
    const text = $("#modelStatusText");
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      const data = await res.json();
      const model = data.model || {};
      if (model.model_loaded) {
        pill.className = "nav-status ok";
        text.textContent = "Model online";
      } else {
        pill.className = "nav-status sim";
        text.textContent = "Simulation mode";
      }
    } catch (e) {
      pill.className = "nav-status down";
      text.textContent = "Backend offline";
    }
  }
  checkHealth();

  // ---------- UPLOAD ----------
  const dropzone = $("#dropzone");
  const fileInput = $("#fileInput");
  const previewWrap = $("#previewWrap");
  const dropzoneInner = $("#dropzoneInner");
  const previewImg = $("#previewImg");
  const analyzeBtn = $("#analyzeBtn");
  const uploadError = $("#uploadError");

  dropzone.addEventListener("click", (e) => {
    if (e.target.id === "changeImageBtn") return;
    fileInput.click();
  });
  ["dragenter", "dragover"].forEach(evt =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); })
  );
  ["dragleave", "drop"].forEach(evt =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); })
  );
  dropzone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
  });
  $("#changeImageBtn").addEventListener("click", (e) => {
    e.stopPropagation();
    resetUpload();
  });

  function resetUpload() {
    selectedFile = null;
    fileInput.value = "";
    previewWrap.classList.add("hidden");
    dropzoneInner.classList.remove("hidden");
    analyzeBtn.disabled = true;
    uploadError.classList.add("hidden");
  }

  function handleFile(file) {
    uploadError.classList.add("hidden");
    const allowed = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      showUploadError(`Unsupported format: ${file.type || "unknown"}. Use JPG, PNG or WEBP.`);
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showUploadError(`File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max is 10MB.`);
      return;
    }
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    dropzoneInner.classList.add("hidden");
    previewWrap.classList.remove("hidden");
    analyzeBtn.disabled = false;
  }

  function showUploadError(msg) {
    uploadError.textContent = msg;
    uploadError.classList.remove("hidden");
  }

  analyzeBtn.addEventListener("click", () => {
    if (!selectedFile) return;
    runAnalysis(selectedFile);
  });

  // ---------- LIVE PIPELINE ----------
  function renderLiveAgentList() {
    const list = $("#agentLiveList");
    list.innerHTML = AGENTS.map((a, i) => `
      <li class="agent-live-item" id="live-agent-${i}">
        <div class="status-icon"><span class="idle">·</span></div>
        <div>
          <div class="agent-live-name">${a.name}</div>
          <div class="agent-live-detail" id="live-agent-detail-${i}">Queued</div>
        </div>
      </li>
    `).join("");
  }

  function setAgentState(i, state, detail) {
    const item = document.getElementById(`live-agent-${i}`);
    if (!item) return;
    item.classList.remove("active", "done");
    const iconWrap = item.querySelector(".status-icon");
    if (state === "active") {
      item.classList.add("active");
      iconWrap.innerHTML = `<span class="spinner"></span>`;
    } else if (state === "done") {
      item.classList.add("done");
      iconWrap.innerHTML = `✓`;
    } else {
      iconWrap.innerHTML = `·`;
    }
    if (detail) document.getElementById(`live-agent-detail-${i}`).textContent = detail;
  }

  async function runAnalysis(file) {
    showView("pipeline");
    renderLiveAgentList();
    $("#pipelinePreviewImg").src = URL.createObjectURL(file);

    // Kick off the real API call immediately
    const formData = new FormData();
    formData.append("file", file);
    const apiPromise = fetch(`${API_BASE}/api/analyze`, { method: "POST", body: formData })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw { message: data?.detail?.message || "Analysis failed", data };
        return data;
      });

    // Animate through the agent list at a readable pace, independent of API latency
    const stepDelay = 550;
    for (let i = 0; i < AGENTS.length; i++) {
      setAgentState(i, "active");
      await sleep(stepDelay);
      setAgentState(i, "done", "Completed");
    }

    try {
      const analysis = await apiPromise;
      currentAnalysis = analysis;
      saveToHistory(analysis, file);
      renderResults(analysis, file);
      showView("results");
    } catch (err) {
      console.error(err);
      showView("upload");
      showUploadError(
        (err && err.message) ||
        "Analysis failed. Please check that the backend is running and try again."
      );
    }
  }

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ---------- RESULTS ----------
  function renderResults(a, file) {
    const banner = $("#verdictBanner");
    const verdictClass = a.verdict === "LIKELY REAL" ? "real" : a.verdict === "LIKELY FAKE" ? "fake" : "uncertain";
    banner.className = `verdict-banner ${verdictClass}`;
    $("#verdictLabel").textContent = a.verdict;
    $("#verdictFile").textContent = `${a.filename} · ${new Date(a.timestamp).toLocaleString()}`;

    const imgUrl = file ? URL.createObjectURL(file) : (a._imgDataUrl || "");
    $("#resultImg").src = imgUrl;
    resetViewer();

    // gauges
    setGauge("modelGaugeFill", "modelGaugeNum", a.confidence.model_confidence);
    setGauge("sysGaugeFill", "sysGaugeNum", a.confidence.system_confidence);
    $("#confidenceBand").textContent = `System confidence band: ${a.confidence.confidence_band}`;

    // detection
    $("#modelSimTag").textContent = a.simulation_mode ? "SIMULATED — no model file" : "";
    $("#modelSimTag").style.display = a.simulation_mode ? "inline-block" : "none";
    setProb("realProbFill", "realProbNum", a.detection.real_probability);
    setProb("fakeProbFill", "fakeProbNum", a.detection.fake_probability);

    // forensic
    const f = a.forensic;
    $("#forensicGrid").innerHTML = [
      ["MIME Type", f.mime_type],
      ["Dimensions", f.dimensions],
      ["Format", f.format],
      ["File Size", `${f.file_size_kb} KB`],
      ["EXIF Present", f.has_exif ? "Yes" : "No"],
      ["Compression", f.estimated_compression],
    ].map(([label, val]) => `
      <div class="forensic-item"><span class="f-label">${label}</span><span class="f-value">${val}</span></div>
    `).join("");
    $("#flagsList").innerHTML = (f.flags || []).map(flag => `<div class="flag-item">⚠ ${flag}</div>`).join("");

    // verification + explanation
    $("#reasoningText").textContent = a.verification.reasoning;
    $("#explanationText").textContent = a.explanation;
    $("#disclaimerText").textContent = a.disclaimer;
  }

  function setGauge(fillId, numId, value) {
    const circumference = 2 * Math.PI * 58; // 364.4
    const fill = document.getElementById(fillId);
    const offset = circumference - (value * circumference);
    requestAnimationFrame(() => { fill.style.strokeDashoffset = offset; });
    document.getElementById(numId).textContent = `${Math.round(value * 100)}%`;
  }

  function setProb(fillId, numId, value) {
    document.getElementById(fillId).style.width = `${Math.round(value * 100)}%`;
    document.getElementById(numId).textContent = `${Math.round(value * 100)}%`;
  }

  $("#newAnalysisBtn").addEventListener("click", () => { resetUpload(); showView("upload"); });

  $("#downloadReportBtn").addEventListener("click", () => {
    if (!currentAnalysis) return;
    window.open(`${API_BASE}/api/report/${currentAnalysis.id}`, "_blank");
  });

  // ---------- IMAGE VIEWER (zoom/pan/fullscreen) ----------
  function resetViewer() {
    zoomLevel = 1;
    const img = $("#resultImg");
    img.style.transform = "scale(1)";
    img.style.transformOrigin = "center center";
  }
  $("#zoomInBtn").addEventListener("click", () => { zoomLevel = Math.min(zoomLevel + 0.3, 3); applyZoom(); });
  $("#zoomOutBtn").addEventListener("click", () => { zoomLevel = Math.max(zoomLevel - 0.3, 1); applyZoom(); });
  $("#zoomResetBtn").addEventListener("click", resetViewer);
  function applyZoom() { $("#resultImg").style.transform = `scale(${zoomLevel})`; }

  $("#fullscreenBtn").addEventListener("click", () => {
    const viewer = $("#imageViewer");
    if (viewer.requestFullscreen) viewer.requestFullscreen();
  });

  let isPanning = false, panStartX = 0, panStartY = 0, imgOffsetX = 0, imgOffsetY = 0;
  const resultImgEl = document.getElementById("resultImg");
  resultImgEl.addEventListener("mousedown", (e) => {
    if (zoomLevel <= 1) return;
    isPanning = true; panStartX = e.clientX; panStartY = e.clientY;
    resultImgEl.style.cursor = "grabbing";
  });
  window.addEventListener("mouseup", () => { isPanning = false; resultImgEl.style.cursor = "grab"; });
  window.addEventListener("mousemove", (e) => {
    if (!isPanning) return;
    imgOffsetX += (e.clientX - panStartX);
    imgOffsetY += (e.clientY - panStartY);
    panStartX = e.clientX; panStartY = e.clientY;
    resultImgEl.style.transform = `scale(${zoomLevel}) translate(${imgOffsetX / zoomLevel}px, ${imgOffsetY / zoomLevel}px)`;
  });

  // ---------- HISTORY (localStorage) ----------
  const HISTORY_KEY = "deepguard_history_v1";

  function saveToHistory(analysis, file) {
    const items = getHistory();
    const record = {
      id: analysis.id,
      filename: analysis.filename,
      timestamp: analysis.timestamp,
      verdict: analysis.verdict,
      system_confidence: analysis.confidence.system_confidence,
      analysis, // full payload so history can be reopened
    };
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        record.thumb = reader.result;
        items.unshift(record);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 30)));
      };
      reader.readAsDataURL(file);
    } else {
      items.unshift(record);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 30)));
    }
  }

  function getHistory() {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || []; }
    catch { return []; }
  }

  function renderHistory() {
    const items = getHistory();
    const list = $("#historyList");
    const empty = $("#historyEmpty");
    if (!items.length) {
      list.innerHTML = "";
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");
    list.innerHTML = items.map(item => {
      const cls = item.verdict === "LIKELY REAL" ? "real" : item.verdict === "LIKELY FAKE" ? "fake" : "uncertain";
      return `
        <div class="history-item" data-id="${item.id}">
          <img class="history-thumb" src="${item.thumb || ''}" alt="" />
          <div class="history-info">
            <div class="history-name">${item.filename}</div>
            <div class="history-meta">${new Date(item.timestamp).toLocaleString()} · ${Math.round((item.system_confidence||0)*100)}% confidence</div>
          </div>
          <span class="history-badge ${cls}">${item.verdict}</span>
        </div>
      `;
    }).join("");

    $$(".history-item").forEach(el => {
      el.addEventListener("click", () => {
        const item = items.find(i => i.id === el.dataset.id);
        if (!item) return;
        currentAnalysis = item.analysis;
        item.analysis._imgDataUrl = item.thumb;
        renderResults(item.analysis, null);
        showView("results");
      });
    });
  }

  // ---------- CHAT ----------
  const chatLauncher = $("#chatLauncher");
  const chatPanel = $("#chatPanel");
  chatLauncher.addEventListener("click", () => chatPanel.classList.toggle("hidden"));
  $("#closeChatBtn").addEventListener("click", () => chatPanel.classList.add("hidden"));

  $("#chatForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("#chatInput");
    const question = input.value.trim();
    if (!question) return;
    appendChat(question, "user");
    input.value = "";
    const typingEl = appendChat("…", "bot");
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, analysis_id: currentAnalysis ? currentAnalysis.id : null }),
      });
      const data = await res.json();
      typingEl.textContent = data.answer || "No answer available.";
    } catch (err) {
      typingEl.textContent = "Couldn't reach DeepGuard's backend. Is it running?";
    }
  });

  function appendChat(text, who) {
    const messages = $("#chatMessages");
    const div = document.createElement("div");
    div.className = `chat-msg chat-msg-${who}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  // init
  showView("landing");
})();
