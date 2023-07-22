import requests
import pyaudiowpatch as pyaudio
import wave
import os
from _spinner_helper import Spinner
import time
import json
import base64
import hashlib
import hmac
import sys



"""Authentication code"""
ACR_API_KEY = ""  # Replace with your ACR Cloud API key
ACR_API_SECRET = ""  # Replace with your ACR Cloud API secret

# Set recording duration
duration = 5.0
# Set file name
filename = "loopback_record.wav"

# ACR Cloud API endpoint and headers
ACR_API_ENDPOINT = "https://identify-eu-west-1.acrcloud.com"
headers = {
    "Content-Type": "application/octet-stream",
    "Access-Key": ACR_API_KEY,
    "Access-Secret": ACR_API_SECRET,
}

# Generate ACR Cloud API signature
http_method = "POST"
http_uri = "/v1/identify"
data_type = "audio"
signature_version = "1"
timestamp = int(time.time())

string_to_sign = http_method + "\n" + http_uri + "\n" + ACR_API_KEY + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)

sign = base64.b64encode(hmac.new(ACR_API_SECRET.encode('ascii'), string_to_sign.encode('ascii'), digestmod=hashlib.sha1).digest()).decode('ascii')

"""Spotify API authentication"""

SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''
SPOTIFY_REDIRECT_URI = 'http://localhost:8080/callback/'
SPOTIFY_SCOPE = 'playlist-modify-public'  # Adjust the scope based on your requirements
SPOTIFY_USER_ID = ""
SPOTIFY_API_URL = ""
SPOTIFY_REFRESH_TOKEN = ""

# Request a new access token
auth_response = requests.post(
    "https://accounts.spotify.com/api/token",
    data={
        "grant_type": "refresh_token",
       "refresh_token":SPOTIFY_REFRESH_TOKEN,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
    },
    auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
)
response_data = auth_response.json()
SPOTIFY_ACCESS_TOKEN = response_data["access_token"]

# Headers
spotify_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SPOTIFY_ACCESS_TOKEN}"
}

if __name__ == "__main__":
    with pyaudio.PyAudio() as p, Spinner() as spinner:
        """
        Create PyAudio instance via context manager.
        Spinner is a helper class, for `pretty` output
        """
        try:
            # Get default WASAPI info
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            spinner.print("Looks like WASAPI is not available on the system. Exiting...")
            spinner.stop()
            exit()

        # Get default WASAPI speakers
        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                """
                Try to find loopback device with same name(and [Loopback suffix]).
                Unfortunately, this is the most adequate way at the moment.
                """
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                spinner.print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                spinner.stop()
                exit()

        spinner.print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")

        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(default_speakers["maxInputChannels"])
        wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(int(default_speakers["defaultSampleRate"]))

        def callback(in_data, frame_count, time_info, status):
            """Write frames and return PA flag"""
            wave_file.writeframes(in_data)
            return (in_data, pyaudio.paContinue)

        with p.open(format=pyaudio.paInt16,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt16),
                    input=True,
                    input_device_index=default_speakers["index"],
                    stream_callback=callback
                    ) as stream:
            """
            Open a PA stream via context manager.
            After leaving the context, everything will
            be correctly closed (Stream, PyAudio manager)            
            """
            spinner.print(f"The next {duration} seconds will be written to {filename}")
            time.sleep(duration)  # Blocking execution while recording

        wave_file.close()

        # Replace "###...###" below with your project's host, access_key, and access_secret.
        access_key = ""
        access_secret = ""
        requrl = ""

        http_method = "POST"
        http_uri = "/v1/identify"
        # default is "fingerprint", it's for recognizing fingerprint,
        # if you want to identify audio, please change data_type="audio"
        data_type = "audio"
        signature_version = "1"
        timestamp = time.time()

        string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
            timestamp)

        sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),
                                         digestmod=hashlib.sha1).digest()).decode('ascii')

        # Supported file formats: mp3, wav, wma, amr, ogg, ape, acc, spx, m4a, mp4, FLAC, etc
        # File size: < 1M, You'd better cut large file to small file, within 15 seconds data size is better
        audio_file_path = "loopback_record.wav"
        sample_bytes = os.path.getsize(audio_file_path)

        files = [
            ('sample', ('loopback.wav', open('loopback_record.wav', 'rb'), 'audio/wav'))
        ]
        data = {
            'access_key': access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version
        }

        r = requests.post(requrl, files=files, data=data)
        r.encoding = "utf-8"
        response_json = r.json()
        print (response_json)
        
        song_info = response_json['metadata']['music'][0]
        song_title = song_info['title']
        artist = song_info['artists'][0]['name']

        print("Song Title:", song_title)
        print("Artist:", artist)
        """searching for and adding the song to spotify"""
        search_url = f"{SPOTIFY_API_URL}/search" 
        query = song_title + artist
        search_params = {
        "q": query,
        "type": "track",
        "limit": 1
}
 
       


    search_response = requests.get(search_url, headers=spotify_headers, params=search_params)
    search_response_data = search_response.json()
   
    tracks = search_response_data['tracks']['items']
    if tracks:
        track_uri = tracks[0]['uri']

    # Add the track to your playlist
    playlist_id = ""  # Replace with your playlist ID
    add_to_playlist_url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks"
    add_to_playlist_params = {
        "uris": [track_uri]
    }

    
    add_to_playlist_response = requests.post(add_to_playlist_url, headers=spotify_headers, json=add_to_playlist_params)

    if add_to_playlist_response.status_code == 201:
        print("Track added to playlist successfully!")
    else:
        print("Failed to add track to playlist.")
        print("Response:", add_to_playlist_response.json())
        print("Full Request:")
        print(f"URL: {add_to_playlist_response.request.url}")
        print("Headers:")
        for name, value in add_to_playlist_response.request.headers.items():
            print(f"{name}: {value}")
        print("Body:")
        print(add_to_playlist_response.request.body.decode('utf-8'))
else:
    print("Track not found on Spotify.")
    