/**
 * CYBERAI Code Security Analyzer Script
 * Implements code pasting, file upload, defensive static analysis rendering,
 * line-by-line vulnerability cards, and remediation code displays.
 */

document.addEventListener("DOMContentLoaded", () => {
  const analyzeBtn = document.getElementById("analyze-btn");
  const fileInput = document.getElementById("code-file-input");
  const dropZone = document.getElementById("drop-zone");
  const codeTextarea = document.getElementById("code-input");
  const langSelect = document.getElementById("code-lang");

  if (!analyzeBtn || !codeTextarea) return;

  analyzeBtn.addEventListener("click", handleCodeAnalysis);

  // Preset Vulnerable Sample Codes for Demo & Testing
  const sampleBtn = document.getElementById("load-sample-btn");
  if (sampleBtn) {
    sampleBtn.addEventListener("click", () => {
      codeTextarea.value = `# CYBERAI Zaiflik Namunasi (Test uchun)
import os, subprocess, hashlib

# 1. Hardcoded Secret
API_KEY = "AKIA1234567890EXAMPLE"
SECRET_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozG4m1e"

# 2. SQL Injection
def get_user_by_id(cursor, user_id):
    # Zaif: f-string orqali SQL tuzish
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return cursor.execute(query)

# 3. Command Injection
def ping_server(host):
    # Zaif: shell=True bilan tizim buyrug'i
    subprocess.Popen(f"ping -c 1 {host}", shell=True)

# 4. Dangerous Code Execution
def calculate_expression(expr):
    return eval(expr)

# 5. Weak Hash
def hash_secret(data):
    return hashlib.md5(data.encode()).hexdigest()
`;
      if (langSelect) langSelect.value = "python";
      showToast("Zaiflik namunasi yuklandi! Endi 'Tahlilni boshlash' tugmasini bosing.", "info");
    });
  }

  // File Upload Handlers
  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) handleUploadedFile(file);
    });
  }

  if (dropZone) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.style.borderColor = "var(--accent-primary)";
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.style.borderColor = "var(--border-color)";
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.style.borderColor = "var(--border-color)";
      if (e.dataTransfer.files.length > 0) {
        handleUploadedFile(e.dataTransfer.files[0]);
      }
    });
  }
});

function handleUploadedFile(file) {
  const codeTextarea = document.getElementById("code-input");
  const langSelect = document.getElementById("code-lang");

  if (file.size > 1_048_576) {
    showToast("Fayl hajmi 1MB dan katta bo'lmasligi kerak.", "error");
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    codeTextarea.value = e.target.result;
    const fname = file.name.toLowerCase();
    if (fname.endsWith(".py")) langSelect.value = "python";
    else if (fname.endsWith(".js") || fname.endsWith(".ts")) langSelect.value = "javascript";
    else if (fname.endsWith(".html") || fname.endsWith(".htm")) langSelect.value = "html";
    showToast(`'${file.name}' fayli tahlilga yuklandi.`, "success");
  };
  reader.readAsText(file);
}

async function handleCodeAnalysis() {
  const codeInput = document.getElementById("code-input");
  const langSelect = document.getElementById("code-lang");
  const analyzeBtn = document.getElementById("analyze-btn");
  const resultsContainer = document.getElementById("analysis-results");

  const code = codeInput.value.trim();
  const language = langSelect.value;

  if (!code) {
    showToast("Iltimos, avval tahlil qilish uchun kod kiriting.", "error");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `
    <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10"></path></svg>
    Tahlil qilinmoqda...
  `;

  try {
    const res = await apiFetch("/api/security/analyze-code", {
      method: "POST",
      body: JSON.stringify({ code, language })
    });

    const data = await res.json();

    if (res.ok) {
      renderAnalysisResults(data);
      resultsContainer.scrollIntoView({ behavior: "smooth" });
      showToast("Kod tahlili muvaffaqiyatli yakunlandi!", "success");
    } else {
      showToast(data.detail || "Tahlil jarayonida xatolik yuz berdi.", "error");
    }
  } catch (err) {
    showToast("Server bilan bog'lanishda xato.", "error");
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      Tahlilni Boshlash
    `;
  }
}

function renderAnalysisResults(data) {
  const resultsContainer = document.getElementById("analysis-results");
  if (!resultsContainer) return;

  resultsContainer.style.display = "block";

  const scoreClass = data.score >= 80 ? "severity-secure" : data.score >= 50 ? "severity-medium" : "severity-critical";

  let findingsHTML = "";
  if (data.findings && data.findings.length > 0) {
    findingsHTML = data.findings.map((f) => `
      <div class="vulnerability-card ${escapeHTML(f.severity)}">
        <div class="vuln-header">
          <div class="vuln-title">
            <span class="severity-badge severity-${f.severity.toLowerCase()}">${escapeHTML(f.severity)}</span>
            <span>${escapeHTML(f.name)}</span>
          </div>
          ${f.line ? `<div class="vuln-line-pill">Qator: ${f.line}</div>` : ""}
        </div>

        <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.4rem;">
          ${escapeHTML(f.explanation)}
        </div>

        ${f.snippet ? `
          <div class="code-block-container" style="margin: 0.5rem 0;">
            <div class="code-header"><span>Aniqlangan kod fragmenti</span></div>
            <pre style="margin: 0; padding: 0.75rem;"><code>${escapeHTML(f.snippet)}</code></pre>
          </div>
        ` : ""}

        <div style="background: rgba(0, 229, 168, 0.05); border: 1px solid rgba(0, 229, 168, 0.2); border-radius: 6px; padding: 0.75rem; margin-top: 0.5rem;">
          <div style="font-weight: 600; color: var(--accent-primary); font-size: 0.85rem; margin-bottom: 0.25rem;">
            🛡️ Tavsiya etilgan tuzatish:
          </div>
          <div style="font-size: 0.85rem; color: var(--text-primary); margin-bottom: 0.5rem;">
            ${escapeHTML(f.fix_recommendation)}
          </div>
          ${f.corrected_code ? `
            <div class="code-block-container" style="margin: 0.35rem 0 0;">
              <div class="code-header">
                <span>Xavfsiz kod namunasi</span>
                <button class="copy-btn" onclick="navigator.clipboard.writeText(this.closest('.code-block-container').querySelector('code').innerText); showToast('Nusxalandi!', 'success');">Nusxalash</button>
              </div>
              <pre style="margin: 0; padding: 0.75rem;"><code style="color: #00E5A8;">${escapeHTML(f.corrected_code)}</code></pre>
            </div>
          ` : ""}
        </div>
      </div>
    `).join("");
  } else {
    findingsHTML = `
      <div style="text-align: center; padding: 3rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px solid var(--accent-primary);">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2" style="margin-bottom: 1rem;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline><path d="M22 12A10 10 0 1 1 12 2"></path></svg>
        <h3 style="color: var(--accent-primary); margin-bottom: 0.5rem;">Zaifliklar Topilmadi!</h3>
        <p style="color: var(--text-secondary); font-size: 0.9rem;">Tahlil qilingan kodingizda xavfli konstruksiyalar, ochiq kalitlar yoki SQL inyeksiyalari aniqlanmadi.</p>
      </div>
    `;
  }

  resultsContainer.innerHTML = `
    <div class="cyber-card" style="margin-bottom: 1.5rem;">
      <div class="card-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        Tahlil Natijalari Xulosasi
      </div>
      <div class="grid-3" style="margin-top: 1rem;">
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(0, 229, 168, 0.1); color: var(--accent-primary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">Xavfsizlik Bali</span>
            <span class="stat-value" style="color: ${data.score >= 80 ? 'var(--accent-primary)' : data.score >= 50 ? 'var(--severity-medium)' : 'var(--severity-critical)'};">${data.score} / 100</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(255, 75, 114, 0.1); color: var(--severity-critical);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">Xavf Darajasi</span>
            <span class="stat-value">${escapeHTML(data.risk_level)}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: rgba(0, 163, 255, 0.1); color: var(--accent-secondary);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          </div>
          <div class="stat-content">
            <span class="stat-label">Aniqlangan Muammolar</span>
            <span class="stat-value">${data.findings_count}</span>
          </div>
        </div>
      </div>
    </div>

    <div style="margin-top: 1.5rem;">
      <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        Batafsil Zaifliklar Ro'yxati (${data.findings_count})
      </h3>
      ${findingsHTML}
    </div>
  `;
}
