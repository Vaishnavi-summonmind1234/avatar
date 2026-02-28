from fastapi import HTTPException
from db.connection import getConnection
from db.messageSchema import message_scehma

def historyController(data: message_scehma):
    con = getConnection()
    try:
        cur = con.cursor()

        # 1️⃣ Get user_id
        cur.execute("SELECT user_id FROM users WHERE user_name=%s", (data.user_name,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user[0]

        # 2️⃣ Get avatar_id
        cur.execute("SELECT id FROM avatar_master WHERE name=%s", (data.avatar,))
        avatar = cur.fetchone()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        avatar_id = avatar[0]

        # 3️⃣ Create NEW conversation if needed
        if not data.conversation_id:  # handles None, 0, empty
            cur.execute("""
                INSERT INTO conversation_master (user_id, avatar_id)
                VALUES (%s, %s)
                RETURNING id
            """, (user_id, avatar_id))

            conversation_id = cur.fetchone()[0]
            con.commit()  # 🔴 commit immediately after creating conversation

        else:
            # 4️⃣ Verify conversation exists
            cur.execute("""
                SELECT id FROM conversation_master
                WHERE id=%s AND user_id=%s AND avatar_id=%s
            """, (data.conversation_id, user_id, avatar_id))

            existing = cur.fetchone()

            if not existing:
                raise HTTPException(status_code=400, detail="Invalid conversation_id")

            conversation_id = data.conversation_id

        # 5️⃣ Insert user message
        cur.execute("""
            INSERT INTO message (user_id, avatar_id, conversation_id, message, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, avatar_id, conversation_id, data.message, "user"))

        con.commit()

        # 6️⃣ Fetch history
        cur.execute("""
            SELECT message, role
            FROM message
            WHERE conversation_id=%s
            ORDER BY id ASC
        """, (conversation_id,))

        messages = cur.fetchall()

        history = [
            {"message": row[0], "role": row[1]}
            for row in messages
        ]

        return {
            "user_name": data.user_name,
            "avatar_name": data.avatar,
            "conversation_id": conversation_id,
            "history": history
        }

    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        con.close()