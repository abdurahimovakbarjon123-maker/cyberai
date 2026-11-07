/**
 * CYBERAI Admin Dashboard Script
 * Manages system metrics, registered user audits, and security activity logs.
 */

document.addEventListener("DOMContentLoaded", () => {
  const adminPage = document.getElementById("admin-dashboard-view");
  if (!adminPage) return;

  loadAdminData();

  const refreshBtn = document.getElementById("refresh-admin-btn");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      loadAdminData();
      showToast("Ma'lumotlar yangilandi.", "info");
    });
  }
});

async function loadAdminData() {
  await Promise.all([
    loadStats(),
    loadUsers(),
    loadAuditLogs()
  ]);
}

async function loadStats() {
  try {
    const res = await apiFetch("/api/admin/stats");
    if (!res.ok) {
      if (res.status === 403) {
        showToast("Administrator huquqi mavjud emas!", "error");
        setTimeout(() => window.location.href = "/", 1000);
      }
      return;
    }

    const stats = await res.json();

    document.getElementById("stat-users-val").textContent = stats.total_users;
    document.getElementById("stat-convs-val").textContent = stats.total_conversations;
    document.getElementById("stat-reports-val").textContent = stats.total_security_reports;
    document.getElementById("stat-ai-provider-val").textContent = stats.ai_provider.toUpperCase();
    document.getElementById("stat-ai-mode-val").textContent = stats.ai_status;
    document.getElementById("stat-health-val").textContent = stats.system_health;

  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

async function loadUsers() {
  const tbody = document.getElementById("admin-users-tbody");
  if (!tbody) return;

  try {
    const res = await apiFetch("/api/admin/users");
    if (!res.ok) return;

    const users = await res.json();
    tbody.innerHTML = "";

    users.forEach((u) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family: monospace; color: var(--text-muted);">#${u.id}</td>
        <td style="font-weight: 600; color: var(--text-primary);">${escapeHTML(u.username)}</td>
        <td style="color: var(--text-secondary);">${escapeHTML(u.email)}</td>
        <td>
          <span class="severity-badge ${u.role === 'admin' ? 'severity-low' : 'severity-secure'}">
            ${escapeHTML(u.role.toUpperCase())}
          </span>
        </td>
        <td style="text-align: center;">${u.conversation_count}</td>
        <td style="text-align: center;">${u.report_count}</td>
        <td style="font-size: 0.8rem; color: var(--text-muted);">${new Date(u.created_at).toLocaleString()}</td>
      </tr>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load users:", err);
  }
}

async function loadAuditLogs() {
  const tbody = document.getElementById("admin-logs-tbody");
  if (!tbody) return;

  try {
    const res = await apiFetch("/api/admin/logs");
    if (!res.ok) return;

    const logs = await res.json();
    tbody.innerHTML = "";

    logs.forEach((l) => {
      const statusPill = l.status === "success"
        ? `<span class="severity-badge severity-secure">Muvaffaqiyatli</span>`
        : l.status === "blocked"
        ? `<span class="severity-badge severity-critical">Bloklangan</span>`
        : `<span class="severity-badge severity-high">Xato</span>`;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-size: 0.8rem; color: var(--text-muted); font-family: monospace;">${new Date(l.created_at).toLocaleTimeString()}</td>
        <td style="font-weight: 600; font-family: monospace; color: var(--accent-secondary);">${escapeHTML(l.action)}</td>
        <td style="color: var(--text-primary);">${escapeHTML(l.username || 'Noma\'lum')}</td>
        <td style="font-family: monospace; font-size: 0.85rem; color: var(--text-muted);">${escapeHTML(l.ip_address || '-')}</td>
        <td>${statusPill}</td>
        <td style="font-size: 0.85rem; color: var(--text-secondary); max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHTML(l.details || '')}">
          ${escapeHTML(l.details || '-')}
        </td>
      </tr>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load audit logs:", err);
  }
}
