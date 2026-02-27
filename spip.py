# SPIP 2026
# WRITTEN BY SOPHIE

from mutagen.mp4 import MP4, MP4Cover, error
import requests
from pathlib import Path
import spotipy
from spipper import sp, validate_name
from pathvalidate import sanitize_filepath

def get_genre(artist_id):

    result = sp.artist(artist_id)
    return result['genres'][0] if result['genres'] else "No Genre"

def id_track(file, track, idx, length):

    try:
        sanitized_file = sanitize_filepath(validate_name(file))

        path = Path(sanitized_file)

        if not path.exists():

            print("WARN: The ID3 data did not save.")
            return


        song = MP4(file)

        track_id = track['id']

        song["\xa9nam"] = [track['name']]
        song["\xa9alb"] = [track['album']['name']]
        song['\xa9ART'] = [track['artists'][0]['name']]
        song['trkn']    = [(idx, length)]
        song['\xa9gen'] = [get_genre(track['artists'][0]['id'])]
        if track_id:
            song["\xa9cmt"] = [track_id]

        response = requests.get(track['album']['images'][0]['url'])

        if response.status_code == 200:
            song['covr'] = [MP4Cover(response.content, MP4Cover.FORMAT_JPEG)]
            song.save()
            print("ID3 Data Saved!")

    except error as e:
        print("Failed to bake ID3 data. ", str(e))