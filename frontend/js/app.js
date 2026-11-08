/**
 * CYBERAI — Global Application Framework
 * Handles authentication lifecycle, multilingual dictionary, notifications, and UI shell.
 */

// Default AI Settings
const DEFAULT_AI_SETTINGS = {
  provider: "gemini",
  model: "gemini-3.5-flash",
  apiKey: "",
  baseUrl: "",
  persona: "senior_architect",
  systemPrompt: "Siz yuqori malakali Senior Kiberxavfsizlik Arxitektori (Defensive Security Architect) va xavfsiz dasturiy ta'minot muhandisisiz. OWASP Top 10, FastAPI/Python xavfsiz arxitekturasi va korporativ mudofaa bo'yicha professional maslahat bering.",
  temperature: 0.7,
  maxTokens: 4096,
  historyLimit: 10,
  soundEnabled: true,
  sendOnEnter: true
};

let loadedSettings = null;
try {
  loadedSettings = JSON.parse(localStorage.getItem("cyberai_settings"));
  if (loadedSettings && ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash-lite"].includes(loadedSettings.model)) {
    loadedSettings.model = "gemini-3.5-flash";
    localStorage.setItem("cyberai_settings", JSON.stringify(loadedSettings));
  }
} catch (e) {}

// Global State
window.CYBERAI = {
  token: localStorage.getItem("cyberai_token") || null,
  user: null,
  lang: localStorage.getItem("cyberai_lang") || "uz",
  settings: Object.assign({}, DEFAULT_AI_SETTINGS, loadedSettings || {}),
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
      input_placeholder: "Har qanday savol, dasturlash (Python, Telegram bot), matematika yoki xavfsizlik bo'yicha yozing...",
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
      input_placeholder: "Ask anything about coding (Python, Bots, JS), math, science, or cybersecurity...",
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
      input_placeholder: "Задайте любой вопрос: программирование (Python, боты), математика, наука или безопасность...",
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
  setupSettingsModal();
});

/**
 * Cyber Chime Synthesizer via Web Audio API
 */
window.playCyberChime = function() {
  if (!CYBERAI.settings || CYBERAI.settings.soundEnabled === false) return;
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
    osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.08); // G5
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.22);
  } catch (e) {}
};

/**
 * Real AI Settings Modal Controller
 */
function setupSettingsModal() {
  const modal = document.getElementById("settings-modal");
  if (!modal) return;

  const openBtns = [
    document.getElementById("open-settings-modal-btn"),
    document.getElementById("sidebar-settings-btn")
  ].filter(Boolean);

  const closeBtn = document.getElementById("close-settings-modal-btn");
  const cancelBtn = document.getElementById("cancel-settings-btn");
  const saveBtn = document.getElementById("save-settings-btn");
  const resetBtn = document.getElementById("reset-settings-btn");
  const toggleKeyBtn = document.getElementById("toggle-key-visibility-btn");

  const providerSelect = document.getElementById("setting-provider");
  const modelInput = document.getElementById("setting-model");
  const apiKeyInput = document.getElementById("setting-api-key");
  const baseUrlInput = document.getElementById("setting-base-url");
  const systemPromptInput = document.getElementById("setting-system-prompt");
  const tempInput = document.getElementById("setting-temperature");
  const tempDisplay = document.getElementById("temp-val-display");
  const maxTokensSelect = document.getElementById("setting-max-tokens");
  const historyInput = document.getElementById("setting-history-limit");
  const historyDisplay = document.getElementById("history-val-display");
  const soundCheck = document.getElementById("setting-sound-enabled");
  const enterCheck = document.getElementById("setting-send-on-enter");

  const PERSONA_PROMPTS = {
    senior_architect: "Siz yuqori malakali Senior Kiberxavfsizlik Arxitektori (Defensive Security Architect) va xavfsiz dasturiy ta'minot muhandisisiz. OWASP Top 10, FastAPI/Python xavfsiz arxitekturasi va korporativ mudofaa bo'yicha professional maslahat bering.",
    ethical_hacker: "Siz sertifikatlangan Ethical Hacker va Penetration Tester (Offensive / Red Team) mutaxassisisiz. Zaifliklarni topish, ularni laboratoriya muhitida xavfsiz tekshirish va tizimni buzilmas qilib mustahkamlash usullarini o'rgatasiz.",
    code_auditor: "Siz qat'iy Kod Xavfsizligi Auditori va Static Code Analysis mutaxassisisiz. Kodlardagi har qanday SQLi, XSS, SSRF, RCE va ochiq kalitlarni aniqlab, qat'iy xavfsiz, tuzatilgan to'liq kod namunalarini taqdim etasiz.",
    beginner_tutor: "Siz kiberxavfsizlik va dasturlashni yangi boshlaganlar uchun sabrli va professional o'qituvchisiz. Barcha tushunchalarni sodda, qiziqarli hayotiy o'xshatishlar va qadamma-qadam ko'rsatmalar bilan tushuntirasiz."
  };

  function syncFormWithSettings() {
    const s = CYBERAI.settings;
    if (providerSelect) providerSelect.value = s.provider || "gemini";
    if (modelInput) modelInput.value = s.model || "gemini-3.5-flash";
    if (apiKeyInput) apiKeyInput.value = s.apiKey || "";
    if (baseUrlInput) baseUrlInput.value = s.baseUrl || "";
    if (systemPromptInput) systemPromptInput.value = s.systemPrompt || PERSONA_PROMPTS[s.persona] || "";
    if (tempInput) {
      tempInput.value = s.temperature !== undefined ? s.temperature : 0.7;
      if (tempDisplay) tempDisplay.textContent = tempInput.value;
    }
    if (maxTokensSelect) maxTokensSelect.value = s.maxTokens || "4096";
    if (historyInput) {
      historyInput.value = s.historyLimit || 10;
      if (historyDisplay) historyDisplay.textContent = historyInput.value + " ta xabar";
    }
    if (soundCheck) soundCheck.checked = s.soundEnabled !== false;
    if (enterCheck) enterCheck.checked = s.sendOnEnter !== false;

    // Highlight active persona preset
    document.querySelectorAll(".persona-preset-card").forEach(card => {
      card.classList.toggle("active", card.dataset.preset === s.persona);
    });
  }

  function openModal() {
    syncFormWithSettings();
    modal.classList.add("active");
  }

  function closeModal() {
    modal.classList.remove("active");
  }

  openBtns.forEach(b => b.addEventListener("click", openModal));
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  // Close modal when clicking outside
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  // Tab switching
  document.querySelectorAll(".settings-tab-btn").forEach(tabBtn => {
    tabBtn.addEventListener("click", () => {
      document.querySelectorAll(".settings-tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".settings-tab-pane").forEach(p => p.classList.remove("active"));
      tabBtn.classList.add("active");
      const targetPane = document.getElementById(tabBtn.dataset.tab);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Persona Presets
  document.querySelectorAll(".persona-preset-card").forEach(card => {
    card.addEventListener("click", () => {
      document.querySelectorAll(".persona-preset-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      const preset = card.dataset.preset;
      CYBERAI.settings.persona = preset;
      if (PERSONA_PROMPTS[preset] && systemPromptInput) {
        systemPromptInput.value = PERSONA_PROMPTS[preset];
      }
    });
  });

  // Slider inputs
  if (tempInput && tempDisplay) {
    tempInput.addEventListener("input", () => {
      tempDisplay.textContent = tempInput.value;
    });
  }

  if (historyInput && historyDisplay) {
    historyInput.addEventListener("input", () => {
      historyDisplay.textContent = historyInput.value + " ta xabar";
    });
  }

  // Toggle API Key visibility
  if (toggleKeyBtn && apiKeyInput) {
    toggleKeyBtn.addEventListener("click", () => {
      if (apiKeyInput.type === "password") {
        apiKeyInput.type = "text";
        toggleKeyBtn.textContent = "Yashirish";
      } else {
        apiKeyInput.type = "password";
        toggleKeyBtn.textContent = "Ko'rsatish";
      }
    });
  }

  // Provider changes: set smart defaults
  if (providerSelect && modelInput) {
    providerSelect.addEventListener("change", () => {
      const p = providerSelect.value;
      if (p === "gemini") {
        modelInput.value = "gemini-3.5-flash";
        if (baseUrlInput) baseUrlInput.placeholder = "Google Generative Language API";
      } else if (p === "deepseek") {
        modelInput.value = "deepseek-chat";
        if (baseUrlInput) baseUrlInput.placeholder = "https://api.deepseek.com/v1";
      } else if (p === "groq") {
        modelInput.value = "llama-3.3-70b-versatile";
        if (baseUrlInput) baseUrlInput.placeholder = "https://api.groq.com/openai/v1";
      } else if (p === "openai") {
        modelInput.value = "gpt-4o-mini";
        if (baseUrlInput) baseUrlInput.placeholder = "https://api.openai.com/v1";
      } else if (p === "ollama") {
        modelInput.value = "llama3";
        if (baseUrlInput) baseUrlInput.placeholder = "http://localhost:11434";
      } else if (p === "cyberai") {
        modelInput.value = "gemini-3.5-flash";
      }
    });
  }

  // Save Settings
  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      CYBERAI.settings = {
        provider: providerSelect ? providerSelect.value : "cyberai",
        model: modelInput ? modelInput.value.trim() || "gpt-4o-mini" : "gpt-4o-mini",
        apiKey: apiKeyInput ? apiKeyInput.value.trim() : "",
        baseUrl: baseUrlInput ? baseUrlInput.value.trim() : "",
        persona: CYBERAI.settings.persona || "senior_architect",
        systemPrompt: systemPromptInput ? systemPromptInput.value.trim() : "",
        temperature: tempInput ? parseFloat(tempInput.value) : 0.7,
        maxTokens: maxTokensSelect ? parseInt(maxTokensSelect.value) : 4096,
        historyLimit: historyInput ? parseInt(historyInput.value) : 10,
        soundEnabled: soundCheck ? soundCheck.checked : true,
        sendOnEnter: enterCheck ? enterCheck.checked : true
      };

      localStorage.setItem("cyberai_settings", JSON.stringify(CYBERAI.settings));

      // Update topbar model dropdown if present
      const topModelSelector = document.getElementById("model-selector");
      if (topModelSelector) {
        let optExists = Array.from(topModelSelector.options).some(o => o.value === CYBERAI.settings.model);
        if (!optExists) {
          const newOpt = document.createElement("option");
          newOpt.value = CYBERAI.settings.model;
          newOpt.textContent = CYBERAI.settings.model;
          topModelSelector.appendChild(newOpt);
        }
        topModelSelector.value = CYBERAI.settings.model;
      }

      showToast("AI Sozlamalari muvaffaqiyatli saqlandi va faollashtirildi!", "success");
      playCyberChime();
      closeModal();
    });
  }

  // Reset to default
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      CYBERAI.settings = Object.assign({}, DEFAULT_AI_SETTINGS);
      localStorage.setItem("cyberai_settings", JSON.stringify(CYBERAI.settings));
      syncFormWithSettings();
      showToast("Barcha sozlamalar standart holatga qaytarildi.", "info");
    });
  }

  // Clear all chats
  const clearChatsBtn = document.getElementById("clear-all-chats-btn");
  if (clearChatsBtn) {
    clearChatsBtn.addEventListener("click", async () => {
      if (!confirm("Barcha suhbatlar tarixini butunlay o'chirib tashlamoqchimisiz?")) return;
      try {
        const res = await apiFetch("/api/conversations");
        if (res.ok) {
          const list = await res.json();
          for (const conv of list) {
            await apiFetch(`/api/conversations/${conv.id}`, { method: "DELETE" });
          }
          showToast("Barcha suhbatlar o'chirildi.", "success");
          closeModal();
          if (typeof startNewChat === "function") startNewChat();
        }
      } catch (e) {
        showToast("Xatolik yuz berdi.", "error");
      }
    });
  }

  // Export all chats
  const exportChatsBtn = document.getElementById("export-all-chats-btn");
  if (exportChatsBtn) {
    exportChatsBtn.addEventListener("click", async () => {
      try {
        const res = await apiFetch("/api/conversations");
        if (res.ok) {
          const list = await res.json();
          const exportData = [];
          for (const conv of list) {
            const detailRes = await apiFetch(`/api/conversations/${conv.id}`);
            if (detailRes.ok) {
              exportData.push(await detailRes.json());
            }
          }
          const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `cyberai-conversations-${new Date().toISOString().slice(0, 10)}.json`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          showToast("Suhbatlar arxivi yuklab olindi!", "success");
        }
      } catch (e) {
        showToast("Eksport qilishda xato yuz berdi.", "error");
      }
    });
  }
}
