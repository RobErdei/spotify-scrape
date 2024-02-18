This is a Flask webapp that facilitates the OAuth authentication flow in order to communicate with Spotify's API and extract song data. Once the API retrieves the data in the form of a JSON document, that doc is parsed through to have a CSV/tabulor output for easier analysis.
The webapp was treated as a means for aunthetication so, to avoid clutter, the main functions were imported as modules..

Notable Modules:
GetPlaylistInfo - Retrieves info of all playlists and then retrieves individual song/artist information from each of the playlists retrieved, mapping the playlist info table to the song info table via a merge operation. 
GetLikedSongsInfo - Retrieves data from both the song and it's associated album(s). Because of Spotify's limit of 50 saved tracks being retrieved at a time, the process is looped by 20 songs until a total of a set number have been retrieved.
