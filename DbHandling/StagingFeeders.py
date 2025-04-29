import psycopg2
from dotenv import load_dotenv
import os

def stagingTable_Playlist(playlistLine):
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
        createTab = '''
            CREATE TABLE "Staging_PlaylistDetails"(
                playlist_id VARCHAR, playlist_name VARCHAR, playlist_url VARCHAR, playlist_owner VARCHAR, playlist_owner_type VARCHAR, track_count INTEGER, playlist_status VARCHAR, song_id VARCHAR, song_name VARCHAR, song_popularity INTEGER, song_type VARCHAR, song_duration INTEGER, song_explicit BOOLEAN, song_uri VARCHAR, object_type VARCHAR, album_id VARCHAR, album_name VARCHAR, album_release_date VARCHAR, album_artist_id VARCHAR, album_artist_name VARCHAR, album_object_type VARCHAR, album_total_tracks INTEGER, other_object_type VARCHAR, album_uri VARCHAR(500), song_number_in_album INTEGER
            )
        '''
        cur.execute(createTab)
        
    insertLine = '''
            INSERT INTO "Staging_PlaylistDetails" (playlist_id, playlist_name, playlist_url, playlist_owner, playlist_owner_type, track_count, playlist_status, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
    cur.execute(insertLine, (playlistLine[0], playlistLine[1], playlistLine[2], playlistLine[3], playlistLine[4], playlistLine[5], playlistLine[6], playlistLine[7], playlistLine[8], playlistLine[9], playlistLine[10], playlistLine[11], playlistLine[12], playlistLine[13], playlistLine[14], playlistLine[15], playlistLine[16], playlistLine[17], playlistLine[18], playlistLine[19], playlistLine[20], playlistLine[21], playlistLine[22], playlistLine[23], playlistLine[24]))
        
    conn.commit()
    cur.close()
    conn.close()

    return

def stagingTable_Artist(artLine):
    # This table serves as a relation between artist and associated tracks. These two will be seperated into their respective destination tables to avoid redundancy

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
        createTab = 'CREATE TABLE "Staging_ArtistDetails" (artist_id VARCHAR, artist_name VARCHAR, artist_genres VARCHAR, associated_track_id VARCHAR, associated_track_name VARCHAR)'
        cur.execute(createTab)

    insertLine = 'INSERT INTO "Staging_ArtistDetails" (artist_id, artist_name, artist_genres, associated_track_id, associated_track_name) VALUES (%s, %s, %s, %s, %s)'
    cur.execute(insertLine, (artLine[0], artLine[1], artLine[2], artLine[3], artLine[4]))

    conn.commit()
    cur.close()
    conn.close()

    return

def stagingTable_Liked(trackDetails):
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
    cur.execute(checkIf, ("Staging_TrackDetails",))
    exists = cur.fetchone()[0]
    
    if exists == True:
        "No action needed"  
    else:
        createTab = '''
            CREATE TABLE "Staging_TrackDetails"(
                song_id VARCHAR, song_name VARCHAR, song_popularity INTEGER, song_type VARCHAR, song_duration INTEGER, song_explicit BOOLEAN, song_uri VARCHAR, object_type VARCHAR, album_id VARCHAR, album_name VARCHAR, album_release_date VARCHAR, album_artist_id VARCHAR, album_artist_name VARCHAR, album_object_type VARCHAR, album_total_tracks INTEGER, other_object_type VARCHAR, album_uri VARCHAR(500), song_number_in_album INTEGER
            )
        '''
        cur.execute(createTab)
        
    insertLine = '''
            INSERT INTO "Staging_TrackDetails" (song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
    cur.execute(insertLine, (trackDetails[0], trackDetails[1], trackDetails[2], trackDetails[3], trackDetails[4], trackDetails[5], trackDetails[6], trackDetails[7], trackDetails[8], trackDetails[9], trackDetails[10], trackDetails[11], trackDetails[12], trackDetails[13], trackDetails[14], trackDetails[15], trackDetails[16], trackDetails[17]))
        
    conn.commit()
    cur.close()
    conn.close()

    return