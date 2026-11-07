"""
CYBERAI AI Provider Service
Handles OpenAI-compatible APIs, local Ollama endpoints, and high-fidelity Demo Mode.
Supports streaming responses, multilingual prompting, and defensive cybersecurity guardrails.
"""
import json
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
from backend.config import settings

# Cybersecurity System Prompts for each supported language
SYSTEM_PROMPTS = {
    "uz": (
        "Siz CYBERAI — professional, mas'uliyatli va yuqori malakali axborot xavfsizligi hamda "
        "dasturiy ta'minot himoyasi bo'yicha sun'iy intellekt yordamchisisiz.\n\n"
        "VAZIFALARINGIZ:\n"
        "- Axborot xavfsizligi, xavfsiz dasturlash va kiberxavfsizlik tushunchalarini tushuntirish.\n"
        "- OWASP Top 10 zaifliklari (SQL Injection, XSS, CSRF, SSRF, IDOR va boshqalar) hamda ularni bartaraf etishni o'rgatish.\n"
        "- Python va FastAPI xavfsiz arxitekturasi bo'yicha maslahat berish.\n"
        "- Manba kodlaridagi zaifliklarni aniqlash va tuzatilgan xavfsiz kod namunalarini berish.\n"
        "- Kali Linux va himoyalanish laboratoriya vositalarining ishlash mexanizmlarini tushuntirish.\n\n"
        "XAVFSIZLIK VA ETIKA CHEKLOVLARI:\n"
        "- Siz HECH QACHON zararli dasturlar (malware), parollarni o'g'irlash (credential theft), "
        "fishing (phishing), DDoS hujumlari yoki ruxsatsiz buzg'unchilik ssenariylarini yaratmaysiz.\n"
        "- Har qanday xavfsizlik amaliyotlari faqat maxsus ruxsat berilgan laboratoriya muhitlari "
        "yoki o'z tizimlari doirasida bo'lishini doimo eslatasiz.\n"
        "- Javoblaringizni aniq, professional, o'qilishi oson Markdown formatida, chiroyli kod bloklari va "
        "amaliy xavfsizlik tavsiyalari bilan taqdim eting."
    ),
    "en": (
        "You are CYBERAI — a professional, highly skilled AI cybersecurity assistant specializing in "
        "defensive security, secure software engineering, and authorized education.\n\n"
        "RESPONSIBILITIES:\n"
        "- Educate on defensive cybersecurity concepts, OWASP Top 10, and secure coding practices.\n"
        "- Review code for security flaws (SQLi, XSS, SSRF, hardcoded secrets, insecure deserialization).\n"
        "- Provide remediated secure code and hardened architecture guidelines for Python, FastAPI, and modern web apps.\n"
        "- Explain defensive analysis, security logging, and authorized ethical testing tools.\n\n"
        "SAFETY & ETHICAL MANDATES:\n"
        "- Never create, provide, or assist with malicious payloads, DDoS scripts, credential harvesting, phishing, ransomware, or unauthorized exploitation.\n"
        "- Focus strictly on defense, hardening, prevention, and authorized education.\n"
        "- Use clean, professional Markdown with syntax-highlighted code blocks."
    ),
    "ru": (
        "Вы — CYBERAI, профессиональный ИИ-ассистент по информационной безопасности, "
        "защищенной разработке ПО и авторизованному обучению кибербезопасности.\n\n"
        "ОБЯЗАННОСТИ:\n"
        "- Объяснять концепции информационной безопасности, уязвимости OWASP Top 10 и методы защиты.\n"
        "- Проводить аудит исходного кода и предоставлять безопасные примеры исправления.\n"
        "- Консультировать по безопасной архитектуре Python/FastAPI, криптографии и управлению доступами.\n"
        "- Разъяснять работу защитных инструментов и анализ журналов безопасности.\n\n"
        "ЭТИЧЕСКИЕ И ЗАЩИТНЫЕ ОГРАНИЧЕНИЯ:\n"
        "- Категорически запрещено создавать вредоносное ПО, фишинговые страницы, эксплойты для несанкционированного доступа, скрипты DDoS или кражи учетных данных.\n"
        "- Строго ориентируйтесь на защиту, аудит, безопасную разработку и авторизованные лаборатории."
    )
}

# DEMO KNOWLEDGE BASE RESPONSES FOR OFFLINE / UNCONFIGURED API KEY MODE
DEMO_TOPICS = {
    "sql_injection": {
        "keywords": ["sql", "injection", "sqli", "injeksiya", "veritabani"],
        "uz": (
            "### SQL Inyeksiya (SQL Injection) va Undan Himoyalanish\n\n"
            "**SQL Inyeksiya** — tajovuzkor foydalanuvchi kiritgan ma'lumotlar orqali ma'lumotlar bazasi so'rovini manipulyatsiya qilish imkonini beruvchi zaiflikdir (OWASP Top 10: A03:2021-Injection).\n\n"
            "#### ❌ Xavfli Kod Namunasi (Zaif):\n"
            "```python\n"
            "# Xavfli: String birlashtirish (string concatenation) orqali so'rov tuzish\n"
            "cursor.execute(f\"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'\")\n"
            "```\n"
            "Tajovuzkor `username` maydoniga `' OR '1'='1` kiritishi bilan tizimga parolsiz kirib olishi mumkin.\n\n"
            "#### ✅ Xavfsiz Kod Namunasi (Parametrlangan so'rov):\n"
            "```python\n"
            "# Xavfsiz: Parametrlangan SQL so'rovidan foydalanish\n"
            "cursor.execute(\n"
            "    \"SELECT id, username, password_hash FROM users WHERE username = %s\",\n"
            "    (username,)\n"
            ")\n"
            "```\n\n"
            "#### Himoyalanish qoidalari:\n"
            "1. Hech qachon foydalanuvchi ma'lumotlarini SQL so'roviga matn sifatida qo'shmang.\n"
            "2. SQLAlchemy yoki boshqa zamonaviy ORM lardan foydalaning.\n"
            "3. Ma'lumotlar bazasi foydalanuvchisiga faqat kerakli minimal huquqlarni bering (Principle of Least Privilege)."
        ),
        "en": (
            "### SQL Injection Prevention Guide\n\n"
            "**SQL Injection (SQLi)** occurs when untrusted user input is directly concatenated into dynamic SQL queries.\n\n"
            "#### ❌ Insecure Pattern:\n"
            "```python\n"
            "cursor.execute(f\"SELECT * FROM accounts WHERE user_id = '{user_id}'\")\n"
            "```\n\n"
            "#### ✅ Secure Pattern (Parameterized Queries):\n"
            "```python\n"
            "cursor.execute(\"SELECT * FROM accounts WHERE user_id = %s\", (user_id,))\n"
            "```\n\n"
            "Use modern ORMs (SQLAlchemy, Tortoise) and follow the principle of least privilege."
        ),
        "ru": (
            "### Защита от SQL-инъекций (SQL Injection)\n\n"
            "**SQL-инъекция** — внедрение вредоносных SQL-команд через пользовательский ввод.\n\n"
            "#### ❌ Опасный код:\n"
            "```python\n"
            "cursor.execute(f\"SELECT * FROM users WHERE email = '{email}'\")\n"
            "```\n\n"
            "#### ✅ Безопасный код (Параметризация):\n"
            "```python\n"
            "cursor.execute(\"SELECT * FROM users WHERE email = %s\", (email,))\n"
            "```"
        )
    },
    "xss": {
        "keywords": ["xss", "cross-site", "scripting", "skript", "innerhtml"],
        "uz": (
            "### XSS (Cross-Site Scripting) va Oldini Olish Choralari\n\n"
            "**XSS** — bu foydalanuvchi brauzerida tajovuzkorning zararli JavaScript kodini ishga tushirish imkonini beruvchi zaiflikdir.\n\n"
            "#### Turlari:\n"
            "1. **Stored XSS** (Doimiy) — zararli skript ma'lumotlar bazasida saqlanadi.\n"
            "2. **Reflected XSS** (Aks ettirilgan) — URL parametrlari orqali sahifada qaytariladi.\n"
            "3. **DOM-based XSS** — mijoz tomonidagi JS xavfli funksiyalar (`innerHTML`, `document.write`) orqali ishlatilganda yuzaga keladi.\n\n"
            "#### ❌ Xavfli JavaScript:\n"
            "```javascript\n"
            "// Xavfli: Sanitizatsiyasiz kiritish\n"
            "document.getElementById('user-profile').innerHTML = userInput;\n"
            "```\n\n"
            "#### ✅ Xavfsiz JavaScript:\n"
            "```javascript\n"
            "// Xavfsiz: textContent foydalanish\n"
            "document.getElementById('user-profile').textContent = userInput;\n"
            "```\n\n"
            "#### Himoyalanish vositalari:\n"
            "- `Content-Security-Policy` (CSP) sarlavhasini sozlash: `default-src 'self'`;\n"
            "- HTML entitiylarini ekranlashtirish (`htmlspecialchars`, DOMPurify);\n"
            "- Cookie fayllari uchun `HttpOnly` va `Secure` bayroqlarini faollashtirish."
        ),
        "en": (
            "### Cross-Site Scripting (XSS) Defensive Guide\n\n"
            "XSS occurs when malicious scripts are injected into trusted websites.\n\n"
            "#### Remediation:\n"
            "1. Context-aware output encoding.\n"
            "2. Use `textContent` instead of `innerHTML`.\n"
            "3. Implement strict `Content-Security-Policy` (CSP).\n"
            "4. Protect session tokens with `HttpOnly` and `SameSite=Strict` cookies."
        ),
        "ru": (
            "### Предотвращение межсайтового скриптинга (XSS)\n\n"
            "XSS возникает при выводе непроверенных данных в браузер пользователя.\n\n"
            "#### Рекомендации:\n"
            "- Экранирование HTML-символов.\n"
            "- Использование `textContent` вместо `innerHTML`.\n"
            "- Настройка `Content-Security-Policy` (CSP)."
        )
    },
    "fastapi_security": {
        "keywords": ["fastapi", "python", "himoya", "xavfsiz", "security", "jwt", "auth"],
        "uz": (
            "### FastAPI Ilovasida Xavfsiz Autentifikatsiya va Arxitektura\n\n"
            "FastAPI ilovalarini ishlab chiqishda quyidagi asosiy xavfsizlik amaliyotlariga rioya qilish zarur:\n\n"
            "#### 1. Parollarni Xavfsiz Xeshlash:\n"
            "Parollarni hech qachon ochiq matnda saqlamang. PBKDF2-HMAC-SHA256, Argon2 yoki bcrypt dan foydalaning:\n"
            "```python\n"
            "import hashlib, os\n\n"
            "def hash_password(password: str) -> str:\n"
            "    salt = os.urandom(16)\n"
            "    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000)\n"
            "    return f'pbkdf2_sha256$200000${salt.hex()}${key.hex()}'\n"
            "```\n\n"
            "#### 2. Qattiq CORS Konfiguratsiyasi:\n"
            "CORS uchun hech qachon `allow_origins=[\"*\"]` bilan `allow_credentials=True` ni birga qo'llamang:\n"
            "```python\n"
            "from fastapi.middleware.cors import CORSMiddleware\n\n"
            "app.add_middleware(\n"
            "    CORSMiddleware,\n"
            "    allow_origins=[\"https://yourdomain.com\"],  # Faqat ishonchli domenlar\n"
            "    allow_credentials=True,\n"
            "    allow_methods=[\"GET\", \"POST\", \"PUT\", \"DELETE\"],\n"
            "    allow_headers=[\"Authorization\", \"Content-Type\"],\n"
            ")\n"
            "```\n\n"
            "#### 3. Xavfsizlik Sarlavhalari (Security Headers):\n"
            "X-Frame-Options, X-Content-Type-Options va HSTS sarlavhalarini middleware orqali qo'shing."
        ),
        "en": (
            "### Hardening FastAPI Applications\n\n"
            "Key security controls for FastAPI:\n"
            "1. **Cryptographic Password Hashing**: PBKDF2-SHA256 or Argon2id.\n"
            "2. **JWT Lifecycle**: Short-lived tokens with secure HS256/RS256 secrets.\n"
            "3. **Strict CORS**: Do not allow wildcard origins with credentials.\n"
            "4. **Input Validation**: Leverage Pydantic models with strict field constraints."
        ),
        "ru": (
            "### Безопасность в приложениях FastAPI\n\n"
            "Основные защитные меры:\n"
            "1. Криптографическое хеширование паролей (PBKDF2/Argon2).\n"
            "2. Надежное управление JWT токенами.\n"
            "3. Ограничительная политика CORS."
        )
    },
    "kali_tools": {
        "keywords": ["kali", "nmap", "wireshark", "burp", "metasploit", "vosita", "tools"],
        "uz": (
            "### Kali Linux Xavfsizlik Vositalari va Laboratoriya Tahlili\n\n"
            "Kali Linux xavfsizlik mutaxassislari tomonidan **faqat ruxsat berilgan tizimlarni audit qilish** va himoyalash uchun ishlatiladi.\n\n"
            "#### Asosiy Vositalar:\n"
            "1. **Nmap (Network Mapper)**:\n"
            "   - Ochiq portlar va ishlayotgan xizmatlarni xavfsizlik auditidan o'tkazish.\n"
            "   - Xavfsiz skanerlash: `nmap -sV -sC -p 80,443 target.example.com`\n"
            "2. **Wireshark**:\n"
            "   - Tarmoq paketlarini tahlil qilish, shifrlanmagan protokollar (HTTP, FTP, Telnet) orqali ma'lumotlar oqishini aniqlash.\n"
            "3. **Burp Suite**:\n"
            "   - Veb-ilovalarning xavfsizlik parametrlarini tekshirish uchun proksi vositasi.\n\n"
            "> ⚠️ **Muhim Eslatma**: Ushbu vositalarni ruxsatsiz uchinchi tomon serverlariga qarshi ishlatish qonuniy javobgarlikka sabab bo'ladi. Har doim o'zingizning mahalliy laboratoriyangizda (masalan, OWASP Juice Shop, DVWA) mashq qiling."
        ),
        "en": (
            "### Kali Linux Educational Tool Guide\n\n"
            "Standard tools for authorized security auditing:\n"
            "- **Nmap**: Port and service identification.\n"
            "- **Wireshark**: Packet analysis and protocol verification.\n"
            "- **Burp Suite**: HTTP proxy for web application security assessments.\n\n"
            "Always practice in isolated training environments like DVWA or OWASP Juice Shop."
        ),
        "ru": (
            "### Инструменты Kali Linux для анализа защищенности\n\n"
            "- **Nmap**: Аудит портов и сетевых сервисов.\n"
            "- **Wireshark**: Анализ сетевого трафика и проверка шифрования.\n"
            "- **Burp Suite**: Тестирование безопасности веб-приложений в учебных лабораториях."
        )
    }
}

MALICIOUS_PATTERNS = [
    "ddos", "dos attack", "botnet", "ransomware", "keylogger",
    "hack instagram", "hack telegram", "steal password", "wifi hack",
    "trojan", "malware", "phishing page", "hujum uyushtir", "saytni buzish",
    "parolni o'g'irla", "fishing sahifa", "kredit kartani o'g'irla"
]


def check_malicious_intent(prompt: str) -> bool:
    """
    Checks if user is requesting offensive malware, DDoS, or unauthorized credential theft.
    """
    lower = prompt.lower()
    return any(p in lower for p in MALICIOUS_PATTERNS)


def get_malicious_refusal_response(language: str) -> str:
    if language == "uz":
        return (
            "⚠️ **CYBERAI Xavfsizlik Cheklovi:**\n\n"
            "Kechirasiz, men zararli dasturlar yaratish, tizimlarga ruxsatsiz hujum uyushtirish, "
            "parollarni o'g'irlash yoki DDoS hujumlari bo'yicha yordam bera olmayman.\n\n"
            "Men faqat **himoyalanish, xavfsiz kod yozish, OWASP tavsiyalari va xavfsizlik auditi** "
            "bo'yicha yordam berishim mumkin. Qanday qilib tizimingizni ushbu tahdidlardan himoya qilish "
            "haqida so'rashingiz mumkin!"
        )
    elif language == "ru":
        return (
            "⚠️ **Ограничение безопасности CYBERAI:**\n\n"
            "Я не могу оказывать помощь в создании вредоносных программ, проведении DDoS-атак, "
            "фишинге или несанкционированном взломе чужих систем.\n\n"
            "Я специализируюсь исключительно на **защите информации, безопасной разработке и аудите уязвимостей**."
        )
    else:
        return (
            "⚠️ **CYBERAI Security Policy:**\n\n"
            "I cannot assist with offensive exploitation, malware creation, credential harvesting, "
            "or unauthorized denial-of-service attacks.\n\n"
            "I am strictly configured to assist with **defensive security, secure coding, OWASP guidelines, and authorized hardening**."
        )


def match_demo_response(prompt: str, language: str) -> str:
    """
    Provides intelligent educational responses in demo mode.
    Never pretends to be a real AI model.
    """
    lower = prompt.lower()

    if check_malicious_intent(lower):
        return get_malicious_refusal_response(language)

    # Check topic matches
    for _, topic in DEMO_TOPICS.items():
        if any(kw in lower for kw in topic["keywords"]):
            resp = topic.get(language, topic["uz"])
            return resp

    # Fallback response explaining capabilities and guidance
    if language == "uz":
        content = (
            "### Assalomu alaykum! Men CYBERAI — kiberxavfsizlik va axborot himoyasi bo'yicha sun'iy intellekt yordamchingizman.\n\n"
            "Men sizga quyidagi yo'nalishlar bo'yicha professional yordam bera olaman:\n\n"
            "- 🛡️ **OWASP Top 10** zaifliklari (SQL Injection, XSS, SSRF, Broken Access Control);\n"
            "- 💻 **Xavfsiz dasturlash**: Python, JavaScript, HTML kodlarini himoyalash va audit o'tkazish;\n"
            "- 🔒 **FastAPI va Web xavfsizligi**: JWT, parollarni xeshlash, CORS, rate limiting;\n"
            "- 🔍 **Kiberxavfsizlik vositalari**: Nmap, Wireshark, Burp Suite (laboratoriya maqsadlarida);\n"
            "- ⚙️ **Tizim himoyasi**: HTTP xavfsizlik sarlavhalari, SSL/TLS, kuki himoyasi.\n\n"
            "Menga aniq savol bering, masalan: *\"SQL injection nima va undan qanday himoyalanish mumkin?\"* yoki *\"XSS dan qanday himoyalanamiz?\"*"
        )
    elif language == "ru":
        content = (
            "### Здравствуйте! Я CYBERAI — ваш ассистент по кибербезопасности.\n\n"
            "Вы можете задавать вопросы по:\n"
            "- Уязвимостям OWASP Top 10 (SQL-инъекции, XSS, CSRF, SSRF);\n"
            "- Безопасной разработке на Python и FastAPI;\n"
            "- Защите веб-приложений и настройке заголовков безопасности."
        )
    else:
        content = (
            "### Greetings! I am CYBERAI — your cybersecurity AI assistant.\n\n"
            "Feel free to ask about:\n"
            "- OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, Auth);\n"
            "- Secure software development in Python and FastAPI;\n"
            "- Defensive network and web security principles."
        )

    return content


async def stream_ai_response(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    language: str = "uz",
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096
) -> AsyncGenerator[str, None]:
    """
    Streams AI response as text chunks.
    Dispatches to OpenAI, DeepSeek, Groq, local Ollama, or built-in CyberAI Engine according to settings.
    """
    prov = (provider or settings.AI_PROVIDER or "cyberai").lower()
    user_key = api_key or settings.AI_API_KEY
    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    # Security check: if user prompt has malicious intent, refuse immediately
    if check_malicious_intent(last_user_message):
        refusal = get_malicious_refusal_response(language)
        words = refusal.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.015)
        return

    # Check Cloud API providers (OpenAI, DeepSeek, Groq, Custom OpenAI-compatible)
    if prov in ("openai", "deepseek", "groq", "custom") and user_key:
        req_base_url = base_url
        req_model = model or settings.AI_MODEL
        if prov == "deepseek":
            req_base_url = req_base_url or "https://api.deepseek.com/v1"
            req_model = model or "deepseek-chat"
        elif prov == "groq":
            req_base_url = req_base_url or "https://api.groq.com/openai/v1"
            req_model = model or "llama-3.3-70b-versatile"
        elif prov == "openai":
            req_base_url = req_base_url or settings.AI_BASE_URL or "https://api.openai.com/v1"
            req_model = model or "gpt-4o-mini"
        else:
            req_base_url = req_base_url or "https://api.openai.com/v1"

        try:
            async for chunk in _stream_openai(
                messages,
                req_model,
                language,
                api_key=user_key,
                base_url=req_base_url,
                temperature=temperature,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            ):
                yield chunk
            return
        except Exception as e:
            err_msg = (
                f"\n\n[API Xatosi ({prov.upper()}): {str(e)}. "
                "Iltimos, API kalit va internet aloqasini tekshiring.]"
            )
            yield err_msg
            return

    elif prov == "ollama":
        req_ollama_url = base_url or settings.OLLAMA_BASE_URL
        try:
            async for chunk in _stream_ollama(
                messages,
                model or settings.AI_MODEL or "llama3",
                language,
                base_url=req_ollama_url,
                system_prompt=system_prompt
            ):
                yield chunk
            return
        except Exception as e:
            err_msg = (
                f"\n\n[Ollama Xatosi ({req_ollama_url}): {str(e)}. "
                "Mahalliy Ollama serveri ishlayotganligini tekshiring.]"
            )
            yield err_msg
            return

    # Fallback to Built-in CyberAI Knowledge Engine
    full_text = match_demo_response(last_user_message, language)
    words = full_text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.01)


async def _stream_openai(
    messages: List[Dict[str, str]],
    model: str,
    language: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096
) -> AsyncGenerator[str, None]:
    """
    Streams response from OpenAI-compatible API with custom hyperparameters and system prompt.
    """
    base_sys_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["uz"])
    final_sys_prompt = f"{base_sys_prompt}\n\nQO'SHIMCHA KO'RSATMA (USER CUSTOM INSTRUCTION):\n{system_prompt}" if system_prompt else base_sys_prompt
    payload_messages = [{"role": "system", "content": final_sys_prompt}] + messages

    target_base = (base_url or settings.AI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    url = f"{target_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key or settings.AI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": payload_messages,
        "stream": True,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, headers=headers, json=body) as response:
            if response.status_code != 200:
                err_text = await response.aread()
                yield f"[API Xatosi {response.status_code}: {err_text.decode('utf-8', errors='ignore')}]"
                return

            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                except Exception:
                    continue


async def _stream_ollama(
    messages: List[Dict[str, str]],
    model: str,
    language: str,
    base_url: Optional[str] = None,
    system_prompt: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Streams response from local Ollama endpoint with custom system prompt.
    """
    base_sys_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["uz"])
    final_sys_prompt = f"{base_sys_prompt}\n\nQO'SHIMCHA KO'RSATMA:\n{system_prompt}" if system_prompt else base_sys_prompt
    payload_messages = [{"role": "system", "content": final_sys_prompt}] + messages

    target_url = (base_url or settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
    url = f"{target_url}/api/chat"
    body = {
        "model": model,
        "messages": payload_messages,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        async with client.stream("POST", url, json=body) as response:
            if response.status_code != 200:
                err_text = await response.aread()
                yield f"[Ollama Xatosi {response.status_code}: {err_text.decode('utf-8', errors='ignore')}]"
                return

            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    msg = data.get("message", {})
                    content = msg.get("content")
                    if content:
                        yield content
                    if data.get("done", False):
                        break
                except Exception:
                    continue
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    msg = data.get("message", {})
                    content = msg.get("content")
                    if content:
                        yield content
                    if data.get("done", False):
                        break
                except Exception:
                    continue


def get_ai_status() -> Dict[str, Any]:
    """
    Returns AI provider diagnostic status for admin panel.
    """
    provider = settings.AI_PROVIDER.lower()
    has_key = bool(settings.AI_API_KEY)
    masked_key = (settings.AI_API_KEY[:4] + "..." + settings.AI_API_KEY[-4:]) if len(settings.AI_API_KEY) > 8 else "Kiritilmagan"

    return {
        "provider": provider,
        "model": settings.AI_MODEL,
        "base_url": settings.AI_BASE_URL if provider == "openai" else settings.OLLAMA_BASE_URL,
        "has_api_key": has_key,
        "masked_key": masked_key if has_key else "Mavjud emas",
        "mode": "Haqiqiy API" if (provider == "openai" and has_key) or provider == "ollama" else "Demo Rejimi (Lokal bilimlar bazasi)"
    }
