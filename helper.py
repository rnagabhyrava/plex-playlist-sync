import logging
import sys
from difflib import SequenceMatcher
from typing import List

import deezer
import spotipy
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

################### Spotify helpers ###################


def get_sp_user_playlists(sp: spotipy.Spotify, userId: str):
    """Gets all the playlist URIs for the given userId

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        userId (str): UserId of the spotify account (get it from open.spotify.com/account)

    Returns:
        tuple(list[str], list[str]): list of URIs, list of playlist names
    """
    playlists = sp.user_playlists(userId)
    return [[playlist['uri'], playlist['name']] for playlist in playlists['items']]


def get_sp_playlist_tracks(sp, userId: str, playlistId: str):
    """Gets tracks in a given playlist

    Args:
        sp ([type]): Spotify configured instance
        userId (str): UserId of the spotify account (get it from open.spotify.com/account)
        playlistId (str): Playlist URI

    Returns:
        List: A list of track objects
    """
    results = sp.user_playlist_tracks(userId, playlistId)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def get_sp_track_names(sp, userId: str, playlistId: str):
    """Returns the track names, artists of the given spotify playlist

    Args:
        sp ([type]): Spotify configured instance
        userId (str): UserId of the spotify account
        playlistId (str): Playlist URI

    Returns:
        zip(list, list): A zip object of track name and corresponding artist
    """
    trackNames, artistNames = [], []
    tracks = get_sp_playlist_tracks(sp, userId, playlistId)
    for track in tracks:
        trackNames.append(track['track']['name'])
        artistNames.append(track['track']['artists'][0]['name'])
    return zip(trackNames, artistNames)


################### Deezer helpers ###################


def get_dz_user_playlists(dz: deezer.Client(), userId: str):
    """Gets all the Deezer playlist URIs, title for the given userId

    Args:
        dz (deezer.Client): Deezer Client (no credentials needed)
        userId (str): UserId of the Deezer account (get it from url of deezer.com -> user profile)

    Returns:
        tuple(list[str], list[str]): list of URIs, list of playlist names
    """
    if not userId:
        return []
    playlists = dz.get_user(userId).get_playlists()
    return [[playlist.id, playlist.title] for playlist in playlists]


def get_dz_playlists_by_ids(dz: deezer.Client(), playlistIds: str):
    """Gets all the Deezer playlist URIs, title for the given playlistsIds(space separated)

    Args:
        dz (deezer.Client): Deezer Client (no credentials needed)
        playlistIds (str): Space separated playlist Ids

    Returns:
        tuple(list[str], list[str]): list of URIs, list of playlist names
    """
    dz_playlist_ids = playlistIds.split()

    playlists = [
        dz.get_playlist(id) for id in dz_playlist_ids
    ]

    return [[playlist.id, playlist.title] for playlist in playlists]


def get_dz_playlist_track_names(dz: deezer.Client(), playlistId: str):
    """Returns the track names, artists of the given deezer playlist Id

    Args:
        deezer (deezer.Client): Deezer Client (no credentials needed)
        playlistId (str): Playlist ID

    Returns:
        zip(list, list): A zip object of track name and corresponding artist
    """
    trackNames, artistNames = [], []
    tracks = dz.get_playlist(playlistId).tracks
    for track in tracks:
        trackNames.append(track.title)
        artistNames.append(track.artist.name)

    return zip(trackNames, artistNames)


################### Playlist Creation helpers ###################


def get_available_plex_tracks(plex: PlexServer, trackZip: List) -> List:
    """For the given spotify track names returns a list of plex.audio.track objects
        - Empty list if none of the tracks are found in Plex

    Args:
        plex (PlexServer): A configured PlexServer instance
        trackNames (List): List of track names

    Returns:
        List: of track objects
    """
    musicTracks = []
    for track, artist in trackZip:
        try:
            search = plex.search(track, mediatype='track', limit=5)
        except BadRequest:
            logging.info("failed to search %s on plex", track)
            search = []
        if not search:
            logging.info("retrying search for %s", track)
            try:
                search = plex.search(
                    track.split('(')[0], mediatype='track', limit=5
                )
                logging.info("search for %s successful", track)
            except BadRequest:
                logging.info("unable to query %s on plex", track)
                search = []

        if search:
            for s in search:
                try:
                    artistSimilarity = SequenceMatcher(
                        None, s.artist().title.lower(), artist.lower()
                    ).quick_ratio()
                    if s.artist().title.lower() == artist.lower() or artistSimilarity >= 0.8:
                        musicTracks.extend(s)
                        break

                except IndexError:
                    logging.info(
                        "Looks like plex mismatched the search for %s, retrying with next result", track)
    return musicTracks


def create_new_plex_playlist(plex: PlexServer, tracksList: List, playlistName: str) -> None:
    """Creates a new plex playlist with given name and tracks

    Args:
        plex (PlexServer): A configured PlexServer instance
        tracksList (List): List of plex.audio.track objects
        playlistName (str): Name of the playlist
    """
    plex.createPlaylist(title=playlistName, items=tracksList)


def create_plex_playlist(plex: PlexServer, tracksList: List, playlistName: str) -> None:
    """Deletes existing playlist (if exists) and
    creates a new playlist with given name and playlist name

    Args:
        plex (PlexServer): A configured PlexServer instance
        tracksList (List):List of plex.audio.track objects
        playlistName (str): Name of the playlist
    """
    if tracksList:
        try:
            plexPlaylist = plex.playlist(playlistName)
            plexPlaylist.delete()
            logging.info("Deleted existing playlist %s", playlistName)
            create_new_plex_playlist(plex, tracksList, playlistName)
            logging.info("Created playlist %s", playlistName)

        except NotFound:
            create_new_plex_playlist(plex, tracksList, playlistName)
            logging.info("Created playlist %s", playlistName)
    else:
        logging.info(
            "No songs for playlist %s were found on plex, skipping the playlist", playlistName)
