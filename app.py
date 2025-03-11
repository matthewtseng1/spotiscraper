from flask import Flask, render_template, request, send_file
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import csv
from io import StringIO, BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Spotify API Credentials
client_ID = os.getenv("SPOTIFY_CLIENT_ID")
client_Secret = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_ID, client_secret=client_Secret))

# Store tracks globally for download
tracks = []
playlist_name = ""

@app.route("/", methods=["GET", "POST"])
def index():
    global tracks, playlist_name
    tracks = []
    playlist_name = ""
    playlist_cover = ""  # Store the playlist cover image URL

    if request.method == "POST":
        playlist_url = request.form.get("playlist_url")

        if playlist_url:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            results = sp.playlist(playlist_id)
            playlist_name = results["name"]
            playlist_cover = results["images"][0]["url"] if results["images"] else ""  # Fetch the playlist cover image

            for idx, item in enumerate(results["tracks"]["items"]):
                track = item["track"]
                if track:
                    name = track["name"]
                    artist = ", ".join(artist["name"] for artist in track["artists"])
                    album = track["album"]["name"]
                    duration = track["duration_ms"] // 1000  # Convert ms to seconds
                    popularity = track["popularity"]
                    release_date = track["album"]["release_date"]
                    track_url = track["external_urls"]["spotify"]
                    explicit = track["explicit"]

                    tracks.append([idx + 1, name, artist, album, duration, popularity, release_date, track_url, explicit])

    return render_template("index.html", tracks=tracks, playlist_name=playlist_name, playlist_cover=playlist_cover)


@app.route("/download")
def download_csv():
    if not tracks:
        return "No data available to download.", 400
    
    output = BytesIO()
    csv_writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(["Index", "Name", "Artist", "Album", "Duration (s)", "Popularity", "Release Date", "Spotify URL", "Explicit"])
    csv_writer.writerows(tracks)
    
    output.seek(0)  # Move cursor to start

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{playlist_name}.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)
