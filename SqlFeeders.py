import psycopg2
from dotenv import load_dotenv
import os

def stagingTable_Playlist(playDetailLine):
    load_dotenv()
    dbUser = os.getenv('DB_USER')
    dbPassword = os.getenv('DB_PASSWORD')

    conn = psycopg2.connect(dbname="spotify", user=dbUser, password=dbPassword)
    cur = conn.cursor()
    
    checkIf = '''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = %s
        )    
    '''
    cur.execute(checkIf, ("Staging_PlaylistDetails",))
    exists = cur.fetchone()[0]
    
    if exists == True:
        "No action needed"  
    else:
        createTab = 'CREATE TABLE "Staging_PlaylistDetails"(playlist_id VARCHAR, playlist_name VARCHAR, playlist_owner VARCHAR, track_count INTEGER, playlist_status VARCHAR, object_type VARCHAR, album_id VARCHAR, album_name VARCHAR, album_release_date VARCHAR, album_artist_id VARCHAR, album_artist_name VARCHAR, album_object_type VARCHAR, album_total_tracks INTEGER, other_object_type VARCHAR, album_uri VARCHAR, song_number_in_album INTEGER, song_id VARCHAR, song_name VARCHAR, song_popularity INTEGER, song_type VARCHAR, song_duration INTEGER, song_explicit BOOLEAN, song_uri VARCHAR)'
        cur.execute(createTab)
        
    insertLine = 'INSERT INTO "Staging_PlaylistDetails" (playlist_id, playlist_name, playlist_owner, track_count, playlist_status, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cur.execute(insertLine, (playDetailLine[0], playDetailLine[1], playDetailLine[2], playDetailLine[3], playDetailLine[4], playDetailLine[5], playDetailLine[6], playDetailLine[7], playDetailLine[8], playDetailLine[9], playDetailLine[10], playDetailLine[11], playDetailLine[12], playDetailLine[13], playDetailLine[14], playDetailLine[15], playDetailLine[16], playDetailLine[17], playDetailLine[18], playDetailLine[19], playDetailLine[20], playDetailLine[21], playDetailLine[22]))
        
    conn.commit()
    cur.close()
    conn.close()

    return

def stagingTable_Artist(artDetLine):
    load_dotenv()
    dbUser = os.getenv('DB_USER')
    dbPassword = os.getenv('DB_PASSWORD')

    conn = psycopg2.connect(dbname="spotify", user=dbUser, password=dbPassword)
    cur = conn.cursor()

    checkIf = '''
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = %s
        )    
    '''
    cur.execute(checkIf, ("Staging_ArtistDetails",))
    exists = cur.fetchone()[0]

    if exists == True:
        "No action needed"
    else:
        createTab = 'CREATE TABLE "Staging_ArtistDetails" (artist_id VARCHAR, artist_name VARCHAR, artist_genres VARCHAR)'
        cur.execute(createTab)

    insertLine = 'INSERT INTO "Staging_ArtistDetails" (artist_id, artist_name, artist_genres) VALUES (%s, %s, %s)'
    cur.execute(insertLine, (artDetLine[0], artDetLine[1], artDetLine[2]))

    conn.commit()
    cur.close()
    conn.close()

    return