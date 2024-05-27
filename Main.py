from Functions import GetPlaylistInfo, GetLikedSongsInfo, ArtistSearchQuery, GetPlaylistGenres
from OAuth import authenticate_client, authenticate_user
import spotipy

from flask import Flask, send_from_directory
from pathlib import Path


html_path = Path(__file__).parent / 'HTML Files'

app = Flask(__name__)


@app.route('/')
def starting_page():
    return send_from_directory(str(html_path), 'Base.html')


@app.route('/get_playlist_info', methods=['POST'])
def get_playlist_info():    # Retrieves info of all the user's playlists
    scope = 'user-library-read playlist-read-private'
    spotify = authenticate_client()
    token = authenticate_user()
    playlistDetails = GetPlaylistInfo(token)
    return playlistDetails

@app.route('/get_playlist_genres', methods=['POST'])
def get_playlist_genres():  # Retrieves genres of specific playlists made by specific users
    scope = 'user-library-read playlist-read-private'
    spotify = authenticate_client()
    token = authenticate_user()

    playlist = ''   #Add your playlist name (str)
    owner = ''  #Add your Spotify username (str)

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
    token1 = authenticate_client()
    token = authenticate_user()
    sp = spotipy.Spotify(auth=token)
    artists = ['Polyphia', 'Taylor Swift', 'Olivia Rodrigo', 'DJ Khalid']   # Add artist name(s) into list
    lis = []
    for i in artists:
        artistName, artistGenres = ArtistSearchQuery(sp, i) # artistName = string, artistGenres = list
        lis.append(str(artistName) + " is " + str(artistGenres))
    return lis


if __name__ == '__main__':
    app.run(debug=True)
