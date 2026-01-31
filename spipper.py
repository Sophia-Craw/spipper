# SPIPPER 2026
# WRITTEN BY SOPHIE

import spotipy
from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyClientCredentials
import os
import requests
import spip
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from pytubefix import YouTube

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
), requests_timeout=20, retries=20)

OUTPUT_FOLDER = "./output/"

def playlist_name(id):
    # Gets playlist name and returns it
    result = sp.playlist(id)
    return result['name']


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
            file = str(i + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a"

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

            # Download and save the audio strea['album']m
            try:
                if not track['is_local']:
                    yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "playlists/" + playlist_name(id), str(i + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a")
                    print(query + f" DONE")
                    spip.id_track(OUTPUT_FOLDER + "playlists/" + playlist_name(id) + "/" + str(i + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a", track)
                    i += 1
                else:
                    print(track['name'] + " is a local file. Skipping...")
            except Exception as e:
                print(f"Failed to download " + query + f" skipping...", str(e))
                i += 1

        print("Doing second ID3 pass...")
        for idx, item in enumerate(track_list):
            track = item['track']
            spip.id_track(OUTPUT_FOLDER + "playlists/" + playlist_name(id) + "/" + str(idx + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a", track)
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
            yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "singles", result['name'] + " - " + result['artists'][0]['name'] + ".m4a")
            spip.id_track(OUTPUT_FOLDER + "singles/" + result['name'] + " - " + result['artists'][0]['name'] + ".m4a", result)
            print("DONE")

        except Exception as e:
            print(f"Failed to download " + query + f" skipping...", str(e))

    else:
        print(f"No track ID provided.")


def album_name(id):
    result = sp.album(id)
    return result['name']

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
                yt.streams.get_audio_only("mp4").download(OUTPUT_FOLDER + "albums/" + album_name(id), str(idx + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a")
                spip.id_track(OUTPUT_FOLDER + "albums/" + album_name(id) + "/" + str(idx + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a", track)
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

            spip.id_track(OUTPUT_FOLDER + "albums/" + album_name(id) + "/" + str(idx + 1) + ". " + track['name'] + " - " + track['artists'][0]['name'] + ".m4a", track)
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