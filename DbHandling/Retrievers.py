import psycopg2
from dotenv import load_dotenv
import os

def getIds(source):

    load_dotenv()
    dbUser = os.getenv('DB_USER')
    dbPassword = os.getenv('DB_PASSWORD')
    conn = psycopg2.connect(dbname="spotify", user=dbUser, password=dbPassword)
    cur = conn.cursor()
    query = f'''SELECT DISTINCT song_id FROM "{source}"'''
    cur.execute(query)

    output = cur.fetchall()
    cur.close()
    conn.close()

    return output