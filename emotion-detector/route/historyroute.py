from fastapi import APIRouter
from controllers.history import historyController
from db.messageSchema import message_scehma

historyrouter = APIRouter()

@historyrouter.post("/history")
def gethistory(data: message_scehma):
    return historyController(data)