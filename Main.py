from Functions import GetPlaylistInfo_single, GetPlaylistInfo_many, GetLikedSongsInfo, ArtistSearchQuery, GetPlaylistGenres
from OAuth import authenticate_client, authenticate_user

import spotipy

#from TEST_SqlFeeder import ConnectionTesting

from flask import Flask, send_from_directory, request, jsonify
from pathlib import Path


html_path = Path(__file__).parent / 'HTML Files'

app = Flask(__name__)


@app.route('/')
def starting_page():
    return send_from_directory(str(html_path), 'Base.html')


@app.route('/get_single_playlist', methods=['POST','GET'])
def getOnePlaylist():    # Retrieves info of specified user playlist
    if request.method == 'POST':
        playlist = request.form.get('playlist', '')
        owner = request.form.get('owner', '')

        sp = authenticate_user(owner)

        if not playlist or not owner:
            return "Playlist name and owner are required. Please enter to continue!", 400
        
        response = GetPlaylistInfo_single(sp, playlist, owner)
        #playlistDetails = response.get_json()
        #print(playlistDetails)

    return response

@app.route('/get_all_Playlists', methods=['POST'])
def GetAllPlaylists():    # Retrieves info of all the user's playlists
    scope = 'user-library-read playlist-read-private'
    spotify = authenticate_client()
    token = authenticate_user()
    playlistDetails = GetPlaylistInfo_many(token)
    return playlistDetails

@app.route('/get_playlist_genres', methods=['POST'])
def get_playlist_genres():
    scope = 'user-library-read playlist-read-private'
    spotify = authenticate_client()
    token = authenticate_user()

    playlist = request.form.get('playlist', '')
    owner = request.form.get('owner', '')

    if not playlist or not owner:
        return "Playlist name and owner are required. Please enter to continue!", 400  

    result = GetPlaylistGenres(token, playlist, owner)
    return result

@app.route('/get_liked_songs_info', methods=['POST'])
def get_liked_songs_info(): # Retrieves a specified amount of the user's liked songs
    scope = 'user-library-read playlist-read-private'
    spotify1 = authenticate_client()
    token = authenticate_user()
    likedSongs = GetLikedSongsInfo(token)
    return likedSongs

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


if __name__ == '__main__':
    app.run(debug=True)
