from pydantic import BaseModel

class AvatarCreate(BaseModel):
    name:str
    emotion:str
    tone:str
    mode:str
    communication_style_id: int
    intensity: int
    domain: str
    type:str
    description:str | None=None
class AvatarResponse(BaseModel):
    id: int
    name: str
    emotion: str
    tone: str
    intensity: int
    mode: str
    communication_style_id: int
    domain: str
    description: str | None
    type: str
class ChatSchema(BaseModel):
    conversation_id: int
    message: str