import psycopg2
from dotenv import load_dotenv
import os

def MigratePlaylists():
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
    cur.execute(checkIf, ("PlaylistDetails",))
    exists = cur.fetchone()[0]

    if exists == True:
        "No action needed"
    else:
        createTab = '''
            CREATE TABLE "PlaylistDetails"(
                playlist_id VARCHAR, playlist_name VARCHAR, playlist_url VARCHAR, playlist_owner VARCHAR, playlist_owner_type VARCHAR, track_count INTEGER, playlist_status VARCHAR, song_id VARCHAR, song_name VARCHAR, song_popularity INTEGER, song_type VARCHAR, song_duration INTEGER, song_explicit BOOLEAN, song_uri VARCHAR, object_type VARCHAR, album_id VARCHAR, album_name VARCHAR, album_release_date VARCHAR, album_artist_id VARCHAR, album_artist_name VARCHAR, album_object_type VARCHAR, album_total_tracks INTEGER, other_object_type VARCHAR, album_uri VARCHAR(500), song_number_in_album INTEGER,
                primary key (playlist_id, song_id)
            )
        '''
        cur.execute(createTab)

    checkExistingCombos = '''
            -- Inserts distinct values from staging into destination table
            INSERT INTO "PlaylistDetails" (playlist_id, playlist_name, playlist_url, playlist_owner, playlist_owner_type, track_count, playlist_status, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album)
            SELECT DISTINCT playlist_id, playlist_name, playlist_url, playlist_owner, playlist_owner_type, track_count, playlist_status, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album
            FROM "Staging_PlaylistDetails" s
            WHERE NOT EXISTS (
                SELECT 1 FROM "PlaylistDetails" p
                WHERE p.playlist_id = s.playlist_id
                AND p.song_id = s.song_id
                );
            
            -- Deletes rows from staging table
            DELETE FROM "Staging_PlaylistDetails" s
            WHERE EXISTS (
                SELECT 1 FROM "PlaylistDetails" p
                WHERE p.playlist_id = s.playlist_id
                AND p.song_id = s.song_id
                );

            -- Updates track count field to reflect any changes made
            UPDATE "PlaylistDetails" AS p
            SET track_count = c.new_count
            FROM (
                SELECT playlist_id, COUNT(*) AS new_count
                FROM "PlaylistDetails"
                GROUP BY playlist_id
            ) AS c
            WHERE p.playlist_id = c.playlist_id;
        '''

    cur.execute(checkExistingCombos)
    

    conn.commit()
    cur.close()
    conn.close()

def MigrateArtists():
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
    cur.execute(checkIf, ("ArtistDetails",))
    exists = cur.fetchone()[0]

    if exists == True:
        "No action needed"
    else:
        createTab = '''
            CREATE TABLE "ArtistDetails" (
                artist_id VARCHAR, artist_name VARCHAR, artist_genres VARCHAR, associated_track_id VARCHAR, associated_track_name VARCHAR,
                primary key (artist_id, associated_track_id)
            )
        '''
        cur.execute(createTab)

    
    checkExistingCombos = '''
            -- Inserts distinct rows into destination table if applicable
            INSERT INTO "ArtistDetails" (artist_id, artist_name, artist_genres, associated_track_id, associated_track_name)
            SELECT DISTINCT artist_id, artist_name, artist_genres, associated_track_id, associated_track_name
            FROM "Staging_ArtistDetails" s
            WHERE NOT EXISTS (
                SELECT 1 FROM "ArtistDetails" a
                WHERE a.artist_id = s.artist_id
                AND a.associated_track_id = s.associated_track_id
                );

            -- Deletes rows from staging table
            DELETE FROM "Staging_ArtistDetails" s
            WHERE EXISTS (
                SELECT 1 FROM "ArtistDetails" a
                WHERE a.artist_id = s.artist_id
                AND a.associated_track_id = s.associated_track_id
            )
        '''
    
    cur.execute(checkExistingCombos)
    
    conn.commit()
    cur.close()
    conn.close()

def MigrateTracks():
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
    cur.execute(checkIf, ("AdditionalTrackDetails",))
    exists = cur.fetchone()[0]

    if exists == True:
        "No action needed"
    else:
        createTab = '''
            CREATE TABLE "AdditionalTrackDetails"(
                song_id VARCHAR, external_id VARCHAR, external_id_type VARCHAR, song_uri VARCHAR, song_name VARCHAR, local VARCHAR, object_type VARCHAR, is_explicit BOOLEAN, disc_number INTEGER, duration INTEGER,
                primary key (song_id, external_id)
            )
        '''
        cur.execute(createTab)

    checkExistingCombos = '''
            -- Inserts distinct values from staging into destination table
            INSERT INTO "AdditionalTrackDetails" (song_id, external_id, external_id_type, song_uri, song_name, local, object_type, is_explicit, disc_number, duration)
            SELECT DISTINCT song_id, external_id, external_id_type, song_uri, song_name, local, object_type, is_explicit, disc_number, duration
            FROM "Staging_AdditionalTrackDetails" s
            WHERE NOT EXISTS (
                SELECT 1 FROM "AdditionalTrackDetails" t
                WHERE t.external_id = s.external_id
                AND t.song_id = s.song_id
                );
            
            -- Deletes rows from staging table
            DELETE FROM "Staging_AdditionalTrackDetails" s
            WHERE EXISTS (
                SELECT 1 FROM "AdditionalTrackDetails" t
                WHERE t.external_id = s.external_id
                AND t.song_id = s.song_id
                )
        '''

    cur.execute(checkExistingCombos)
    

    conn.commit()
    cur.close()
    conn.close()
