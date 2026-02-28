from pydantic import BaseModel
from datetime import datetime

class message_scehma(BaseModel):
    message:str
    user_name:str
    avatar:str

class userSchema(BaseModel):
    user_name:str

class userRes(BaseModel):
    user_id:int
    user_name:str
    created_at:datetime
