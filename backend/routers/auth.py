"""
CYBERAI Authentication Router
Endpoints for user registration, login, and current profile retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from backend.auth import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user, log_audit_event, check_rate_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    req: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Registers a new user with securely hashed credentials.
    The first registered user is automatically granted 'admin' role.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Check if username already exists
    existing_user = db.query(User).filter(User.username.ilike(req.username)).first()
    if existing_user:
        log_audit_event(db, "register_failed", None, client_ip, "failed", f"Username exists: {req.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu foydalanuvchi nomi allaqachon band qilingan."
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email.ilike(req.email)).first()
    if existing_email:
        log_audit_event(db, "register_failed", None, client_ip, "failed", f"Email exists: {req.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu elektron pochta manzili allaqachon ro'yxatdan o'tgan."
        )

    # Assign admin role to first user or if username is 'admin'
    user_count = db.query(User).count()
    role = "admin" if (user_count == 0 or req.username.lower() == "admin") else "user"

    new_user = User(
        username=req.username,
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(db, "user_registered", new_user.id, client_ip, "success", f"Role: {role}")

    # Generate JWT
    access_token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username, "role": new_user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(
    req: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Authenticates user and returns JWT access token.
    Supports login via username or email.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Search by username or email
    user = db.query(User).filter(
        (User.username.ilike(req.username)) | (User.email.ilike(req.username))
    ).first()

    if not user or not verify_password(req.password, user.password_hash):
        log_audit_event(db, "login_failed", None, client_ip, "failed", f"Invalid credentials for {req.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi nomi yoki parol noto'g'ri (Invalid credentials)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        log_audit_event(db, "login_blocked", user.id, client_ip, "blocked", "Inactive account")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ushbu akkaunt faolsizlantirilgan."
        )

    log_audit_event(db, "login_success", user.id, client_ip, "success", f"User: {user.username}")

    access_token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/guest", response_model=TokenResponse)
def guest_auth(request: Request, db: Session = Depends(get_db)):
    """
    Creates or retrieves an instant guest/demo session.
    Ensures seamless onboarding without requiring manual registration.
    """
    client_ip = request.client.host if request.client else "unknown"

    guest_user = db.query(User).filter(User.username == "demo_guest").first()
    if not guest_user:
        guest_user = User(
            username="demo_guest",
            email="guest@cyberai.local",
            password_hash=hash_password("GuestSecurePassword2026"),
            role="user",
            is_active=True
        )
        db.add(guest_user)
        db.commit()
        db.refresh(guest_user)

    log_audit_event(db, "guest_login", guest_user.id, client_ip, "success", "Auto guest token issued")

    access_token = create_access_token(data={"sub": str(guest_user.id), "username": guest_user.username, "role": guest_user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(guest_user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns profile information for the authenticated user.
    """
    return UserResponse.model_validate(current_user)
