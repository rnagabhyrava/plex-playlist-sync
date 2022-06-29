# Plex Playlist Sync

Create spotify and deezer playlists in your plex account using tracks from your server and keeps plex playlists in sync with original playlists. 

This DOES NOT download any songs from anywhere.

## Features
* From Spotify: Sync all of the given user account's public playlists to plex
* From Deezer: Sync all of the given user account's public playlists and/or any given public playlist IDs to plex
* --- New ---
* Option to write missing songs as a csv
* Option to include poster and description in playlists.

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
  * Grab the profile ID from the URL
  *  Example: https://www.deezer.com/us/profile/9999999 - Here 9999999 is the profile ID
OR
* Get playlists IDs of playlists you want to sync
  *  Example: https://www.deezer.com/us/playlist/1313621735 - Here 1313621735 is the playlist ID

## Docker Setup
You need either docker or docker with docker-compose to run this. Docker images are available on [the hub](https://hub.docker.com/r/rnagabhyrava/plexplaylistsync/tags) for amd64, arm64 and arm/v7 and will be auto pulled based on your platform.

Configure the parameters as needed. Plex URL and TOKEN are mandatory and either one of the Options (1,2,3) fields are required.

### Docker Run

```
docker run -d \
  --name=playlistSync \
  -e PLEX_URL=<your local plex url> \
  -e PLEX_TOKEN=<your plex token> \
  -e WRITE_MISSING_AS_CSV=<1 or 0> # Default 0, 1 = writes missing tracks from each playlist to a csv
  -e ADD_PLAYLIST_POSTER=<1 or 0> # Default 1, 1 = add poster for each playlist
  -e ADD_PLAYLIST_DESCRIPTION=<1 or 0> # Default 1, 1 = add description for each playlist
  -e APPEND_INSTEAD_OF_SYNC=0 # Default 0, 1 = Sync tracks, 0 = Append only
  -e SECONDS_TO_WAIT=84000 # Seconds to wait between syncs \
  -e SPOTIFY_CLIENT_ID=<your spotify client id> # Option 1 \
  -e SPOTIFY_CLIENT_SECRET=<your spotify client secret> # Option 1 \
  -e SPOTIFY_USER_ID=<your spotify user id from the account page> # Option 1 \
  -e DEEZER_USER_ID=<your deezer user id> # Option 2 \
  -e DEEZER_PLAYLIST_ID= #<deezer playlist ids space seperated> # Option 3 \
  -v <Path where you want to write missing tracks>:/data \
  --restart unless-stopped \
  rnagabhyrava/plexplaylistsync:latest
```
#### Notes
- Include `http://` in the PLEX_URL
- Remove comments (ex: `# Optional x`) before running 

### Docker Compose

docker-compose.yml can be configured as follows. See [docker-compose-example.yml](https://github.com/rnagabhyrava/plex-playlist-sync/blob/main/docker-compose-example.yml) for example
```
version: "2.1"
services:
  playlistSync:
    image: rnagabhyrava/plexplaylistsync:latest
    container_name: playlistSync
    # optional only if you chose WRITE_MISSING_AS_CSV=1 in env
    volumes:
      - <Path where you want to write missing tracks>:/data
    environment:
      - PLEX_URL= <your local plex url>
      - PLEX_TOKEN=<your plex token>
      - WRITE_MISSING_AS_CSV=<1 or 0> # Default 0, 1 = writes missing tracks from each playlist to a csv
      - ADD_PLAYLIST_POSTER=<1 or 0> # Default 1, 1 = add poster for each playlist
      - ADD_PLAYLIST_DESCRIPTION=<1 or 0> # Default 1, 1 = add description for each playlist
      - APPEND_INSTEAD_OF_SYNC=0 # Default 0, 1 = Sync tracks, 0 = Append only
      - SECONDS_TO_WAIT=84000
      - SPOTIFY_CLIENT_ID=<your spotify client id>
      - SPOTIFY_CLIENT_SECRET=<your spotify client secret>
      - SPOTIFY_USER_ID=<your spotify user id>
      - DEEZER_USER_ID=<your spotify user id>
      - DEEZER_PLAYLIST_ID= #<deezer playlist ids space seperated>
    restart: unless-stopped

```
And run with :
```
docker-compose up
```

### Issues
Something's off? See room for improvement? Feel free to open an issue with as much info as possible. Cheers!
