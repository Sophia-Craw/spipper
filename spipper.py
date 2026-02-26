# SPIPPER 2026
# WRITTEN BY SOPHIE

import spotipy
from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyClientCredentials
import os
import requests
import spip
from pathlib import Path
from pathvalidate import sanitize_filepath
from dotenv import load_dotenv
import re

load_dotenv()

from pytubefix import YouTube

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
), requests_timeout=20, retries=20)

OUTPUT_FOLDER = "./output/"

folder_path = Path(OUTPUT_FOLDER)

folder_path.mkdir(parents=True, exist_ok=True)

def playlist_name(id):
    # Gets playlist name and returns it
    result = sp.playlist(id)
    return sanitize_filepath(result['name'])

def validate_name(name):
    emoj = re.compile("["           # Strip special chars
        u"\U0001F600-\U0001F64F"  
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"  
        u"\U00002500-\U00002BEF"  
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', name)

track_list = []

def playlist_all_tracks(id):
    global track_list
    # Fetch playlist
    result = sp.playlist_items(str(id), additional_types="track")
    tracks = result['items']

    # Page through playlist
    while result['next']:
        result = sp.next(result)
        tracks.extend(result['items'])

    track_list = tracks
    print(f"Found: " + str(len(tracks)) + f" tracks. Download will begin shortly...")
    return tracks


def download_playlist(id):
    global track_list
    if id:
        print(f"Spipper is preparing playlist " + playlist_name(id))
        
        existing_files = []
        if (os.path.exists(OUTPUT_FOLDER + "playlists/" + playlist_name(id))):
            existing_files = set(os.listdir(OUTPUT_FOLDER + "playlists/" + playlist_name(id)))

        # Iterate playlist
        i = 0
        playlist_all_tracks(id)
        while i < len(track_list):
            track = track_list[i]['track']
            file = validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a")

            # if track was already downloaded. Skip it.
            if i < len(existing_files):
                if file in existing_files:
                    print(track['name'] + " already exists. Skipping...")
                    i += 1
                    continue

            # Building query for youtube search for each track
            query = track['name'] + " by " + track['artists'][0]['name']

            # Creating the YouTube instance for download
            yt_result = YoutubeSearch(query + " audio", 1).to_dict()
            print("Track", str(i + 1) + ":", "Beginning download...")
            url = "https://www.youtube.com/watch?v=" + yt_result[0]['id']
            yt = YouTube(url)

            # Download and save the audio stream
            try:
                if not track['is_local']:
                    yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "playlists/" + playlist_name(id), validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"))
                    print(query + f" DONE")
                    spip.id_track(OUTPUT_FOLDER + "playlists/" + playlist_name(id) + "/" + validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"), track, i + 1, len(track_list))
                    i += 1
                else:
                    del track_list[i]
                    continue

            except Exception as e:
                print(f"Failed to download " + query + f" skipping...", str(e))
                i += 1

        print("Doing second ID3 pass...")
        for idx, item in enumerate(track_list):
            track = item['track']
            spip.id_track(OUTPUT_FOLDER + "playlists/" + playlist_name(id) + "/" + validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"), track, idx + 1, len(track_list))
            print(str(idx + 1) + "/" + str(len(track_list)) + " rescanned.")
    
        print("ALL DONE")
    else:
        print(f"No playlist ID provided.")
        return
    

def download_single(id):
    if id:
        # Fetch single
        result = sp.track(id)
        query = result['name'] + " by " + result['artists'][0]['name'] + " audio"

        # Create YouTube instance for download.
        yt_result = YoutubeSearch(query, 1).to_dict()
        print("Beginning download for", result['name'] + " by " + result['artists'][0]['name'], "...")
        url = "https://www.youtube.com/watch?v=" + yt_result[0]['id']
        yt = YouTube(url)
        
        # Download
        try:
            yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "singles", validate_name(result['name']) + " - " + validate_name(result['artists'][0]['name'] + ".m4a"))
            spip.id_track(OUTPUT_FOLDER + "singles/" + validate_name(result['name']) + " - " + validate_name(result['artists'][0]['name'] + ".m4a"), result, 1, 1)
            print("DONE")

        except Exception as e:
            print(f"Failed to download " + query + f" skipping...", str(e))

    else:
        print(f"No track ID provided.")


def album_name(id):
    result = sp.album(id)
    return sanitize_filepath(result['name'])

def cover_art(id):
    result = sp.album(id)
    return result['images']

def download_album(id):
    if id:
        result = sp.album_tracks(id)

        print("Spipper is preparing album " + album_name(id))
        print("Download will begin shortly...")

        if not Path.exists(OUTPUT_FOLDER + "albums/" + album_name(id)):
            Path.mkdir(OUTPUT_FOLDER + "albums/" + album_name(id), 511, True)
        
        # Fetch and save cover
        try:
            response = requests.get(cover_art(id), stream=True)
            response.raise_for_status()

            with open(OUTPUT_FOLDER + "albums/" + album_name(id) + "/cover.jpg", "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            
            print("Cover art sucessfully saved.")

        except requests.exceptions.RequestException as e:
            print("Saving cover art for " + album_name(id) + " failed...")
        
        albname = album_name(id)
        albart = cover_art(id)
        for idx, item in enumerate(result['items']):
            track = item
            if 'album' not in track:
                track['album'] = {}
            track['album']['name'] = albname
            track['album']['images'] = albart

            query = track['name'] + " by " + track['artists'][0]['name']

            yt_result = YoutubeSearch(query + " audio", 1).to_dict()
            url = "https://www.youtube.com/watch?v=" + yt_result[0]['id']
            
            print("Track", str(idx + 1) + ":", "Beginning download...")
            yt = YouTube(url)
            try:
                yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "albums/" + album_name(id), validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"))
                spip.id_track(OUTPUT_FOLDER + "albums/" + album_name(id) + "/" + validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"), track, idx + 1, len(result['items']))
                print(query + f" DONE")
            except Exception as e:
                print(f"Failed to download " + query + f" skipping...", str(e))
                continue

        print("Doing second ID3 pass...")
        for idx, item in enumerate(result['items']):
            track = item
            if 'album' not in track:
                track['album'] = {}
            track['album']['name'] = albname
            track['album']['images'] = albart

            spip.id_track(OUTPUT_FOLDER + "albums/" + album_name(id) + "/" + validate_name(track['name']) + " - " + validate_name(track['artists'][0]['name'] + ".m4a"), track, idx + 1, len(result['items']))
            print(str(idx + 1) + "/" + str(len(result['items'])) + " rescanned.")
    
        print("ALL DONE")
    else:
        print("No album ID provided")


def help():
    print("SPIPPER USAGE:")
    print("--help", "See how to use Spipper")
    print("\n")
    print("Flags:")
    print("--playlist [id]", " - Download a playlist.")
    print("--single   [id]", " - Download a single track")
    print("--album    [id]", " - Download an album")
    print("\n")
    print("EXAMPLE USAGE:")
    print("./spipper --playlist 55NmnqA76BgOUsbvDYM5So")

if __name__ == "__main__":
    # Trigger entry point
    import sys
    FLAG = ""
    ID = ""

    if len(sys.argv) >= 2:
        FLAG = str(sys.argv[1])
    
    if len(sys.argv) >= 3:
        ID = str(sys.argv[2])

    if not FLAG or not ID:
        help()
    elif FLAG == "--playlist":
        download_playlist(ID)
    elif FLAG == "--single":
        download_single(ID)
    elif FLAG == "--album":
        download_album(ID)
    elif FLAG == "--help":
        help()