import csv
import logging
import pathlib
import sys
from difflib import SequenceMatcher
from typing import List

from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer

from .helperClasses import Playlist, Track

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def _write_csv(tracks: List[Track], name: str, path: str = "/data") -> None:
    """Write given tracks with given name as a csv.

    Args:
        tracks (List[Track]): List of Track objects
        name (str): Name of the file to write to
    """
    # pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    data_folder = pathlib.Path(path)
    data_folder.mkdir(parents=True, exist_ok=True)
    file = data_folder / f"{name}.csv"

    with open(file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["title", "artist", "album", "url"])
        for track in tracks:
            writer.writerow([track.title, track.artist, track.album, track.url])


def _get_available_plex_tracks(plex: PlexServer, tracks: List[Track]) -> List:
    """Search given list of tracks in plex and
    returns list of tracks available in plex

    Args:
        plex (PlexServer): A configured PlexServer instance
        tracks (List[Track]): list of track objects

    Returns:
        List: of plex track objects
    """
    plex_tracks, missing_tracks = [], []
    for track in tracks:
        search = []
        try:
            search = plex.search(track.title, mediatype="track", limit=5)
        except BadRequest:
            logging.info("failed to search %s on plex", track.title)
        if (not search) or len(track.title.split("(")) > 1:
            logging.info("retrying search for %s", track.title)
            try:
                search += plex.search(
                    track.title.split("(")[0], mediatype="track", limit=5
                )
                logging.info("search for %s successful", track.title)
            except BadRequest:
                logging.info("unable to query %s on plex", track.title)

        found = False
        if search:
            for s in search:
                try:
                    artist_similarity = SequenceMatcher(
                        None, s.artist().title.lower(), track.artist.lower()
                    ).quick_ratio()

                    if artist_similarity >= 0.9:
                        plex_tracks.extend(s)
                        found = True
                        break

                    album_similarity = SequenceMatcher(
                        None, s.album().title.lower(), track.album.lower()
                    ).quick_ratio()

                    if album_similarity >= 0.9:
                        plex_tracks.extend(s)
                        found = True
                        break

                except IndexError:
                    logging.info(
                        "Looks like plex mismatched the search for %s, retrying with next result",
                        track,
                    )
        if not found:
            missing_tracks.append(track)

    return plex_tracks, missing_tracks


def _update_plex_playlist(
    plex: PlexServer, available_tracks: List, playlist: Playlist
) -> None:
    """Update existing plex playlist with new tracks and metadata.

    Args:
        plex (PlexServer): A configured PlexServer instance
        available_tracks (List): list of plex track objects
        playlist (Playlist): Playlist object

    Returns:
        plexapi.playlist: plex playlist object
    """
    plex_playlist = plex.playlist(playlist.name)
    plex_playlist.removeItems(plex_playlist.items())
    plex_playlist.addItems(available_tracks)
    return plex_playlist


def update_or_create_plex_playlist(
    plex: PlexServer,
    playlist: Playlist,
    tracks: List[Track],
    save_missing: bool = False,
    add_poster: bool = True,
    add_description: bool = True,
) -> None:
    """If playlist with same name exists, Updates existing playlist,
    else create a new playlist.

    Args:
        plex (PlexServer): A configured PlexServer instance
        available_tracks (List): List of plex.audio.track objects
        playlist (Playlist): Playlist object
    """
    available_tracks, missing_tracks = _get_available_plex_tracks(plex, tracks)
    if available_tracks:
        try:
            plex_playlist = _update_plex_playlist(plex, available_tracks, playlist)
            logging.info("Updated playlist %s", playlist.name)
        except NotFound:
            plex.createPlaylist(title=playlist.name, items=available_tracks)
            logging.info("Created playlist %s", playlist.name)
            plex_playlist = plex.playlist(playlist.name)

        if playlist.description and add_description:
            plex_playlist.edit(summary=playlist.description)
        if playlist.poster and add_poster:
            plex_playlist.uploadPoster(url=playlist.poster)
        logging.info("Updated playlist %s with summary and poster", playlist.name)

    else:
        logging.info(
            "No songs for playlist %s were found on plex, skipping the playlist creation",
            playlist.name,
        )
    if missing_tracks and save_missing:
        try:
            _write_csv(missing_tracks, playlist.name)
            logging.info("Missing tracks written to %s.csv", playlist.name)
        except:
            logging.info(
                "Failed to write missing tracks for %s, likely permission issue",
                playlist.name,
            )
