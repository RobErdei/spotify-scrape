import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import requests

def Test_GetPlaylistInfo(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']
    return current_playlists[0]

def Test_GetLikedSongsInfo(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    likedSongs = sp.current_user_saved_tracks(limit=20)['items']
    list = ([int([len(likedSongs)][0])][0]) + 30
    return str(list)
    
def Misc(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']
    song = '5Tp9Ojtfm0VX7vR3u8oHwv'
    return sp.song_features(song)
    


def Test_newerFunc(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    artist_id = '1vOTVnnyLvVTeuwrZLghCN'
    track_artist_genre = sp.artist(artist_id)
    return track_artist_genre
