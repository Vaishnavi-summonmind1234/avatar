from fastapi import FastAPI,HTTPException
from db.connection import getConnection
from db.messageSchema import message_scehma,userRes,userSchema

def historyController(data:message_scehma):
    con=getConnection()
    try:
        cur=con.cursor()
        cur.execute("""SELECT user_id FROM users WHERE user_name=%s""",(data.user_name,))
        user=cur.fetchone()
        if not user:
            raise HTTPException(status_code=404,detail="no user fdound")
        user_id=user[0]
        cur.execute("""SELECT id from avatar_master WHERE name=%s""",(data.avatar,))
        avatar=cur.fetchone()
        if not avatar:
            raise HTTPException(status_code=404, detail="not found avatar")
        avatar_id=avatar[0]
        cur.execute(
            """
            INSERT INTO message (user_id, avatar_id, message)
            VALUES (%s, %s, %s)
            """,
            (user_id, avatar_id, data.message)
        )
        con.commit()
        cur.execute(
            """
            SELECT message
            FROM message
            WHERE user_id=%s AND avatar_id=%s
            ORDER BY created_at ASC
            """,
            (user_id, avatar_id)
        )
        message=cur.fetchall()
        history = [row[0] for row in message]
        return {
            "user_name":data.user_name,
            "avatar_name":data.avatar,
            "history":history

        }
    except Exception as e:
        raise HTTPException(status_code=500 , detail=print(e))
    


 