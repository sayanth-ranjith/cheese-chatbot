from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid",)
    message_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    message_id: str