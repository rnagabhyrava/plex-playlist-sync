import logging
import os
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from utils.deezer import deezer_playlist_sync
from utils.spotify import spotify_playlist_sync

# Read ENV variables
PLEX_URL = os.environ.get("PLEX_URL")
PLEX_TOKEN = os.environ.get("PLEX_TOKEN")

WRITE_MISSING_AS_CSV = os.environ.get("WRITE_MISSING_AS_CSV", "0") == "1"
ADD_PLAYLIST_POSTER = os.environ.get("ADD_PLAYLIST_POSTER", "1") == "1"
ADD_PLAYLIST_DESCRIPTION = os.environ.get("ADD_PLAYLIST_DESCRIPTION", "1") == "1"

SPOTIPY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_USER_ID = os.environ.get("SPOTIFY_USER_ID")

DEEZER_USER_ID = os.environ.get("DEEZER_USER_ID")
DEEZER_PLAYLIST_IDS = os.environ.get("DEEZER_PLAYLIST_ID")

WAIT_SECONDS = int(os.environ.get("SECONDS_TO_WAIT", 86400))

while True:
    logging.info("Starting playlist sync")

    if PLEX_URL and PLEX_TOKEN:
        try:
            plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        except:
            logging.error("Plex Authorization error")
            break
    else:
        logging.error("Missing Plex Authorization Variables")
        break

    ########## SPOTIFY SYNC ##########

    logging.info("Starting Spotify playlist sync")

    SP_AUTHSUCCESS = False

    if SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET and SPOTIFY_USER_ID:
        try:
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
                )
            )
            SP_AUTHSUCCESS = True
        except:
            logging.info("Spotify Authorization error, skipping spotify sync")

    else:
        logging.info(
            "Missing one or more Spotify Authorization Variables, skipping spotify sync"
        )

    if SP_AUTHSUCCESS:
        spotify_playlist_sync(
            sp,
            SPOTIFY_USER_ID,
            plex,
            WRITE_MISSING_AS_CSV,
            ADD_PLAYLIST_POSTER,
            ADD_PLAYLIST_DESCRIPTION,
        )

    logging.info("Spotify playlist sync complete")

    ########## DEEZER SYNC ##########

    logging.info("Starting Deezer playlist sync")
    dz = deezer.Client()
    deezer_playlist_sync(
        dz,
        DEEZER_USER_ID,
        DEEZER_PLAYLIST_IDS,
        plex,
        WRITE_MISSING_AS_CSV,
        ADD_PLAYLIST_POSTER,
        ADD_PLAYLIST_DESCRIPTION,
    )
    logging.info("Deezer playlist sync complete")

    logging.info("All playlist(s) sync complete")
    logging.info("sleeping for %s seconds" % WAIT_SECONDS)

    time.sleep(WAIT_SECONDS)
