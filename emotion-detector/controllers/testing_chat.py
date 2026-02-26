
from dotenv import load_dotenv
from db.connection import getConnection
from fastapi import HTTPException
# from langchain_openai import ChatOpenAI 
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print(os.getenv("OPENAI_API_KEY"))
def test_chat(data):
    con = getConnection()
    try:
        cur = con.cursor()

        # ✅ fixed table name
        cur.execute(
            "SELECT  name, emotion_id, tone_id, description FROM avatar_master WHERE id=%s",
            (data.avatar_id,)
        )
        avatar = cur.fetchone()

        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")

        name, emotion, tone, description = avatar

        system_prompt = f"""
You are {name}.
Emotion style: {emotion}
Tone: {tone}
Description: {description}
Respond in this personality.
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

        # cur.execute(
        #     "INSERT INTO chat_history (avatar_id, user_message, ai_response) VALUES (%s,%s,%s)",
        #     (data.avatar_id, data.message, ai_reply)
        # )

        con.commit()

        return {"response": ai_reply}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if con:
            con.close()