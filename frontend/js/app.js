/**
 * CYBERAI — Global Application Framework
 * Handles authentication lifecycle, multilingual dictionary, notifications, and UI shell.
 */

// Global State
window.CYBERAI = {
  token: localStorage.getItem("cyberai_token") || null,
  user: null,
  lang: localStorage.getItem("cyberai_lang") || "uz",
  translations: {
    uz: {
      new_chat: "Yangi Suhbat",
      chat_history: "Suhbatlar tarixi",
      code_analyzer: "Kod Tahlili",
      website_scanner: "Sayt Xavfsizligi",
      admin_panel: "Admin Boshqaruvi",
      logout: "Chiqish",
      settings: "Sozlamalar",
      model: "Model",
      language: "Til",
      demo_badge: "Demo Rejimi",
      online_status: "Himoya Faol",
      input_placeholder: "Kiberxavfsizlik bo'yicha savolingizni yozing...",
      send: "Yuborish",
      stop: "To'xtatish",
      copy: "Nusxalash",
      copied: "Nusxalandi!",
      regenerate: "Qayta yaratish",
      delete_chat_confirm: "Haqiqatan ham bu suhbatni o'chirmoqchimisiz?",
      code_analyzer_title: "Manba Kodi Xavfsizlik Tahlili",
      code_analyzer_desc: "Python, JavaScript va HTML kodlaridagi zaifliklarni statik tekshirish",
      scanner_title: "Veb-sayt Xavfsizlik Auditi",
      scanner_desc: "Xavfsizlik sarlavhalari, SSL konfiguratsiyasi va kuki himoyasini tahlil qilish",
      admin_title: "Tizim Administratori Paneli",
      admin_desc: "Foydalanuvchilar, AI faoliyati va xavfsizlik audit jurnallari",
      scan_btn: "Tahlilni boshlash",
      upload_file: "Fayl yuklash (.py, .js, .html)",
      auth_confirm: "Men ushbu domenga egalik qilishimni yoki tekshirish vakolatim borligini tasdiqlayman."
    },
    en: {
      new_chat: "New Chat",
      chat_history: "Conversation History",
      code_analyzer: "Code Analyzer",
      website_scanner: "Website Scanner",
      admin_panel: "Admin Dashboard",
      logout: "Sign Out",
      settings: "Settings",
      model: "Model",
      language: "Language",
      demo_badge: "Demo Mode",
      online_status: "Active Shield",
      input_placeholder: "Ask anything about cybersecurity and defense...",
      send: "Send",
      stop: "Stop",
      copy: "Copy",
      copied: "Copied!",
      regenerate: "Regenerate",
      delete_chat_confirm: "Are you sure you want to delete this conversation?",
      code_analyzer_title: "Static Code Security Analyzer",
      code_analyzer_desc: "Defensive static auditing for Python, JavaScript, and HTML source code",
      scanner_title: "Website Security Checker",
      scanner_desc: "Non-destructive audit of HTTP security headers, SSL/TLS, and cookies",
      admin_title: "Admin System Console",
      admin_desc: "System metrics, user registry, and security audit logs",
      scan_btn: "Run Analysis",
      upload_file: "Upload Source File (.py, .js, .html)",
      auth_confirm: "I confirm ownership or explicit authorization to audit this domain."
    },
    ru: {
      new_chat: "Новый чат",
      chat_history: "История диалогов",
      code_analyzer: "Анализатор кода",
      website_scanner: "Аудит сайтов",
      admin_panel: "Админ-панель",
      logout: "Выйти",
      settings: "Настройки",
      model: "Модель",
      language: "Язык",
      demo_badge: "Демо Режим",
      online_status: "Защита активна",
      input_placeholder: "Задайте вопрос по кибербезопасности и защите...",
      send: "Отправить",
      stop: "Остановить",
      copy: "Копировать",
      copied: "Скопировано!",
      regenerate: "Перегенерировать",
      delete_chat_confirm: "Вы уверены, что хотите удалить этот диалог?",
      code_analyzer_title: "Статический анализ безопасности кода",
      code_analyzer_desc: "Аудит исходного кода Python, JavaScript и HTML на наличие уязвимостей",
      scanner_title: "Аудит безопасности веб-сайтов",
      scanner_desc: "Неразрушающая проверка заголовков безопасности, SSL/TLS и cookies",
      admin_title: "Панель администратора",
      admin_desc: "Пользователи, метрики ИИ и журналы аудита безопасности",
      scan_btn: "Запустить анализ",
      upload_file: "Загрузить файл (.py, .js, .html)",
      auth_confirm: "Я подтверждаю владение или авторизованный доступ для проверки данного домена."
    }
  }
};

/**
 * Reusable Authenticated Fetch Wrapper
 */
async function apiFetch(url, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};

  if (CYBERAI.token) {
    headers["Authorization"] = `Bearer ${CYBERAI.token}`;
  }

  // Set default JSON Content-Type if body is stringified and not FormData
  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    // Expired or invalid token: purge and redirect if not on login/register
    const currentPath = window.location.pathname;
    if (currentPath !== "/login" && currentPath !== "/register") {
      logoutUser();
    }
  }

  return response;
}

/**
 * Toast Notification System
 */
function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  const iconSvg = type === "success" 
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00E5A8" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`
    : type === "error"
    ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF4B72" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`
    : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;

  toast.innerHTML = `
    <div>${iconSvg}</div>
    <div style="flex: 1;">${escapeHTML(message)}</div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/**
 * Helper to escape HTML to prevent XSS
 */
function escapeHTML(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Client-Side Authentication Check
 */
async function checkAuthStatus() {
  const currentPath = window.location.pathname;
  const isAuthPage = currentPath === "/login" || currentPath === "/register";

  if (!CYBERAI.token) {
    if (isAuthPage) return null;

    // Automatically issue seamless guest session
    try {
      const guestRes = await fetch("/api/auth/guest", { method: "POST" });
      if (guestRes.ok) {
        const guestData = await guestRes.json();
        CYBERAI.token = guestData.access_token;
        CYBERAI.user = guestData.user;
        localStorage.setItem("cyberai_token", guestData.access_token);
        localStorage.setItem("cyberai_user", JSON.stringify(guestData.user));
        renderUserProfile(guestData.user);
        return guestData.user;
      }
    } catch (err) {
      console.warn("Guest auth fallback:", err);
    }
    return null;
  }

  try {
    const res = await apiFetch("/api/auth/me");
    if (res.ok) {
      const user = await res.json();
      CYBERAI.user = user;
      localStorage.setItem("cyberai_user", JSON.stringify(user));
      renderUserProfile(user);

      if (isAuthPage) {
        window.location.href = "/";
      }

      // Check admin link visibility
      const adminNav = document.getElementById("admin-nav-item");
      if (adminNav) {
        adminNav.style.display = user.role === "admin" ? "flex" : "none";
      }

      return user;
    } else {
      if (!isAuthPage) {
        // Try auto-renewing guest session instead of locking out
        try {
          const guestRes = await fetch("/api/auth/guest", { method: "POST" });
          if (guestRes.ok) {
            const guestData = await guestRes.json();
            CYBERAI.token = guestData.access_token;
            CYBERAI.user = guestData.user;
            localStorage.setItem("cyberai_token", guestData.access_token);
            localStorage.setItem("cyberai_user", JSON.stringify(guestData.user));
            renderUserProfile(guestData.user);
            return guestData.user;
          }
        } catch (e) {}
      }
    }
  } catch (err) {
    console.error("Auth check failed:", err);
  }
  return null;
}

/**
 * Render user info in sidebar
 */
function renderUserProfile(user) {
  const avatar = document.getElementById("user-avatar-initial");
  const name = document.getElementById("user-display-name");
  const badge = document.getElementById("user-role-badge");

  if (avatar && user.username) {
    avatar.textContent = user.username.charAt(0).toUpperCase();
  }
  if (name) {
    name.textContent = user.username;
  }
  if (badge) {
    badge.textContent = user.role.toUpperCase();
    if (user.role === "admin") {
      badge.style.color = "#00A3FF";
      badge.style.background = "rgba(0, 163, 255, 0.15)";
    }
  }
}

/**
 * Logout User
 */
function logoutUser() {
  localStorage.removeItem("cyberai_token");
  localStorage.removeItem("cyberai_user");
  CYBERAI.token = null;
  CYBERAI.user = null;
  window.location.href = "/login";
}

/**
 * Language Switcher
 */
function setLanguage(lang) {
  if (!CYBERAI.translations[lang]) return;
  CYBERAI.lang = lang;
  localStorage.setItem("cyberai_lang", lang);

  // Apply translations to data-i18n elements
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const trans = CYBERAI.translations[lang][key];
    if (trans) {
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        el.placeholder = trans;
      } else {
        el.textContent = trans;
      }
    }
  });

  const langSelect = document.getElementById("lang-selector");
  if (langSelect) {
    langSelect.value = lang;
  }
}

/**
 * Sidebar Toggle logic
 */
function setupSidebar() {
  const sidebar = document.getElementById("main-sidebar");
  const toggleBtn = document.getElementById("toggle-sidebar-btn");
  const mobileToggle = document.getElementById("mobile-menu-btn");

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("mobile-open");
    });
  }
}

// Global initialization on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  setupSidebar();
  setLanguage(CYBERAI.lang);

  const langSelect = document.getElementById("lang-selector");
  if (langSelect) {
    langSelect.value = CYBERAI.lang;
    langSelect.addEventListener("change", (e) => setLanguage(e.target.value));
  }

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      logoutUser();
    });
  }

  checkAuthStatus();

  // AI Key Modal Handlers
  const openModalBtn = document.getElementById("open-api-modal-btn");
  const modal = document.getElementById("api-key-modal");
  const closeModalBtn = document.getElementById("close-api-modal-btn");
  const cancelModalBtn = document.getElementById("cancel-api-modal-btn");
  const saveKeyBtn = document.getElementById("save-api-modal-btn");

  if (openModalBtn && modal) {
    openModalBtn.addEventListener("click", () => {
      modal.classList.add("active");
    });
  }

  function closeModal() {
    if (modal) modal.classList.remove("active");
  }

  if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
  if (cancelModalBtn) cancelModalBtn.addEventListener("click", closeModal);

  if (saveKeyBtn) {
    saveKeyBtn.addEventListener("click", async () => {
      const provider = document.getElementById("modal-ai-provider").value;
      const apiKey = document.getElementById("modal-ai-key").value.trim();
      const model = document.getElementById("modal-ai-model").value.trim();

      if (!apiKey) {
        showToast("Iltimos, API kalitini kiriting.", "error");
        return;
      }

      let baseUrl = "https://api.openai.com/v1";
      if (provider === "groq") baseUrl = "https://api.groq.com/openai/v1";
      else if (provider === "openrouter") baseUrl = "https://openrouter.ai/api/v1";
      else if (provider === "ollama") baseUrl = "http://localhost:11434";

      try {
        const res = await apiFetch("/api/admin/ai-config", {
          method: "POST",
          body: JSON.stringify({
            provider,
            api_key: apiKey,
            model: model || (provider === "groq" ? "llama-3.3-70b-versatile" : "gpt-4o-mini"),
            base_url: baseUrl
          })
        });
        const data = await res.json();
        if (res.ok) {
          showToast(data.message || "API kalit muvaffaqiyatli ulandi!", "success");
          closeModal();
        } else {
          showToast(data.detail || "Kalitni saqlab bo'lmadi.", "error");
        }
      } catch (err) {
        showToast("Xatolik yuz berdi.", "error");
      }
    });
  }
});
