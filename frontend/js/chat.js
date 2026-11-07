/**
 * CYBERAI Chat Engine
 * Handles real-time streaming, conversation history, Markdown formatting,
 * code syntax highlighting, copy mechanisms, and generation aborts.
 */

let activeConversationId = null;
let currentAbortController = null;
let isStreaming = false;
let lastUserMessageText = "";

document.addEventListener("DOMContentLoaded", () => {
  // Check if we are on the chat page (index.html)
  const chatMessages = document.getElementById("chat-messages");
  if (!chatMessages) return;

  initChat();
});

function initChat() {
  loadConversationsList();

  const sendBtn = document.getElementById("send-btn");
  const stopBtn = document.getElementById("stop-btn");
  const chatInput = document.getElementById("chat-input");
  const newChatBtn = document.getElementById("new-chat-btn");
  const modelSelect = document.getElementById("model-selector");

  // Sync model selector with settings
  if (modelSelect && window.CYBERAI && window.CYBERAI.settings) {
    if (CYBERAI.settings.model) {
      modelSelect.value = CYBERAI.settings.model;
    }
    modelSelect.addEventListener("change", (e) => {
      CYBERAI.settings.model = e.target.value;
      localStorage.setItem("cyberai_settings", JSON.stringify(CYBERAI.settings));
    });
  }

  if (sendBtn) {
    sendBtn.addEventListener("click", handleSendMessage);
  }

  if (stopBtn) {
    stopBtn.addEventListener("click", handleStopStreaming);
  }

  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      startNewChat();
    });
  }

  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      const sendOnEnter = window.CYBERAI && window.CYBERAI.settings ? (CYBERAI.settings.sendOnEnter !== false) : true;
      if (sendOnEnter && e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    });

    // Auto-grow textarea
    chatInput.addEventListener("input", function() {
      this.style.height = "auto";
      this.style.height = Math.min(this.scrollHeight, 180) + "px";
    });
  }
}

/**
 * Load Conversation History for the Sidebar
 */
async function loadConversationsList() {
  const container = document.getElementById("chat-history-list");
  if (!container) return;

  try {
    const res = await apiFetch("/api/conversations");
    if (!res.ok) return;

    const list = await res.json();
    container.innerHTML = "";

    if (list.length === 0) {
      container.innerHTML = `<div style="padding: 0.75rem; font-size: 0.8rem; color: var(--text-muted);">Suhbatlar tarixi bo'sh</div>`;
      return;
    }

    list.forEach((conv) => {
      const item = document.createElement("div");
      item.className = `chat-history-item ${conv.id === activeConversationId ? "active" : ""}`;
      item.dataset.id = conv.id;

      item.innerHTML = `
        <span title="${escapeHTML(conv.title)}">${escapeHTML(conv.title)}</span>
        <div class="history-actions">
          <button class="history-btn edit-title-btn" title="Nomini o'zgartirish">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
          </button>
          <button class="history-btn delete-conv-btn" title="O'chirish">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      `;

      item.addEventListener("click", (e) => {
        if (e.target.closest(".history-actions")) return;
        selectConversation(conv.id);
      });

      const editBtn = item.querySelector(".edit-title-btn");
      editBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        renameConversation(conv.id, conv.title);
      });

      const delBtn = item.querySelector(".delete-conv-btn");
      delBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteConversation(conv.id);
      });

      container.appendChild(item);
    });
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

/**
 * Switch Active Conversation
 */
async function selectConversation(id) {
  if (isStreaming) {
    showToast("Javob yaratilmoqda, avval to'xtating.", "info");
    return;
  }

  activeConversationId = id;
  updateActiveSidebarItem(id);

  const chatMessages = document.getElementById("chat-messages");
  chatMessages.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Suhbat yuklanmoqda...</div>`;

  try {
    const res = await apiFetch(`/api/conversations/${id}`);
    if (!res.ok) {
      showToast("Suhbatni yuklab bo'lmadi.", "error");
      return;
    }

    const data = await res.json();
    chatMessages.innerHTML = "";

    if (data.messages && data.messages.length > 0) {
      data.messages.forEach((msg) => {
        appendMessageBubble(msg.role, msg.content);
      });
      // Store last user message for regenerate functionality
      const lastUser = [...data.messages].reverse().find(m => m.role === "user");
      if (lastUser) lastUserMessageText = lastUser.content;
    } else {
      renderWelcomeScreen();
    }

    scrollToBottom();
  } catch (err) {
    console.error("Error loading conversation:", err);
  }
}

/**
 * Start New Chat
 */
function startNewChat() {
  if (isStreaming) {
    handleStopStreaming();
  }
  activeConversationId = null;
  updateActiveSidebarItem(null);
  renderWelcomeScreen();
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = "";
    input.focus();
  }
}

/**
 * Rename Conversation
 */
async function renameConversation(id, currentTitle) {
  const newTitle = prompt("Suhbat uchun yangi nom kiriting:", currentTitle);
  if (!newTitle || newTitle.trim() === "" || newTitle === currentTitle) return;

  try {
    const res = await apiFetch(`/api/conversations/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ title: newTitle.trim() })
    });
    if (res.ok) {
      showToast("Suhbat nomi yangilandi.", "success");
      loadConversationsList();
    }
  } catch (err) {
    showToast("Nomni o'zgartirib bo'lmadi.", "error");
  }
}

/**
 * Delete Conversation
 */
async function deleteConversation(id) {
  const confirmMsg = CYBERAI.translations[CYBERAI.lang]?.delete_chat_confirm || "Haqiqatan ham bu suhbatni o'chirmoqchimisiz?";
  if (!confirm(confirmMsg)) return;

  try {
    const res = await apiFetch(`/api/conversations/${id}`, {
      method: "DELETE"
    });
    if (res.ok) {
      showToast("Suhbat o'chirildi.", "info");
      if (activeConversationId === id) {
        startNewChat();
      }
      loadConversationsList();
    }
  } catch (err) {
    showToast("Suhbatni o'chirishda xatolik yuz berdi.", "error");
  }
}

function updateActiveSidebarItem(id) {
  document.querySelectorAll(".chat-history-item").forEach(item => {
    item.classList.toggle("active", item.dataset.id === id);
  });
}

/**
 * Send Message & Handle Streaming SSE
 */
async function handleSendMessage() {
  const input = document.getElementById("chat-input");
  const text = input ? input.value.trim() : "";

  if (!text || isStreaming) return;

  lastUserMessageText = text;
  input.value = "";
  input.style.height = "56px";

  // Hide welcome placeholder if present
  const welcome = document.getElementById("welcome-placeholder");
  if (welcome) welcome.remove();

  // Render User Message
  appendMessageBubble("user", text);
  scrollToBottom();

  // Prepare Assistant Placeholder Bubble with Streaming Cursor
  const assistantBubble = appendMessageBubble("assistant", "");
  const markdownContainer = assistantBubble.querySelector(".markdown-body");
  const cursor = document.createElement("span");
  cursor.className = "streaming-cursor";
  markdownContainer.appendChild(cursor);

  setStreamingState(true);

  // Read Settings, Model, and Language
  const modelSelect = document.getElementById("model-selector");
  const selectedModel = modelSelect ? modelSelect.value : (CYBERAI.settings?.model || "gpt-4o-mini");
  const s = CYBERAI.settings || {};

  currentAbortController = new AbortController();

  let accumulatedContent = "";

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${CYBERAI.token}`
      },
      body: JSON.stringify({
        message: text,
        conversation_id: activeConversationId,
        model: s.model || selectedModel,
        language: CYBERAI.lang,
        provider: s.provider || "cyberai",
        api_key: s.apiKey || undefined,
        base_url: s.baseUrl || undefined,
        temperature: s.temperature !== undefined ? parseFloat(s.temperature) : 0.7,
        system_prompt: s.systemPrompt || undefined,
        max_tokens: s.maxTokens ? parseInt(s.maxTokens) : 4096,
        history_limit: s.historyLimit ? parseInt(s.historyLimit) : 10
      }),
      signal: currentAbortController.signal
    });

    if (!response.ok) {
      cursor.remove();
      const errData = await response.json().catch(() => ({}));
      const errMsg = errData.detail || "Server bilan bog'lanishda xato yuz berdi.";
      markdownContainer.innerHTML = `<span style="color: var(--severity-critical);">${escapeHTML(errMsg)}</span>`;
      setStreamingState(false);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep remainder

      for (const block of lines) {
        if (!block.startsWith("data: ")) continue;
        const jsonStr = block.replace(/^data: /, "").trim();
        if (!jsonStr) continue;

        try {
          const payload = JSON.parse(jsonStr);

          if (payload.conversation_id && !activeConversationId) {
            activeConversationId = payload.conversation_id;
            loadConversationsList();
          }

          if (payload.chunk) {
            accumulatedContent += payload.chunk;
            markdownContainer.innerHTML = renderMarkdown(accumulatedContent);
            markdownContainer.appendChild(cursor);
            scrollToBottom();
          }

          if (payload.done) {
            cursor.remove();
            if (typeof playCyberChime === "function") {
              playCyberChime();
            }
            break;
          }
        } catch (e) {
          // ignore chunk parse errors
        }
      }
    }

  } catch (err) {
    if (err.name === "AbortError") {
      console.log("Streaming cancelled by user.");
    } else {
      markdownContainer.innerHTML += `<br/><span style="color: var(--severity-critical);">[Ulanish uzildi: ${escapeHTML(err.message)}]</span>`;
    }
  } finally {
    cursor.remove();
    // Attach code copy buttons and message action toolbar
    attachCodeBlockHandlers(assistantBubble);
    attachMessageActions(assistantBubble, accumulatedContent);
    setStreamingState(false);
    scrollToBottom();
  }
}

/**
 * Stop Streaming Generation
 */
function handleStopStreaming() {
  if (currentAbortController) {
    currentAbortController.abort();
    currentAbortController = null;
  }
  setStreamingState(false);
  showToast("Javob yaratish to'xtatildi.", "info");
}

function setStreamingState(streaming) {
  isStreaming = streaming;
  const sendBtn = document.getElementById("send-btn");
  const stopBtn = document.getElementById("stop-btn");

  if (sendBtn && stopBtn) {
    if (streaming) {
      sendBtn.style.display = "none";
      stopBtn.style.display = "inline-flex";
    } else {
      sendBtn.style.display = "inline-flex";
      stopBtn.style.display = "none";
    }
  }
}

/**
 * Append Message Bubble to DOM
 */
function appendMessageBubble(role, content) {
  const container = document.getElementById("chat-messages");
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatarContent = role === "assistant" 
    ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`
    : (CYBERAI.user ? CYBERAI.user.username.charAt(0).toUpperCase() : "U");

  row.innerHTML = `
    <div class="message-avatar">${avatarContent}</div>
    <div class="message-bubble">
      <div class="markdown-body">${renderMarkdown(content)}</div>
    </div>
  `;

  container.appendChild(row);

  if (role === "assistant" && content) {
    attachCodeBlockHandlers(row);
    attachMessageActions(row, content);
  }

  return row;
}

/**
 * Message Action Bar (Copy message, Regenerate)
 */
function attachMessageActions(bubbleRow, textContent) {
  const bubble = bubbleRow.querySelector(".message-bubble");
  if (!bubble || bubble.querySelector(".message-actions")) return;

  const actions = document.createElement("div");
  actions.className = "message-actions";

  actions.innerHTML = `
    <button class="action-icon-btn copy-msg-btn" title="Javobni nusxalash">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
      <span>Nusxalash</span>
    </button>
    <button class="action-icon-btn speak-msg-btn" title="Ovozli o'qish">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
      <span>Ovoz</span>
    </button>
    <button class="action-icon-btn regen-btn" title="Qayta yaratish">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
      <span>Qayta</span>
    </button>
  `;

  const copyBtn = actions.querySelector(".copy-msg-btn");
  copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(textContent).then(() => {
      copyBtn.querySelector("span").textContent = "Nusxalandi!";
      setTimeout(() => copyBtn.querySelector("span").textContent = "Nusxalash", 2000);
    });
  });

  const speakBtn = actions.querySelector(".speak-msg-btn");
  speakBtn.addEventListener("click", () => {
    if (!('speechSynthesis' in window)) {
      showToast("Brauzeringiz ovoz sintezini qo'llab-quvvatlamaydi.", "info");
      return;
    }
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      speakBtn.querySelector("span").textContent = "Ovoz";
      return;
    }
    // Clean markdown symbols for cleaner speech
    const cleanSpeechText = textContent.replace(/[*#`_~\[\]]/g, '').replace(/```[\s\S]*?```/g, 'Kod namunasi.');
    const utterance = new SpeechSynthesisUtterance(cleanSpeechText.slice(0, 1000));
    utterance.lang = CYBERAI.lang === "ru" ? "ru-RU" : (CYBERAI.lang === "en" ? "en-US" : "uz-UZ");
    utterance.rate = 1.0;
    utterance.onend = () => { speakBtn.querySelector("span").textContent = "Ovoz"; };
    utterance.onerror = () => { speakBtn.querySelector("span").textContent = "Ovoz"; };
    speakBtn.querySelector("span").textContent = "To'xtatish";
    window.speechSynthesis.speak(utterance);
  });

  const regenBtn = actions.querySelector(".regen-btn");
  regenBtn.addEventListener("click", () => {
    if (lastUserMessageText) {
      const input = document.getElementById("chat-input");
      if (input) input.value = lastUserMessageText;
      handleSendMessage();
    }
  });

  bubble.appendChild(actions);
}

/**
 * Attach Copy Handlers to Code Blocks
 */
function attachCodeBlockHandlers(container) {
  container.querySelectorAll(".copy-code-btn").forEach((btn) => {
    btn.onclick = function() {
      const pre = this.closest(".code-block-container").querySelector("pre code");
      if (!pre) return;
      navigator.clipboard.writeText(pre.innerText).then(() => {
        const originalText = this.innerHTML;
        this.innerHTML = `✓ Nusxalandi!`;
        this.style.color = "var(--accent-primary)";
        setTimeout(() => {
          this.innerHTML = originalText;
          this.style.color = "";
        }, 2000);
      });
    };
  });
}

/**
 * Lightweight, Safe Markdown Parser
 */
function renderMarkdown(md) {
  if (!md) return "";

  let html = md;

  // 1. Fenced Code Blocks: ```lang ... ```
  html = html.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang.trim() || "code";
    return `
      <div class="code-block-container">
        <div class="code-header">
          <span>${escapeHTML(language)}</span>
          <button class="copy-btn copy-code-btn">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            Nusxalash
          </button>
        </div>
        <pre><code class="language-${escapeHTML(language)}">${escapeHTML(code.trim())}</code></pre>
      </div>
    `;
  });

  // 2. Inline Code `code`
  html = html.replace(/`([^`]+)`/g, (match, inline) => {
    return `<code>${escapeHTML(inline)}</code>`;
  });

  // 3. Blockquotes > quote
  html = html.replace(/^>\s?(.*)$/gm, (match, quote) => {
    return `<blockquote>${quote}</blockquote>`;
  });

  // 4. Headers: ### H3, ## H2, # H1
  html = html.replace(/^### (.*$)/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.*$)/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.*$)/gm, "<h1>$1</h1>");

  // 5. Bold & Italic
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");

  // 6. Unordered Lists
  html = html.replace(/^\s*[-*]\s+(.*)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");

  // 7. Paragraph line breaks
  html = html.replace(/\n\n+/g, "</p><p>");
  html = html.replace(/\n/g, "<br/>");

  return `<p>${html}</p>`;
}

function scrollToBottom() {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function renderWelcomeScreen() {
  const chatMessages = document.getElementById("chat-messages");
  if (!chatMessages) return;

  chatMessages.innerHTML = `
    <div id="welcome-placeholder" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; gap: 1.5rem; padding: 2.5rem 1rem;">
      <div style="width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, rgba(0, 245, 212, 0.2), rgba(139, 92, 246, 0.25)); display: flex; align-items: center; justify-content: center; border: 1px solid rgba(0, 245, 212, 0.45); box-shadow: 0 0 25px rgba(0, 245, 212, 0.3);">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00F5D4" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      </div>
      <div>
        <h2 style="font-size: 1.75rem; margin-bottom: 0.5rem; background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">CYBERAI Super Sun'iy Intellekt</h2>
        <p style="color: var(--text-secondary); max-width: 580px; font-size: 0.98rem; line-height: 1.6;">
          Dasturlash (Python, Bot, JS), matematika, fan, umumiy bilimlar va jahon standartidagi kiberxavfsizlik himoyasini birlashtirgan universal AI yordamchi.
        </p>
      </div>
      <div style="display: flex; flex-wrap: wrap; gap: 0.85rem; justify-content: center; max-width: 760px;">
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('Python da qanday qilib Telegram bot yaratish mumkin?')">
          🤖 Python Telegram Bot (aiogram)
        </button>
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('SQL Injection nima va undan qanday himoyalanamiz?')">
          🛡️ SQL Injection & OWASP
        </button>
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('FastAPI da xavfsiz JWT autentifikatsiyani sozlash')">
          🔑 Xavfsiz JWT & FastAPI
        </button>
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('25 * 4 + 150 ning yechimi va tushuntirishi')">
          🧮 Matematik Hisoblash
        </button>
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('Kvant fizikasi nima va kvant kompyuterlar qanday ishlaydi?')">
          🌌 Kvant Fizikasi & Fan
        </button>
        <button class="btn btn-secondary prompt-chip" onclick="quickPrompt('Dasturchilar va himoyachilar haqida ilhomlantiruvchi she\'r yoz')">
          ✍️ Ijodiy She'r & Matn
        </button>
      </div>
    </div>
  `;
}

window.quickPrompt = function(text) {
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = text;
    handleSendMessage();
  }
};
