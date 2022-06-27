import logging
import os
import time

import deezer
import spotipy
from plexapi.server import PlexServer
from spotipy.oauth2 import SpotifyClientCredentials

from utils.deezer import deezer_playlist_sync
from utils.helperClasses import UserInputs
from utils.spotify import spotify_playlist_sync

# Read ENV variables
userInputs = UserInputs(
    plex_url=os.environ.get("PLEX_URL"),
    plex_token=os.environ.get("PLEX_TOKEN"),
    write_missing_as_csv=os.environ.get("WRITE_MISSING_AS_CSV", "0") == "1",
    add_playlist_poster=os.environ.get("ADD_PLAYLIST_POSTER", "1") == "1",
    add_playlist_description=os.environ.get("ADD_PLAYLIST_DESCRIPTION", "1") == "1",
    append_instead_of_sync=os.environ.get("APPEND_INSTEAD_OF_SYNC", False) == "1",
    wait_seconds=int(os.environ.get("SECONDS_TO_WAIT", 86400)),
    spotipy_client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
    spotipy_client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
    spotify_user_id=os.environ.get("SPOTIFY_USER_ID"),
    deezer_user_id=os.environ.get("DEEZER_USER_ID"),
    deezer_playlist_ids=os.environ.get("DEEZER_PLAYLIST_ID"),
)
while True:
    logging.info("Starting playlist sync")

    if userInputs.plex_url and userInputs.plex_token:
        try:
            plex = PlexServer(userInputs.plex_url, userInputs.plex_token)
        except:
            logging.error("Plex Authorization error")
            break
    else:
        logging.error("Missing Plex Authorization Variables")
        break

    ########## SPOTIFY SYNC ##########

    logging.info("Starting Spotify playlist sync")

    SP_AUTHSUCCESS = False

    if (
        userInputs.spotipy_client_id
        and userInputs.spotipy_client_secret
        and userInputs.spotify_user_id
    ):
        try:
            sp = spotipy.Spotify(
                auth_manager=SpotifyClientCredentials(
                    userInputs.spotipy_client_id, userInputs.spotipy_client_secret
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
        spotify_playlist_sync(sp, plex, userInputs)

    logging.info("Spotify playlist sync complete")

    ########## DEEZER SYNC ##########

    logging.info("Starting Deezer playlist sync")
    dz = deezer.Client()
    deezer_playlist_sync(dz, plex, userInputs)
    logging.info("Deezer playlist sync complete")

    logging.info("All playlist(s) sync complete")
    logging.info("sleeping for %s seconds" % userInputs.wait_seconds)

    time.sleep(userInputs.wait_seconds)
