import logging
from typing import List

import spotipy
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track, UserInputs
from .plex import update_or_create_plex_playlist


def _get_sp_user_playlists(
    sp: spotipy.Spotify, user_id: str, suffix: str = " - Spotify"
) -> List[Playlist]:
    """Get metadata for playlists in the given user_id.

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
        while sp_playlists:
            for playlist in sp_playlists['items']:
                playlists.append(
                    Playlist(
                        id=playlist["uri"],
                        name=playlist["name"] + suffix,
                        description=playlist.get("description", ""),
                        # playlists may not have a poster in such cases return ""
                        poster=""
                        if len(playlist["images"]) == 0
                        else playlist["images"][0].get("url", ""),
                    )
                )
            if sp_playlists['next']:
                sp_playlists = sp.next(sp_playlists)
            else:
                sp_playlists = None
    except:
        logging.error("Spotify User ID Error")
    return playlists


def _get_sp_tracks_from_playlist(
    sp: spotipy.Spotify, user_id: str, playlist: Playlist
) -> List[Track]:
    """Return list of tracks with metadata.

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        user_id (str): spotify user id
        playlist (Playlist): Playlist object
    Returns:
        List[Track]: list of Track objects with track metadata fields
    """

    def extract_sp_track_metadata(track) -> Track:
        title = track["track"]["name"]
        artist = track["track"]["artists"][0]["name"]
        album = track["track"]["album"]["name"]
        # Tracks may no longer be on spotify in such cases return ""
        url = track["track"]["external_urls"].get("spotify", "")
        return Track(title, artist, album, url)

    sp_playlist_tracks = sp.user_playlist_tracks(user_id, playlist.id)

    # Only processes first 100 tracks
    tracks = list(
        map(
            extract_sp_track_metadata,
            [i for i in sp_playlist_tracks["items"] if i.get("track")],
        )
    )

    # If playlist contains more than 100 tracks this loop is useful
    while sp_playlist_tracks["next"]:
        sp_playlist_tracks = sp.next(sp_playlist_tracks)
        tracks.extend(
            list(
                map(
                    extract_sp_track_metadata,
                    [i for i in sp_playlist_tracks["items"] if i.get("track")],
                )
            )
        )
    return tracks


def spotify_playlist_sync(
    sp: spotipy.Spotify, plex: PlexServer, userInputs: UserInputs
) -> None:
    """Create/Update plex playlists with playlists from spotify.

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        user_id (str): spotify user id
        plex (PlexServer): A configured PlexServer instance
    """
    playlists = _get_sp_user_playlists(
        sp,
        userInputs.spotify_user_id,
        " - Spotify" if userInputs.append_service_suffix else "",
    )
    if playlists:
        for playlist in playlists:
            tracks = _get_sp_tracks_from_playlist(
                sp, userInputs.spotify_user_id, playlist
            )
            update_or_create_plex_playlist(plex, playlist, tracks, userInputs)
    else:
        logging.error("No spotify playlists found for given user")
