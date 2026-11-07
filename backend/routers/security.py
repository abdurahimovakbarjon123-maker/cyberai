"""
CYBERAI Security Router
Handles static code security analysis and non-destructive website security audits.
"""
import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, SecurityReport
from backend.schemas import (
    CodeAnalyzeRequest,
    CodeAnalyzeResponse,
    WebsiteCheckRequest,
    WebsiteCheckResponse,
    SecurityReportListItem
)
from backend.dependencies import get_current_user, log_audit_event, check_rate_limit
from backend.security_analyzer import analyze_code_security
from backend.website_checker import check_website_security, SSRFValidationError

router = APIRouter(prefix="/api/security", tags=["Defensive Security"])


@router.post("/analyze-code", response_model=CodeAnalyzeResponse)
def analyze_code_endpoint(
    req: CodeAnalyzeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Performs defensive static analysis on submitted code string.
    Never executes submitted code.
    """
    client_ip = request.client.host if request.client else "unknown"

    analysis = analyze_code_security(
        code=req.code,
        language=req.language or "python",
        filename=req.filename
    )

    report_id = str(uuid.uuid4())
    summary = f"Xavf darajasi: {analysis['risk_level']}, Ball: {analysis['score']}/100, Topilganlar: {analysis['findings_count']}"

    report = SecurityReport(
        id=report_id,
        user_id=current_user.id,
        report_type="code_analysis",
        target=analysis["target"],
        summary=summary,
        score=analysis["score"],
        findings_json=json.dumps(analysis)
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(
        db,
        "code_scan",
        current_user.id,
        client_ip,
        "success",
        f"Score: {analysis['score']}, Findings: {analysis['findings_count']}"
    )

    return CodeAnalyzeResponse(
        id=report.id,
        target=analysis["target"],
        score=analysis["score"],
        risk_level=analysis["risk_level"],
        findings_count=analysis["findings_count"],
        findings=analysis["findings"],
        created_at=report.created_at
    )


@router.post("/analyze-file", response_model=CodeAnalyzeResponse)
async def analyze_file_endpoint(
    file: UploadFile = File(...),
    language: Optional[str] = Form("python"),
    request: Request = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Upload and analyze source code files (Python, JS, HTML).
    File is read as UTF-8 text and statically scanned.
    """
    client_ip = request.client.host if request and request.client else "unknown"

    # Enforce safe file size limit (max 1MB for source files)
    contents = await file.read()
    if len(contents) > 1_048_576:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fayl hajmi 1MB dan oshmasligi kerak."
        )

    try:
        code_text = contents.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faqat UTF-8 matnli manba kod fayllari (.py, .js, .html, .txt) qabul qilinadi."
        )

    # Determine language from extension if not specified
    fname = file.filename or "unknown"
    if fname.endswith(".py"):
        lang = "python"
    elif fname.endswith((".js", ".ts")):
        lang = "javascript"
    elif fname.endswith((".html", ".htm")):
        lang = "html"
    else:
        lang = language or "python"

    analysis = analyze_code_security(code_text, language=lang, filename=fname)

    report_id = str(uuid.uuid4())
    summary = f"Fayl: {fname}, Xavf: {analysis['risk_level']}, Ball: {analysis['score']}/100"

    report = SecurityReport(
        id=report_id,
        user_id=current_user.id,
        report_type="code_analysis",
        target=fname,
        summary=summary,
        score=analysis["score"],
        findings_json=json.dumps(analysis)
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(db, "file_scan", current_user.id, client_ip, "success", f"File: {fname}")

    return CodeAnalyzeResponse(
        id=report.id,
        target=fname,
        score=analysis["score"],
        risk_level=analysis["risk_level"],
        findings_count=analysis["findings_count"],
        findings=analysis["findings"],
        created_at=report.created_at
    )


@router.post("/check-website", response_model=WebsiteCheckResponse)
async def check_website_endpoint(
    req: WebsiteCheckRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Performs strictly authorized, non-destructive website security audits.
    Enforces SSRF prevention, timeouts, and authorization verification.
    """
    client_ip = request.client.host if request.client else "unknown"

    try:
        audit_result = await check_website_security(req.url, req.confirm_authorization)
    except SSRFValidationError as s_err:
        log_audit_event(db, "ssrf_blocked", current_user.id, client_ip, "blocked", f"Target: {req.url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Xavfsizlik cheklovi (SSRF): {str(s_err)}"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sayt xavfsizligini tekshirishda xatolik: {str(e)}"
        )

    report_id = str(uuid.uuid4())
    summary = f"Baho: {audit_result['grade']}, Ball: {audit_result['score']}/100, HTTPS: {audit_result['https_valid']}"

    report = SecurityReport(
        id=report_id,
        user_id=current_user.id,
        report_type="website_check",
        target=audit_result["target"],
        summary=summary,
        score=audit_result["score"],
        findings_json=json.dumps(audit_result)
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    log_audit_event(
        db,
        "website_scan",
        current_user.id,
        client_ip,
        "success",
        f"Target: {audit_result['target']}, Score: {audit_result['score']}"
    )

    return WebsiteCheckResponse(
        id=report.id,
        target=audit_result["target"],
        score=audit_result["score"],
        grade=audit_result["grade"],
        https_valid=audit_result["https_valid"],
        response_time_ms=audit_result.get("response_time_ms"),
        server_info=audit_result.get("server_info"),
        headers=audit_result["headers"],
        cookies=audit_result["cookies"],
        findings=audit_result["findings"],
        recommendations=audit_result["recommendations"],
        created_at=report.created_at
    )


@router.get("/reports", response_model=List[SecurityReportListItem])
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns history of security reports for the authenticated user.
    """
    reports = (
        db.query(SecurityReport)
        .filter(SecurityReport.user_id == current_user.id)
        .order_by(SecurityReport.created_at.desc())
        .limit(50)
        .all()
    )
    return [SecurityReportListItem.model_validate(r) for r in reports]


@router.get("/reports/{report_id}")
def get_report_detail(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full JSON findings for a specific report.
    """
    report = db.query(SecurityReport).filter(
        SecurityReport.id == report_id,
        SecurityReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hisobot topilmadi."
        )

    try:
        data = json.loads(report.findings_json)
    except Exception:
        data = {}

    data["id"] = report.id
    data["created_at"] = report.created_at.isoformat()
    data["report_type"] = report.report_type
    return data


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a user's security report.
    """
    report = db.query(SecurityReport).filter(
        SecurityReport.id == report_id,
        SecurityReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hisobot topilmadi."
        )

    db.delete(report)
    db.commit()
    return None
