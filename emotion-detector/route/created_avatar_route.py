from fastapi import FastAPI,APIRouter
from  db.AvatarSchema import AvatarResponse
from controllers.add_avatar import add_avatar

router=APIRouter()
@router.post('/avatarpost')
def add_av(data:AvatarResponse):
    return add_avatar(data)