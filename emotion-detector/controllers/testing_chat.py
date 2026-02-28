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

        # 1️⃣ Get conversation details
        cur.execute("""
            SELECT user_id, avatar_id
            FROM conversation_master
            WHERE id=%s
        """, (data.conversation_id,))

        conversation = cur.fetchone()

        if not conversation:
            raise HTTPException(status_code=404, detail="Invalid conversation_id")

        user_id = conversation["user_id"]
        avatar_id = conversation["avatar_id"]
        conversation_id = data.conversation_id

        # 2️⃣ Insert USER message
        cur.execute("""
            INSERT INTO message (user_id, avatar_id, conversation_id, message, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, avatar_id, conversation_id, data.message, "user"))

        con.commit()

        # 3️⃣ Fetch avatar personality
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

        system_prompt = f"""
You are {avatar['name']}.

Emotion: {emotion}
Tone: {tone}
Description: {avatar['description']}

Communication Rules:
{chr(10).join(instructions)}

Follow structure strictly.
Stay consistent with personality.
"""

        # 4️⃣ Fetch conversation history
        cur.execute("""
            SELECT role, message
            FROM message
            WHERE conversation_id=%s
            ORDER BY id ASC
        """, (conversation_id,))

        history_rows = cur.fetchall()

        openai_messages = [{"role": "system", "content": system_prompt}]

        for row in history_rows:
            openai_messages.append({
                "role": row["role"],
                "content": row["message"]
            })

        # 5️⃣ Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.2
        )

        ai_reply = response.choices[0].message.content

        # 6️⃣ Store assistant reply
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