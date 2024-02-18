import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

def GetPlaylistInfo(token_info):
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']

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
        "Object Type": [],
        "Album Id": [],
        "Album Name": [],
        "Album Release Date ": [],
        "Album Artist Id": [],
        "Album Artist Name": [],
        "Album Object Type": [],
        "Album Total Tracks": [],
        "Other Object Type": [],
        "Album Uri": [],
        "Song Number In Album": [],
        "Song Id": [],
        "Song Name": [],
        "Song Popularity": [],
        "Song Type": [],
        "Song Duration": [],
        "Song Explicit": [],
        "Song Uri": []
    })

    #Artist Info Table
    df3 = pd.DataFrame({
        "ID":[], #KEY
        "Name": [],
        "Genres": []
    })

    #Song Features
    df4 = pd.DataFrame({

    })
    
    for i in current_playlists: #Appends specified fields to df1 (the "Playlist Info" table)
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
                track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                df3.loc[len(df3.index)] = [track_artist_id, track_artist_name, track_artist_genre]
                                
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
        break    

    df3.drop_duplicates(subset=['ID'], keep=False) #Ensures artist ID field is unique in Artist table
    PlaylistInfo_1 = pd.merge(df1,df2, on='Playlist ID', how='right') #all from second, matching from first
    PlaylistInfo = pd.merge(PlaylistInfo_1,df3[['ID','Genres']], left_on='Album Artist Id', right_on='ID', how='left') #Merge on ID, include only Genres field from other table

    return PlaylistInfo.to_dict()

def GetLikedSongsInfo(token_info): #Gets LikedSongs info and exports to tabular/csv output
    df_song = pd.DataFrame({
        "Artist ID": [],
        "Artist Name": [],
        "Artist URI": [],
        "Song ID": [],
        "Song Name": [],
        "Song Popularity":[],
        "Song URI": [],
        "Added On":[],
        "Song Artist Followers": [],
        "Song Artist Genre": []
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
    while start <= 50: #otiginally 2000
        likedSongs = sp.current_user_saved_tracks(limit=20,offset=start)['items']
        for i in likedSongs:
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

                song_artist_followers = str(sp.artist(song_artist_id)['followers']['total'])
                song_artist_genres = ','.join([i for i in sp.artist(song_artist_id)['genres']])

                df_song.loc[len(df_album.index)] = [song_artist_id, song_artist_name, song_artist_uri, song_id, song_name, song_popularity, song_uri, saved_on_DateTime, song_artist_followers, song_artist_genres]

        start = start + 20
    
    return df_song.to_dict()

