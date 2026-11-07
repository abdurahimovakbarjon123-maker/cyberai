"""
CYBERAI Defensive Static Code Security Analyzer
Analyzes Python, JavaScript, and HTML code statically without executing it.
Detects hardcoded secrets, SQL injection, dangerous functions, XSS, and weak configurations.
"""
import ast
import re
from typing import List, Dict, Any, Optional

# Secret detection regex patterns
SECRET_PATTERNS = [
    (
        "AWS Access Key ID",
        r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
        "CRITICAL",
        "Secrets",
        "Koddagi AWS Access Key ochiq holda qoldirilgan. Bu tajovuzkorga bulut infratuzilmasiga kirish imkonini beradi.",
        "Maxfiy kalitlarni kodda saqlamang. Ularni muhit o'zgaruvchilari (environment variables) yoki AWS Secrets Manager orqali yuklang.",
        "import os\naws_key = os.getenv('AWS_ACCESS_KEY_ID')"
    ),
    (
        "Hardcoded Private Key",
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "CRITICAL",
        "Secrets",
        "Xususiy kriptografik kalit ochiq matnda saqlanmoqda. Bu shifrlangan ma'lumotlar fosh bo'lishiga olib keladi.",
        "Kalitni fayl tizimida xavfsiz ruxsatlar bilan yoki maxfiy omborlarda (Vault) saqlang.",
        "# Kalitni fayl yoki Vault orqali yuklang\nwith open('/secure/path/key.pem', 'r') as f:\n    private_key = f.read()"
    ),
    (
        "JSON Web Token (JWT)",
        r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",
        "HIGH",
        "Secrets",
        "Koddagi qattiq yozilgan (hardcoded) JWT tokeni aniqlandi. Token orqali ruxsatsiz kirish amalga oshirilishi mumkin.",
        "Statik tokenlardan foydalanmang. Tokenlarni dinamik tarzda autentifikatsiya orqali oling va xavfsiz saqlang.",
        "token = request.headers.get('Authorization').replace('Bearer ', '')"
    ),
    (
        "Generic Secret or API Key",
        r"""(?i)(?:api_key|apikey|secret_key|secret|password|passwd|auth_token)\s*=\s*['\"][a-zA-Z0-9_!@#$%^&*()\-+=]{8,}['\"]""",
        "HIGH",
        "Secrets",
        "Parol, API kalit yoki maxfiy o'zgaruvchi kod ichida ochiq yozilgan.",
        "Maxfiy ma'lumotlarni .env fayllarida yoki tizim muhit o'zgaruvchilarida saqlang.",
        "import os\nSECRET_KEY = os.environ.get('SECRET_KEY')"
    )
]

# Regex patterns for Python SQL Injection fallback
PYTHON_SQL_INJECTION_PATTERNS = [
    (
        r"""(?i)f["'].*?(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).*?\{.+?\}""",
        "CRITICAL",
        "SQL Injection",
        "SQL so'rovi Python f-string orqali dinamik tuzilmoqda. Bu bevosita SQL Injection zaifligini keltirib chiqaradi.",
        "Foydalanuvchi parametrlarini f-string orqali qo'shmang. Parametrlangan so'rovlardan (parameterized queries) foydalaning.",
        "# To'g'rilangan variant:\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
    ),
    (
        r"""(?i)(?:SELECT|INSERT|UPDATE|DELETE)\s+.*['\"]\s*%\s*\(?""",
        "CRITICAL",
        "SQL Injection",
        "SQL so'rovi % operatori orqali string formatlanmoqda. Bu SQL inyeksiyasiga yo'l ochadi.",
        "Parametrlarni ma'lumotlar bazasi drayverining o'z parametrlash mexanizmiga o'tkazing.",
        "cursor.execute('SELECT * FROM users WHERE name = %s', (name,))"
    ),
    (
        r"""(?i)(?:SELECT|INSERT|UPDATE|DELETE)\s+.*['\"]\s*\+\s*\w+""",
        "CRITICAL",
        "SQL Injection",
        "SQL so'rovi string qo'shish (+) orqali dinamik tuzilmoqda.",
        "String concatenation o'rniga parametrlangan so'rovlardan foydalaning.",
        "cursor.execute('SELECT * FROM items WHERE category = %s', (category,))"
    )
]

# Regex patterns for JavaScript
JS_VULNERABILITY_PATTERNS = [
    (
        r"""\beval\s*\(""",
        "HIGH",
        "Dangerous Execution",
        "eval() funksiyasidan foydalanish o'zboshimcha JavaScript kodini ishga tushirish (Arbitrary Code Execution) xavfini tug'diradi.",
        "eval() dan butunlay voz keching. JSON ma'lumotlar uchun JSON.parse() dan foydalaning.",
        "// eval() o'rniga xavfsiz JSON.parse:\nconst data = JSON.parse(jsonString);"
    ),
    (
        r"""document\.write\s*\(""",
        "HIGH",
        "XSS",
        "document.write() DOM-ga to'g'ridan-to'g'ri yozish orqali Cross-Site Scripting (XSS) zaifligini keltirib chiqarishi mumkin.",
        "Zamonaviy DOM API usullari (masalan, createElement yoki textContent) dan foydalaning.",
        "const el = document.createElement('p');\nel.textContent = safeText;\ndocument.body.appendChild(el);"
    ),
    (
        r"""\.innerHTML\s*=""",
        "MEDIUM",
        "XSS",
        "innerHTML orqali ma'lumot kiritish XSS zaifligiga olib kelishi mumkin, ayniqsa kiritilgan matnda HTML teglari bo'lsa.",
        "Faqat matn joylashtirish uchun textContent dan foydalaning yoki HTML kiritish zarur bo'lsa DOMPurify bilan tozalang.",
        "element.textContent = userMessage;"
    ),
    (
        r"""dangerouslySetInnerHTML""",
        "HIGH",
        "XSS",
        "React-da dangerouslySetInnerHTML tozalashsiz ishlatilsa XSS xurujlariga yo'l ochadi.",
        "DOMPurify kabi kutubxonalar yordamida HTML tarkibini tozalang yoki oddiy matn ko'rinishida chiqaring.",
        "<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(cleanHtml) }} />"
    ),
    (
        r"""new\s+Function\s*\(""",
        "HIGH",
        "Dangerous Execution",
        "new Function() eval() kabi dinamik kod bajaradi va xavfsizlikka tahdid soladi.",
        "new Function konstruktsiyasidan foydalanmang.",
        "// Dinamik kod o'rniga oddiy funksiya yoki obyekt lug'atidan foydalaning."
    )
]

# Regex patterns for HTML
HTML_VULNERABILITY_PATTERNS = [
    (
        r"""<form[^>]*method\s*=\s*['\"]get['\"][^>]*>""",
        "MEDIUM",
        "Information Disclosure",
        "Forma ma'lumotlarini (ayniqsa parollarni) GET metodi orqali yuborish ma'lumotlarni URL manzilida va brauzer tarixida fosh qiladi.",
        "Maxfiy ma'lumotlarni uzatuvchi formalar uchun POST metodidan foydalaning.",
        "<form method=\"POST\" action=\"/login\">"
    ),
    (
        r"""target\s*=\s*['\"]_blank['\"](?![^>]*rel\s*=\s*['\"][^'\"]*noopener)""",
        "LOW",
        "Reverse Tabnabbing",
        "target='_blank' bilan ochilgan havolalarda rel='noopener noreferrer' ko'rsatilmagan (Reverse Tabnabbing xavfi).",
        "Havolaga rel=\"noopener noreferrer\" atributini qo'shing.",
        "<a href=\"https://example.com\" target=\"_blank\" rel=\"noopener noreferrer\">Link</a>"
    ),
    (
        r"""<script[^>]*src\s*=\s*['\"]http://""",
        "HIGH",
        "Mixed Content",
        "Skript shifrlanmagan HTTP protokoli orqali yuklanmoqda (Mixed Content / Man-in-the-Middle xavfi).",
        "Barcha tashqi resurslarni faqat HTTPS orqali yuklang.",
        "<script src=\"https://cdn.example.com/lib.js\"></script>"
    )
]


class ASTPythonVisitor(ast.NodeVisitor):
    """
    Static AST visitor for Python code.
    Detects unsafe function calls, debug flags, and insecure patterns.
    """
    def __init__(self, code_lines: List[str]):
        self.code_lines = code_lines
        self.findings = []

    def visit_JoinedStr(self, node: ast.JoinedStr):
        """
        Detects dynamic SQL injection inside Python f-strings.
        """
        has_formatted = any(isinstance(v, ast.FormattedValue) for v in node.values)
        sql_keywords = {"SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER"}
        has_sql = False
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                up = v.value.upper()
                if any(kw in up for kw in sql_keywords):
                    has_sql = True
                    break

        if has_formatted and has_sql:
            line_num = getattr(node, "lineno", 1)
            snippet = self.code_lines[line_num - 1] if 0 < line_num <= len(self.code_lines) else ""
            self.findings.append({
                "name": "SQL Injection in Python f-string",
                "severity": "CRITICAL",
                "category": "SQL Injection",
                "line": line_num,
                "snippet": snippet.strip(),
                "explanation": "SQL so'rovi Python f-string orqali dinamik tuzilmoqda. Bu bevosita SQL Injection zaifligini keltirib chiqaradi.",
                "fix_recommendation": "Foydalanuvchi parametrlarini f-string orqali qo'shmang. Parametrlangan so'rovlardan (parameterized queries) foydalaning.",
                "corrected_code": "# To'g'rilangan variant:\ncursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
            })
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # 1. Check eval() and exec()
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        line_num = getattr(node, "lineno", 1)
        snippet = self.code_lines[line_num - 1] if 0 < line_num <= len(self.code_lines) else ""

        if func_name in ("eval", "exec"):
            self.findings.append({
                "name": f"Dangerous Dynamic Code Execution ({func_name})",
                "severity": "CRITICAL",
                "category": "RCE / Code Execution",
                "line": line_num,
                "snippet": snippet.strip(),
                "explanation": f"`{func_name}()` foydalanuvchi kiritgan har qanday Python kodini serverda bajarishi mumkin (Remote Code Execution).",
                "fix_recommendation": f"`{func_name}()` dan butunlay voz keching. Ma'lumotlarni qayta ishlash uchun xavfsiz parserlardan (masalan, ast.literal_eval yoki json.loads) foydalaning.",
                "corrected_code": "import ast\nsafe_data = ast.literal_eval(user_input)  # Faqat xavfsiz Python literallarini tahlil qiladi"
            })

        # 2. Check subprocess shell=True
        if func_name in ("Popen", "run", "call", "check_output", "check_call"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    self.findings.append({
                        "name": "Command Injection Risk (shell=True)",
                        "severity": "HIGH",
                        "category": "Command Injection",
                        "line": line_num,
                        "snippet": snippet.strip(),
                        "explanation": "`subprocess` chaqiruvida `shell=True` qo'llanilgan. Agar buyruq tarkibiga foydalanuvchi ma'lumotlari kiritilsa, tajovuzkor qo'shimcha tizim buyruqlarini (Command Injection) bajarishi mumkin.",
                        "fix_recommendation": "`shell=False` qiling va buyruq argumentlarini ro'yxat (list) ko'rinishida uzating.",
                        "corrected_code": "import subprocess\nsubprocess.run(['ls', '-la', safe_path], shell=False)"
                    })

        # 3. Check os.system and os.popen
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                if node.func.attr in ("system", "popen"):
                    self.findings.append({
                        "name": f"Dangerous OS Command Execution (os.{node.func.attr})",
                        "severity": "HIGH",
                        "category": "Command Injection",
                        "line": line_num,
                        "snippet": snippet.strip(),
                        "explanation": f"`os.{node.func.attr}()` tizim shell buyruqlarini tekshiruvsiz ishga tushiradi.",
                        "fix_recommendation": "`os.system()` o'rniga `subprocess.run(..., shell=False)` dan argumentlar ro'yxati bilan foydalaning.",
                        "corrected_code": "import subprocess\nsubprocess.run(['ping', '-c', '1', host], check=True)"
                    })

        # 4. Check pickle.loads
        if func_name == "loads":
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id in ("pickle", "_pickle"):
                    self.findings.append({
                        "name": "Insecure Deserialization (pickle.loads)",
                        "severity": "CRITICAL",
                        "category": "Insecure Deserialization",
                        "line": line_num,
                        "snippet": snippet.strip(),
                        "explanation": "`pickle` orqali begona ma'lumotlarni o'qish tajovuzkorga serverda istalgan kodni ishga tushirish imkonini beradi.",
                        "fix_recommendation": "Ishonchsiz ma'lumotlarni deserializatsiya qilish uchun hech qachon `pickle` ishlatmang. JSON yoki Protobuf dan foydalaning.",
                        "corrected_code": "import json\ndata = json.loads(payload)"
                    })

        # 5. Check requests/httpx verify=False
        for kw in node.keywords:
            if kw.arg == "verify" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                self.findings.append({
                    "name": "Disabled SSL Certificate Verification (verify=False)",
                    "severity": "HIGH",
                    "category": "Insecure Transport",
                    "line": line_num,
                    "snippet": snippet.strip(),
                    "explanation": "SSL sertifikatini tekshirish o'chirilgan (`verify=False`). Bu ilovani Man-in-the-Middle (MitM) hujumlariga qarshi mutlaqo himoyasiz qiladi.",
                    "fix_recommendation": "`verify=False` parametrini olib tashlang yoki to'g'ri CA sertifikat yo'lini ko'rsating.",
                    "corrected_code": "response = httpx.get(url, verify=True)"
                })

        # 6. Check weak hashes (md5, sha1)
        if func_name in ("md5", "sha1"):
            self.findings.append({
                "name": f"Weak Cryptographic Hash ({func_name.upper()})",
                "severity": "MEDIUM",
                "category": "Cryptography",
                "line": line_num,
                "snippet": snippet.strip(),
                "explanation": f"{func_name.upper()} algoritmi kolliziyaga chidamsiz va parollar yoki xavfsizlik imzolash uchun eskirgan hisoblanadi.",
                "fix_recommendation": "Parollar uchun Argon2id yoki PBKDF2-SHA256, ma'lumotlar butunligi uchun SHA-256 yoki SHA-3 dan foydalaning.",
                "corrected_code": "import hashlib\nhash_val = hashlib.sha256(data).hexdigest()"
            })

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # Check debug=True or DEBUG=True
        line_num = getattr(node, "lineno", 1)
        snippet = self.code_lines[line_num - 1] if 0 < line_num <= len(self.code_lines) else ""
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.upper() in ("DEBUG", "APP_DEBUG"):
                if isinstance(node.value, ast.Constant) and node.value.value is True:
                    self.findings.append({
                        "name": "Debug Mode Enabled in Code",
                        "severity": "MEDIUM",
                        "category": "Configuration",
                        "line": line_num,
                        "snippet": snippet.strip(),
                        "explanation": "DEBUG rejimining yoqiq qoldirilishi xatolik sahifalarida maxfiy kalitlar, stack trace va server muhitini fosh etadi.",
                        "fix_recommendation": "Ishlab chiqarish (production) muhitida DEBUG parametrini har doim `False` qilib belgilang.",
                        "corrected_code": "import os\nDEBUG = os.getenv('DEBUG', 'false').lower() == 'true'"
                    })
        self.generic_visit(node)


def analyze_code_security(code: str, language: Optional[str] = "python", filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point for static code analysis.
    Safely parses code and applies rule checks.
    """
    lang = (language or "python").lower().strip()
    code_lines = code.split("\n")
    findings: List[Dict[str, Any]] = []

    # 1. Universal Secret Scan
    for line_idx, line in enumerate(code_lines, start=1):
        for pattern_name, regex, severity, category, expl, fix, corr in SECRET_PATTERNS:
            match = re.search(regex, line)
            if match:
                snippet_text = line.strip()
                if len(snippet_text) > 120:
                    snippet_text = snippet_text[:117] + "..."
                findings.append({
                    "name": pattern_name,
                    "severity": severity,
                    "category": category,
                    "line": line_idx,
                    "snippet": snippet_text,
                    "explanation": expl,
                    "fix_recommendation": fix,
                    "corrected_code": corr
                })

    # 2. Python specific analysis
    if lang == "python" or lang.endswith(".py"):
        # AST analysis
        try:
            tree = ast.parse(code)
            visitor = ASTPythonVisitor(code_lines)
            visitor.visit(tree)
            findings.extend(visitor.findings)
        except SyntaxError as se:
            findings.append({
                "name": "Syntax Error in Python Code",
                "severity": "INFO",
                "category": "Syntax",
                "line": se.lineno or 1,
                "snippet": se.text.strip() if se.text else "",
                "explanation": f"Kodni AST tahlilidan o'tkazishda sintaktik xatolik aniqlandi: {se.msg}",
                "fix_recommendation": "Koddagi sintaktik xatolikni to'g'rilang.",
                "corrected_code": None
            })

        # Regex SQL Injection check fallback
        for line_idx, line in enumerate(code_lines, start=1):
            for regex, severity, category, expl, fix, corr in PYTHON_SQL_INJECTION_PATTERNS:
                if re.search(regex, line):
                    findings.append({
                        "name": "Unsafe Dynamic SQL Query Construction",
                        "severity": severity,
                        "category": category,
                        "line": line_idx,
                        "snippet": line.strip(),
                        "explanation": expl,
                        "fix_recommendation": fix,
                        "corrected_code": corr
                    })

    # 3. JavaScript specific analysis
    elif lang in ("javascript", "js", "typescript", "ts") or lang.endswith((".js", ".ts")):
        for line_idx, line in enumerate(code_lines, start=1):
            for regex, severity, category, expl, fix, corr in JS_VULNERABILITY_PATTERNS:
                if re.search(regex, line):
                    findings.append({
                        "name": f"JavaScript Security Issue ({category})",
                        "severity": severity,
                        "category": category,
                        "line": line_idx,
                        "snippet": line.strip(),
                        "explanation": expl,
                        "fix_recommendation": fix,
                        "corrected_code": corr
                    })

    # 4. HTML specific analysis
    elif lang in ("html", "htm") or lang.endswith((".html", ".htm")):
        for line_idx, line in enumerate(code_lines, start=1):
            for regex, severity, category, expl, fix, corr in HTML_VULNERABILITY_PATTERNS:
                if re.search(regex, line):
                    findings.append({
                        "name": f"HTML Insecure Configuration ({category})",
                        "severity": severity,
                        "category": category,
                        "line": line_idx,
                        "snippet": line.strip(),
                        "explanation": expl,
                        "fix_recommendation": fix,
                        "corrected_code": corr
                    })

    # Deduplicate findings by (name, line)
    seen = set()
    deduped_findings = []
    for f in findings:
        key = (f["name"], f.get("line"))
        if key not in seen:
            seen.add(key)
            deduped_findings.append(f)

    # Compute Security Score (100 base)
    score = 100
    for f in deduped_findings:
        sev = f["severity"].upper()
        if sev == "CRITICAL":
            score -= 25
        elif sev == "HIGH":
            score -= 15
        elif sev == "MEDIUM":
            score -= 8
        elif sev == "LOW":
            score -= 4
        elif sev == "INFO":
            score -= 2

    score = max(0, min(100, score))

    # Risk level classification
    if score >= 90:
        risk_level = "SECURE"
    elif score >= 75:
        risk_level = "LOW"
    elif score >= 55:
        risk_level = "MEDIUM"
    elif score >= 35:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    target_name = filename or f"Snippet ({lang.upper()})"

    return {
        "target": target_name,
        "score": score,
        "risk_level": risk_level,
        "findings_count": len(deduped_findings),
        "findings": deduped_findings
    }
