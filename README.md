# SpotiFile
## A simple and open source spotify scraper.
*Python 3.8+*

---

## Quick Start
Make sure you have python 3.8 or above.  
$ git clone https://github.com/Michael-K-Stein/SpotiFile.git  
$ cd SpotiFile  
Now open config.py and setup your SP_KEY (Spotify has renamed this to sp_adid) and SP_DC tokens ([see below](https://github.com/Michael-K-Stein/SpotiFile#sp_key--sp_dc-tokens))  
$ python main.py  

---

*DISCLAIMER: This script is intended for personal and non-commercial use only. The purpose of this script is to create datasets for training machine learning models. Any use of this script that violates Deezer's Terms of Use or infringes on its intellectual property rights is strictly prohibited. The writer of this script is not responsible for any illegal or unauthorized use of the script by third parties. Users of this script assume all responsibility for their actions and agree to use the script at their own risk.*
*AVIS DE NON-RESPONSABILITÉ : Ce script est destiné à un usage personnel et non commercial uniquement. Le but de ce script est de créer des ensembles de données pour entraîner des modèles d'apprentissage automatique. Toute utilisation de ce script qui viole les Conditions d'utilisation de Deezer ou porte atteinte à ses droits de propriété intellectuelle est strictement interdite en vertu de la loi française. L'auteur de ce script n'est pas responsable de toute utilisation illégale ou non autorisée du script par des tiers. Les utilisateurs de ce script assument toutes les responsabilités de leurs actions et conviennent de l'utiliser à leurs propres risques.*

---

## What?
SpotiFile is a script which allows users to simply and easily, using a web-gui, scrape on Spotify playlists, albums, artists, etc.
More advanced usages can be done by importing the relevant classes (e.g. 
```python
from spotify_scraper import SpotifyScraper
```
) and then using IPython to access specific Spotify API features.
### Advantages
The main advantage of using SpotiFile is that it completely circumvents all of Spotify's api call limmits and restrictions. Spotifile offers an API to communicate with Spotify's API as if it were a real user.
This allows SpotiFile to download information en-masse quickly.

---

## Why?
Downloading massive amounts of songs and meta data can help if you prefer listening to music offline, or if you are desgining a music server which runs on an airgapped network.
*We do not encourage music piracy nor condone any illegal activity. SpotiFile is a usefull research tool. Usage of SpotiFile for other purposes is at the user's own risk. Be warned, we will not bear any responsibility for improper use of this educational software!*
### Proper and legitimate uses of SpotiFile:
+ Scraping tracks to create datasets for machine learning models.
+ Creating remixes (for personal use only!)
+ Downloading music which no longer falls under copyright law ([Generally, content who's original artist passed away over 70 years ago](https://www.copyright.gov/help/faq/faq-duration.html)).
### Please notice Spotify's User Guidelines, and make sure you understand them. See section 5; 
*The following is not permitted for any reason whatsoever in relation to the Services and the material or content made available through the Services, or any part thereof: 
5. "crawling" or "scraping", whether manually or by automated means, or otherwise using any automated means (including bots, scrapers, and spiders), to view, access or collect information;*
Usage of this "scraper" is in violation of Spotify's User Guidelines. By using this code, you assume responsibility - as *you* are the one "scraping" Spotify using automated means.
### Please notice Deezer's Terms of Use, and make sure you understand them. See article 8 - Intellectual property;
*The Recordings on the Deezer Free Service are protected digital files by national and international copyright and neighboring rights. They may only therefore be listened to within a private or family setting. Any use for a non-private purpose will expose the Deezer Free User to civil and/or criminal proceedings. Any other use of the Recordings is strictly forbidden and more particularly any download or attempt to download, any transfer or attempt to transfer permanently or temporarily on the hard drive of a computer or any other device (notably music players), any burn or attempt to burn a CD or any other support are expressly forbidden. Any resale, exchange or renting of these files is strictly prohibited.*
Storing, or attempting to store files from Deezer is strictly prohibited. Use this software only to create, for personal use, a custom streaming app. Notice that you can only use this streaming app in a private or family setting. By using this code, you assume responsibility to perform only legal actions - such as *streaming* music from Deezer for personal use.
### Do adhere to your local laws regarding intellectual property!
#### Notice: Local law (where this was written), explicitly permits reverse engeneering for non-commercial purposes.

---

## How?
SpotiFile starts its life by authenticating as a normal Spotify user, and then performs a wide range of conventional and unconventional API calls to Spotify in order to retrieve relevant information.
SpotiFile does not actually download audio from Spotify, since they use proper DRM encryption to protect against piracy. Rather, SpotiFile finds the relevant audio file on Deezer, using the copyright id (ironically). Then SpotiFile downloads the "encrypted" audio file from Deezer, which failed to implement DRM properly. Credit for reversing Deezer's encryption goes to https://git.fuwafuwa.moe/toad/ayeBot/src/branch/master/bot.py & https://notabug.org/deezpy-dev/Deezpy/src/master/deezpy.py & https://www.reddit.com/r/deemix/ (Original reversing algorithm has been taken down).

---

## Features
+ Authenticating as a legitimate Spotify user.
+ Scraping tracks from a playlist.
+ Scraping tracks from an album.
+ Scraping tracks from an artist.
+ Scraping playlists from a user.
+ Scraping playlists from a catergory.
+ Scraping a track from a track url.
+ Scraping artist images.
+ Scraping popular playlists' metadata and tracks.
+ Premium user token snatching (experimental).
+ Scraping song lyrics (time synced when possible).
+ Scraping track metadata.
+ Scraping category metadata.

---

## SP_KEY & SP_DC tokens
Obtaining sp_dc and sp_key cookies (sp_key is now called sp_adid)
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

---

# Example usages:
## Using SpotiFile to create a song recommendation module based off song lyrics' semantic similarity: 
```python
from spotify_scraper import SpotifyScraper
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys


def semantic_similarity(paragraph1, paragraph2):
    # Preprocess text
    stop_words = set(stopwords.words('english'))
    paragraph1 = ' '.join([word.lower() for word in nltk.word_tokenize(paragraph1) if word.lower() not in stop_words])
    paragraph2 = ' '.join([word.lower() for word in nltk.word_tokenize(paragraph2) if word.lower() not in stop_words])

    # Compute similarity score
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([paragraph1, paragraph2])
    similarity_score = cosine_similarity(tfidf_matrix)[0][1]

    return similarity_score


# Usage
scraper = SpotifyScraper()

lyrics1 = '\n'.join(x['words'] for x in scraper.get_lyrics(sys.argv[1])['lyrics']['lines'])
lyrics2 = '\n'.join(x['words'] for x in scraper.get_lyrics(sys.argv[2])['lyrics']['lines'])

sim = semantic_similarity(lyrics1, lyrics2)

print(f'The similarity between the two tracks is: {sim}')

```
