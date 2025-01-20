from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.openai_service import OpenAIService
from ..services.cosmos_service import CosmosService
from typing import List, Optional

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    conversation_id: Optional[str]
    user_id: str

openai_service = OpenAIService()
cosmos_service = CosmosService()

@router.post("/ai-assisted")
async def chat_ai_assisted(request: ChatRequest):
    try:
        response = await openai_service.get_chat_completion(request.messages)
        await cosmos_service.save_conversation(
            request.user_id,
            request.conversation_id,
            request.messages[-1].content,
            response
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/self-service")
async def chat_self_service(request: ChatRequest):
    try:
        response = await openai_service.get_self_service_response(request.messages)
        await cosmos_service.save_conversation(
            request.user_id,
            request.conversation_id,
            request.messages[-1].content,
            response
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
