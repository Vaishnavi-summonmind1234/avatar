import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import cursor


def getConnection():
    load_dotenv()
    try:
        connection=psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
             user=os.getenv("DB_USER"),
             password=os.getenv("DB_PASSWORD"),
             host=os.getenv("DB_HOST"),
             port=os.getenv('DB_PORT')
        )
        cur=connection.cursor()
        return connection

    except Exception as e:    
         print("error:",e)
if __name__ == "__main__":
    conn = getConnection()
    if conn:
        print("✅ Connected successfully")
        conn.close()
