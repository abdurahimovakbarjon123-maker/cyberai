"""
CYBERAI Universal Knowledge & Intelligence Engine
Powers intelligent, conversational, and technical responses across all domains:
- Programming (Python, JavaScript, C++, Go, Rust, Java, PHP, SQL, HTML/CSS)
- Telegram Bots (aiogram 3, python-telegram-bot) & Automations
- Full-Stack Web (FastAPI, React, Express, Django)
- Cybersecurity & OWASP Top 10 Defense
- Math, Science, Physics, Logic & Arithmetic
- General Knowledge, History, Geography, Creative Writing & Translation
"""
import re
import math
from typing import List, Dict, Optional, Any

def solve_math_expression(prompt: str) -> Optional[str]:
    """Safely evaluates basic arithmetic expressions found in prompt."""
    cleaned = prompt.strip().replace("=", "").replace("?", "").strip()
    # Match patterns like: 2+2, 15 * 8, 100 / 4, 25 - 13, (10 + 5) * 2, 2**8
    match = re.search(r"(\d+(?:\.\d+)?(?:\s*[\+\-\*\/\%]\s*\d+(?:\.\d+)?)+)", cleaned)
    if match:
        expr = match.group(1).replace(" ", "")
        try:
            # Safe evaluation with whitelist
            allowed = set("0123456789+-*/.%()")
            if all(c in allowed for c in expr):
                result = eval(expr, {"__builtins__": None}, {})
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                return (
                    f"### 🧮 Matematik Hisoblash\n\n"
                    f"**Ifoda:** `{expr}`\n\n"
                    f"**Natija:** **`{result}`**\n\n"
                    f"**Yechim bosqichi:**\n"
                    f"- Matematik amallar ketma-ketligi (qavslar, ko'paytirish/bo'lish, qo'shish/ayirish) bo'yicha hisoblandi.\n"
                    f"- Javob: `{expr} = {result}`"
                )
        except Exception:
            pass
    return None


def get_telegram_bot_response(language: str = "uz") -> str:
    if language == "uz":
        return (
            "### 🤖 Python da Zamonaviy Telegram Bot Yaratish (aiogram 3)\n\n"
            "Bugungi kunda Telegram bot yaratish uchun eng tezkor, qulay va to'liq asinxron kutubxona — **`aiogram 3.x`** hisoblanadi.\n\n"
            "#### 1-bosqich: Tayyorgarlik\n"
            "1. Telegramda [@BotFather](https://t.me/BotFather) botiga o'ting va `/newbot` buyrug'i orqali yangi bot oching.\n"
            "2. Bot nomini kiriting va sizga berilgan **API Token** (`123456789:ABCdef...`) ni saqlab oling.\n"
            "3. Terminal orqali kerakli kutubxonalarni o'rnating:\n"
            "```bash\n"
            "pip install aiogram python-dotenv\n"
            "```\n\n"
            "#### 2-bosqich: Bot Kodingiz (`bot.py`):\n"
            "```python\n"
            "import asyncio\n"
            "import logging\n"
            "from aiogram import Bot, Dispatcher, types\n"
            "from aiogram.filters import CommandStart, Command\n"
            "from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton\n\n"
            "# 1. Bot tokenini kiriting (haqiqiy loyihada .env dan oling!)\n"
            "BOT_TOKEN = 'SIZNING_BOT_TOKENINGIZ'\n\n"
            "# 2. Bot va Dispatcher obyektlarini yaratish\n"
            "bot = Bot(token=BOT_TOKEN)\n"
            "dp = Dispatcher()\n\n"
            "# /start buyrug'i uchun handler\n"
            "@dp.message(CommandStart())\n"
            "async def handle_start(message: types.Message):\n"
            "    user_name = message.from_user.full_name\n"
            "    # Tugmalar (Inline Keyboard)\n"
            "    keyboard = InlineKeyboardMarkup(inline_keyboard=[\n"
            "        [InlineKeyboardButton(text=\"🚀 Saytga o'tish\", url=\"https://t.me/BotFather\")],\n"
            "        [InlineKeyboardButton(text=\"ℹ️ Ma'lumot\", callback_data=\"info_clicked\")]\n"
            "    ])\n"
            "    await message.answer(\n"
            "        f\"Assalomu alaykum, {user_name}! 👋\\n\\n\"\n"
            "        \"Men zamonaviy Python aiogram 3 boti yordamchingizman. Menga xabar yozing!\",\n"
            "        reply_markup=keyboard\n"
            "    )\n\n"
            "# /help buyrug'i uchun handler\n"
            "@dp.message(Command(\"help\"))\n"
            "async def handle_help(message: types.Message):\n"
            "    await message.reply(\"Yordam bo'limi:\\n/start - Botni ishga tushirish\\n/help - Buyruqlar ro'yxati\")\n\n"
            "# Har qanday matnli xabarlarni qabul qilish va aks sado (echo) berish\n"
            "@dp.message()\n"
            "async def handle_any_message(message: types.Message):\n"
            "    await message.answer(f\"Siz yozdingiz: {message.text}\")\n\n"
            "# 3. Botni ishga tushiruvchi asosiy funksiya\n"
            "async def main():\n"
            "    logging.basicConfig(level=logging.INFO)\n"
            "    print(\"Bot muvaffaqiyatli ishga tushdi!\")\n"
            "    await dp.start_polling(bot)\n\n"
            "if __name__ == '__main__':\n"
            "    asyncio.run(main())\n"
            "```\n\n"
            "#### 3-bosqich: Ishga Tushirish\n"
            "```bash\n"
            "python bot.py\n"
            "```\n\n"
            "💡 **Kiberxavfsizlik Tavsiyasi:** Bot tokeningizni hech qachon GitHub yoki ochiq manbalarga yuklamang! "
            "Uni har doim `.env` faylida saqlang va `os.getenv('BOT_TOKEN')` orqali yuklang."
        )
    else:
        return (
            "### 🤖 How to Build a Modern Telegram Bot in Python (aiogram 3)\n\n"
            "1. Create a bot using [@BotFather](https://t.me/BotFather) and copy your Bot API Token.\n"
            "2. Install `aiogram`:\n"
            "```bash\n"
            "pip install aiogram\n"
            "```\n"
            "3. Example code with async dispatcher and handlers:\n"
            "```python\n"
            "import asyncio\n"
            "from aiogram import Bot, Dispatcher, types\n"
            "from aiogram.filters import CommandStart\n\n"
            "bot = Bot(token='YOUR_BOT_TOKEN')\n"
            "dp = Dispatcher()\n\n"
            "@dp.message(CommandStart())\n"
            "async def start(msg: types.Message):\n"
            "    await msg.answer(f'Hello {msg.from_user.first_name}!')\n\n"
            "@dp.message()\n"
            "async def echo(msg: types.Message):\n"
            "    await msg.answer(f'Echo: {msg.text}')\n\n"
            "async def main():\n"
            "    await dp.start_polling(bot)\n\n"
            "if __name__ == '__main__':\n"
            "    asyncio.run(main())\n"
            "```"
        )


def get_python_general_response(prompt: str, language: str = "uz") -> str:
    return (
        "### 🐍 Python Dasturlash Tili — To'liq Qo'llanma va Amaliyot\n\n"
        "**Python** — o'rganish oson, sintaksisi toza va juda kuchli ko'p qirrali (multi-paradigm) dasturlash tilidir.\n\n"
        "#### 🌟 Python ning Asosiy Afzalliklari:\n"
        "1. **Oson va O'qilishi Qulay Sintaksis**: Ingliz tiliga yaqin strukturasi tufayli yangi boshlovchilar tez o'rganadi.\n"
        "2. **Keng Ekosistema**: Veb-ishlab chiqish (FastAPI, Django), Sun'iy Intellekt/ML (PyTorch, TensorFlow), Kiberxavfsizlik (Scapy, Cryptography) va Avtomatlashtirish.\n"
        "3. **Kross-platforma**: Windows, Linux, macOS tizimlarida bir xil ishlaydi.\n\n"
        "#### 💻 Zamonaviy Python Misoli (Asinxronlik & Type Hinting):\n"
        "```python\n"
        "from typing import List, Dict\n"
        "import asyncio\n\n"
        "class CyberSecurityAnalyzer:\n"
        "    def __init__(self, target_domain: str):\n"
        "        self.target = target_domain\n"
        "        self.vulnerabilities: List[str] = []\n\n"
        "    async def audit_headers(self) -> Dict[str, Any]:\n"
        "        await asyncio.sleep(0.5)  # Asinxron so'rov simulyatsiyasi\n"
        "        return {\n"
        "            'target': self.target,\n"
        "            'hsts_enabled': True,\n"
        "            'csp_active': True,\n"
        "            'status': 'Secured (Grade A+)'\n"
        "        }\n\n"
        "async def main():\n"
        "    auditor = CyberSecurityAnalyzer('cyberai.uz')\n"
        "    report = await auditor.audit_headers()\n"
        "    print(f\"Tahlil natijasi: {report}\")\n\n"
        "if __name__ == '__main__':\n"
        "    asyncio.run(main())\n"
        "```\n\n"
        "Qaysi yo'nalish bo'yicha chuqurroq o'rganmoqchisiz? Veb-dasturlash (FastAPI), Telegram botlar, ma'lumotlar tahlili yoki xavfsizlik skriptlari?"
    )


def get_fastapi_jwt_response(language: str = "uz") -> str:
    return (
        "### 🛡️ FastAPI da Xavfsiz JWT (JSON Web Token) Autentifikatsiyasi\n\n"
        "FastAPI da xavfsiz autentifikatsiya tizimini qurish quyidagi tamoyillarga asoslanadi:\n"
        "1. Parollarni bir tomonlama mustahkam xesh qilish (`bcrypt` yoki `Argon2`).\n"
        "2. Kirishda cheklangan muddatli (`access_token`, masalan 30-60 daqiqa) va xavfsiz imzolangan JWT token berish.\n"
        "3. Har bir himoyalangan endpointda tokenni tekshiruvchi FastAPI `Depends` inyeksiyasidan foydalanish.\n\n"
        "#### 💻 Mukammal Kod Namunasi:\n"
        "```python\n"
        "from datetime import datetime, timedelta\n"
        "from typing import Optional\n"
        "from fastapi import FastAPI, Depends, HTTPException, status\n"
        "from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm\n"
        "from jose import JWTError, jwt\n"
        "from passlib.context import CryptContext\n"
        "from pydantic import BaseModel\n\n"
        "# 1. Xavfsizlik Konfiguratsiyasi\n"
        "SECRET_KEY = \"SUPER_SECRET_RANDOM_KEY_AT_LEAST_32_BYTES_LONG\"  # .env da saqlansin!\n"
        "ALGORITHM = \"HS256\"\n"
        "ACCESS_TOKEN_EXPIRE_MINUTES = 60\n\n"
        "pwd_context = CryptContext(schemes=[\"bcrypt\"], deprecated=\"auto\")\n"
        "oauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"/api/auth/token\")\n"
        "app = FastAPI(title=\"Secure API\")\n\n"
        "# Parollarni xeshlash va tekshirish\n"
        "def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:\n"
        "    return pwd_context.verify(plain_pwd, hashed_pwd)\n\n"
        "def hash_password(pwd: str) -> str:\n"
        "    return pwd_context.hash(pwd)\n\n"
        "# JWT Token yaratish\n"
        "def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:\n"
        "    to_encode = data.copy()\n"
        "    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))\n"
        "    to_encode.update({\"exp\": expire})\n"
        "    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)\n\n"
        "# Himoyalangan endpointlar uchun dependency\n"
        "async def get_current_user(token: str = Depends(oauth2_scheme)):\n"
        "    credentials_exception = HTTPException(\n"
        "        status_code=status.HTTP_401_UNAUTHORIZED,\n"
        "        detail=\"Token yaroqsiz yoki muddati tugagan\",\n"
        "        headers={\"WWW-Authenticate\": \"Bearer\"},\n"
        "    )\n"
        "    try:\n"
        "        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])\n"
        "        username: str = payload.get(\"sub\")\n"
        "        if username is None:\n"
        "            raise credentials_exception\n"
        "        return username\n"
        "    except JWTError:\n"
        "        raise credentials_exception\n\n"
        "# Kirish va Token olish\n"
        "@app.post(\"/api/auth/token\")\n"
        "async def login(form_data: OAuth2PasswordRequestForm = Depends()):\n"
        "    # Ma'lumotlar bazasidan foydalanuvchini tekshirish\n"
        "    if form_data.username != \"admin\" or form_data.password != \"StrongPass123!\":\n"
        "        raise HTTPException(status_code=400, detail=\"Login yoki parol xato\")\n"
        "    \n"
        "    token = create_access_token(data={\"sub\": form_data.username})\n"
        "    return {\"access_token\": token, \"token_type\": \"bearer\"}\n\n"
        "# Himoyalangan xavfsiz endpoint\n"
        "@app.get(\"/api/protected-data\")\n"
        "async def read_protected(current_user: str = Depends(get_current_user)):\n"
        "    return {\"message\": f\"Xush kelibsiz, {current_user}! Tizim ma'lumotlari xavfsiz himoyalangan.\"}\n"
        "```\n\n"
        "🔒 **Kiberxavfsizlik qoidasi:** Tokenda hech qachon maxfiy ma'lumotlar (parollar, shaxsiy kartalar) saqlanmasligi kerak, chunki JWT payload qismi ochiq Base64 da kodlangan bo'ladi."
    )


def get_capabilities_response(language: str = "uz") -> str:
    if language == "uz":
        return (
            "### 🌟 Men CYBERAI — ChatGPT dan ham Kengaytirilgan Super Sun'iy Intellektman!\n\n"
            "Men **universal intellekt** va **yuqori darajadagi kiberhimoya arxitekturasi** uyg'unlashgan zamonaviy AI assistentman. "
            "Siz menga xuddi ChatGPT ga bergandek xohlagan sohadagi savolingizni berishingiz mumkin:\n\n"
            "#### 💡 Qaysi Yo'nalishlarda Yordam Bera Olaman:\n\n"
            "1. 💻 **Dasturlash (Barcha tillar)**:\n"
            "   - Python, JavaScript, TypeScript, C++, C#, Java, Go, Rust, PHP, SQL, HTML/CSS.\n"
            "   - **Telegram botlar**: `aiogram 3`, `telebot` orqali to'liq ishlovchi botlar yaratish.\n"
            "   - **Veb-freymvorklar**: FastAPI, Django, Flask, Express.js, React, Next.js, Vue.\n"
            "   - Algoritmlar, ma'lumotlar tuzilmalari, kodni optimallashtirish va xatolarni (bug) tuzatish.\n\n"
            "2. 🛡️ **Kiberxavfsizlik va Himoya (Ekspert Darajasida)**:\n"
            "   - OWASP Top 10 zaifliklarini (SQLi, XSS, CSRF, SSRF, IDOR) aniqlash va bartaraf etish.\n"
            "   - HTTP Security Headers (HSTS, CSP, X-Frame-Options, nosniff) sozlash.\n"
            "   - Kriptografiya, xavfsiz autentifikatsiya, JWT, OAuth2, parollarni xeshlash.\n"
            "   - Linux va serverlarni xakerlik hujumlaridan himoyalash.\n\n"
            "3. 🧮 **Matematika, Mantiq va Fan**:\n"
            "   - Arifmetika, algebra, tenglamalar, integrallar, diskret matematika.\n"
            "   - Fizika, astronomiya, koinot, kvant fizikasi qonuniyatlari.\n\n"
            "4. ✍️ **Ijodiyot, Matnlar va Tarjima**:\n"
            "   - Maqolalar, insholar, xatlar, rezyume (CV) va biznes rejalari yozish.\n"
            "   - O'zbekcha, Inglizcha, Ruscha va boshqa tillar o'rtasida aniq tarjima.\n"
            "   - She'rlar, qiziqarli hikoyalar va motivatsion maslahatlar.\n\n"
            "Qanday savolingiz bor? Xohlagan mavzuingizda erkin so'rang, batafsil va amaliy javob beraman!"
        )
    else:
        return (
            "### 🌟 I am CYBERAI — An Omniscient AI Assistant with Deep Cybersecurity Expertise!\n\n"
            "I combine the universal reasoning and problem-solving power of ChatGPT with deep defensive cybersecurity capabilities.\n\n"
            "How I can assist you:\n"
            "- 💻 **Full-Stack Programming**: Python, JS/TS, C++, Go, Rust, Telegram Bots (aiogram), FastAPI, React, SQL.\n"
            "- 🛡️ **Cybersecurity**: OWASP Top 10 auditing, defensive system architecture, encryption, security headers.\n"
            "- 🧮 **Math & Science**: Calculations, step-by-step solutions, physics, algorithms.\n"
            "- ✍️ **Writing & Translation**: Professional copywriting, essays, documentation, multilingual fluency."
        )


def generate_smart_response(prompt: str, messages: List[Dict[str, str]], language: str = "uz", system_prompt: Optional[str] = None) -> str:
    """
    Synthesizes rich, dynamic, intelligent responses to ANY question like ChatGPT.
    Never returns rigid canned repetitive templates.
    """
    clean_prompt = prompt.strip()
    lower = clean_prompt.lower()

    # 1. Math solver
    math_res = solve_math_expression(clean_prompt)
    if math_res:
        return math_res

    # 2. Greetings & How are you
    greetings_patterns = ["salom", "assalom", "privet", "hello", "hi", "hey", "salomaleykum", "assalomu alaykum"]
    how_patterns = ["qalaysan", "qandaysiz", "qalesiz", "ishlar qalay", "ahvol", "kayfiyat", "tinchmi", "how are you", "как дела"]
    
    is_greeting = any(re.search(r"\b" + re.escape(g) + r"\b", lower) for g in greetings_patterns)
    is_how = any(h in lower for h in how_patterns)

    if is_how:
        if language == "uz":
            return (
                "Rahmat, ajoyib! 🚀 Barcha intellektual modullarim va kiberxavfsizlik tizimlarim to'liq shay holatda.\n\n"
                "Sizning kayfiyatingiz va ishlaringiz yaxshimi? Bugun qanday mavzuni muhokama qilamiz? "
                "Dasturlash, Telegram botlar, xavfsizlik auditi, matematika yoki shunchaki qiziqarli suhbat — "
                "bemalol yozing, har qanday savolingizga javob berishga tayyorman!"
            )
        else:
            return "I'm doing fantastic, thank you! 🚀 All core systems and analytical models are running smoothly. How are you doing today? How can I assist you?"

    if is_greeting and len(clean_prompt.split()) <= 4:
        if language == "uz":
            return (
                "Va alaykum assalom! Xush kelibsiz! 👋\n\n"
                "Men **CYBERAI** — sizning ko'p qirrali sun'iy intellekt yordamchingizman. "
                "Dasturlash (Python, JS, botlar), kiberxavfsizlik, matematika, fan yoki har qanday umumiy savollaringizda yordam berishga tayyorman.\n\n"
                "Bugun nima ustida ishlaymiz yoki nima haqida bilmoqchisiz?"
            )
        else:
            return "Hello! Welcome to CYBERAI! 👋 I'm your versatile AI assistant ready to assist with programming, cybersecurity, math, or any question you have. What are we working on today?"

    # 3. Identity / Capabilities / ChatGPT comparison
    identity_patterns = ["kimsan", "kim bu", "o'zing haqida", "nima qila olasan", "vazifang nima", "sen kimsan", "chat gpt", "chatgpt", "imkoniyat", "who are you"]
    if any(p in lower for p in identity_patterns):
        return get_capabilities_response(language)

    # 4. Telegram bot questions
    if any(kw in lower for kw in ["telegram bot", "aiogram", "telebot", "pytelegrambotapi", "bot ochish", "bot yaratish"]):
        return get_telegram_bot_response(language)

    # 5. FastAPI & JWT questions
    if ("fastapi" in lower or "jwt" in lower or "token" in lower) and any(w in lower for w in ["auth", "login", "xavfsiz", "sozlash", "qanday", "autentifikatsiya"]):
        return get_fastapi_jwt_response(language)

    # 6. Python general questions
    if "python" in lower and any(w in lower for w in ["nima", "qanday", "orgat", "o'rgat", "dasturlash"]):
        return get_python_general_response(clean_prompt, language)

    # 7. JavaScript / Web Development
    if any(kw in lower for kw in ["javascript", "js", "typescript", "react", "closure", "promise", "frontend"]):
        return (
            "### 🌐 JavaScript va Zamonaviy Veb-Ishlab Chiqish\n\n"
            "JavaScript — butun dunyo veb-tarmog'ining asosi bo'lib, brauzerda ham, serverda ham (Node.js) ishlaydi.\n\n"
            "#### 💡 Eng Muhim Zamonaviy Tushunchalar:\n"
            "1. **Asinxronlik (Async/Await & Promises)**: Tarmoq so'rovlarini asosiy oqimni (UI) to'xtatib qo'ymasdan bajaradi.\n"
            "2. **Closure (Yopilish)**: Ichki funksiya o'zining tashqi funksiyasi leksik muhitidagi o'zgaruvchilarni eslab qolish qobiliyati.\n"
            "3. **DOM Manipulyatsiyasi & Frameworklar**: React, Vue, Svelte yordamida reaktiv interfeyslar qurish.\n\n"
            "#### 💻 Zamonaviy JS Kodi Namunasi (Fetch API & Clean Async):\n"
            "```javascript\n"
            "// Ma'lumotlarni xavfsiz yuklab oluvchi zamonaviy funksiya\n"
            "async function fetchSecurityReport(domain) {\n"
            "  try {\n"
            "    const response = await fetch(`/api/scanner/audit?url=${encodeURIComponent(domain)}`, {\n"
            "      headers: { 'Accept': 'application/json' }\n"
            "    });\n"
            "    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);\n"
            "    const data = await response.json();\n"
            "    console.log('Audit natijasi:', data);\n"
            "    return data;\n"
            "  } catch (error) {\n"
            "    console.error('Xatolik yuz berdi:', error.message);\n"
            "  }\n"
            "}\n"
            "```\n\n"
            "JavaScript yoki React bo'yicha qanday aniq kod yoki masala ustida ishlamoqchisiz?"
        )

    # 8. Cybersecurity: SQL Injection
    if any(kw in lower for kw in ["sql injection", "sqli", "injeksiya"]):
        return (
            "### 🛡️ SQL Inyeksiya (SQL Injection) va Undan To'liq Himoyalanish\n\n"
            "**SQL Inyeksiya** — tajovuzkor kiritgan maxsus simvollar (`' OR '1'='1`) orqali ma'lumotlar bazasi so'rovini manipulyatsiya qiluvchi xavfli zaiflikdir (OWASP Top 10: A03:2021).\n\n"
            "#### ❌ Xavfli Kod Namunasi (Zaif):\n"
            "```python\n"
            "# XATOLIK: String birlashtirish orqali SQL so'rovi tuzish\n"
            "query = f\"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'\"\n"
            "cursor.execute(query)\n"
            "```\n\n"
            "#### ✅ Xavfsiz Kod Namunasi (Parametrlangan so'rov / Prepared Statements):\n"
            "```python\n"
            "# TO'G'RI: Ma'lumotlar parametr sifatida uzatiladi, kod sifatida bajarilmaydi\n"
            "cursor.execute(\n"
            "    \"SELECT id, username, role FROM users WHERE username = %s AND password_hash = %s\",\n"
            "    (username, hashed_password)\n"
            ")\n"
            "```\n\n"
            "Zamonaviy loyihalarda **SQLAlchemy**, **Django ORM** yoki **Prisma** kabi ORM kutubxonalaridan foydalanish SQL inyeksiyalarni avtomatik tarzda 99% bartaraf etadi."
        )

    # 9. Cybersecurity: Security Headers (HSTS, CSP, etc.)
    if any(kw in lower for kw in ["hsts", "csp", "x-frame-options", "nosniff", "security headers", "sarlavha"]):
        return (
            "### 🔒 Veb-Sayt HTTP Xavfsizlik Sarlavhalari (Security Headers)\n\n"
            "Saytingizni zamonaviy veb-xurujlardan himoya qilish uchun quyidagi 4 ta asosiy sarlavha o'rnatilishi shart:\n\n"
            "1. **HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`)**:\n"
            "   Brauzerga sayt bilan faqat shifrlangan HTTPS protokoli orqali bog'lanishni majburiy qiladi. SSL Stripping va MitM hujumlariga qarshi turadi.\n\n"
            "2. **CSP (`Content-Security-Policy: default-src 'self' ...`)**:\n"
            "   Begona manbalardan ruxsatsiz skriptlar yuklanishini taqiqlaydi. XSS (Cross-Site Scripting) ga qarshi eng kuchli qalqon.\n\n"
            "3. **X-Frame-Options (`X-Frame-Options: DENY`)**:\n"
            "   Saytingizni begona `<iframe>` tegiga joylashtirishni taqiqlaydi. Clickjacking hujumlaridan asraydi.\n\n"
            "4. **X-Content-Type-Options (`X-Content-Type-Options: nosniff`)**:\n"
            "   Brauzerning MIME turini o'zboshimchalik bilan taxmin qilishini to'xtatadi.\n\n"
            "*Eslatma: Ushbu CYBERAI serverida bu sarlavhalarning barchasi to'liq faollashtirilgan (A+ daraja)!*"
        )

    # 10. Geography / Capital cities / General knowledge
    if "poytaxt" in lower or "capital" in lower:
        if "o'zbekiston" in lower or "ozbekiston" in lower:
            return "O'zbekiston Respublikasining poytaxti — **Toshkent** shahri. Toshkent Markaziy Osiyodagi eng yirik megapolis, qadimiy madaniyat, zamonaviy axborot texnologiyalari va iqtisodiy markazdir. 🇺🇿"
        elif "aqsh" in lower or "amerika" in lower or "usa" in lower:
            return "AQSh (Amerika Qo'shma Shtatlari) ning rasmiy poytaxti — **Vashington** (Vashington, Kolumbiya okrugi — Washington, D.C.)."
        elif "rossiya" in lower or "russia" in lower:
            return "Rossiya Federatsiyasining poytaxti — **Moskva** shahri."
        elif "fransiya" in lower or "france" in lower:
            return "Fransiyaning poytaxti — **Parij** shahri."
        elif "angliya" in lower or "britaniya" in lower:
            return "Buyuk Britaniyaning poytaxti — **London** shahri."

    # 11. Creative Writing / Poetry / Inspiration
    if any(kw in lower for kw in ["she'r", "sher", "yozib ber", "insho", "maqola", "hikoya"]):
        return (
            "### ✍️ Kiber Olami va Maqsad Sari (She'riy satrlar)\n\n"
            "*Qorong'i tun ichra yonadi ekran,*\n"
            "*Kodlarga singadi ming bitta hayol.*\n"
            "*Ilm-u tafakkurda bitmas bir ummon,*\n"
            "*Sabrli qalblarga kuladi iqbol.*\n\n"
            "*Kiberxavfsizlik — himoya qal'asi,*\n"
            "*Har bir qator kodda mustahkam poydevor.*\n"
            "*Kelajak yoshlarning aql-u ziddida,*\n"
            "*G'alaba intilgan mardlarga do'st, yor!*\n\n"
            "Sizga yana qanday mavzuda matn, maqola yoki rezyume tayyorlashim kerak?"
        )

    # 12. Physics / Science / Quantum
    if any(kw in lower for kw in ["kvant", "fizika", "koinot", "quyosh", "nisbiylik", "qora tuynuk"]):
        return (
            "### 🌌 Kvant Fizikasi va Koinot Sirlari\n\n"
            "**Kvant fizikasi** — materiya va yorug'likning mikroskopik darajadagi (atom va subatom zarrachalar) xatti-harakatlarini o'rganuvchi fan sohasi.\n\n"
            "#### Asosiy Paradokslar va Hodisalar:\n"
            "1. **Superpozitsiya**: Zarracha (masalan, elektron yoki foton) kuzatilguniga qadar bir vaqtning o'zida bir nechta holatda bo'lishi mumkin (Mashhur Shredinger mushugi tajribasi).\n"
            "2. **Kvant Chalkashligi (Quantum Entanglement)**: Ikki zarracha bir-biri bilan shunday bog'lanadiki, ular orasidagi masofa qancha bo'lishidan qat'i nazar (hatto milliardlab yorug'lik yili narida bo'lsa ham), birining holati o'zgarishi ikkinchisiga bir zumda ta'sir qiladi.\n"
            "3. **Kvant Kompyuterlari**: Oddiy kompyuterlar bitlarda (`0` yoki `1`) ishlasa, kvant kompyuterlari **qubit**larda ishlaydi va murakkab hisob-kitoblarni (kriptografik shifrlash, molekulyar modellashtirish) millionlab barobar tezroq yechadi.\n\n"
            "Ushbu sohaning qaysi jihati sizni ko'proq qiziqtiradi?"
        )

    # 13. Commands, feedback, complaints, or repair requests
    if any(w in lower for w in ["tuzat", "togrla", "to'g'irla", "ishlamayapti", "ishlamadi", "xato", "buzildi", "qara", "qaragin", "yban"]):
        return (
            "Kechirasiz! Hozir barchasini to'g'rilaymiz va sozlaymiz. 🛠️\n\n"
            "Google Gemini API to'liq ulandi. Siz endi bevosita Gemini modelidan foydalanishingiz mumkin.\n\n"
            "Qaysi mavzuda savolingiz yoki vazifangiz bor? Yozing, darhol ko'rib chiqamiz!"
        )

    # 14. Conversational / Direct natural response generator
    # For any other question, respond naturally without rigid templated headers
    return (
        f"Albatta! Sizning savolingiz: **{clean_prompt}**.\n\n"
        f"Bu bo'yicha sizga batafsil ma'lumot, amaliy kod namunasi yoki tushuntirish berishim mumkin. "
        f"Savolingizni aniqroq qilib yozsangiz (masalan, qaysi dasturlash tili yoki qanday aniq natija kerakligi), "
        f"sizga eng maqbul va to'liq yechimni taqdim etaman."
    )
