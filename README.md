# CYBERAI — Full Stack AI Cybersecurity Platform

**CYBERAI** — zamonaviy sun'iy intellekt, axborot xavfsizligi va dasturiy ta'minot mudofaasi bo'yicha to'liq ishchi (full-stack) professional kiberxavfsizlik platformasi.

Ilova premium shishasimon (**Glassmorphism / Glass UI**) kiberxavfsizlik interfeysi, **FastAPI**, **SQLAlchemy**, **SQLite**, **PyJWT**, **Modern Vanilla JavaScript** va moslashuvchan **AI Provider arxitekturasi** (OpenAI, lokal Ollama va oflayn Demo rejim) asosida qurilgan.

---

## 🌐 24/7 BEPUL CLOUD HOSTING (Kompyuter o'chirilganda ham 24/7 ishlash)

Ilovangiz kompyuteringiz o'chiq bo'lganda ham internetda 24 soat to'xtovsiz ishlashi uchun quyidagi bepul bulutli xizmatlardan biriga 1 ta klik bilan ulab qo'yishingiz mumkin:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/abdurahimovakbarjon123-maker/cyberai)

### 1-Usul: Render orqali (100% Bepul va Oson):
1. **[Render.com](https://render.com)** saytiga kiring va GitHub hisobingiz (`abdurahimovakbarjon123-maker`) orqali kiring.
2. Yuqoridagi **"Deploy to Render"** tugmasini bosing yoki **"New +" -> "Web Service"** ni tanlang.
3. Repozitoriy sifatida `cyberai` ni tanlang.
4. Render avtomatik ravishda `render.yaml` va `Dockerfile` ni tanib, serverni ishga tushiradi.
5. Tayyor! Sizga `https://cyberai-xxxx.onrender.com` doimiy bepul HTTPS domen beriladi va u kompyuteringiz o'chiq bo'lsa ham **24/7** ishlab turadi!

---

## 🚀 ASOSIY IMKONIYATLAR

1. **AI Kiberxavfsizlik Yordamchisi (AI Chat):**
   - Real vaqtda oqimli (SSE Streaming) javob qaytarish.
   - Ko'p suhbatlar (Multiple conversations), suhbatlarni qayta nomlash va o'chirish.
   - O'zbek tili (birlamchi), ingliz va rus tillarini to'liq qo'llab-quvvatlash.
   - Markdown formatlash, kod sintaksisi yoritilishi va 1-klik bilan nusxalash.
   - Kiberxavfsizlik etikasi va himoya filtrlari (DDoS, fishing, zararli dasturlar yaratish qat'iyan rad etiladi; faqat mudofaa va ta'lim maqsadlarida yordam beradi).
   - Generatsiyani to'xtatish (Stop) va qayta yaratish (Regenerate).

2. **Manba Kodi Xavfsizlik Tahlili (Static Code Security Analyzer):**
   - Python, JavaScript va HTML kodlarini statik tahlil qilish (kod serverda **hech qachon bajarilmaydi**).
   - Matn ko'rinishida kod kiritish yoki fayl (.py, .js, .html) yuklash.
   - Aniqlanadigan zaifliklar:
     * Koddagi ochiq qoldirilgan maxfiy kalitlar (AWS Access Keys, JWT tokenlar, Private Keys, parollar).
     * Dinamik SQL inyeksiyalari (Python f-string, `%` formatlash, string concatenation).
     * Xavfli buyruqlar va kod ijrosi (`eval()`, `exec()`, `os.system()`, `subprocess(shell=True)`, `pickle.loads()`).
     * XSS zaifliklari (`innerHTML =`, `document.write()`, `dangerouslySetInnerHTML`).
     * Zaif kriptografiya (`MD5`, `SHA1`, `verify=False`).
     * Noto'g'ri konfiguratsiyalar (`DEBUG=True`).
   - Har bir topilgan zaiflik uchun: xavf darajasi (CRITICAL, HIGH, MEDIUM, LOW), qator raqami, tushuntirish, tuzatish tavsiyasi va to'g'rilangan xavfsiz kod namunasi.

3. **Veb-sayt Xavfsizlik Auditi (Website Security Checker):**
   - Non-destruktiv (zararsiz) xavfsizlik auditi.
   - **Qat'iy SSRF himoyasi**: `localhost`, `127.0.0.1`, RFC1918 ichki tarmoqlari (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), bulut metadata manzillari (`169.254.169.254`) va lokal domenlar qat'iyan bloklanadi.
   - Egasi ekanligini yoki tekshirish vakolatini tasdiqlovchi majburiy rozilik nazorati.
   - HTTP Security Headers tekshiruvi: HSTS, CSP, X-Frame-Options (Clickjacking), X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
   - HTTPS va SSL konfiguratsiyasi tahlili.
   - Cookie xavfsizlik atributlari tekshiruvi (`Secure`, `HttpOnly`, `SameSite`).
   - Xavfsizlik bali (0-100) va daraja (A+, A, B, C, D, F).
   - JSON formatida yuklab olish va qog'ozga chop etish / PDF eksport.

4. **Xavfsiz Autentifikatsiya va Rollar:**
   - Foydalanuvchilarni ro'yxatdan o'tkazish va kirish.
   - Parollarni xavfsiz xeshlash: **PBKDF2-HMAC-SHA256** (200,000 iteratsiya, kriptografik tasodifiy tuz (salt)).
   - **JWT (JSON Web Token)** asosida seans boshqaruvi.
   - Foydalanuvchilar ma'lumotlarini qat'iy izolyatsiya qilish.
   - Tizimda ro'yxatdan o'tgan birinchi foydalanuvchiga avtomatik `admin` roli beriladi.

5. **Administrator Boshqaruv Markazi (Admin Dashboard):**
   - Ro'yxatdan o'tgan foydalanuvchilar, suhbatlar, xabarlar va skanerlash statistikasi.
   - AI provayder holati va tizim salomatligi monitoringi.
   - Foydalanuvchilar ro'yxati (parollar yoki maxfiy kalitlar hech qachon ko'rsatilmaydi).
   - Xavfsizlik audit jurnali (Audit Logs) monitoringi.

---

## 🛠️ TEXNOLOGIYALAR STACKI

### Backend:
- Python 3.11+ / 3.14
- FastAPI
- Uvicorn
- SQLAlchemy (SQLite)
- Pydantic v2
- HTTPX
- PyJWT
- Python dotenv
- Pytest & Pytest-asyncio

### Frontend:
- HTML5, CSS3, Modern JavaScript (ES6+)
- Maxsus Cyberpunk / Dark minimalistik dizayn (`#080B10`, `#10151D`, `#00E5A8`, `#00A3FF`)
- Mijoz tomonidagi xavfsiz Markdown rendereri
- O'zbek, ingliz va rus tillari uchun dinamik ko'p tilli lug'at

---

## 📁 LOYIHA TUZILISHI

```
cyberai/
├── main.py                     # FastAPI ilovasining asosiy kirish nuqtasi va statik server
├── requirements.txt            # Python kutubxonalari ro'yxati
├── .env.example                # Muhit o'zgaruvchilari namunasi
├── .env                        # Konfiguratsiya fayli
├── .gitignore                  # Git tomonidan e'tiborsiz qoldiriladigan fayllar
├── README.md                   # Loyiha hujjatlari va yo'riqnoma
├── backend/
│   ├── __init__.py
│   ├── config.py               # Loyiha sozlamalari (Pydantic Settings)
│   ├── database.py             # SQLite engine va SessionLocal
│   ├── models.py               # SQLAlchemy ma'lumotlar bazasi modellari
│   ├── schemas.py              # Pydantic validatsiya sxemalari
│   ├── auth.py                 # PBKDF2 xeshlash va JWT token boshqaruvi
│   ├── dependencies.py         # Avtorizatsiya, rollar va rate limiter
│   ├── ai_service.py           # OpenAI, Ollama va Demo AI provayderlari
│   ├── security_analyzer.py    # Statik kod xavfsizligi analizatori
│   ├── website_checker.py      # Non-destruktiv veb-sayt tekshiruvi va SSRF himoyasi
│   └── routers/
│       ├── __init__.py
│       ├── auth.py             # /api/auth yo'nalishlari
│       ├── chat.py             # /api/conversations va /api/chat/stream
│       ├── security.py         # /api/security yo'nalishlari
│       └── admin.py            # /api/admin himoyalangan boshqaruv yo'nalishlari
├── frontend/
│   ├── index.html              # AI Chat asosiy sahifasi
│   ├── login.html              # Kirish sahifasi
│   ├── register.html           # Ro'yxatdan o'tish sahifasi
│   ├── analyzer.html           # Kod xavfsizlik tahlili sahifasi
│   ├── scanner.html            # Veb-sayt xavfsizlik tekshiruvi sahifasi
│   ├── admin.html              # Administrator boshqaruv paneli
│   ├── css/
│   │   └── style.css           # Premium quyuq kiberxavfsizlik UI uslublari
│   └── js/
│       ├── app.js              # Umumiy skriptlar, ko'p tilli lug'at, bildirishnomalar
│       ├── chat.js             # Oqimli chat, tarix, kod nusxalash
│       ├── auth.js             # Autentifikatsiya va validatsiya
│       ├── analyzer.js         # Kod tahlili interfeysi
│       ├── scanner.js          # Sayt skaneri va baho shkalasi
│       └── admin.js            # Administrator statistikasi va jurnallar
└── tests/
    ├── __init__.py
    ├── test_auth.py            # Autentifikatsiya testlari
    ├── test_chat.py            # AI suhbat va cheklovlar testlari
    ├── test_security.py        # Kod tahlili va SSRF himoyasi testlari
    └── test_admin.py           # Admin huquqlari va salomatlik testlari
```

---

## 💻 O'RNATISH VA ISHGA TUSHIRISH YO'RIQNOMASI

Loyiha Windows tizimida **VS Code**, **PyCharm** yoki **Terminal** (PowerShell / CMD) orqali to'liq ishlaydi.

### 1-qadam: Loyiha papkasiga o'tish
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\cyberai
```

### 2-qadam: Python virtual muhitini yaratish (Tavsiya etiladi)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3-qadam: Kutubxonalarni o'rnatish
```powershell
py -m pip install -r requirements.txt
```

### 4-qadam: Muhit sozlamalarini (.env) tekshirish
Loyiha ildizidagi `.env` faylida AI provayderini sozlashingiz mumkin:

```env
# 1. OFFLINE DEMO REJIMI (API kalit talab etilmaydi):
AI_PROVIDER=demo
AI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./cyberai.db
JWT_SECRET_KEY=cyberai-super-secret-jwt-key-2026-secure
DEBUG=true

# 2. AGAR OPENAI / OPENAI-COMPATIBLE ISHLATMOQCHI BO'LSANGIZ:
# AI_PROVIDER=openai
# AI_API_KEY=sk-your-openai-api-key-here
# AI_MODEL=gpt-4o-mini
# AI_BASE_URL=https://api.openai.com/v1

# 3. AGAR MAHALLIY OLLAMA ISHLATMOQCHI BO'LSANGIZ:
# AI_PROVIDER=ollama
# AI_MODEL=llama3
# OLLAMA_BASE_URL=http://localhost:11434
```

> **Eslatma:** Hech qanday API kalit kiritilmagan bo'lsa ham, dastur to'liq ishlaydi va o'rnatilgan kiberxavfsizlik bilimlar bazasiga tayangan **Demo Rejimi**da xizmat ko'rsatadi.

### 5-qadam: Serverni ishga tushirish
FastAPI serveri frontend statik fayllarini to'g'ridan-to'g'ri taqdim etadi (alohida frontend server talab etilmaydi):

```powershell
py main.py
```
yoki Uvicorn orqali:
```powershell
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 6-qadam: Brauzerda ochish
Brauzeringizda quyidagi manzilni oching:
```
http://127.0.0.1:8000
```

1. Yangi hisob ochish uchun `/register` sahifasiga o'ting.
2. Tizimda **birinchi bo'lib ro'yxatdan o'tgan foydalanuvchi avtomatik tarzda ADMIN huquqini** oladi.
3. Administrator paneliga kirish uchun menyudagi `Admin Panel` havolasini bosing yoki `/admin` sahifasiga o'ting.

---

## 🧪 AVTOMATLASHGAN TESTLARNI ISHGA TUSHIRISH

Loyiha uchun barcha asosiy mexanizmlarni tekshiruvchi 23 ta integratsion va unit testlar yozilgan:

```powershell
py -m pytest tests -v
```

### Test qamrovi:
- Foydalanuvchini ro'yxatdan o'tkazish va zaif parollarni rad etish.
- Foydalanuvchi nomi yoki elektron pochta orqali tizimga kirish.
- JWT token yaratilishi va yaroqsiz parollarni bloklash.
- Himoyalangan yo'llar (`/api/auth/me`).
- Suhbat yaratish, ro'yxatlash, qayta nomlash va o'chirish.
- Kiberxavfsizlik etikasi: DDoS yoki zararli buzg'unchilik so'rovlarini rad etish.
- Statik kod tahlili: ochiq AWS kalitlari, private keys va parollarni topish.
- Statik kod tahlili: f-string va string concatenation SQL inyeksiyalarini aniqlash.
- Statik kod tahlili: `eval()`, `os.system()` va `subprocess(shell=True)` ni fosh etish.
- Statik kod tahlili: JavaScript `innerHTML` va `eval` zaifliklarini topish.
- Qat'iy SSRF himoyasi: `localhost`, `127.0.0.1`, `10.0.0.1`, `192.168.1.1` va `169.254.169.254` manziliga so'rovlarni taqiqlash.
- Veb-sayt xavfsizlik tekshiruvida egalik roziligini talab qilish.
- Administrator huquqlari va oddiy foydalanuvchini bloklash.
- Tizim salomatligi tekshiruvi (`/api/health`).

---

## 📡 ASOSIY REST API ENDPOINTLARI

| Metod | Manzil | Tavsif | Ruxsat |
|---|---|---|---|
| `POST` | `/api/auth/register` | Yangi foydalanuvchi ro'yxatdan o'tkazish | Ochiq |
| `POST` | `/api/auth/login` | Tizimga kirish va JWT olish | Ochiq |
| `GET` | `/api/auth/me` | Joriy foydalanuvchi ma'lumotlari | Bearer Token |
| `GET` | `/api/conversations` | Foydalanuvchining barcha suhbatlari | Bearer Token |
| `POST` | `/api/conversations` | Yangi suhbat yaratish | Bearer Token |
| `GET` | `/api/conversations/{id}` | Suhbat va xabarlar tarixi | Bearer Token |
| `PATCH` | `/api/conversations/{id}` | Suhbat nomini o'zgartirish | Bearer Token |
| `DELETE` | `/api/conversations/{id}` | Suhbatni o'chirish | Bearer Token |
| `POST` | `/api/chat` | Sinxron AI javobi olish | Bearer Token |
| `POST` | `/api/chat/stream` | Real vaqtda SSE oqimli AI javobi | Bearer Token |
| `POST` | `/api/security/analyze-code` | Manba kodini statik tahlil qilish | Bearer Token |
| `POST` | `/api/security/analyze-file` | Fayl yuklab kodni tahlil qilish | Bearer Token |
| `POST` | `/api/security/check-website` | Veb-sayt xavfsizlik auditi (SSRF himoyalangan) | Bearer Token |
| `GET` | `/api/security/reports` | Skanerlash hisobotlari ro'yxati | Bearer Token |
| `GET` | `/api/admin/stats` | Administrator statistikasi | Admin |
| `GET` | `/api/admin/users` | Foydalanuvchilar ro'yxati | Admin |
| `GET` | `/api/admin/logs` | Xavfsizlik audit jurnallari | Admin |
| `GET` | `/api/admin/system` | Tizim salomatligi va AI provayder holati | Admin |
| `GET` | `/api/health` | Tizim salomatligi | Ochiq |

---

## 🛡️ XAVFSIZLIK VA ETİK QOIDALAR

- Ushbu platforma faqat **mudofaa (defensive security)**, axborot xavfsizligi ta'limi va xavfsiz dasturiy ta'minot yaratish uchun mo'ljallangan.
- Har qanday ruxsatsiz buzish, tajovuz yoki zarar yetkazish maqsadidagi harakatlar avtomatik filtrlar tomonidan bloklanadi.
- Serverga yuborilgan hech qanday foydalanuvchi kodi serverda ishga tushirilmaydi (faqat statik AST va leksik tahlil o'tkaziladi).
