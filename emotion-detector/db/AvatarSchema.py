from pydantic import BaseModel

class AvatarCreate(BaseModel):
    name:str
    emotion:str
    tone:str
    mode:str
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
    domain: str
    description: str | None
    type: str
