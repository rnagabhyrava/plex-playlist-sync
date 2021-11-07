import os
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from helper import *

# Read ENV variables
PLEX_URL = os.environ.get('PLEX_URL')
PLEX_TOKEN = os.environ.get('PLEX_TOKEN')

SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIFY_USER_ID = os.environ.get('SPOTIFY_USER_ID')

DEEZER_USER_ID = os.environ.get('DEEZER_USER_ID')
DEEZER_PLAYLIST_IDS = os.environ.get('DEEZER_PLAYLIST_ID')

WAIT_SECONDS = int(os.environ.get('SECONDS_TO_WAIT'))

spAuthSuccess = False


def auth_spotify(client_id: str, client_secret: str):
    """Creates a spotify authenticator

    Args:
        client_id (str): Spotify client ID
        client_secret (str): Spotify client secret

    Returns:
        sp: spotify configured client
    """
    auth = SpotifyClientCredentials(client_id, client_secret)
    return spotipy.Spotify(auth_manager=auth)


while True:
    logging.info("Starting playlist sync")

    if PLEX_URL and PLEX_TOKEN:
        try:
            plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        except:
            logging.error("Plex Authorization error")
            break

    if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET and SPOTIFY_USER_ID:
        try:
            sp = auth_spotify(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)
            spAuthSuccess = True
        except:
            logging.info("Spotify Authorization error, skipping spotify sync")

    dz = deezer.Client()

    # spotify playlists
    if spAuthSuccess:
        logging.info("Starting spotify playlist sync")
        try:
            sp_playlists = get_sp_user_playlists(sp=sp, userId=SPOTIFY_USER_ID)
        except:
            logging.error("Spotify User ID Error")
            sp_playlists = []

        if not sp_playlists:
            logging.error("No spotify playlists found for given user")
        else:
            for playlist, name in sp_playlists:
                track_names = get_sp_track_names(sp, SPOTIFY_USER_ID, playlist)
                trackList = get_available_plex_tracks(plex, track_names)
                create_plex_playlist(plex, tracksList=trackList,
                                     playlistName=name+" - Spotify")
            logging.info("Spotify playlist sync complete")

    # deezer playlists
    logging.info("Starting Deezer playlist sync")
    dz_user_playlists, dz_id_playlists = [], []
    if DEEZER_USER_ID:
        try:
            dz_user_playlists = get_dz_user_playlists(
                dz=dz, userId=DEEZER_USER_ID
            )
        except:
            dz_user_playlists = []
            logging.info(
                "Can't get playlists from this user, skipping deezer user playlists"
            )

    if DEEZER_PLAYLIST_IDS:
        try:
            dz_id_playlists = get_dz_playlists_by_ids(
                dz=dz, playlistIds=DEEZER_PLAYLIST_IDS
            )
        except:
            dz_id_playlists = []
            logging.info(
                "Unable to get the playlists from given ids, skipping deezer playlists for IDs"
            )

    dz_playlists = dz_user_playlists + dz_id_playlists
    # remove duplicates if any
    dz_playlists = [list(t) for t in set([tuple(t) for t in dz_playlists])]

    if not dz_playlists:
        logging.error("No deezer playlist code(s) found")
    else:
        for playlist, name in dz_playlists:
            track_names = get_dz_playlist_track_names(dz, playlist)
            trackList = get_available_plex_tracks(plex, track_names)
            create_plex_playlist(plex, tracksList=trackList,
                                 playlistName=name+" - Deezer")
        logging.info("Deezer playlist sync complete")

    logging.info("All playlist(s) sync complete")
    logging.info("sleeping for %s seconds" % WAIT_SECONDS)
    time.sleep(WAIT_SECONDS)
