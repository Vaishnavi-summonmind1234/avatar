
from dotenv import load_dotenv
from db.connection import getConnection
from fastapi import HTTPException
# from langchain_openai import ChatOpenAI 
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# print(os.getenv("OPENAI_API_KEY"))
def test_chat(data):
    con = getConnection()
    try:
        cur = con.cursor()

        # 1️⃣ Fetch avatar
        cur.execute("""
            SELECT name, emotion_id, tone_id, description, communication_style_id
            FROM avatar_master
            WHERE id=%s
        """, (data.avatar_id,))
        avatar = cur.fetchone()

        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")

        name, emotion_id, tone_id, description, style_id = avatar

        # 2️⃣ Fetch emotion name
        cur.execute("SELECT emotion FROM emotions WHERE id=%s", (emotion_id,))
        emotion = cur.fetchone()[0]

        # 3️⃣ Fetch tone name
        cur.execute("SELECT tone FROM tones WHERE id=%s", (tone_id,))
        tone = cur.fetchone()[0]

        # 4️⃣ Fetch communication rules
        cur.execute("""
            SELECT step, option
            FROM communication_styles
            WHERE id=%s
        """, (style_id,))
        rules = cur.fetchall()

        # 5️⃣ Build communication instructions
        instructions = []
        for step, option in rules:
            instructions.append(f"{step}: {option}.")

        communication_structure_instructions = "\n".join(instructions)

        # 6️⃣ Build strong system prompt
        system_prompt = f"""
You are {name}.

PERSONALITY:
Emotion: {emotion}
Tone: {tone}
Description: {description}

COMMUNICATION STRUCTURE:
{communication_structure_instructions}

Follow the structure strictly.
Avoid generic reassurance.
Stay consistent with tone and emotional stance.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data.message}
            ],
            temperature=0.2
        )

        ai_reply = response.choices[0].message.content
        return {"response": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        con.close()