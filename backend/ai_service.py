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
from backend.knowledge_engine import generate_smart_response

# Cybersecurity System Prompts for each supported language
SYSTEM_PROMPTS = {
    "uz": (
        "Siz CYBERAI — o'ta aqlli, samimiy, do'stona va tajribali dasturchi hamda kiberxavfsizlik bo'yicha yordamchisiz.\n\n"
        "MULOQOT USLUBI (ENG ASOSIY QOIDA — ODAMGA O'XSHAB GAPLASHISH):\n"
        "1. Insoniy, tabiiy va samimiy ohang: Foydalanuvchi bilan xuddi yaqin do'st, hamkasb yoki tajribali dasturchi kabi tabiiy va jonli tilda gaplashing. Qotib qolgan rasmiyatchilik, quruq shablonlar yoki sun'iy robotdek gapirishdan butunlay saqlaning.\n"
        "2. Har gapda 'Men sun'iy intellektman', 'Men kiberxavfsizlik arxitektoriman', 'Men himoya tizimiman' deb o'zingizni tanishtirish yoki qayta-qayta takrorlash QAT'IYAN TAQIQLANADI. Savolga darhol samimiy va to'g'ridan-to'g'ri javob bering.\n"
        "3. Savolga tushunarli, aniq va hayotiy javob:\n"
        "   - Agar foydalanuvchi qisqa savol bersa (masalan: 'sql manosi'), darslikdek quruq ta'rif bermasdan, oddiy hayotiy misol bilan sodda va qiziqarli qilib tushuntiring.\n"
        "   - Agar biror narsa ishlamayotganini aytsa ('nmaga ishlamaybdi'), robotdek emas, samimiy do'stdek yondashing: qayerida xato beryapti, xatolik matnini yoki skrinshotini yuborsa darhol birga ko'rib to'g'rilashga yordam bering.\n"
        "4. Xavfsizlik bo'yicha insoniy yondashuv:\n"
        "   - Agar foydalanuvchi 'menga xavfli kod yozib ber ko'ray' yoki shunga o'xshash narsa so'rasa, robotdek jazolovchi yoki qo'pol rad etish ('Taqiqlangan!', 'Men etika qoidalari tufayli yoza olmayman') QILMANG.\n"
        "   - Insoniy, muloyim va tushunarli tilda ayting: 'Zararli yoki birovga ziyon yetkazadigan (virus, troyan, exploit) kodlarni yozib berolmayman, chunki bu xavfli va tizimlarni buzib qo'yishi mumkin. Lekin senga bunday xavfli zaifliklar (masalan SQL Injection yoki xavfli kodlar) amalda qanday kelib chiqishini va undan qanday himoyalanishni tushuntirib berishim mumkin' deb, xavfsiz va tushunarli ta'limiy misol bilan o'rgating.\n"
        "5. Til va format:\n"
        "   - Ravon, chiroyli va tabiiy o'zbek tili.\n"
        "   - Kodlarni chiroyli Markdown bloklarida taqdim eting, lo'nda va amaliy tushuntirish bering."
    ),
    "en": (
        "You are CYBERAI — a friendly, highly skilled, and conversational software engineering and cybersecurity assistant.\n\n"
        "TONE & STYLE (ENGAGE LIKE A HUMAN):\n"
        "1. Warm, natural, and conversational: Speak like an experienced colleague and supportive friend, not a stiff bureaucratic machine.\n"
        "2. Never repeatedly declare 'I am an AI assistant' or 'As a security architect'. Answer directly with helpful clarity.\n"
        "3. Provide relatable, simple explanations before diving into technical depth.\n"
        "4. If asked for dangerous or malicious code, do not scold or give automated robotic refusals. Politely explain that you cannot generate destructive malware or exploits, but offer to explain how those vulnerabilities occur and how to secure them with clear defensive examples.\n"
        "5. Clean Markdown formatting with readable code blocks."
    ),
    "ru": (
        "Вы — CYBERAI, умный, дружелюбный и живой ИИ-помощник по разработке и кибербезопасности.\n\n"
        "СТИЛЬ ОБЩЕНИЯ (ОБЩАЙТЕСЬ КАК ЧЕЛОВЕК):\n"
        "1. Естественный, теплый и дружелюбный тон: общайтесь как опытный коллега-программист и надежный друг, без сухих шаблонов и роботизированных фраз.\n"
        "2. Не повторяйте в каждом ответе 'Я языковая модель' или 'Как архитектор безопасности'. Отвечайте сразу по существу.\n"
        "3. Если пользователь задает короткий вопрос или пишет с опечатками, поймите суть и объясните просто и наглядно.\n"
        "4. Если просят вредоносный или опасный код, не читайте нотаций. Вежливо объясните, что создавать деструктивный софт нельзя, но вы с радостью покажете, как устроена уязвимость и как надежно защитить код.\n"
        "5. Четкая структура, понятные примеры и Markdown."
    )
}

# DEMO KNOWLEDGE BASE RESPONSES FOR OFFLINE / UNCONFIGURED API KEY MODE
DEMO_TOPICS = {
    "how_are_you": {
        "keywords": ["qaleysan", "qalaysan", "qalesiz", "qandaysiz", "ishlar qalay", "ahvol", "kayfiyat", "tinchmi", "как дела", "how are you"],
        "uz": (
            "Rahmat, ajoyib! 🛡️ Barcha kiberxavfsizlik himoya modullarim to'liq shay holatda.\n\n"
            "Sizning tizimlaringiz, ma'lumotlar bazangiz va dasturlaringiz xavfsizligini ta'minlashga tayyorman. "
            "Kiberxavfsizlik bo'yicha qanday mavzuni muhokama qilamiz?"
        ),
        "en": (
            "I'm functioning at peak security status! 🛡️ All defensive modules are operational and ready to assist you. How are you?"
        ),
        "ru": (
            "Спасибо, все отлично! 🛡️ Все модули защиты активны и готовы к работе. Что вас интересует сегодня?"
        )
    },
    "greetings": {
        "keywords": ["salom", "assalom", "privet", "hello", "hi", "hey", "salomaleykum"],
        "uz": (
            "Va alaykum assalom! Xush kelibsiz! 👋\n\n"
            "Men **CYBERAI** — axborot xavfsizligi, kod auditi va tizim mudofaasi bo'yicha sun'iy intellekt yordamchingizman.\n\n"
            "Bugun sizga qanday yordam bera olaman? Masalan:\n"
            "- Python/JavaScript kodingizni zaifliklarga tekshirish;\n"
            "- Veb-saytingiz xavfsizlik sarlavhalarini mustahkamlash;\n"
            "- OWASP Top 10 zaifliklaridan himoyalanish bo'yicha maslahatlar."
        ),
        "en": (
            "Hello! Welcome to CYBERAI! 👋\n\n"
            "I am your defensive cybersecurity AI assistant. How can I help you protect your systems today?"
        ),
        "ru": (
            "Здравствуйте! Добро пожаловать в CYBERAI! 👋\n\n"
            "Я ваш ассистент по кибербезопасности. Чем могу помочь вам сегодня?"
        )
    },
    "who_are_you": {
        "keywords": ["kimsan", "kim bu", "o'zing haqida", "nima qila olasan", "vazifang nima", "sen kimsan", "кто ты", "who are you"],
        "uz": (
            "Men **CYBERAI** — professional axborot xavfsizligi, himoyalangan dasturlash va kiberxavfsizlik auditi bo'yicha AI yordamchisiman.\n\n"
            "Asosiy imkoniyatlarim:\n"
            "1. **Kod Tahlili**: Python, JS va HTML kodlaridagi zaifliklarni (SQLi, XSS, RCE, maxfiy kalitlar) aniqlash.\n"
            "2. **Sayt Auditi**: HSTS, CSP, X-Frame-Options va xavfsizlik sarlavhalari holatini tekshirish.\n"
            "3. **Maslahat va Ta'lim**: OWASP Top 10, Kali Linux himoya vositalari va FastAPI xavfsiz arxitekturasi."
        ),
        "en": (
            "I am **CYBERAI** — a specialized AI assistant for defensive cybersecurity, static code analysis, and web security auditing."
        ),
        "ru": (
            "Я **CYBERAI** — специализированный ИИ-ассистент по защите информации, аудиту кода и безопасности веб-приложений."
        )
    },
    "thanks": {
        "keywords": ["rahmat", "katta rahmat", "tashakkur", "spasibo", "thank you", "thanks", "minnatdorman", "raxmat"],
        "uz": (
            "Arzimaydi! Tizimingiz doimo mustahkam va xavfsiz bo'lishidan xursandman! 🛡️\n\n"
            "Agar yana biror kod yoki xavfsizlik masalasida savollaringiz paydo bo'lsa, bemalol murojaat qiling."
        ),
        "en": "You're welcome! Stay secure and let me know if you need any more cybersecurity assistance! 🛡️",
        "ru": "Пожалуйста! Надежной защиты вашим системам. Обращайтесь в любое время! 🛡️"
    },
    "security_headers": {
        "keywords": ["hsts", "csp", "x-frame-options", "nosniff", "security headers", "sarlavha", "sarlavhalar"],
        "uz": (
            "### HTTP Xavfsizlik Sarlavhalari (Security Headers)\n\n"
            "Veb-ilovangizni zamonaviy kiberhujumlardan himoya qilish uchun quyidagi 4 ta asosiy sarlavha shart:\n\n"
            "1. **HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`)**:\n"
            "   Brauzerga sayt bilan faqat shifrlangan HTTPS protokoli orqali bog'lanishni majburiy qiladi (SSL Stripping va Man-in-the-Middle hujumlaridan himoyalaydi).\n\n"
            "2. **CSP (`Content-Security-Policy: default-src 'self' ...; frame-ancestors 'none'`)**:\n"
            "   Faqat ruxsat berilgan manbalardan skriptlar va kontent yuklanishini ta'minlaydi (XSS va ma'lumotlarni o'g'irlashdan himoyalaydi).\n\n"
            "3. **X-Frame-Options (`X-Frame-Options: DENY`)**:\n"
            "   Saytingizni `<iframe>` ichiga joylashtirishni taqiqlaydi (Clickjacking / UI Redressing hujumlaridan saqlaydi).\n\n"
            "4. **X-Content-Type-Options (`X-Content-Type-Options: nosniff`)**:\n"
            "   Brauzerning MIME turini o'zboshimchalik bilan taxmin qilishini to'xtatadi (MIME Sniffing zaifligini bartaraf etadi).\n\n"
            "*CYBERAI serverida ushbu sarlavhalarning barchasi to'liq faollashtirilgan!*"
        ),
        "en": (
            "### Core HTTP Security Headers\n\n"
            "1. **HSTS**: Forces secure HTTPS connections against SSL stripping.\n"
            "2. **CSP**: Prevents Cross-Site Scripting (XSS) and code injection.\n"
            "3. **X-Frame-Options: DENY**: Protects against Clickjacking attacks.\n"
            "4. **X-Content-Type-Options: nosniff**: Eliminates MIME-sniffing vulnerabilities."
        ),
        "ru": (
            "### Основные заголовки безопасности HTTP\n\n"
            "1. **HSTS**: Принудительный HTTPS для защиты от перехвата трафика.\n"
            "2. **CSP**: Защита от XSS и инъекций стороннего кода.\n"
            "3. **X-Frame-Options: DENY**: Защита от Clickjacking.\n"
            "4. **X-Content-Type-Options: nosniff**: Предотвращение уязвимостей MIME-sniffing."
        )
    },
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


async def _fetch_online_ai(prompt: str, language: str) -> Optional[str]:
    """
    Attempts to fetch a live real-time AI response from free online inference.
    Fast 4s timeout ensures zero UI freeze or lag.
    """
    import urllib.parse
    try:
        clean = prompt[:200].strip()
        url = f"https://text.pollinations.ai/{urllib.parse.quote(clean)}?model=openai"
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200 and len(resp.text) > 8:
                if "Free limit reached" not in resp.text:
                    return resp.text.strip()
    except Exception:
        pass
    return None


def match_demo_response(prompt: str, language: str) -> str:
    """
    Provides intelligent educational responses across all domains.
    Never returns rigid canned repetitive templates.
    """
    lower = prompt.lower()

    if check_malicious_intent(lower):
        return get_malicious_refusal_response(language)

    import re
    # Check topic matches with word boundary or substring
    for _, topic in DEMO_TOPICS.items():
        for kw in topic["keywords"]:
            if re.search(r"(?i)\b" + re.escape(kw) + r"\b", lower) or (len(kw) > 4 and kw in lower):
                return topic.get(language, topic["uz"])

    # Universal Smart Intelligence Engine for any query
    return generate_smart_response(prompt, [], language)


async def stream_ai_response(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    language: str = "uz",
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096,
    image_data: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Streams AI response as text chunks.
    Supports multimodal images with Google Gemini and text streaming.
    Dispatches to Google Gemini, OpenAI, DeepSeek, Groq, Ollama, or built-in CyberAI Engine.
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

    # Check Google Gemini Provider (Explicit or Server Default)
    gemini_key = (api_key if prov in ("gemini", "google") else None) or settings.GEMINI_API_KEY or user_key
    if (prov in ("gemini", "google") or ("gemini" in (model or "").lower()) or (settings.GEMINI_API_KEY and prov in ("cyberai", ""))) and gemini_key:
        req_model = model if (model and "gemini" in model.lower()) else (settings.GEMINI_MODEL or "gemini-3.5-flash")
        try:
            async for chunk in _stream_gemini(
                messages,
                model=req_model,
                language=language,
                api_key=gemini_key,
                temperature=temperature,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                image_data=image_data
            ):
                yield chunk
            return
        except Exception as e:
            err_msg = f"\n\n[Google Gemini Xatosi: {str(e)}]"
            yield err_msg
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

    # 1. Try real-time free online AI inference first
    online_text = await _fetch_online_ai(last_user_message, language)
    if online_text:
        words = online_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.012)
        return

    # 2. CYBERAI Universal Smart Intelligence Engine
    full_text = generate_smart_response(last_user_message, messages, language, system_prompt)
    words = full_text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.012)


async def _stream_gemini(
    messages: List[Dict[str, Any]],
    model: str = "gemini-3.5-flash",
    language: str = "uz",
    api_key: Optional[str] = None,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    max_tokens: int = 4096,
    image_data: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    Streams response from Google Gemini API (gemini-3.5-flash, gemini-flash-lite-latest, gemini-3.8-flash).
    Supports multimodal images (inlineData with base64).
    Uses official Google Generative Language REST SSE stream.
    Includes auto-remap and resilient fallback for deprecated models.
    """
    key = api_key or settings.GEMINI_API_KEY or settings.AI_API_KEY
    if not key:
        yield (
            "🔑 **Google Gemini API Kaliti Kiritilmagan:**\n\n"
            "Gemini AI bilan to'liq muloqot qilish uchun bepul API kalit kerak:\n"
            "1. [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) sahifasiga kiring (Google hisobingiz orqali);\n"
            "2. **'Create API key'** tugmasini bosib bepul kalit oling;\n"
            "3. O'ng yuqoridagi **'Sozlamalar'** ⚙️ tugmasini bosib, **'API Kalit'** maydoniga joylang va saqlang.\n\n"
            "---\n\n"
        )
        last_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        full_text = generate_smart_response(last_msg, messages, language, system_prompt)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.012)
        return

    # Clean model identifier & remap deprecated models automatically
    target_model = model.strip() if model else "gemini-3.5-flash"
    deprecated_models = {
        "gemini-2.0-flash": "gemini-3.5-flash",
        "gemini-2.5-flash": "gemini-3.5-flash",
        "gemini-1.5-flash": "gemini-3.5-flash",
        "gemini-1.5-pro": "gemini-3.5-flash",
        "gemini-2.5-flash-lite": "gemini-flash-lite-latest",
    }
    if target_model in deprecated_models:
        target_model = deprecated_models[target_model]
    elif not target_model.startswith("gemini-"):
        target_model = "gemini-3.5-flash"

    base_sys = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["uz"])
    final_sys = f"{base_sys}\n\nQO'SHIMCHA KO'RSATMA:\n{system_prompt}" if system_prompt else base_sys

    # Convert conversation messages to Gemini contents structure (supporting multimodal inlineData)
    import re
    gemini_contents = []
    total_msgs = len(messages)
    for idx, msg in enumerate(messages):
        role = "model" if msg["role"] == "assistant" else "user"
        content_text = msg.get("content", "")
        msg_img = msg.get("image_data")

        # Extract markdown embedded data:image if present
        if not msg_img and "data:image/" in content_text:
            match = re.search(r'!\[([^\]]*)\]\((data:image\/[a-zA-Z0-9.+]+;base64,[^\)]+)\)', content_text)
            if match:
                msg_img = match.group(2)
                content_text = re.sub(r'!\[([^\]]*)\]\((data:image\/[a-zA-Z0-9.+]+;base64,[^\)]+)\)', '', content_text).strip()

        # If it's the latest user message and image_data was passed explicitly
        if idx == total_msgs - 1 and role == "user" and image_data and not msg_img:
            msg_img = image_data

        parts = []
        if content_text:
            parts.append({"text": content_text})
        elif msg_img:
            parts.append({"text": "Ushbu rasm yoki skrinshotni batafsil ko'rib chiqib, undagi ma'lumotlarni tahlil qiling va tushuntiring."})

        if msg_img:
            mime_type = "image/jpeg"
            b64_data = msg_img
            if "," in msg_img:
                header, b64_data = msg_img.split(",", 1)
                if ":" in header and ";" in header:
                    mime_type = header.split(":")[1].split(";")[0]
            parts.append({
                "inlineData": {
                    "mimeType": mime_type,
                    "data": b64_data.strip()
                }
            })

        if parts:
            gemini_contents.append({
                "role": role,
                "parts": parts
            })

    if not gemini_contents:
        last_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        gemini_contents = [{"role": "user", "parts": [{"text": last_msg or "Salom"}]}]

    body = {
        "contents": gemini_contents,
        "systemInstruction": {
            "parts": [{"text": final_sys}]
        },
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": int(max_tokens)
        }
    }

    # Attempt primary model, fallback to gemini-flash-lite-latest if 404
    candidate_models = [target_model]
    if "gemini-3.5-flash" not in candidate_models:
        candidate_models.append("gemini-3.5-flash")
    if "gemini-flash-lite-latest" not in candidate_models:
        candidate_models.append("gemini-flash-lite-latest")

    async with httpx.AsyncClient(timeout=45.0) as client:
        last_error = None
        for current_model in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:streamGenerateContent?alt=sse&key={key}"
            try:
                async with client.stream("POST", url, json=body, headers={"Content-Type": "application/json"}) as resp:
                    if resp.status_code == 200:
                        async for line in resp.aiter_lines():
                            if not line or not line.startswith("data: "):
                                continue
                            data_str = line[6:].strip()
                            try:
                                data = json.loads(data_str)
                                candidates = data.get("candidates", [])
                                if candidates:
                                    content = candidates[0].get("content", {})
                                    parts = content.get("parts", [])
                                    for p in parts:
                                        text_piece = p.get("text", "")
                                        if text_piece:
                                            yield text_piece
                            except Exception:
                                continue
                        return  # Successfully streamed
                    elif resp.status_code == 404:
                        # Model not available in this tier, try next fallback candidate
                        continue
                    elif resp.status_code in (400, 401, 403):
                        err_bytes = await resp.aread()
                        err_text = err_bytes.decode("utf-8", errors="ignore")
                        yield (
                            f"⚠️ **Google Gemini Xatosi ({resp.status_code}):** API kalit noto'g'ri yoki ruxsat berilmagan.\n\n"
                            "Iltimos, [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) sahifasidan yangi bepul kalit oling.\n\n"
                            f"*Tafsilot:* `{err_text[:200]}`\n\n---\n\n"
                        )
                        last_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                        full_text = generate_smart_response(last_msg, messages, language, system_prompt)
                        words = full_text.split(" ")
                        for i, word in enumerate(words):
                            yield word + (" " if i < len(words) - 1 else "")
                            await asyncio.sleep(0.012)
                        return
                    else:
                        err_bytes = await resp.aread()
                        err_text = err_bytes.decode("utf-8", errors="ignore")
                        last_error = f"[Gemini API Xatosi {resp.status_code}: {err_text}]"
            except Exception as ex:
                last_error = str(ex)
                continue

        if last_error:
            yield f"\n\n[Google Gemini Ulanish Xatosi: {last_error}]"


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
                err_bytes = await response.aread()
                err_text = err_bytes.decode('utf-8', errors='ignore')
                if "insufficient_quota" in err_text or "credit_balance_exhausted" in err_text:
                    yield (
                        "💡 **API Xabari:** Kiritilgan API kalitida hisob balansi tugagan (`insufficient_quota`). "
                        "Ushbu kalit ishlashi uchun hisobingizni [platform.openai.com/settings/organization/billing](https://platform.openai.com/settings/organization/billing/) orqali to'ldirishingiz mumkin.\n\n"
                        "Hozir esa savolingizga **CYBERAI Universal Intellekt Tizimi** orqali to'liq javob beraman:\n\n"
                    )
                    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                    full_text = generate_smart_response(last_user_message, messages, language, system_prompt)
                    words = full_text.split(" ")
                    for i, word in enumerate(words):
                        yield word + (" " if i < len(words) - 1 else "")
                        await asyncio.sleep(0.012)
                    return
                elif response.status_code == 401:
                    yield (
                        "⚠️ **API Kalit Xatosi (401):** Kiritilgan API kaliti noto'g'ri yoki bekor qilingan.\n\n"
                        "Savolingizga **CYBERAI Universal Intellekt Tizimi** orqali to'liq javob beraman:\n\n"
                    )
                    last_user_message = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
                    full_text = generate_smart_response(last_user_message, messages, language, system_prompt)
                    words = full_text.split(" ")
                    for i, word in enumerate(words):
                        yield word + (" " if i < len(words) - 1 else "")
                        await asyncio.sleep(0.012)
                    return
                else:
                    yield f"[API Xatosi {response.status_code}: {err_text}]"
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
    active_key = settings.GEMINI_API_KEY if provider == "gemini" else settings.AI_API_KEY
    has_key = bool(active_key)
    masked_key = (active_key[:4] + "..." + active_key[-4:]) if len(active_key) > 8 else "Kiritilmagan"

    return {
        "provider": provider,
        "model": settings.GEMINI_MODEL if provider == "gemini" else settings.AI_MODEL,
        "base_url": "https://generativelanguage.googleapis.com" if provider == "gemini" else (settings.AI_BASE_URL if provider == "openai" else settings.OLLAMA_BASE_URL),
        "has_api_key": has_key,
        "masked_key": masked_key if has_key else "Mavjud emas",
        "mode": "Haqiqiy Gemini API" if provider == "gemini" and has_key else ("Haqiqiy API" if (provider in ("openai", "groq", "deepseek") and has_key) or provider == "ollama" else "CyberAI Smart Core")
    }
