"""
CYBERAI Pydantic Schemas for Request Validation and Responses
"""
import re
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# ==========================================
# Auth & User Schemas
# ==========================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Foydalanuvchi nomi")
    email: str = Field(..., description="Elektron pochta manzili")
    password: str = Field(..., min_length=8, max_length=128, description="Kamida 8 belgidan iborat xavfsiz parol")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        clean = v.strip()
        if not clean.isalnum() and "_" not in clean and "-" not in clean:
            raise ValueError("Foydalanuvchi nomida faqat harflar, raqamlar, '_' va '-' bo'lishi mumkin")
        return clean

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError("To'g'ri elektron pochta manzilini kiriting (masalan: nom@misol.uz)")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgidan iborat bo'lishi kerak")
        has_alpha = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_alpha and has_digit):
            raise ValueError("Parol kamida bitta harf va bitta raqamdan iborat bo'lishi shart")
        return v


class UserLogin(BaseModel):
    username: str = Field(..., description="Foydalanuvchi nomi yoki elektron pochta")
    password: str = Field(..., description="Parol")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==========================================
# Chat & Conversation Schemas
# ==========================================

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: Optional[str] = Field("Ushbu rasmni tahlil qiling", max_length=15000, description="Xabar matni")
    image_data: Optional[str] = Field(None, description="Base64 rasm kodi yoki Data URL (data:image/...)")
    conversation_id: Optional[str] = Field(None, description="Mavjud suhbat identifikatori (agar yangi bo'lsa bo'sh)")
    model: Optional[str] = Field("gemini-3.5-flash", description="Tanlangan AI modeli")
    language: Optional[str] = Field("uz", description="Suhbat tili ('uz', 'en', 'ru')")
    provider: Optional[str] = Field("gemini", description="AI Provayder ('gemini', 'cyberai', 'openai', 'deepseek', 'groq', 'ollama', 'custom')")
    api_key: Optional[str] = Field(None, description="Foydalanuvchining shaxsiy API kaliti")
    base_url: Optional[str] = Field(None, description="Maxsus API Base URL")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Kreativlik harorati")
    system_prompt: Optional[str] = Field(None, description="Maxsus tizim ko'rsatmasi / AI Personasi")
    max_tokens: Optional[int] = Field(4096, ge=128, le=16384, description="Maksimal tokenlar")
    history_limit: Optional[int] = Field(10, ge=1, le=50, description="Kontekst xotirasi uzunligi")


class ConversationResponse(BaseModel):
    id: str
    title: str
    model: str
    language: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    model: str
    language: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    model_config = ConfigDict(from_attributes=True)


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


# ==========================================
# Code Security Analyzer Schemas
# ==========================================

class CodeAnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000, description="Tahlil qilinadigan manba kodi")
    language: Optional[str] = Field("python", description="Dasturlash tili: python, javascript, html")
    filename: Optional[str] = Field(None, description="Fayl nomi")


class CodeVulnerabilityFinding(BaseModel):
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # Secrets, SQL Injection, XSS, RCE, Config, Cryptography
    line: Optional[int] = None
    snippet: Optional[str] = None
    explanation: str
    fix_recommendation: str
    corrected_code: Optional[str] = None


class CodeAnalyzeResponse(BaseModel):
    id: str
    target: str
    score: int
    risk_level: str
    findings_count: int
    findings: List[CodeVulnerabilityFinding]
    created_at: datetime


# ==========================================
# Website Security Checker Schemas
# ==========================================

class WebsiteCheckRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=500, description="Tekshiriladigan URL (faqat http:// yoki https://)")
    confirm_authorization: bool = Field(
        ...,
        description="Foydalanuvchi sayt egasi ekanligini yoki tekshirish huquqiga ega ekanligini tasdiqlashi shart"
    )

    @field_validator("confirm_authorization")
    @classmethod
    def must_confirm(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Tekshiruvni boshlash uchun egalik yoki ruxsat tasdiqlanishi shart!")
        return v


class HeaderAnalysisItem(BaseModel):
    header: str
    status: str  # "present", "missing", "insecure", "deprecated"
    value: Optional[str] = None
    description: str
    recommendation: str


class CookieAnalysisItem(BaseModel):
    name: str
    secure: bool
    httponly: bool
    samesite: Optional[str] = None
    issues: List[str]


class WebsiteCheckResponse(BaseModel):
    id: str
    target: str
    score: int
    grade: str
    https_valid: bool
    response_time_ms: Optional[float] = None
    server_info: Optional[str] = None
    headers: List[HeaderAnalysisItem]
    cookies: List[CookieAnalysisItem]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    created_at: datetime


# ==========================================
# Security Reports Schemas
# ==========================================

class SecurityReportListItem(BaseModel):
    id: str
    report_type: str
    target: str
    summary: Optional[str]
    score: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Admin Schemas
# ==========================================

class AdminStatsResponse(BaseModel):
    total_users: int
    total_conversations: int
    total_messages: int
    total_security_reports: int
    total_code_scans: int
    total_website_scans: int
    ai_provider: str
    ai_model: str
    ai_status: str
    system_health: str


class AdminUserListItem(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    conversation_count: int
    report_count: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    ip_address: Optional[str]
    status: str
    details: Optional[str]
    created_at: datetime
