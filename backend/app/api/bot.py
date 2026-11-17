import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import get_db
from app.api.dependencies import get_current_user
from app.models.postgres.auth import User
from app.services.bot_service import BotService

router = APIRouter(prefix="/bot", tags=["RAG Assistant"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Interact with the RAG Assistant. It uses the user's query to find relevant products
    or orders and generates an AI response.
    """
    bot_service = BotService(db)
    
    # current_user.id is a UUID.
    reply = await bot_service.chat(user_id=current_user.id, query=request.query)
    
    return ChatResponse(reply=reply)
