from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid",)
    message_id: str
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    message_id: str
    sources: list[str] = []
    conversation_id: str | None = None