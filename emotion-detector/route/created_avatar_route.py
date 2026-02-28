from fastapi import APIRouter
from db.AvatarSchema import AvatarResponse
from db.messageSchema import message_scehma
from controllers.add_avatar import add_avatar
from controllers.testing_chat import test_chat

router = APIRouter()

@router.post('/avatarpost')
def add_av(data: AvatarResponse):
    return add_avatar(data)

@router.post('/chattext')
def chat_av(data: message_scehma):
    return test_chat(data)   # ✅ fixed here