from WebQueries import GetPlaylistInfo_single, GetPlaylistInfo_many, GetLikedSongsInfo, ArtistSearchQuery, GetPlaylistGenres, GetTrackDetails
from OAuth import authenticate_user

import spotipy

from flask import Flask, send_from_directory, request
from pathlib import Path


html_path = Path(__file__).parent / 'HtmlTemplates'

app = Flask(__name__)


@app.route('/')
def starting_page():
    return send_from_directory(str(html_path), 'Homepage.html')


@app.route('/get_single_playlist', methods=['POST','GET'])
def getOnePlaylist():    # Retrieves info of specified user playlist
    if request.method == 'POST':
        
        playlist = request.form.get('playlist', '')
        owner = request.form.get('owner', '')
        token = authenticate_user(owner)

        if not playlist or not owner:
            return "Playlist name and owner are required. Please enter to continue!", 400
        
        response = GetPlaylistInfo_single(token, playlist, owner)
        
    return response

@app.route('/get_all_Playlists', methods=['POST','GET'])
def GetAllPlaylists():    # Retrieves info of all the user's playlists
    if request.method == 'POST':

        userName = request.form.get('userName', '')
        token = authenticate_user(userName)

        if not userName:
            return "Username is required. Please enter to continue!", 400

        response = GetPlaylistInfo_many(token)
    return response

@app.route('/get_playlist_genres', methods=['POST'])
def get_playlist_genres():  # Retrieves genres of artists present in a playlist
    if request.method == 'POST':

        playlist = request.form.get('playlist', '')
        owner = request.form.get('owner', '')
        token = authenticate_user(owner)

        if not playlist or not owner:
            return "Playlist name and owner are required. Please enter to continue!", 400  

        response = GetPlaylistGenres(token, playlist, owner)
    return response

@app.route('/get_liked_songs_info', methods=['POST','GET'])
def get_liked_songs_info(): # Retrieves info of all the user's liked songs
    if request.method == 'POST':

        userName = request.form.get('userName_Liked', '')
        token = authenticate_user(userName)

        if not userName:
            return "Username is required. Please enter to continue!", 400

        response = GetLikedSongsInfo(userName, token)
    return response

@app.route('/search_artist_genres', methods=['POST'])
def search_artist_genres(): # Retrieves genres of specified artist
    
    token = authenticate_user()
    sp = spotipy.Spotify(auth=token)
    
    artists = ['']   # Add artist name(s) into list
    lis = []
    for i in artists:
        artistName, artistGenres = ArtistSearchQuery(sp, i) # artistName = string, artistGenres = list
        lis.append(str(artistName) + " is " + str(artistGenres))
    return lis

@app.route('/get_additional_track_details', methods=['POST']) # Retrieves additional track data that's not availible in the other queries
def get_additional_track_details():
    if request.method == 'POST':

        userName = request.form.get('userName_Liked', '')
        token = authenticate_user(userName)
        if not userName:
            return "Username is required. Please enter to continue!", 400
            
        response = GetTrackDetails(token)
    return response


if __name__ == '__main__':
    app.run(debug=True)
