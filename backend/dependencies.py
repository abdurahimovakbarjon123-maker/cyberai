"""
CYBERAI FastAPI Dependencies
Implements authentication dependencies, user isolation, and rate limiting.
"""
import time
from collections import defaultdict
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, AuditLog
from backend.auth import decode_access_token
from backend.config import settings

# HTTP Bearer scheme
security_bearer = HTTPBearer(auto_error=False)

# Simple thread-safe in-memory rate limiter: ip -> list of timestamps
_rate_limit_records = defaultdict(list)


def check_rate_limit(request: Request):
    """
    In-memory sliding window rate limiter.
    Limits requests to settings.RATE_LIMIT_PER_MINUTE per minute per client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60.0

    # Prune old timestamps
    timestamps = [t for t in _rate_limit_records[client_ip] if t > window_start]
    if len(timestamps) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="So'rovlar soni me'yordan oshdi. Iltimos, bir daqiqadan so'ng qayta urinib ko'ring (Rate limit exceeded)."
        )

    timestamps.append(now)
    _rate_limit_records[client_ip] = timestamps


def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[str]:
    """
    Extracts Bearer token from header or query param (?token=...).
    """
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    # Fallback to query param (useful for EventSource / SSE if needed)
    token_param = request.query_params.get("token")
    if token_param:
        return token_param
    return None


def get_current_user(
    token: Optional[str] = Depends(get_token_from_request),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that authenticates the user via JWT.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kirish talab etiladi. Token topilmadi (Authentication required)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yaroqsiz yoki muddati o'tgan token (Invalid or expired token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ma'lumotlari xato",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi tizimda topilmadi",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi hisobi faol emas",
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency ensuring the authenticated user has 'admin' privileges.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ushbu amalni bajarish uchun administrator huquqi talab etiladi",
        )
    return current_user


def log_audit_event(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    status: str = "success",
    details: Optional[str] = None
):
    """
    Records security-relevant audit logs into database.
    """
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            status=status,
            details=details[:500] if details else None
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
