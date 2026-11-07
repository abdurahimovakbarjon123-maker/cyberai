/**
 * CYBERAI Website Security Checker Script
 * Visualizes non-destructive security headers, SSL status, cookies, and score gauge.
 */

let lastScanReport = null;

document.addEventListener("DOMContentLoaded", () => {
  const scanBtn = document.getElementById("start-scan-btn");
  const urlInput = document.getElementById("target-url");
  const authCheckbox = document.getElementById("auth-confirm-check");

  if (!scanBtn || !urlInput) return;

  scanBtn.addEventListener("click", handleWebsiteScan);

  urlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleWebsiteScan();
    }
  });

  // Export Buttons
  const exportJsonBtn = document.getElementById("export-json-btn");
  const printReportBtn = document.getElementById("print-report-btn");

  if (exportJsonBtn) {
    exportJsonBtn.addEventListener("click", () => {
      if (!lastScanReport) return;
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(lastScanReport, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `cyberai_scan_${Date.now()}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });
  }

  if (printReportBtn) {
    printReportBtn.addEventListener("click", () => {
      window.print();
    });
  }
});

async function handleWebsiteScan() {
  const urlInput = document.getElementById("target-url");
  const authCheckbox = document.getElementById("auth-confirm-check");
  const scanBtn = document.getElementById("start-scan-btn");
  const resultsContainer = document.getElementById("scan-results");

  const url = urlInput.value.trim();
  const confirmed = authCheckbox ? authCheckbox.checked : false;

  if (!url) {
    showToast("Iltimos, tekshiriladigan URL manzilni kiriting.", "error");
    return;
  }

  if (!confirmed) {
    showToast("Davom etish uchun saytga egalik yoki tekshirish vakolatini tasdiqlashingiz shart!", "error");
    authCheckbox.focus();
    return;
  }

  scanBtn.disabled = true;
  scanBtn.innerHTML = `
    <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle><path d="M12 2a10 10 0 0 1 10 10"></path></svg>
    Auditor Tekshirmoqda...
  `;

  try {
    const res = await apiFetch("/api/security/check-website", {
      method: "POST",
      body: JSON.stringify({ url, confirm_authorization: confirmed })
    });

    const data = await res.json();

    if (res.ok) {
      lastScanReport = data;
      renderScanReport(data);
      resultsContainer.style.display = "block";
      resultsContainer.scrollIntoView({ behavior: "smooth" });
      showToast("Veb-sayt xavfsizlik auditi muvaffaqiyatli yakunlandi!", "success");
    } else {
      showToast(data.detail || "Tekshiruv amalga oshmadi.", "error");
    }
  } catch (err) {
    showToast("Server bilan bog'lanishda xato yuz berdi.", "error");
  } finally {
    scanBtn.disabled = false;
    scanBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 14 14"></polyline><path d="M22 12A10 10 0 1 1 12 2"></path></svg>
      Xavfsizlik Auditini Boshlash
    `;
  }
}

function renderScanReport(data) {
  const resultsContainer = document.getElementById("scan-results");
  if (!resultsContainer) return;

  const gradeClass = `grade-${data.grade.charAt(0).toLowerCase()}`;

  // Headers table rows
  const headersRows = data.headers.map(h => {
    const statusPill = h.status === "present"
      ? `<span class="severity-badge severity-secure">Mavjud</span>`
      : h.status === "insecure"
      ? `<span class="severity-badge severity-medium">Zaif</span>`
      : `<span class="severity-badge severity-critical">Mavjud Emas</span>`;

    return `
      <tr>
        <td style="font-weight: 600; font-family: monospace;">${escapeHTML(h.header)}</td>
        <td>${statusPill}</td>
        <td style="font-size: 0.85rem; color: var(--text-secondary); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
          ${h.value ? escapeHTML(h.value) : '<span style="color: var(--text-muted);">-</span>'}
        </td>
        <td style="font-size: 0.85rem;">${escapeHTML(h.recommendation)}</td>
      </tr>
    `;
  }).join("");

  // Cookies cards
  let cookiesHTML = "";
  if (data.cookies && data.cookies.length > 0) {
    cookiesHTML = data.cookies.map(c => `
      <div style="background: var(--bg-card-hover); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span style="font-weight: 700; font-family: monospace; color: var(--accent-primary);">${escapeHTML(c.name)}</span>
          <div style="display: flex; gap: 0.5rem;">
            <span class="severity-badge ${c.secure ? 'severity-secure' : 'severity-critical'}">Secure: ${c.secure ? 'HA' : 'YO\'Q'}</span>
            <span class="severity-badge ${c.httponly ? 'severity-secure' : 'severity-critical'}">HttpOnly: ${c.httponly ? 'HA' : 'YO\'Q'}</span>
            <span class="severity-badge ${c.samesite !== 'Ko\'rsatilmagan' ? 'severity-secure' : 'severity-medium'}">SameSite: ${escapeHTML(c.samesite)}</span>
          </div>
        </div>
        ${c.issues && c.issues.length > 0 ? `
          <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--severity-critical); margin-top: 0.5rem;">
            ${c.issues.map(iss => `<li>${escapeHTML(iss)}</li>`).join("")}
          </ul>
        ` : `<div style="font-size: 0.8rem; color: var(--accent-primary);">✓ Kuki xavfsiz sozlangan</div>`}
      </div>
    `).join("");
  } else {
    cookiesHTML = `<div style="color: var(--text-muted); font-size: 0.9rem; padding: 1rem 0;">Sayt javobida Set-Cookie sarlavhasi aniqlanmadi.</div>`;
  }

  // Recommendations list
  let recsHTML = "";
  if (data.recommendations && data.recommendations.length > 0) {
    recsHTML = data.recommendations.map(r => `
      <li style="margin-bottom: 0.6rem; color: var(--text-primary);">
        <strong style="color: var(--accent-primary);">•</strong> ${escapeHTML(r)}
      </li>
    `).join("");
  } else {
    recsHTML = `<li style="color: var(--accent-primary);">✓ Barcha standart xavfsizlik sarlavhalari to'g'ri sozlangan!</li>`;
  }

  resultsContainer.innerHTML = `
    <!-- Top Gauge and Grade -->
    <div class="cyber-card" style="margin-bottom: 1.5rem;">
      <div class="score-gauge-wrapper">
        <div class="score-circle">
          <svg viewBox="0 0 100 100">
            <circle class="circle-bg" cx="50" cy="50" r="40"></circle>
            <circle id="gauge-circle" class="circle-progress" cx="50" cy="50" r="40"
              stroke-dasharray="251.2"
              stroke-dashoffset="${251.2 - (251.2 * data.score / 100)}"
              style="stroke: ${data.score >= 80 ? 'var(--accent-primary)' : data.score >= 55 ? 'var(--severity-medium)' : 'var(--severity-critical)'};"
            ></circle>
          </svg>
          <div class="score-text-center">
            <div class="score-number">${data.score}</div>
            <div class="score-label">Ball / 100</div>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
          <div class="grade-badge-large ${gradeClass}">${data.grade}</div>
          <span style="font-size: 0.85rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em;">Xavfsizlik Bahosi</span>
        </div>

        <div style="display: flex; flex-direction: column; gap: 0.5rem; border-left: 1px solid var(--border-color); padding-left: 2rem;">
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted);">Tekshirilgan Manzil:</span>
            <div style="font-weight: 600; font-family: monospace; color: var(--accent-secondary);">${escapeHTML(data.target)}</div>
          </div>
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted);">HTTPS Himoyasi:</span>
            <div>${data.https_valid ? '<span class="severity-badge severity-secure">✓ HTTPS Faol</span>' : '<span class="severity-badge severity-critical">✗ HTTP (Shifrlanmagan)</span>'}</div>
          </div>
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted);">Javob Vaqti:</span>
            <div style="font-size: 0.9rem; font-family: monospace;">${data.response_time_ms ? data.response_time_ms + ' ms' : 'N/A'}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Security Headers Table -->
    <div class="cyber-card" style="margin-bottom: 1.5rem;">
      <div class="card-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        HTTP Xavfsizlik Sarlavhalari Tahlili
      </div>
      <div class="cyber-table-container">
        <table class="cyber-table">
          <thead>
            <tr>
              <th>Xavfsizlik Sarlavhasi</th>
              <th>Holat</th>
              <th>Hozirgi Qiymat</th>
              <th>Tavsiya</th>
            </tr>
          </thead>
          <tbody>
            ${headersRows}
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cookies & Recommendations Grid -->
    <div class="grid-2">
      <div class="cyber-card">
        <div class="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M8 12h8"></path><path d="M12 8v8"></path></svg>
          Cookie Fayllari Xavfsizligi
        </div>
        ${cookiesHTML}
      </div>

      <div class="cyber-card">
        <div class="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          Tizimni Kuchaytirish Bo'yicha Tavsiyalar
        </div>
        <ul style="list-style: none; padding: 0;">
          ${recsHTML}
        </ul>
      </div>
    </div>
  `;
}
