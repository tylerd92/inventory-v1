from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatbot_service import process_chat

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    """Send a message to the chatbot and get a response."""
    try:
        response = process_chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")