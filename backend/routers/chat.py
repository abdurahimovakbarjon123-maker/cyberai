"""
CYBERAI Chat & Conversation Router
Endpoints for real-time AI conversations, streaming, history management, and chat lifecycle.
"""
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, Conversation, Message
from backend.schemas import (
    ChatRequest,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationUpdate,
    MessageResponse
)
from backend.dependencies import get_current_user, log_audit_event, check_rate_limit
from backend.ai_service import stream_ai_response, SYSTEM_PROMPTS
from backend.config import settings
import re

router = APIRouter(prefix="/api", tags=["Chat & Conversations"])


def generate_smart_title(message: str, has_image: bool = False, language: str = "uz") -> str:
    """
    Generates a clean, human-friendly, concise topic title (2-5 words)
    instead of storing raw user prompt sentences and typos.
    """
    raw = (message or "").strip()
    if not raw and has_image:
        return "Rasm va Tasvir Tahlili" if language == "uz" else "Image Analysis"

    lower = raw.lower()

    # 1. Greetings
    if any(lower.startswith(g) for g in ["salom", "assalom", "privet", "hello", "hi", "hey"]):
        return "Umumiy Suhbat" if language == "uz" else "General Conversation"

    # 2. Database & SQL
    if "sql" in lower:
        if any(w in lower for w in ["mano", "nima", "tushun", "haqida"]):
            return "SQL Tushunchasi va Ma'nosi"
        if any(w in lower for w in ["injeksiya", "injection", "sqli"]):
            return "SQL Injection Himoyasi"
        return "SQL va Ma'lumotlar Bazasi"

    if any(w in lower for w in ["database", "baza", "postgresql", "mysql", "sqlite", "mongodb"]):
        return "Ma'lumotlar Bazasi Tahlili"

    # 3. Dangerous/malicious code & exploits
    if any(w in lower for w in ["havli", "xavfli", "virus", "trojan", "malware", "zararli"]):
        return "Xavfli Kodlar Tahlili"
    if any(w in lower for w in ["xaker", "hacker", "hack", "buzib", "pen-test", "pentest"]):
        return "Kiberxavfsizlik Tahlili"

    # 4. Errors & Debugging
    if any(w in lower for w in ["ishlamaybdi", "ishlamayapti", "ishlamadi", "xato", "error", "bug", "crash", "muammo"]):
        return "Xatolik va Muammoni Bartaraf Etish"

    # 5. Telegram Bot
    if any(w in lower for w in ["telegram bot", "aiogram", "bot yaratish", "tg bot"]):
        return "Telegram Bot Dasturlash"

    # 6. Programming Languages & Frameworks
    if "python" in lower:
        return "Python Dasturlash"
    if any(w in lower for w in ["javascript", "react", "vue", "frontend", "html", "css"]):
        return "Frontend Dasturlash"
    if any(w in lower for w in ["fastapi", "django", "flask", "backend"]):
        return "Backend Dasturlash"

    # 7. Math
    if any(op in raw for op in ["+", "-", "*", "/"]) and any(c.isdigit() for c in raw):
        return "Matematik Hisoblash"

    # 8. Website security / checking
    if any(w in lower for w in ["sayt", "domen", "url", "https"]):
        return "Veb-sayt Tahlili"

    # 9. General semantic cleanup
    cleaned = re.sub(
        r"\b(manga|menga|yozb\s*ber|yozib\s*ber|ber|ko|koray|ko'ray|iltimos|aka|uka|bir|qilib\s*ber|qilb\s*ber|haqida|ayt|aytib\s*ber)\b",
        "",
        raw,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r"[?!.,;:_\"'()\[\]]+", " ", cleaned).strip()
    words = [w for w in cleaned.split() if len(w) > 1]

    if not words:
        return "Yangi Suhbat" if language == "uz" else "New Conversation"

    short_title = " ".join(words[:4]).title()
    if has_image:
        short_title = f"{short_title} (Rasm)"
    return short_title[:40]


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns list of conversations belonging to authenticated user.
    """
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    result = []
    for c in convs:
        # Auto-clean legacy slang or raw message titles in history
        if c.title and (any(c.title.lower().startswith(s) for s in ["manga", "nmaga", "sql manosi", "ushbu rasm"]) or len(c.title) > 35):
            c.title = generate_smart_title(c.title, has_image=("rasm" in c.title.lower()), language=c.language)
            try:
                db.commit()
            except Exception:
                db.rollback()

        count = len(c.messages)
        res_item = ConversationResponse(
            id=c.id,
            title=c.title,
            model=c.model,
            language=c.language,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=count
        )
        result.append(res_item)
    return result


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new blank conversation for the current user.
    """
    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title="Yangi suhbat",
        model=settings.AI_MODEL,
        language=settings.DEFAULT_LANGUAGE
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        model=conv.model,
        language=conv.language,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns full conversation details with ordered messages.
    Enforces user isolation.
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suhbat topilmadi yoki sizda unga kirish huquqi yo'q."
        )

    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        model=conv.model,
        language=conv.language,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponse.model_validate(m) for m in conv.messages]
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    req: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Renames a conversation.
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suhbat topilmadi."
        )

    conv.title = req.title.strip()
    db.commit()
    db.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        model=conv.model,
        language=conv.language,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=len(conv.messages)
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes conversation and associated messages.
    """
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suhbat topilmadi."
        )

    db.delete(conv)
    db.commit()
    return None


@router.post("/chat")
async def chat_synchronous(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Non-streaming synchronous chat endpoint.
    Appends messages to conversation and returns complete assistant reply.
    """
    conversation = None
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    if not conversation:
        title = generate_smart_title(req.message, has_image=bool(req.image_data), language=req.language or "uz")
        conversation = Conversation(
            id=req.conversation_id or str(uuid.uuid4()),
            user_id=current_user.id,
            title=title,
            model=req.model or settings.AI_MODEL,
            language=req.language or "uz"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_content = req.message or "Ushbu rasmni tahlil qiling"
    if req.image_data and "data:image" in req.image_data and req.image_data not in user_content:
        user_content = f"{user_content}\n\n![Yuklangan rasm]({req.image_data})"

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_content
    )
    db.add(user_msg)
    db.commit()

    # Build history context
    h_limit = req.history_limit or 10
    history = [
        {"role": m.role, "content": m.content}
        for m in conversation.messages[-h_limit:]
    ]
    if not any(m["role"] == "user" and m["content"] == user_content for m in history):
        history.append({"role": "user", "content": user_content})

    # Collect response chunks
    full_response = []
    async for chunk in stream_ai_response(
        history,
        model=req.model or conversation.model,
        language=req.language or conversation.language,
        provider=req.provider,
        api_key=req.api_key,
        base_url=req.base_url,
        temperature=req.temperature or 0.7,
        system_prompt=req.system_prompt,
        max_tokens=req.max_tokens or 4096,
        image_data=req.image_data
    ):
        full_response.append(chunk)

    assistant_reply = "".join(full_response)

    # Save assistant message
    asst_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_reply
    )
    db.add(asst_msg)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
        "message": assistant_reply
    }


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _rate=Depends(check_rate_limit)
):
    """
    Server-Sent Events (SSE) streaming chat endpoint.
    Streams incremental response tokens with automatic database persistence.
    """
    conversation = None
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        ).first()

    is_new = False
    if not conversation:
        is_new = True
        title = generate_smart_title(req.message, has_image=bool(req.image_data), language=req.language or "uz")
        conversation = Conversation(
            id=req.conversation_id or str(uuid.uuid4()),
            user_id=current_user.id,
            title=title,
            model=req.model or settings.AI_MODEL,
            language=req.language or "uz"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Save user message
    user_content = req.message or "Ushbu rasmni tahlil qiling"
    if req.image_data and "data:image" in req.image_data and req.image_data not in user_content:
        user_content = f"{user_content}\n\n![Yuklangan rasm]({req.image_data})"

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=user_content
    )
    db.add(user_msg)
    db.commit()

    # Build history context
    h_limit = req.history_limit or 10
    history = [
        {"role": m.role, "content": m.content}
        for m in conversation.messages[-h_limit:]
    ]

    conv_id = conversation.id
    conv_title = conversation.title
    model_to_use = req.model or conversation.model
    lang_to_use = req.language or conversation.language

    async def event_generator():
        # First send conversation metadata
        init_payload = {
            "conversation_id": conv_id,
            "title": conv_title,
            "is_new": is_new,
            "chunk": "",
            "done": False
        }
        yield f"data: {json.dumps(init_payload)}\n\n"

        assistant_chunks = []
        try:
            async for chunk in stream_ai_response(
                history,
                model=model_to_use,
                language=lang_to_use,
                provider=req.provider,
                api_key=req.api_key,
                base_url=req.base_url,
                temperature=req.temperature or 0.7,
                system_prompt=req.system_prompt,
                max_tokens=req.max_tokens or 4096,
                image_data=req.image_data
            ):
                assistant_chunks.append(chunk)
                payload = {
                    "conversation_id": conv_id,
                    "chunk": chunk,
                    "done": False
                }
                yield f"data: {json.dumps(payload)}\n\n"
        except Exception as e:
            err_payload = {
                "conversation_id": conv_id,
                "chunk": f"\n\n[Xatolik: {str(e)}]",
                "done": False
            }
            yield f"data: {json.dumps(err_payload)}\n\n"

        # Finalize and save assistant message to DB
        full_text = "".join(assistant_chunks)
        try:
            # Create a new local db session for saving completed message
            from backend.database import SessionLocal
            save_db = SessionLocal()
            try:
                asst_msg = Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=full_text
                )
                save_db.add(asst_msg)
                save_db.commit()
            finally:
                save_db.close()
        except Exception:
            pass

        # Send terminal done event
        done_payload = {
            "conversation_id": conv_id,
            "chunk": "",
            "done": True
        }
        yield f"data: {json.dumps(done_payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
