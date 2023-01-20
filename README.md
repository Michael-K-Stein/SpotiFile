# SpotiFile
## A simple and open source spotify scraper.

---

## What?
SpotiFile is a script which allows users to simply and easily, using a web-gui, scrape on Spotify playlists, albums, artists, etc.
More advanced usages can be done by importing the relevant classes (e.g. from "spotify_scraper import SpotifyScraper") and then using IPython to access specific Spotify API features.
### Advantages
The main advantage of using SpotiFile is that it completely circumvents all of Spotify's api call limmits and restrictions. Spotifile offers an API to communicate with Spotify's API as if it were a real user.
This allows SpotiFile to download information en-masse quickly.

---

## Why?
Downloading massive amounts of songs and meta data can help if you prefer listening to music offline, or if you are desgining a music server which runs on an airgapped network.
*We do not encourage music piracy nor condone any illegal activity. SpotiFile is a usefull research tool. Usage of SpotiFile for other purposes is at the user's own risk.*

---

## How?
SpotiFile starts its life by authenticating as a normal Spotify user, and then performs a wide range of conventional and unconventional API calls to Spotify in order to retrieve relevant information.
SpotiFile does not actually download audio from Spotify, since they use proper DRM encryption to protect against piracy. Rather, SpotiFile finds the relevant audio file on Deezer, using the copyright id (ironically). Then SpotiFile downloads the "encrypted" audio file from deezer, and decrypts it using the private key that Deezer leaked a while ago.

---

## Features
+ Authenticating as a legitimate Spotify user.
+ Scraping tracks from a playlist.
+ Scraping tracks from an album.
+ Scraping tracks from an artist.
+ Scraping playlists from a user.
+ Scraping a track from a track url.
+ Scraping artist images.
+ Scraping popular playlists' metadata and tracks.
+ Premium user token snatching (experimental).
+ Scraping song lyrics (time synced when possible).
+ Scraping track metadata.

---

## SP_KEY & SP_DC tokens
Obtaining sp_dc and sp_key cookies
SpotiFile uses two cookies to authenticate against Spotify in order to have access to the required services.
*Shoutout to @fondberg for the explanation https://github.com/fondberg/spotcast*

To obtain the cookies, these different methods can be used:

### Chrome based browser
Open a new Incognito window at https://open.spotify.com and login to Spotify.
Press Command+Option+I (Mac) or Control+Shift+I or F12. This should open the developer tools menu of your browser.
Go into the application section.
In the menu on the left go int Storage/Cookies/open.spotify.com.
Find the sp_dc and sp_key and copy the values.
Close the window without logging out (Otherwise the cookies are made invalid).

### Firefox based browser
Open a new Incognito window at https://open.spotify.com and login to Spotify.
Press Command+Option+I (Mac) or Control+Shift+I or F12. This should open the developer tools menu of your browser.
Go into the Storage section. (You might have to click on the right arrows to reveal the section).
Select the Cookies sub-menu and then https://open.spotify.com.
Find the sp_dc and sp_key and copy the values.
Close the window without logging out (Otherwise the cookies are made invalid).

