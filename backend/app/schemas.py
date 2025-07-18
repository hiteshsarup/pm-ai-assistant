from pydantic import BaseModel
from typing import List, Literal, Optional

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    mode: Literal["generator", "reviewer"]
    approachType: Literal["quick_fix", "generic"]

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
