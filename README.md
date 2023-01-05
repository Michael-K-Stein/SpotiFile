# SpotiFile
## A simple and open source spotify scraper.

## What?
SpotiFile is a script which allows users to simply and easily, using a web-gui, scrape on Spotify playlists, albums, artists, etc.
More advanced usages can be done by importing the relevant classes (e.g. from "spotify_scraper import SpotifyScraper") and then using IPython to access specific Spotify API features.
### Advantages
The main advantage of using SpotiFile is that it completely circumvents all of Spotify's api call limmits and restrictions. Spotifile offers an API to communicate with Spotify's API as if it were a real user.
This allows SpotiFile to download information en-masse quickly.

## Why?
Downloading massive amounts of songs and meta data can help if you prefer listening to music offline, or if you are desgining a music server which runs on an airgapped network.
*We do not encourage music piracy or condone any illegal activity. SpotiFile is a usefull research tool. Usage of SpotiFile for other purposes is at the user's own risk.*

## How?
SpotiFile starts its life by authenticating as a normal Spotify user, and then performs a wide range of conventional and unconventional API calls to Spotify in order to retrieve relevant information.

## Features
+ Authenticating as a legitimate Spotify user.
+ Scraping tracks from a playlist.
+ Scraping tracks from an album.
+ Scraping tracks from an artist.
+ Scraping a track from a track url.
+ Scraping artist images.
+ Scraping popular playlists' metadata and tracks.
+ Premium user token snatching (experimental).
+ Scraping song lyrics (time synced when possible).
+ Scraping track metadata.