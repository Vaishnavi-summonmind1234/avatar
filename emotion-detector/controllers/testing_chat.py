from dotenv import load_dotenv
from db.connection import getConnection
from fastapi import HTTPException
from openai import OpenAI
import os
import psycopg2.extras

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_chat(data):
    con = getConnection()
    try:
        cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # 1️⃣ Get user_id
        cur.execute(
            "SELECT user_id FROM users WHERE user_name=%s",
            (data.user_name,)
        )
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user["user_id"]

        # 2️⃣ Get avatar_id
        cur.execute(
            "SELECT id FROM avatar_master WHERE name=%s",
            (data.avatar,)
        )
        avatar_row = cur.fetchone()
        if not avatar_row:
            raise HTTPException(status_code=404, detail="Avatar not found")
        avatar_id = avatar_row["id"]

        # 3️⃣ Create or Use Conversation
        if data.conversation_id is None:
            cur.execute("""
                INSERT INTO conversation_master (user_id, avatar_id)
                VALUES (%s, %s)
                RETURNING id
            """, (user_id, avatar_id))
            conversation_id = cur.fetchone()["id"]
        else:
            conversation_id = data.conversation_id

        # 4️⃣ Insert USER message with conversation_id
        cur.execute("""
            INSERT INTO message (user_id, avatar_id, conversation_id, message, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, avatar_id, conversation_id, data.message, "user"))

        con.commit()

        # 5️⃣ Fetch avatar personality (same as before)
        cur.execute("""
            SELECT name, emotion_id, tone_id, description, communication_style_id
            FROM avatar_master
            WHERE id=%s
        """, (avatar_id,))
        avatar = cur.fetchone()

        cur.execute("SELECT emotion FROM emotions WHERE id=%s", (avatar["emotion_id"],))
        emotion = cur.fetchone()["emotion"]

        cur.execute("SELECT tone FROM tones WHERE id=%s", (avatar["tone_id"],))
        tone = cur.fetchone()["tone"]

        cur.execute("""
            SELECT step, option
            FROM communication_styles
            WHERE id=%s
        """, (avatar["communication_style_id"],))
        rules = cur.fetchall()

        instructions = [
            f"{rule['step']}: {rule['option']}."
            for rule in rules
        ]
        communication_structure = "\n".join(instructions)

        # 6️⃣ System Prompt
        system_prompt = f"""
You are {avatar['name']}.

PERSONALITY:
Emotion: {emotion}
Tone: {tone}
Description: {avatar['description']}

COMMUNICATION STRUCTURE:
{communication_structure}

Follow structure strictly.
Stay consistent with personality.
"""

        # 7️⃣ Fetch history ONLY for this conversation
        cur.execute("""
            SELECT role, message
            FROM message
            WHERE conversation_id=%s
            ORDER BY id ASC
        """, (conversation_id,))

        history_rows = cur.fetchall()

        # 8️⃣ Convert to OpenAI format
        openai_messages = [{"role": "system", "content": system_prompt}]

        for row in history_rows:
            openai_messages.append({
                "role": row["role"],
                "content": row["message"]
            })

        # 9️⃣ Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.2
        )

        ai_reply = response.choices[0].message.content

        # 🔟 Store AI reply with conversation_id
        cur.execute("""
            INSERT INTO message (user_id, avatar_id, conversation_id, message, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, avatar_id, conversation_id, ai_reply, "assistant"))

        con.commit()

        return {
            "response": ai_reply,
            "conversation_id": conversation_id
        }

    except Exception as e:
        con.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        con.close()