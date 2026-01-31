# SPIP 2026
# WRITTEN BY SOPHIE

from mutagen.mp4 import MP4, MP4Cover, error
import requests
from pathlib import Path

def id_track(file, track):

    path = Path(file)

    while not path.exists():

        print("WARN: File not created before ID3 attempt. This should be resolve in the second pass.")
        return


    song = MP4(file)

    song["\xa9nam"] = [track['name']]
    song["\xa9alb"] = [track['album']['name']]
    song['\xa9ART'] = [track['artists'][0]['name']]

    response = requests.get(track['album']['images'][0]['url'])

    if response.status_code == 200:
        song['covr'] = [MP4Cover(response.content, MP4Cover.FORMAT_JPEG)]
    
    try:
        song.save()
        print("ID3 Data Saved!")
    except error as e:
        print("Failed to bake ID3 data. ", str(e))