"""
CYBERAI Website Security Checker
Performs strictly non-destructive security header, SSL, and cookie analysis with hardened SSRF protection.
"""
import time
import socket
import ipaddress
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
import httpx

# List of banned IP networks for SSRF protection
BANNED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),          # Private RFC1918
    ipaddress.ip_network("100.64.0.0/10"),       # Shared Address Space
    ipaddress.ip_network("127.0.0.0/8"),         # Loopback
    ipaddress.ip_network("169.254.0.0/16"),       # Link-Local / Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),       # Private RFC1918
    ipaddress.ip_network("192.0.0.0/24"),        # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),        # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),      # 6to4 Relay Anycast
    ipaddress.ip_network("192.168.0.0/16"),      # Private RFC1918
    ipaddress.ip_network("198.18.0.0/15"),       # Network Interconnect Device Benchmark
    ipaddress.ip_network("198.51.100.0/24"),     # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),      # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),         # Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # Reserved
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6 banned ranges
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),             # IPv6 Loopback
    ipaddress.ip_network("::ffff:0:0/96"),       # IPv4-mapped IPv6
    ipaddress.ip_network("64:ff9b::/96"),        # IPv4-IPv6 translation
    ipaddress.ip_network("100::/64"),            # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),       # Documentation
    ipaddress.ip_network("fc00::/7"),            # Unique Local Unicast (ULA)
    ipaddress.ip_network("fe80::/10"),           # Link-Local Unicast
    ipaddress.ip_network("ff00::/8"),            # Multicast
]

FORBIDDEN_HOSTNAMES = {
    "localhost", "localhost.localdomain", "127.0.0.1", "::1",
    "metadata.google.internal", "metadata", "instance-data",
    "router.local", "routerlogin.net", "broadcasthost"
}


class SSRFValidationError(ValueError):
    """Raised when URL resolves to internal, private, or loopback network."""
    pass


def validate_and_resolve_url(url_string: str) -> Tuple[str, str, List[str]]:
    """
    Validates URL scheme, hostname, resolves DNS, and verifies no resolved IP is private or restricted.
    Returns (cleaned_url, hostname, resolved_ips).
    """
    clean_url = url_string.strip()
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        clean_url = "https://" + clean_url

    parsed = urllib.parse.urlparse(clean_url)

    if parsed.scheme not in ("http", "https"):
        raise SSRFValidationError("Faqat HTTP yoki HTTPS protokollariga ruxsat beriladi.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFValidationError("Noto'g'ri URL manzil: host ko'rsatilmagan.")

    hostname_lower = hostname.lower()

    if hostname_lower in FORBIDDEN_HOSTNAMES or hostname_lower.endswith((".local", ".internal", ".localhost", ".onion")):
        raise SSRFValidationError("Lokal, ichki yoki metadata domenlariga kirish xavfsizlik nuqtai nazaridan taqiqlangan.")

    # Resolve hostname to all IPs
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        addr_info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise SSRFValidationError(f"Domen nomini aniqlab bo'lmadi (DNS lookup failed): {str(e)}")

    resolved_ips = []
    for family, _, _, _, sockaddr in addr_info:
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFValidationError(f"Yaroqsiz IP manzil: {ip_str}")

        # Check against banned networks
        for banned in BANNED_NETWORKS:
            if ip_obj in banned:
                raise SSRFValidationError(
                    f"Xavfsizlik himoyasi (SSRF): Ichki yoki cheklangan IP manziliga ({ip_str}) kirish qat'iyan taqiqlangan."
                )

        # Check IPv4 mapped in IPv6
        if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
            mapped_v4 = ip_obj.ipv4_mapped
            for banned in BANNED_NETWORKS:
                if mapped_v4 in banned:
                    raise SSRFValidationError(f"SSRF cheklovi: Ichki IPv4-mapped manzil ({mapped_v4}) taqiqlangan.")

        if ip_str not in resolved_ips:
            resolved_ips.append(ip_str)

    if not resolved_ips:
        raise SSRFValidationError("Domen uchun birorta ham faol tashqi IP manzil topilmadi.")

    return clean_url, hostname, resolved_ips


async def check_website_security(url_string: str, confirm_authorization: bool = True) -> Dict[str, Any]:
    """
    Executes non-destructive defensive checks against authorized websites:
    - SSRF prevention & DNS validation
    - HTTPS enforcement & connection test
    - Security headers analysis (HSTS, CSP, X-Frame-Options, etc.)
    - Cookie security flags (Secure, HttpOnly, SameSite)
    - Server exposure headers
    - Security scoring (0 - 100) & Grade (A+ to F)
    """
    if not confirm_authorization:
        raise ValueError("Tekshiruvni bajarish uchun domenga egalik yoki vakolat tasdiqlanishi shart!")

    clean_url, hostname, resolved_ips = validate_and_resolve_url(url_string)

    headers_results: List[Dict[str, Any]] = []
    cookies_results: List[Dict[str, Any]] = []
    findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    score = 100
    https_valid = clean_url.startswith("https://")
    server_info = None
    response_time_ms = 0.0

    # Custom redirect-handling client to prevent SSRF through redirect chains
    timeout = httpx.Timeout(5.0, connect=5.0)

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=True, follow_redirects=False) as client:
            current_target = clean_url
            max_redirects = 4
            redirect_count = 0
            response = None

            while redirect_count < max_redirects:
                # Validate current_target on each hop
                validate_and_resolve_url(current_target)

                resp = await client.get(current_target, headers={"User-Agent": "CYBERAI-Security-Auditor/1.0 (+https://cyberai.local)"})
                response = resp

                if resp.is_redirect and "location" in resp.headers:
                    redirect_count += 1
                    location = resp.headers["location"]
                    # Handle relative redirect URLs
                    current_target = urllib.parse.urljoin(current_target, location)
                else:
                    break

            response_time_ms = round((time.time() - start_time) * 1000, 2)

    except SSRFValidationError as s_err:
        raise s_err
    except httpx.ConnectTimeout:
        raise ValueError("Serverga ulanish vaqti tugadi (Timeout). Server javob bermadi.")
    except httpx.ConnectError as ce:
        raise ValueError(f"Serverga ulanib bo'lmadi: {str(ce)}")
    except Exception as e:
        raise ValueError(f"Tekshirishda kutilmagan xatolik yuz berdi: {str(e)}")

    if not response:
        raise ValueError("Serverdan javob olinmadi.")

    resp_headers = {k.lower(): v for k, v in response.headers.items()}

    # Check 1: HTTPS & Transport Security
    if not clean_url.startswith("https://"):
        score -= 25
        findings.append({
            "title": "Shifrlanmagan HTTP Protokoli",
            "severity": "HIGH",
            "detail": "Sayt HTTPS o'rniga oddiy HTTP orqali ochilmoqda. Foydalanuvchi ma'lumotlari shifrlanmagan holda uzatiladi."
        })
        recommendations.append("Saytga bepul Let's Encrypt yoki tijorat SSL/TLS sertifikatini o'rnating va barcha so'rovlarni HTTPS ga yo'naltiring.")

    # Check 2: Strict-Transport-Security (HSTS)
    hsts = resp_headers.get("strict-transport-security")
    if hsts:
        headers_results.append({
            "header": "Strict-Transport-Security",
            "status": "present",
            "value": hsts,
            "description": "Brauzerni faqat HTTPS orqali bog'lanishga majbur qiladi (HSTS).",
            "recommendation": "To'g'ri sozlangan."
        })
    else:
        score -= 15
        headers_results.append({
            "header": "Strict-Transport-Security",
            "status": "missing",
            "value": None,
            "description": "HSTS sarlavhasi yo'q. SSL Striping hujumlari xavfi mavjud.",
            "recommendation": "Quyidagi sarlavhani qo'shing: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`"
        })
        recommendations.append("HSTS (Strict-Transport-Security) sarlavhasini faollashtiring.")

    # Check 3: Content-Security-Policy (CSP)
    csp = resp_headers.get("content-security-policy")
    if csp:
        has_unsafe = "unsafe-inline" in csp or "unsafe-eval" in csp
        if has_unsafe:
            score -= 5
            headers_results.append({
                "header": "Content-Security-Policy",
                "status": "insecure",
                "value": csp[:100] + "..." if len(csp) > 100 else csp,
                "description": "CSP mavjud, ammo 'unsafe-inline' yoki 'unsafe-eval' kabi zaif direktivalarni o'z ichiga oladi.",
                "recommendation": "'unsafe-inline' dan voz keching, skriptlar uchun nonce yoki hash lardan foydalaning."
            })
        else:
            headers_results.append({
                "header": "Content-Security-Policy",
                "status": "present",
                "value": csp[:100] + "..." if len(csp) > 100 else csp,
                "description": "Qat'iy Content Security Policy o'rnatilgan.",
                "recommendation": "Mukammal sozlangan."
            })
    else:
        score -= 20
        headers_results.append({
            "header": "Content-Security-Policy",
            "status": "missing",
            "value": None,
            "description": "Content-Security-Policy (CSP) sarlavhasi yo'q. Bu XSS va ma'lumotlar sizib chiqishi xavfini oshiradi.",
            "recommendation": "Sayt resurslari uchun qat'iy CSP sarlavhasini sozlang: `default-src 'self'`."
        })
        recommendations.append("XSS xurujlariga qarshi Content-Security-Policy (CSP) sarlavhasini joriy eting.")

    # Check 4: X-Frame-Options (Clickjacking)
    xfo = resp_headers.get("x-frame-options")
    if xfo and xfo.upper() in ("DENY", "SAMEORIGIN"):
        headers_results.append({
            "header": "X-Frame-Options",
            "status": "present",
            "value": xfo,
            "description": "Sahifani iframe ichida ko'rsatishni cheklaydi (Clickjacking himoyasi).",
            "recommendation": "To'g'ri sozlangan."
        })
    else:
        score -= 10
        headers_results.append({
            "header": "X-Frame-Options",
            "status": "missing" if not xfo else "insecure",
            "value": xfo,
            "description": "X-Frame-Options sarlavhasi yo'q yoki noto'g'ri. Sayt Clickjacking hujumlariga moyil bo'lishi mumkin.",
            "recommendation": "`X-Frame-Options: DENY` yoki `SAMEORIGIN` qiymatini sozlang."
        })
        recommendations.append("Clickjacking hujumlarining oldini olish uchun X-Frame-Options sarlavhasini qo'shing.")

    # Check 5: X-Content-Type-Options (MIME Sniffing)
    xcto = resp_headers.get("x-content-type-options")
    if xcto and "nosniff" in xcto.lower():
        headers_results.append({
            "header": "X-Content-Type-Options",
            "status": "present",
            "value": xcto,
            "description": "Brauzer fayl turini o'zboshimcha o'zgartirishini (MIME sniffing) taqiqlaydi.",
            "recommendation": "To'g'ri sozlangan."
        })
    else:
        score -= 8
        headers_results.append({
            "header": "X-Content-Type-Options",
            "status": "missing",
            "value": xcto,
            "description": "X-Content-Type-Options: nosniff mavjud emas.",
            "recommendation": "`X-Content-Type-Options: nosniff` sarlavhasini qo'shing."
        })
        recommendations.append("MIME-sniffing zaifligini bartaraf etish uchun `X-Content-Type-Options: nosniff` ni qo'shing.")

    # Check 6: Referrer-Policy
    ref_pol = resp_headers.get("referrer-policy")
    if ref_pol:
        headers_results.append({
            "header": "Referrer-Policy",
            "status": "present",
            "value": ref_pol,
            "description": "Havolalar orqali o'tganda Referer sarlavhasida qanday ma'lumot uzatilishini nazorat qiladi.",
            "recommendation": "To'g'ri sozlangan."
        })
    else:
        score -= 5
        headers_results.append({
            "header": "Referrer-Policy",
            "status": "missing",
            "value": None,
            "description": "Referrer-Policy ko'rsatilmagan.",
            "recommendation": "`Referrer-Policy: strict-origin-when-cross-origin` yoki `no-referrer` o'rnating."
        })

    # Check 7: Permissions-Policy
    perm_pol = resp_headers.get("permissions-policy")
    if perm_pol:
        headers_results.append({
            "header": "Permissions-Policy",
            "status": "present",
            "value": perm_pol[:80] + "..." if len(perm_pol) > 80 else perm_pol,
            "description": "Brauzer imkoniyatlaridan (kamera, mikrofon, geolokatsiya) ruxsatsiz foydalanishni cheklaydi.",
            "recommendation": "To'g'ri sozlangan."
        })
    else:
        headers_results.append({
            "header": "Permissions-Policy",
            "status": "missing",
            "value": None,
            "description": "Permissions-Policy yo'q.",
            "recommendation": "`Permissions-Policy: geolocation=(), camera=(), microphone=()` tavsiya etiladi."
        })

    # Check 8: Information Disclosure (Server & X-Powered-By)
    server_header = resp_headers.get("server")
    x_powered_by = resp_headers.get("x-powered-by")
    if server_header:
        server_info = server_header
        if any(c.isdigit() for c in server_header):
            score -= 5
            findings.append({
                "title": "Server Versiyasi Fosh Qilingan (Information Disclosure)",
                "severity": "LOW",
                "detail": f"Server sarlavhasida aniq versiya ko'rsatilgan: {server_header}"
            })
            recommendations.append("Server dasturiy ta'minoti versiyasini (Apache, Nginx va h.k.) sarlavhalarda yashiring.")

    if x_powered_by:
        score -= 5
        findings.append({
            "title": "X-Powered-By Texnologiya Fosh Qilingan",
            "severity": "LOW",
            "detail": f"X-Powered-By orqali server backend texnologiyasi ma'lum: {x_powered_by}"
        })
        recommendations.append("X-Powered-By sarlavhasini veb-server konfiguratsiyasida o'chirib qo'ying.")

    # Check 9: Cookies Analysis
    raw_cookies = response.headers.get_list("set-cookie")
    for cookie_header in raw_cookies:
        parts = [p.strip() for p in cookie_header.split(";")]
        name_val = parts[0].split("=", 1)
        c_name = name_val[0]
        flags = [p.lower() for p in parts[1:]]

        is_secure = "secure" in flags
        is_httponly = "httponly" in flags
        samesite_val = None
        for f in flags:
            if f.startswith("samesite="):
                samesite_val = f.split("=")[1].capitalize()

        issues = []
        if not is_secure:
            score -= 5
            issues.append("Secure bayrog'i yo'q (cookie shifrlanmagan ulanishda o'g'irlanishi mumkin)")
        if not is_httponly:
            score -= 5
            issues.append("HttpOnly bayrog'i yo'q (JavaScript orqali XSS orqali o'qilishi mumkin)")
        if not samesite_val:
            score -= 3
            issues.append("SameSite atributi belgilanmagan (CSRF xavfi)")

        cookies_results.append({
            "name": c_name,
            "secure": is_secure,
            "httponly": is_httponly,
            "samesite": samesite_val or "Ko'rsatilmagan",
            "issues": issues
        })

    # Calculate final score and grade
    score = max(0, min(100, score))
    if score >= 95:
        grade = "A+"
    elif score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 55:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {
        "target": clean_url,
        "score": score,
        "grade": grade,
        "https_valid": https_valid,
        "response_time_ms": response_time_ms,
        "server_info": server_info,
        "headers": headers_results,
        "cookies": cookies_results,
        "findings": findings,
        "recommendations": recommendations,
        "resolved_ips": resolved_ips
    }
