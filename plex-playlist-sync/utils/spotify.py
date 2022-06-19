import logging
from typing import List

import spotipy
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track
from .plex import update_or_create_plex_playlist


def _get_sp_user_playlists(
    sp: spotipy.Spotify, user_id: str, suffix: str = " - Spotify"
) -> List[Playlist]:
    """Gets metadata for playlists in the given user_id
    Args:
        sp (spotipy.Spotify): Spotify configured instance
        userId (str): UserId of the spotify account (get it from open.spotify.com/account)
        suffix (str): Identifier for source
    Returns:
        List[Playlist]: list of Playlist objects with playlist metadata fields
    """

    playlists = []

    try:
        sp_playlists = sp.user_playlists(user_id)
        for playlist in sp_playlists["items"]:
            playlists.append(
                Playlist(
                    id=playlist["uri"],
                    name=playlist["name"] + suffix,
                    description=playlist.get("description", ""),
                    poster=playlist["images"][0].get("url", ""),
                )
            )
    except:
        logging.error("Spotify User ID Error")
    return playlists


def _get_sp_tracks_from_playlist(
    sp: spotipy.Spotify, user_id: str, playlist: Playlist
) -> List[Track]:
    """Returns list of tracks with metadata
    Args:
        sp (spotipy.Spotify): Spotify configured instance
        user_id (str): spotify user id
        playlist (Playlist): Playlist object
    Returns:
        List[Track]: list of Track objects with track metadata fields
    """

    def extract_sp_track_metadata(track):
        title = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        album = track["track"]["album"]["name"]
        url = track["track"]["external_urls"]["spotify"]
        return Track(title, artist, album, url)

    sp_playlist_tracks = sp.user_playlist_tracks(user_id, playlist.id)

    # Only processes first 100 tracks
    tracks = list(map(extract_sp_track_metadata, sp_playlist_tracks["items"]))

    # If playlist contains more than 100 tracks this loop is useful
    while sp_playlist_tracks["next"]:
        sp_playlist_tracks = sp.next(sp_playlist_tracks)
        tracks.extend(list(map(extract_sp_track_metadata, sp_playlist_tracks["items"])))
    return tracks


def spotify_playlist_sync(
    sp: spotipy.Spotify,
    user_id: str,
    plex: PlexServer,
    save_missing: bool,
    add_poster: bool,
    add_description: bool,
) -> None:
    """Creates/Updates plex playlists with playlists from spotify

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        user_id (str): spotify user id
        plex (PlexServer): A configured PlexServer instance
    """
    playlists = _get_sp_user_playlists(sp, user_id)
    if playlists:
        for playlist in playlists:
            tracks = _get_sp_tracks_from_playlist(sp, user_id, playlist)
            update_or_create_plex_playlist(
                plex, playlist, tracks, save_missing, add_poster, add_description
            )
    else:
        logging.error("No spotify playlists found for given user")
