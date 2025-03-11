import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import tkinter as tk
from tkinter import messagebox, filedialog

# Spotify API Credentials
client_ID = "164e2d55cb484222931b2227b1c8e92f"
client_Secret = "80a50e90a8234d12a58cce4981c9c77e"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_ID, client_secret=client_Secret))


def fetch_playlist():
    playlist_ID = entry.get().strip()
    if not playlist_ID:
        messagebox.showerror("Error", "Please enter a valid playlist ID")
        return

    try:
        results = sp.playlist(playlist_ID)
        playlist_name = results["name"].replace("/", "-") 

        tracks = []
        for index, item in enumerate(results["tracks"]["items"], start=1):
            track = item["track"]
            if track:
                name = track["name"]
                artist = ", ".join(artist["name"] for artist in track["artists"])
                album = track["album"]["name"]
                release_date = track["album"]["release_date"]
                popularity = track["popularity"]
                url = track["external_urls"]["spotify"]
                explicit = "Yes" if track["explicit"] else "No"
                duration_ms = track["duration_ms"]
                duration_min = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}"

                tracks.append([index, name, artist, album, release_date, duration_min, popularity, explicit, url])

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=playlist_name)
        if not save_path:
            return  

        with open(save_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Song Name", "Artist", "Album", "Release Date", "Duration", "Popularity", "Explicit", "Track URL"])
            writer.writerows(tracks)

        messagebox.showinfo("Success", f"CSV saved as:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch playlist:\n{str(e)}")


root = tk.Tk()
root.title("Spotify Playlist Scraper")
root.geometry("400x200")

tk.Label(root, text="Enter Spotify Playlist ID:", font=("Arial", 12)).pack(pady=5)
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

tk.Button(root, text="Download CSV", command=fetch_playlist, font=("Arial", 12), bg="green", fg="white").pack(pady=10)

root.mainloop()
