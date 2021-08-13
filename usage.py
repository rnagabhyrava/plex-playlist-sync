import os
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from helper import *

PLEX_URL = os.environ.get('PLEX_URL')
PLEX_TOKEN = os.environ.get('PLEX_TOKEN')

SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIFY_USER_ID = os.environ.get('SPOTIFY_USER_ID')

WAIT_SECONDS = int(os.environ.get('SECONDS_TO_WAIT'))
auth_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
)

plex = PlexServer(PLEX_URL, PLEX_TOKEN)
sp = spotipy.Spotify(auth_manager=auth_manager)
deez = deezer.Client()

# sp playlists
sp_playlists = get_sp_user_playlists(sp=sp, userId=SPOTIFY_USER_ID)

# deezer playlists
deez_playlist_ids = os.environ.get('DEEZER_PLAYLIST_ID').split()
deez_playlist_titles = [
    deez.get_playlist(code).title for code in deez_playlist_ids
]
deez_playlists = zip(deez_playlist_ids, deez_playlist_titles)

if not sp_playlists:
    logging.error("No spotify playlists found for given user")

if not deez_playlist_ids:
    logging.error("No deezer playlist code(s) found")


while True:
    logging.info("Starting playlist sync")
    for playlist, name in sp_playlists:
        track_names = get_sp_track_names(sp, SPOTIFY_USER_ID, playlist)
        trackList = get_available_plex_tracks(plex, track_names)
        create_plex_playlist(plex, tracksList=trackList,
                             playlistName="Spotify "+name)

    for playlist, name in deez_playlists:
        track_names = get_deez_playlist_track_names(deez, playlist)
        trackList = get_available_plex_tracks(plex, track_names)
        create_plex_playlist(plex, tracksList=trackList,
                             playlistName="Deezer "+name)

    logging.info("playlist sync complete")
    logging.info("sleeping for %s seconds" % WAIT_SECONDS)
    time.sleep(WAIT_SECONDS)
