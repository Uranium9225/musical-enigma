import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import yt_dlp


c_id = "YOUR_CLIENT_ID"
c_secret = "YOUR_CLIENT_SECRET"

# Initialize Spotipy client with client credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=c_id, client_secret=c_secret
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def extract_tracks_from_playlist(playlist_url):
    # Extract playlist ID from the URL using regular expression
    playlist_id = re.findall(r"playlist/([^?]+)", playlist_url)[0]

    try:
        # Fetch tracks from the playlist
        results = spotify.playlist_tracks(playlist_id)

        # Extract track information from the playlist
        tracks = results["items"]
        while results["next"]:
            results = spotify.next(results)
            tracks.extend(results["items"])

        return tracks

    except spotipy.SpotifyException as e:
        print("Error:", e)
        return []


def download_playlist_tracks(playlist_url):
    tracks = extract_tracks_from_playlist(playlist_url)
    for track in tracks:
        song_url = get_song_url(track["track"]["name"])
        if song_url:
            download_audio(song_url)


def get_playlist_tracks(playlist_url):
    tracks = extract_tracks_from_playlist(playlist_url)
    for track in tracks:
        song_artists = track["track"]["artists"][0]["name"]
        song_name = track["track"]["name"]
        print(f"[{song_name} by {song_artists}]")
        print(f"\t---> {get_spotify_track_url(track["track"]["uri"])}")


def get_spotify_track_url(track_uri):
    track_info = spotify.track(track_uri)
    external_urls = track_info["external_urls"]
    return external_urls["spotify"]

def extract_playlist_name(playlist_url):
    # Use regular expression to extract the playlist name from the URL
    match = re.search(r"playlist/([^/?]+)", playlist_url)
    if match:
        return match.group(1)
    else:
        return None
    
def download_audio(song_url):

        # Create a folder with the playlist name on the desktop if it doesn't exist
    folder_path = os.path.join(
        os.path.expanduser("~"),
        "Desktop",
        extract_playlist_name(playlist_url))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Configure options for youtube_dl
    ydl_opts = {
        "default_search": "ytsearch",  # Search on YouTube
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "outtmpl": os.path.join(folder_path, "%(title)s.%(ext)s"),  # Output filename template
        # "verbose": True,
        # "--ffmpeg-location": "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
    }
    # Download audio from the Spotify URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([song_url])
        # ydl.download_with_info_file([song_url])


def get_song_url(song_name):
    # Configure options for youtube_dl
    ydl_opts = {
        "default_search": "ytsearch",  # Search on YouTube
        "quiet": True,  # Suppress console output
        # "--ffmpeg-location": "C:/Program Files/ffmpeg/bin/ffmpeg.exe",
    }
    # Download audio from the Spotify URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(song_name, download=False)
        if "entries" in result:
            first_entry = result["entries"][0]
            if first_entry:
                # print("URL:", first_entry["webpage_url"])  # Print the URL
                return first_entry["webpage_url"]


playlist_url = input("Paste link to [PUBLIC] Spotify Playlist :\n\t")
choice = input(
    "Press 'L' or 'l' to list the songs in the playlist or 'D' or 'd' to download them all:\n\t"
)
if choice.lower() == "l":
    get_playlist_tracks(playlist_url)
elif choice.lower() == "d":
    download_playlist_tracks(playlist_url)
else:
    print("Invalid choice. Please enter 'L' or 'D' next time.")
