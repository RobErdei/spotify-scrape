from spotipy.oauth2 import SpotifyOAuth
import time
from flask import Flask, request, url_for, session, redirect

import os
from dotenv import load_dotenv

#Establish important filepaths
main_path = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(main_path, 'EnvResources')
dotenv_path = os.path.join(main_path, 'EnvResources', '.env')
csv_Rep = os.path.join(main_path, 'CSV_Dumps')
json_Rep = os.path.join(main_path, 'JSON_Dumps')

load_dotenv(dotenv_path) #loads environment variables (.env) file

app = Flask(__name__) #defines the instance of your Flask application. code will only execute if this instance is "__main__", or the main program

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = os.getenv("CLIENT_SECRET")

TOKEN_INFO = "temp_value"

@app.route('/')
def login():
    auth_url = create_spotify_OAuth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():     #saves token info to current session. Future function calls saif info
    session.clear()
    code = request.args.get('code')     #retrieves value from an HTTP request with the authorization query key 'code'. example: http://example.com/some/path?code=your_code_here
    token_info = create_spotify_OAuth().get_access_token(code)  #exchanges value of code query for access token
    session[TOKEN_INFO] = token_info
    return redirect(url_for('execution', external=True))

@app.route('/execution')
def execution():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect('/')
    
    #call functions here
        #VVVVVVVV
    environment = 0 #1 is probuction enviornment, 0 is test
    os.chdir(env_path)

    if environment == 1:
        from AllFunctions import GetLikedSongsInfo, GetPlaylistInfo
        GetPlaylistInfo(token_info)
        return "Prod Complete"
    elif environment == 0:
        from TestFunctions import Test_GetPlaylistInfo, Test_GetLikedSongsInfo, Misc
        return Test_GetLikedSongsInfo(token_info)
    else:
        return "invalid entry"

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external=False))
    now = int(time.time()) #gets current time
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_OAuth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_OAuth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('redirect_page', _external = True), #returns the full domain of the redirect address and not just the flask route '/redirect'
        scope = 'user-library-read playlist-read-private' #scope needed for authorization (in my case, user data and playlist data). Specific to spotify API documentation
    )

app.run(debug = True)