import spotipy
import pandas as pd
from flask import Response, stream_with_context

from DbHandling.StagingFeeders import stagingTable_Playlist, stagingTable_Artist, stagingTable_Track
from DbHandling.DestinationFeeders import MigratePlaylists, MigrateArtists, MigrateTracks
from DbHandling.Retrievers import getIds


def GetPlaylistInfo_single(token_info, playlist, owner): # Get a specific playlist's details
    sp = spotipy.Spotify(auth=token_info)

    result = sp.search(q=playlist, type='playlist')

    playIdMatch = ''
    getPlayInf = []
    for play in result['playlists']['items']:
        if play['owner']['display_name'].lower() == owner.lower():
            getPlayInf.append(play['id'])
            playIdMatch = getPlayInf[0]
            getPlayInf.append(play['name'])
            getPlayInf.append(play['owner']['display_name'])
            getPlayInf.append(play['tracks']['total'])
            getPlayInf.append(play['public'])
            getPlayInf.append(play['href'])
            getPlayInf.append(play["owner"]["type"])
            break

    if not playIdMatch:
        return {"error": "No matching playlist found for the given owner."}
    
    batchSize = 100
    desiredTotal = getPlayInf[3]
    iterations = (desiredTotal // batchSize) + (1 if desiredTotal % batchSize != 0 else 0)
    
    # Sets up respective table rows to be fed to staging via generator
    def JsonParsing():
        for i in range(iterations):
            fromVal = i * batchSize
            content = sp.playlist_items(playIdMatch, offset=fromVal)["items"]

            for song in content:
                # General Playlist Info
                playID = getPlayInf[0]
                playName = getPlayInf[1]
                playOwner = getPlayInf[2]
                playTrackCount = getPlayInf[3]
                playStatus = getPlayInf[4]
                playUrl = getPlayInf[5]
                playOwnerType = getPlayInf[6]

                # Song/Track Info
                song_id = song["track"]["id"]
                song_name = song["track"]["name"]
                song_popularity = song["track"]["popularity"]
                song_type = song["track"]["type"]
                song_duration = int(song["track"]["duration_ms"]*(1/1000))    # Converts song duration from milisecond to seconds
                song_explicit =song["track"]["explicit"]
                song_uri = song["track"]["uri"]

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

                newSongRow = (playID, playName, playUrl, playOwner, playOwnerType, playTrackCount, playStatus, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album)

                yield ("playlist", newSongRow)

                # Artist data
                for artist in song["track"]["artists"]:
                    track_artist_id = artist["id"]
                    track_artist_name = artist["name"]
                    track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                    associated_track_id = song_id
                    associated_track_name = song_name
                    
                    newArtistRow = (track_artist_id, track_artist_name, track_artist_genre, associated_track_id, associated_track_name)
                    
                    yield ("artist", newArtistRow)
    
    # Handles generator so, once feeders are finished, the rows can be validated and moved
    def genHandling():
        genOutput = JsonParsing()
        for tag,row in genOutput:
            if tag == "playlist":
                stagingTable_Playlist(row)
            elif tag == "artist":
                stagingTable_Artist(row)
            else:
                print(f"Unknown tag: {tag}")

            yield f"{row}\n"
        MigratePlaylists()
        MigrateArtists()
    
    return Response(stream_with_context(genHandling()), content_type='text/plain')


def GetPlaylistInfo_many(token_info): # Get all of a user's playlist details
    sp = spotipy.Spotify(auth=token_info)
    current_playlists = sp.current_user_playlists()['items']

    playIDs = []
    getPlayInf = {
        "playID": [],
        "playName": [],
        "playOwner": [],
        "playTrackCount": [],
        "playStatus": [],
        "playUrl": [],
        "playOwnerType": []
    }

    for play in current_playlists: # Get overview playlist data
        playIDs.append(play["id"])
        getPlayInf["playID"].append(play["id"])
        getPlayInf["playName"].append(play['name'])
        getPlayInf["playOwner"].append(play['owner']['display_name'])
        getPlayInf["playTrackCount"].append(play['tracks']['total'])
        getPlayInf["playStatus"].append(play['public'])
        getPlayInf["playUrl"].append(play['href'])
        getPlayInf["playOwnerType"].append(play["owner"]["type"])

    def JsonParsing():
        playIt = 0
        for row in playIDs:

            batchSize = 100
            playIndex = getPlayInf["playID"].index(row)
            desiredTotal = getPlayInf["playTrackCount"][playIndex]
            iterations = (desiredTotal // batchSize) + (1 if desiredTotal % batchSize != 0 else 0)

            for i in range(iterations):
                fromVal = i * batchSize
                content = sp.playlist_items(row, offset=fromVal)["items"]

                for song in content:
                    # General Playlist Info
                    playID = getPlayInf["playID"][playIt]
                    playName = getPlayInf["playName"][playIt]
                    playOwner = getPlayInf["playOwner"][playIt]
                    playTrackCount = getPlayInf["playTrackCount"][playIt]
                    playStatus = getPlayInf["playStatus"][playIt]
                    playUrl = getPlayInf["playUrl"][playIt]
                    playOwnerType = getPlayInf["playOwnerType"][playIt]

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
                                        
                    # Song/Track Info
                    song_id = song["track"]["id"]
                    song_name = song["track"]["name"]
                    song_popularity = song["track"]["popularity"]
                    song_type = song["track"]["type"]
                    song_duration = int(song["track"]["duration_ms"]*(1/1000))    # Converts song duration from milisecond to seconds
                    song_explicit =song["track"]["explicit"]
                    song_uri = song["track"]["uri"]

                    # Artist data
                    for artist in song["track"]["artists"]:
                        track_artist_id = artist["id"]
                        track_artist_name = artist["name"]
                        track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                        associated_track_id = song_id
                        associated_track_name = song_name
                        
                        newArtistRow = (track_artist_id, track_artist_name, track_artist_genre, associated_track_id, associated_track_name)

                        yield ("artist", newArtistRow)

                    newSongRow = (playID, playName, playUrl, playOwner, playOwnerType, playTrackCount, playStatus, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album)

                    yield ("playlist", newSongRow)

            playIt += 1

    def genHandling():
        genOutput = JsonParsing()
        for tag,row in genOutput:
            if tag == "playlist":
                stagingTable_Playlist(row)
            elif tag == "artist":
                stagingTable_Artist(row)
            else:
                print(f"Unknown tag: {tag}")

            yield f"{row}\n"
        MigratePlaylists()
        MigrateArtists()

    return Response(stream_with_context(genHandling()), content_type='text/plain')
    

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


def GetLikedSongsInfo(userName, token_info): # Get Liked songs details
    sp = spotipy.Spotify(auth=token_info)

    batchSize = 20  # Max amount of songs API can pull for at once
    desiredTotal = 10000  # Limit for liked songs that can be saved to spotify users' account

    iterations = (desiredTotal // batchSize) + (1 if desiredTotal % batchSize != 0 else 0)
    
    def JsonParsing():
        for i in range(iterations):
            fromVal = i * batchSize
            currentBatchSize = min(batchSize, desiredTotal - fromVal)  # Handle last batch size

            userCol = sp.current_user_saved_tracks(limit=currentBatchSize, offset=fromVal)
            likedSongs = userCol['items']

            playID = "LikedSongs_" + userName
            playName = "Liked Songs Collection"
            playOwner = userName
            playTrackCount = userCol['total']
            playStatus = "false"
            playUrl = userCol['href'].split('?')[0] # The standalone URL for the user's liked songs contains the limit and offset which is not ideal
            playOwnerType = "user"

            for song in likedSongs:

                # Song/Track Info
                song_id = song["track"]["id"]
                song_name = song["track"]["name"]
                song_popularity = song["track"]["popularity"]
                song_type = song["track"]["type"]
                song_duration = int(song["track"]["duration_ms"]*(1/1000))    # Converts song duration from milisecond to seconds
                song_explicit =song["track"]["explicit"]
                song_uri = song["track"]["uri"]

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

                newSongRow = (playID, playName, playUrl, playOwner, playOwnerType, playTrackCount, playStatus, song_id, song_name, song_popularity, song_type, song_duration, song_explicit, song_uri, object_type, album_id, album_name, album_release_date, album_artist_id, album_artist_name, album_object_type, album_total_tracks, other_object_type, album_uri, song_number_in_album)
                yield ("playlist", newSongRow)
                
                # For artist table
                for artist in song['track']['album']['artists']:
                    track_artist_id = artist["id"]
                    track_artist_name = artist["name"]
                    track_artist_genre = ','.join([i for i in sp.artist(track_artist_id)['genres']])
                    associated_track_id = song_id
                    associated_track_name = song_name

                    newArtistRow = (track_artist_id, track_artist_name, track_artist_genre, associated_track_id, associated_track_name)
                    yield ("artist", newArtistRow)

    # Handles generator so, once feeders are finished, the rows can be validated and moved
    def genHandling():
        genOutput = JsonParsing()
        for tag,row in genOutput:
            if tag == "playlist":
                stagingTable_Playlist(row)
            elif tag == "artist":
                stagingTable_Artist(row)
            else:
                print(f"Unknown tag: {tag}")

            yield f"{row}\n"
        MigratePlaylists()
        MigrateArtists()
    

    return Response(stream_with_context(genHandling()), content_type='text/plain')


def ArtistSearchQuery(token, art):  # Get Artist Genres
    sp = token
    artist = art
    result = sp.search(artist, type='artist')
    artistName = result['artists']['items'][0]['name']
    artistGenres = result['artists']['items'][0]['genres']

    return artistName, artistGenres


def GetTrackDetails(token_info):
    sp = spotipy.Spotify(auth=token_info)

    sourceTab = "PlaylistDetails"

    dbTracks = [i[0] for i in getIds(sourceTab)] # Gets list of song IDs through existing DB tables instead of requests
    batchSize = 50
    total = len(dbTracks)
    iterations = (total // batchSize) + (1 if total % batchSize != 0 else 0)

    def JsonParsing():
        for i in range(iterations):
            fromVal = i * batchSize
            currentBatchSize = min(batchSize, total - fromVal)
            currentTracks = dbTracks[fromVal:fromVal+currentBatchSize]
            
            for song in sp.tracks(currentTracks)["tracks"]:
                for IDs in song["external_ids"]:
                    songID = song["id"]
                    externalIDType = IDs
                    externalID = song["external_ids"][IDs]
                    song_uri = song['uri']
                    songName = song['name']
                    local = song['is_local']
                    objectType = song['type']
                    isExplicit = song['explicit']
                    discNumber = song['disc_number']
                    duration = int(song['duration_ms']*(1/1000))

                    newSongRow = (songID, externalID, externalIDType, song_uri, songName, local, objectType, isExplicit, discNumber, duration)
                    
                    yield ("trackMapping", newSongRow)

    def genHandling():
        genOutput = JsonParsing()
        for tag,row in genOutput:
            if tag == "trackMapping":
                stagingTable_Track(row)
            else:
                print(f"Unknown tag: {tag}")

            yield f"{row}\n"
        MigrateTracks()
    
    return Response(stream_with_context(genHandling()), content_type='text/plain')