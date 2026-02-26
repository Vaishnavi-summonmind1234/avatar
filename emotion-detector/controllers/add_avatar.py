from db.connection import getConnection
from fastapi import HTTPException
from psycopg2.extensions import cursor

def add_avatar(data):
    con=getConnection()
    try:
        cur=con.cursor()
        cur.execute("""SELECT id FROM emotions WHERE emotion=%s """,(data.emotion,))
        emotion=cur.fetchone()
        if not emotion:
            return HTTPException(status_code=404,details="emotion not found")
        emotion_id = emotion[0]
        cur.execute("""SELECT id FROM tones WHERE tone=%s""",(data.tone,))
        tone=cur.fetchone()
        if not tone:
            return HTTPException(status_code=404,detail="tone not found")
        tone_id=tone[0]
        cur.execute("""SELECT id FROM modes WHERE mode_name=%s""",(data.mode,))
        mode =cur.fetchone()
        if not mode:
            return HTTPException(status_code=404,detail="mode not found")
        mode_id=mode[0]
        cur.execute("""SELECT id FROM domains WHERE name=%s""",(data.domain,))
        domain=cur.fetchone()
        if not domain:
            return HTTPException(status_code=404,detail="domain not found")
        domain_id=domain[0]
        cur.execute("""
            INSERT INTO avatar_master
            (name, emotion_id, tone_id, intensity_id, mode_id, description, type, domain)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.name,
            emotion_id,
            tone_id,
            data.intensity,
            mode_id,
            data.description,
            data.type,
            domain_id
            
        ))
        avatar_id=cur.fetchone()[0]
        con.commit()
        return {
            "success": True,
            "avatar_id": avatar_id
        }
    except Exception as e:
        con.rollback()
        return {"error": str(e)}


