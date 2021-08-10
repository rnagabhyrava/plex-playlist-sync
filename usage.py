import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from helper import *

baseurl = 'http://192.168.1.99:32400'
token = '_oiMrxQaAc-LdBosBWyb'
plex = PlexServer(baseurl, token)

# TODO: Set as env variables"
SPOTIPY_CLIENT_ID = "0d5191aca40a4c5d8d8d994c17fc0802"
SPOTIPY_CLIENT_SECRET = "0bdfaf1e33ed415296129bde0890b065"
USER_ID = "pe1myvbjlnx1i5eqw1e8k09h7"
SCOPE = "user-library-read"

auth_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = get_sp_user_playlists(sp=sp, userId=USER_ID)

for playlist, name in playlists:
    track_names = get_sp_track_names(sp, USER_ID, playlist)
    trackList = get_available_plex_tracks(plex, track_names)
    create_plex_playlist(plex, tracksList=trackList, playlistName=name)
