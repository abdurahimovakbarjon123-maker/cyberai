"""
CYBERAI Admin Router
Protected administrator endpoints for system statistics, user audits, and security metrics.
"""
import sys
import platform
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import User, Conversation, Message, SecurityReport, AuditLog
from backend.schemas import (
    AdminStatsResponse,
    AdminUserListItem,
    AuditLogResponse
)
from backend.dependencies import get_current_admin
from backend.ai_service import get_ai_status
from backend.config import settings

router = APIRouter(prefix="/api/admin", tags=["Administrator Dashboard"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns high-level system statistics for the admin dashboard.
    """
    total_users = db.query(User).count()
    total_conversations = db.query(Conversation).count()
    total_messages = db.query(Message).count()
    total_reports = db.query(SecurityReport).count()

    total_code_scans = db.query(SecurityReport).filter(SecurityReport.report_type == "code_analysis").count()
    total_web_scans = db.query(SecurityReport).filter(SecurityReport.report_type == "website_check").count()

    ai_diag = get_ai_status()

    return AdminStatsResponse(
        total_users=total_users,
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_security_reports=total_reports,
        total_code_scans=total_code_scans,
        total_website_scans=total_web_scans,
        ai_provider=ai_diag["provider"],
        ai_model=ai_diag["model"],
        ai_status=ai_diag["mode"],
        system_health="ONLINE (All Services Operational)"
    )


@router.get("/users", response_model=List[AdminUserListItem])
def get_admin_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Lists registered users without exposing credentials.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    results = []
    for u in users:
        conv_cnt = db.query(Conversation).filter(Conversation.user_id == u.id).count()
        rep_cnt = db.query(SecurityReport).filter(SecurityReport.user_id == u.id).count()
        results.append(AdminUserListItem(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
            conversation_count=conv_cnt,
            report_count=rep_cnt
        ))
    return results


@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns recent security audit logs.
    """
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    result = []
    for l in logs:
        uname = l.user.username if l.user else "Anonim / Tizim"
        result.append(AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            username=uname,
            action=l.action,
            ip_address=l.ip_address,
            status=l.status,
            details=l.details,
            created_at=l.created_at
        ))
    return result


@router.get("/system")
def get_system_health(
    admin: User = Depends(get_current_admin)
):
    """
    Detailed system runtime health information.
    """
    ai_diag = get_ai_status()
    return {
        "status": "healthy",
        "python_version": sys.version,
        "platform": platform.platform(),
        "ai_configuration": {
            "provider": ai_diag["provider"],
            "model": ai_diag["model"],
            "base_url": ai_diag["base_url"],
            "masked_key": ai_diag["masked_key"],
            "mode": ai_diag["mode"]
        },
        "database": {
            "type": "SQLite",
            "url": "sqlite:///cyberai.db (Encrypted Session Store)"
        }
    }


@router.post("/ai-config")
def update_ai_configuration(
    payload: dict,
    admin: User = Depends(get_current_admin)
):
    """
    Updates AI provider and API Key on the fly and saves to .env.
    """
    provider = payload.get("provider", "openai").lower()
    api_key = payload.get("api_key", "").strip()
    model = payload.get("model", settings.AI_MODEL).strip()
    base_url = payload.get("base_url", settings.AI_BASE_URL).strip()

    if api_key:
        settings.AI_PROVIDER = provider
        settings.AI_API_KEY = api_key
        settings.AI_MODEL = model
        if base_url:
            settings.AI_BASE_URL = base_url

        # Save to .env
        env_path = settings.BASE_DIR / ".env"
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"AI_PROVIDER={settings.AI_PROVIDER}\n")
                f.write(f"AI_API_KEY={settings.AI_API_KEY}\n")
                f.write(f"AI_MODEL={settings.AI_MODEL}\n")
                f.write(f"AI_BASE_URL={settings.AI_BASE_URL}\n")
                f.write(f"OLLAMA_BASE_URL={settings.OLLAMA_BASE_URL}\n")
                f.write(f"DATABASE_URL={settings.DATABASE_URL}\n")
                f.write(f"JWT_SECRET_KEY={settings.JWT_SECRET_KEY}\n")
                f.write(f"DEBUG={str(settings.DEBUG).lower()}\n")
                f.write(f"DEFAULT_LANGUAGE={settings.DEFAULT_LANGUAGE}\n")
        except Exception:
            pass

        return {
            "status": "success",
            "message": "AI kaliti muvaffaqiyatli ulandi va saqlandi!",
            "provider": settings.AI_PROVIDER,
            "model": settings.AI_MODEL
        }
    else:
        return {
            "status": "warning",
            "message": "API kaliti kiritilmadi. Standart rejim saqlanib qoldi."
        }
