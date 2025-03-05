# Spotify Scraper

This is a Flask webapp that facilitates the OAuth authentication flow in order to communicate with Spotify's API and extract song data. The OAuth process is relegated to a single script to avoid clutter. The site currently has 4 Functionalities: 
![image](https://github.com/user-attachments/assets/9631340d-0a67-4f65-848d-8368a9542221)


## Get Playlist Info
This button retrieves the playlist, artist and song details of either all or specific playlists under a user's profile.

## Get Liked Songs Info
This button retrieves all song, album and artist details from the user's liked songs.

## Search Artist(s) Genres
This button takes a list of artist names (to be filled out by the user) and queries the genres spotify assigned to them. Genres through the Spotify API are only assigned on an artist level, not to any particular song of theirs.

## Get Playlist Genres
Retrieves the genres of all artists present in a specified playlist. Required arguments are the playlist's name and it's owner.
