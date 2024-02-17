import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import pandas as pd
from pathlib import Path
from flask import Flask, request, url_for, session, redirect

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'doosngif3455ish78cvgaa4444444'

TOKEN_INFO = 'Token_info'

@app.route('/')
def login():
    auth_url = create_spotify_OAuth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_OAuth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('get_playlists', external=True))

@app.route('/playlists')
def get_playlists():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')

    #Playlist Info table
    df1 = pd.DataFrame({
        "Playlist ID": [],
        "Playlist Name": [],
        "Link": [],
        "Owner": [],
        "Owner Type": [],
        "Track Count": [],
        "Object Type": []
    })

    #Genral Song Info table
    df2 = pd.DataFrame({
        "Playlist ID": [],
        "Object Type ": [],
        "Album Id ": [],
        "Album Name ": [],
        "Album Release Date ": [],
        "Album Artist Id ": [],
        "Album Artist Name ": [],
        "Album Object Type ": [],
        "Album Total Tracks ": [],
        "Other Object Type ": [],
        "Album Uri ": [],
        "Song Number In Album ": [],
        "Song Id ": [],
        "Song Name ": [],
        "Song Popularity ": [],
        "Song Type ": [],
        "Song Duration ": [],
        "Song Explicit ": [],
        "Song Uri ": []
    })

    #Artist Info Table
    df3 = pd.DataFrame({
        "ID":[],
        "Name": [],
    })

    #Song Features
    df4 = pd.DataFrame({

    })
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']
    
    for i in current_playlists: #Appends specified fields to dfa (the "Playlist Info" table)
        play_id = i["id"]
        play_name = i["name"]
        link = i["href"]
        owner = i["owner"]["display_name"]
        owner_type = i["owner"]["type"]
        track_count = i["tracks"]["total"]
        obj_type = i["type"]
        df1.loc[len(df1.index)] = [play_id, play_name, link, owner, owner_type, track_count, obj_type]
        

    for row in df1["Playlist ID"]:
        content = sp.playlist_items(row)["items"]
        for song in content:
            #Album Info
            object_type = song["track"]["album"]["album_type"]
            album_id = song["track"]["album"]['id']
            album_name = song["track"]["album"]['name']
            album_release_date = song["track"]["album"]["release_date"]
            album_artist_id = song["track"]["album"]["artists"][0]["id"]
            album_artist_name = song["track"]["album"]["artists"][0]["name"]
            album_object_type = song["track"]["album"]["artists"][0]["type"]
            album_total_tracks = song["track"]["album"]["total_tracks"]
            other_object_type = song["track"]["album"]["type"]
            album_uri = song["track"]["album"]["uri"]
            song_number_in_album = song["track"]["track_number"]
            
            #Artist data (to be mapped afterwards through merge)
            for artist in song["track"]["artists"]:
                track_artist_id = artist["id"]
                track_artist_name = artist["name"]
                df3.loc[len(df3.index)] = [track_artist_id, track_artist_name]
                #df3.drop_duplicates(subset=['ID'])
            
            #Song/Track Info
            song_id = song["track"]["id"]
            song_name = song["track"]["name"]
            song_popularity = song["track"]["popularity"]
            song_type = song["track"]["type"]
            song_duration = int(song["track"]["duration_ms"]*(1/1000))    #converts song duration from milisecond to seconds
            song_explicit =song["track"]["explicit"]
            song_uri = song["track"]["uri"]
            new_row = [row, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri]
            df2.loc[len(df2.index)] = new_row
    df2.join(df1, lsuffix="Playlist ID", rsuffix="Playlist ID")
    filepath = Path('C:/Users/rober/Documents/General work stuff/CodingProjects/PythonStuff/Web Scraping/Music/Spotify/PlaylistInfo.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df2.to_csv(filepath)
    return content[0]


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external=False))
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_OAuth
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info



def create_spotify_OAuth():
    return SpotifyOAuth(
        client_id = 'bfd1ddcd3ce14d8a981b8b2d0b82269f',
        client_secret = '4d51fb39beaf42599a72b277aca979aa',
        redirect_uri = url_for('redirect_page', _external=True),
        scope = 'user-library-read playlist-read-private'
        )


app.run(debug=True)