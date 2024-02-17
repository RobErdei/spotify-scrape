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
    return redirect(url_for('get_LikedSongs', external=True))

@app.route('/LikedSongs')
def get_LikedSongs():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')
    
    df_song = pd.DataFrame({
        "Artist ID": [],
        "Artist Name": [],
        "Artist URI": [],
        "Song ID": [],
        "Song Name": [],
        "Song Popularity":[],
        "Song URI": [],
        "Added On":[]
    })

    df_album = pd.DataFrame({
        "Album Type": [],
        "Album Artist Name": [],
        "Album Artist ID": [],
        "Album ID": [],
        "Album Name": [],
        "Album Release Date": [],
        "Album URI": []
    })

    sp = spotipy.Spotify(auth=token_info['access_token'])
    start = 0
    likedSongs = sp.current_user_saved_tracks(limit=20)['items']
    while start <= 10000:
        likedSongs = sp.current_user_saved_tracks(limit=20,offset=start)['items']
        for i in likedSongs:
            #saved_on_DateTime = (i["added_at"][:10])+ " " +(i["added_at"][10:])
            
            for artist in i['track']['album']['artists']:   #for album table
                album_type = i['track']['album']['album_type']
                artist_name = artist['name']
                artist_id = artist['id']
                album_id = i['track']['album']['id']
                album_name = i['track']['album']['name']
                album_release_date = i['track']['album']['release_date']
                album_uri = i['track']['album']['uri']
                df_album.loc[len(df_album.index)] = [album_type, artist_name, artist_id, album_id, album_name, album_release_date, album_uri]
            
            for artist in i['track']['artists']:            #for song table
                song_artist_id = artist['id']
                song_artist_name = artist['name']
                song_artist_uri = artist['uri']
                song_id = i['track']['id']
                song_name = i['track']['name']
                song_popularity = i['track']['popularity']
                song_uri = i['track']['uri']
                saved_on_DateTime = (i["added_at"][:10])+ " " +(i["added_at"][10:])
                df_song.loc[len(df_album.index)] = [song_artist_id, song_artist_name, song_artist_uri, song_id, song_name, song_popularity, song_uri, saved_on_DateTime]
        start = start + 20
    filepath = Path('C:/Users/rober/Documents/General work stuff/CodingProjects/PythonStuff/Web Scraping/Music/Spotify/LikedSongsInfo.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_song.to_csv(filepath)
    return df_song.to_dict()










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