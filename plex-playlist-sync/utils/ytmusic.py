import logging
import re
from typing import Dict, List, Tuple

import ytmusicapi
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track
from .plex import update_or_create_plex_playlist


def _get_ytm_playlist_and_tracks(
    yt: ytmusicapi.YTMusic, playlist_id: str, suffix: str = " - YTMusic"
) -> Tuple[Playlist, List[Track]]:
    """Get metadata for playlist and tracks for given playlist_id.

    Args:
        yt (ytmusicapi.YTMusic): YTM Client (no credentials needed)
        playlist_id (str): ytm playlist id
        suffix (str): Identifier for source

    Returns:
        Tuple[Playlist, List[Track]]: A tuple with Playlist and list of Tracks.
    """
    try:
        ytplaylist = yt.get_playlist(playlistId=playlist_id)
        playlist = Playlist(
            id=ytplaylist["id"],
            name=ytplaylist["title"],
            description=ytplaylist["description"],
            poster=ytplaylist["thumbnails"][-1]["url"],
        )
    except:
        playlist = None
        logging.info("Unable to get YT playlist %s" % playlist_id)
    tracks = []
    if playlist:
        for track in ytplaylist["tracks"]:
            title = re.split(
                "\\(Official|\\[Official|\\(Audio|\\[Audio|\\(Lyric|\\[Lyric]",
                track["title"],
                flags=re.IGNORECASE,
            )[0].strip()
            tracks.append(
                Track(
                    title=title,
                    artist=track["artists"][0]["name"],
                    album=track["album"]["name"] if track["album"] else None,
                    url="https://music.youtube.com/watch?v="
                    + track["videoId"],
                )
            )
    return (playlist, tracks)


def ytm_playlist_sync(
    yt: ytmusicapi.YTMusic, plex: PlexServer, userInputs: Dict
) -> None:
    """Create/Update plex playlists with playlists from yt music.

    Args:
        yt (ytmusicapi.YTMusic): YTM Client (no credentials needed)
        plex (PlexServer): A configured PlexServer instance
        userInputs (Dict): Inputs from user
    """

    for playlist_id in userInputs["ytm_playlist_ids"].split():
        playlist, tracks = _get_ytm_playlist_and_tracks(yt, playlist_id)
        if playlist and tracks:
            update_or_create_plex_playlist(plex, playlist, tracks, userInputs)
