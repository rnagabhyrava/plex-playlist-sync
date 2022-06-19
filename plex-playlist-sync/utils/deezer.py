import logging
from typing import List

from plexapi.server import PlexServer

import deezer

from .helperClasses import Playlist, Track
from .plex import update_or_create_plex_playlist


def _get_dz_playlists(
    dz: deezer.Client(),
    user_id: str = None,
    playlist_ids: str = None,
    suffix: str = " - Deezer",
) -> List[Playlist]:
    """Gets metadata for playlists in the given user_id

    Args:
        dz (deezer.Client): Deezer Client (no credentials needed)
        user_id (str): UserId of the Deezer account (get it from url of deezer.com -> user profile)
        playlist_ids (str): deezer playlist ids as space seperated string
        suffix (str): Identifier for source
    Returns:
        List[Playlist]: list of Playlist objects with playlist metadata fields
    """
    dz_user_playlists, dz_id_playlists = [], []

    if user_id:
        try:
            dz_user_playlists = dz.get_user(user_id).get_playlists()
        except:
            dz_user_playlists = []
            logging.info(
                "Can't get playlists from this user, skipping deezer user playlists"
            )

    if playlist_ids:
        try:
            dz_playlist_ids = playlist_ids.split()
            dz_id_playlists = [dz.get_playlist(id) for id in dz_playlist_ids]
        except:
            dz_id_playlists = []
            logging.info(
                "Unable to get the playlists from given ids, skipping deezer playlists for IDs"
            )

    dz_playlists = list(set(dz_user_playlists + dz_id_playlists))

    playlists = []
    if dz_playlists:
        for playlist in dz_playlists:
            d = playlist.as_dict()
            playlists.append(
                Playlist(
                    id=d["id"],
                    name=d["title"] + suffix,
                    description=d.get("description", ""),
                    poster=d["picture_big"],
                )
            )
    return playlists


def _get_dz_tracks_from_playlist(
    dz: deezer.Client(),
    playlist: Playlist,
) -> List[Track]:
    """Returns list of tracks with metadata

    Args:
        dz (deezer.Client): Deezer Client (no credentials needed)
        playlist (Playlist): Playlist object

    Returns:
        List[Track]: list of Track objects with track metadata fields
    """

    def extract_dz_track_metadata(track):
        track = track.as_dict()
        title = track["title"]
        artist = track["artist"]["name"]
        album = track["album"]["title"]
        url = track["link"]
        return Track(title, artist, album, url)

    dz_playlist_tracks = dz.get_playlist(playlist.id).tracks

    return list(map(extract_dz_track_metadata, dz_playlist_tracks))


def deezer_playlist_sync(
    dz: deezer.Client(),
    user_id: str,
    playlist_ids: str,
    plex: PlexServer,
    save_missing: bool,
    add_poster: bool,
    add_description: bool,
) -> None:
    """Creates/Updates plex playlists with playlists from deezer

    Args:
        dz (deezer.Client):  Deezer Client (no credentials needed)
        user_id (str): UserId of the Deezer account (get it from url of deezer.com -> user profile)
        playlist_ids (str): deezer playlist ids as space seperated string
        plex (PlexServer): A configured PlexServer instance
    """
    playlists = _get_dz_playlists(dz, user_id, playlist_ids)
    if playlists:
        for playlist in playlists:
            tracks = _get_dz_tracks_from_playlist(dz, playlist)
            update_or_create_plex_playlist(
                plex, playlist, tracks, save_missing, add_poster, add_description
            )
    else:
        logging.error("No deezer playlists found for given user")
