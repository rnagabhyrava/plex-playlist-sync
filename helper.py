from plexapi.server import PlexServer
import spotipy
from spotipy import Spotify
from typing import List
import logging
from plexapi.audio import Track



def get_sp_user_playlists(sp: spotipy.Spotify, userId: str):
    """Gets all the playlist URIs for the given userId

    Args:
        sp (spotipy.Spotify): Spotify configured instance
        userId (str): UserId of the spotify account (get it from open.spotify.com/account)

    Returns:
        list[str]: list of URIs
    """
    playlists = sp.user_playlists(userId)
    return ([(playlist['uri'], playlist['name']) for playlist in playlists['items']])


def get_sp_playlist_tracks(sp, userId: str, playlistId: str) -> List:
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
    trackNames = []
    tracks = get_sp_playlist_tracks(sp, userId, playlistId)
    for track in tracks:
        trackNames.append(track['track']['name'])
    return trackNames


def get_available_plex_tracks(plex: PlexServer, trackNames: List):
    musicTracks = []
    for track in trackNames:
        search = []
        search = plex.search(track, mediatype='track', limit=1)
        if not search:
            search = plex.search(track.split('(')[0], mediatype='track', limit=1)
        if search and (search[0].title[:3].lower() != track[:3].lower()):
            search = [] 
        if search:
            musicTracks.extend(search)
    return musicTracks


def create_new_plex_playlist(plex: PlexServer, tracksList, playlistName):
    logging.info('Created playlist %s' % playlistName)
    plex.createPlaylist(title=playlistName, items=tracksList)
    logging.info('%s created' % playlistName)

def create_plex_playlist(plex: PlexServer, tracksList, playlistName):
    try:
        plexPlaylist = plex.playlist(playlistName)
        plexPlaylist.delete()
        create_new_plex_playlist(plex, tracksList, playlistName)
    except:
        create_new_plex_playlist(plex, tracksList, playlistName)
        logging.warn("Failed to create playlist %s" % playlistName)