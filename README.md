# Plex Playlist Sync

Gets an accounts spotify and/or deezer playlist(s) and creates playlist(s) in plex with media already available on plex server.

This DOES NOT download any songs from anywhere.

## Features
* From Spotify: Sync all of the given user account's public playlists to plex
* From Deezer: Sync all of the given user account's public playlists and/or any given public playlist IDs to plex

## Prerequisites
### Plex
* Plex server's host and port
* Plex token - [Don't know where to find it?](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

### To use Spotify sync
* Spotify client ID and client secret - Can be obtained from [spotify developer](https://developer.spotify.com/dashboard/login)
* Spotify user ID - This can be found on spotify [account page](https://www.spotify.com/us/account/overview/)

### To use Deezer sync
* Deezer profile ID of the account from which playlists need to sync from
  * Login to deezer.com
  * Click on your profile
  * Grab the profile ID from the URLCancel changes
  *  Example: https://www.deezer.com/us/profile/9999999 - Here 9999999 is the profile ID
OR
* Get playlists IDs of playlists you want to sync
  *  Example: https://www.deezer.com/us/playlist/1313621735 - Here 1313621735 is the playlist ID

## Docker Setup
You need either docker or docker with docker-compose to run this. Configure the parameters as needed. Plex URL and TOKEN are mandatory and either one of the Optinal (1,2,3) fields are required.

### Docker Run (Untested)

```
docker run -d \
  --name=playlistSync \
  -e PLEX_URL= <your local plex url> \
  -e PLEX_TOKEN=<your plex token> \
  -e SPOTIPY_CLIENT_ID=<your spotify client id> # Optional 1 \
  -e SPOTIPY_CLIENT_SECRET=<your spotify client secret> # Optional 1 \
  -e DEEZER_USER_ID=<your spotify user id> # Optional 2 \
  -e DEEZER_PLAYLIST_ID= #<deezer playlist ids space seperated> # Optional 3
  -e SECONDS_TO_WAIT=84000 # Seconds to wait between syncs
  --restart unless-stopped \
  rnagabhyrava/plexplaylistsync:latest
```

### Docker Compose

docker-compose.yml can be configured as follows. See docker-compose-example.yml for example
```
version: "2.1"
services:
  playlistSync:
    image: rnagabhyrava/plexplaylistsync:latest
    container_name: playlistSync
    environment:
      - PLEX_URL= <your local plex url>
      - PLEX_TOKEN=<your plex token>
      - SPOTIPY_CLIENT_ID=<your spotify client id> # Optional 1
      - SPOTIPY_CLIENT_SECRET=<your spotify client secret> # Optional 1
      - SPOTIFY_USER_ID=<your spotify user id> # Optional 1
      - DEEZER_USER_ID=<your spotify user id> # Optional 2
      - DEEZER_PLAYLIST_ID= #<deezer playlist ids space seperated> # Optional 3
      - SECONDS_TO_WAIT=84000 # Seconds to wait between syncs
    restart: unless-stopped
```
And run with :
```
docker-compose up
```

### Issues
Something's off? See room for improvement? Feel free to open an issue with as much info as possible. Cheers!
