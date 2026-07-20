from fastapi import APIRouter

from app.schemas.ChatModels import ChatResponse, ChatRequest

router = APIRouter(prefix="/ask/cheese", tags=["cheese"])

@router.post("", response_model=ChatResponse)
async def cheese_ask(request: ChatRequest):
    message_id = request.message_id
    response = "Success"
    response = ChatResponse(message_id=message_id, response=response)
    return response.__dict__
