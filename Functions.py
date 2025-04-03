import spotipy
import pandas as pd
from flask import Response, stream_with_context
from SqlFeeders import stagingTable_Playlist, stagingTable_Artist


def GetPlaylistInfo_many(token_info):
    sp = spotipy.Spotify(auth=token_info)
    current_playlists = sp.current_user_playlists()['items']

    playIDs = []

    for i in current_playlists: # Get overview playlist data
        play_id = i["id"]
        playIDs.append(play_id)
        play_name = i["name"]
        link = i["href"]
        owner = i["owner"]["display_name"]
        owner_type = i["owner"]["type"]
        track_count = i["tracks"]["total"]
        obj_type = i["type"]
        newPlayRow = [play_id, play_name, link, owner, owner_type, track_count, obj_type]

    def parsePlaylistsJSON():
        for row in playIDs:
            content = sp.playlist_items(row)["items"]

            for song in content:
                # Album Info
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
                
                # Artist data (to be mapped afterwards through merge)
                for artist in song["track"]["artists"]:
                    track_artist_id = artist["id"]
                    track_artist_name = artist["name"]
                    track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                    newArtistRow = F"('{track_artist_id}', '{track_artist_name}', '{track_artist_genre}')\n"
                    yield newArtistRow
                                    
                # Song/Track Info
                song_id = song["track"]["id"]
                song_name = song["track"]["name"]
                song_popularity = song["track"]["popularity"]
                song_type = song["track"]["type"]
                song_duration = int(song["track"]["duration_ms"]*(1/1000))    # Converts song duration from milisecond to seconds
                song_explicit =song["track"]["explicit"]
                song_uri = song["track"]["uri"]
                newSongRow = F"('{row}', '{object_type}', '{album_id}', '{album_name}', '{album_release_date}', '{album_artist_id}', '{album_artist_name}', '{album_object_type}', '{album_total_tracks}', '{other_object_type}', '{album_uri}', '{song_number_in_album}', '{song_id}', '{song_name}', '{song_popularity}', '{song_type}', '{song_duration}', '{song_explicit}', '{song_uri}')\n" 
                
                yield newSongRow

    return Response(stream_with_context(parsePlaylistsJSON()), content_type='text/plain')


def GetPlaylistInfo_single(token_info, playlist, owner):
    sp = spotipy.Spotify(auth=token_info)

    result = sp.search(q=playlist, type='playlist')

    playIdMatch = ''
    genPlayInf = []
    for play in result['playlists']['items']:
        if play['owner']['display_name'].lower() == owner.lower():
            genPlayInf.append(play['id'])
            playIdMatch = genPlayInf[0]
            genPlayInf.append(play['name'])
            genPlayInf.append(play['owner']['display_name'])
            genPlayInf.append(play['tracks']['total'])
            genPlayInf.append(play['public'])
            break

    if not playIdMatch:
        return {"error": "No matching playlist found for the given owner."}

    content = sp.playlist_items(playIdMatch)["items"]

    def JsonParsing():
        for song in content:
            # General Playlist Info
            playID = genPlayInf[0]
            playName = genPlayInf[1]
            playOwner = genPlayInf[2]
            playTrackCount = genPlayInf[3]
            playStatus = genPlayInf[4]

            # Album Info
            object_type = song["track"]["album"]["album_type"]
            album_id = song["track"]["album"]['id']
            album_name = song["track"]["album"]['name']
            album_release_date = song["track"]["album"]["release_date"]
            album_artist_id  = song["track"]["album"]["artists"][0]["id"]
            album_artist_name = song["track"]["album"]["artists"][0]["name"]
            album_object_type = song["track"]["album"]["artists"][0]["type"]
            album_total_tracks = song["track"]["album"]["total_tracks"]
            other_object_type = song["track"]["album"]["type"]
            album_uri = song["track"]["album"]["uri"]
            song_number_in_album = song["track"]["track_number"]
                                
            # Song/Track Info
            song_id = song["track"]["id"]
            song_name = song["track"]["name"]
            song_popularity = song["track"]["popularity"]
            song_type = song["track"]["type"]
            song_duration = int(song["track"]["duration_ms"]*(1/1000))    # Converts song duration from milisecond to seconds
            song_explicit =song["track"]["explicit"]
            song_uri = song["track"]["uri"]

            newSongRow = (playID, playName, playOwner, playTrackCount, playStatus, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri)

            stagingTable_Playlist(newSongRow)
            
            yield str(newSongRow) + '\n'

            # Artist data
            for artist in song["track"]["artists"]:
                track_artist_id = artist["id"]
                track_artist_name = artist["name"]
                track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                
                newArtistRow = f"('{track_artist_id}', '{track_artist_name}', '{track_artist_genre}')\n"
                newArtistRow = (track_artist_id, track_artist_name, track_artist_genre)
                
                stagingTable_Artist(newArtistRow)
                yield str(newArtistRow) + '\n'
        

    return Response(stream_with_context(JsonParsing()), content_type='text/plain')


def GetPlaylistGenres(token_info, playlist, owner): # Get playlist genres
    sp = spotipy.Spotify(auth=token_info)
    result = sp.search(playlist, type='playlist')

    artistDF = pd.DataFrame({
      'ArtistGenres' : []
    })

    playID = ''
    for play in result['playlists']['items']:
        if str(play['owner']['display_name']) == str(owner):
            playID = play['id']
            break

    for song in sp.playlist_items(playID)['items']:
        for artist in song['track']['artists']:
            artistID = artist['id']
            for genre in sp.artist(artistID)['genres']:
                ArtistGenres = genre
                newRow = [ArtistGenres]
                artistDF.loc[len(artistDF.index)] = newRow 
    
    artistDF = artistDF.rename(columns={'ArtistGenres' : str(playlist)})
    genres = artistDF[str(playlist)].sort_values(ascending=True).drop_duplicates()

    frame = pd.DataFrame(genres)    # Only needed so result can be returned to_html

    return frame.to_html(index=False)


def GetLikedSongsInfo(token_info):
    sp = spotipy.Spotify(auth=token_info)

    batchSize = 20  # Max amount of songs API can pull for at once
    desiredTotal = 10000  # Limit for liked songs that can be saved to spotify users' account

    iterations = (desiredTotal // batchSize) + (1 if desiredTotal % batchSize != 0 else 0)

    def parseBatchesJSON():
        for i in range(iterations):
            fromVal = i * batchSize
            currentBatchSize = min(batchSize, desiredTotal - fromVal)  # Handle last batch size

            likedSongs = sp.current_user_saved_tracks(limit=currentBatchSize, offset=fromVal)['items']
            
            # Collect artist IDs in batch for optimization
            artist_ids = []
            for song in likedSongs:
                for artist in song['track']['artists']:
                    artist_ids.append(artist['id'])

            artist_details = {artist["id"]: artist for artist in sp.artists(artist_ids)["artists"]}

            for song in likedSongs:
                for artist in song['track']['album']['artists']:  # For album table
                    album_type = song['track']['album']['album_type']
                    artist_name = artist['name']
                    artist_id = artist['id']
                    album_id = song['track']['album']['id']
                    album_name = song['track']['album']['name']
                    album_release_date = song['track']['album']['release_date']
                    album_uri = song['track']['album']['uri']
                    newArtistAlbumRow = f"('{album_type}', '{artist_name}', '{artist_id}', '{album_id}', '{album_name}', '{album_release_date}', '{album_uri}')\n"
                    yield newArtistAlbumRow
                
                for artist in song['track']['artists']:  # For song table
                    song_artist_id = artist['id']
                    song_artist_name = artist['name']
                    song_artist_uri = artist['uri']
                    song_id = song['track']['id']
                    song_name = song['track']['name']
                    song_popularity = song['track']['popularity']
                    song_uri = song['track']['uri']
                    saved_on_DateTime = song["added_at"][:10] + " " + song["added_at"][10:]

                    # Use pre-fetched artist details
                    artist_info = artist_details.get(song_artist_id, {})
                    song_artist_followers = str(artist_info.get('followers', {}).get('total', 0))
                    song_artist_genres = ','.join(artist_info.get('genres', []))

                    newArtistSongRow = f"('{song_artist_id}', '{song_artist_name}', '{song_artist_uri}', '{song_id}', '{song_name}', '{song_popularity}', '{song_uri}', '{saved_on_DateTime}', '{song_artist_followers}', '{song_artist_genres}')\n"
                    yield newArtistSongRow

    return Response(stream_with_context(parseBatchesJSON()), content_type='text/plain')


def ArtistSearchQuery(token, art):  # Get Artist Genres
    sp = token
    artist = art
    result = sp.search(artist, type='artist')
    artistName = result['artists']['items'][0]['name']
    artistGenres = result['artists']['items'][0]['genres']

    return artistName, artistGenres
