import sys
import os
from dotenv import load_dotenv
import spotipy
import spotipy.util as sp_util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException

scope = 'user-library-read playlist-read-private'

def authenticate_client():

    load_dotenv()
    client_id = os.getenv('SPOTIPY_CLIENT_ID')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
    redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

    try:
        # Get an auth token for this user
        client_credentials = SpotifyClientCredentials()
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials)
        return spotify
    except SpotifyOauthError as e:
        print('API credentials not set.  Please see README for instructions on setting credentials.')
        sys.exit(1)

def authenticate_user():
    username = ''   # Enter Spotify Username
    try:
        token = sp_util.prompt_for_user_token(username, scope=scope)

        print("++User Auth Aquired++")
        return token
    
    except SpotifyException as e:
        print("API Credentials not set")
        sys.exit(1)
    except SpotifyOauthError as e:
        redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
        if redirect_uri is not None:
            print("Unlisted redirect URI:   ".format(redirect_uri))
        else:
            print("No URI Set:  ")
        sys.exit(1)

def testFunc(token):
    sp = spotipy.Spotify(auth=token)
    current_playlists = sp.current_user_playlists()['items']
    return [i['id'] for i in current_playlists]


