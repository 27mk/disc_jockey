from flask import Flask, render_template, jsonify
import os
import json
import discogs_client
from collections import defaultdict
import re
import time

app = Flask(__name__)

#-DISCOGS---------------------------------------------------------------------------------------------------------------
consumer_key = os.getenv("DISCOGS_CONSUMER_KEY")
consumer_secret = os.getenv("DISCOGS_CONSUMER_SECRET")
user_agent = "api_access_retro_player"

def load_tokens():
    access_token = os.getenv("DISCOGS_ACCESS_TOKEN")
    access_secret = os.getenv("DISCOGS_ACCESS_SECRET")

    if access_token and access_secret:
        return access_token, access_secret
    else:
        return None, None

def clean_text(text):
    text = re.sub(r"\s\(\d+\)$", "", text)
    text = text.replace('\t', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def get_collection():
    access_token, access_secret = load_tokens()

    if not access_token or not access_secret:
        return "Discogs auth failed: check access tokens"

    client = discogs_client.Client(
        user_agent,
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        token = access_token,
        secret = access_secret
    )

    user = client.identity()
    print(f"Logged in as {user.username}")

    data = []
    for item in user.collection_folders[0].releases:
        rec = client.release(item.id)

        album_data = {
            "id": item.id,
            "name": clean_text(rec.title),
            "artists": [clean_text(artist.name) for artist in rec.artists],
            "release_year": rec.year,
            "genres": rec.genres,
            "tracklist": {}
        }

        tracklist = defaultdict(list)
        for track in rec.tracklist:
            if track.position:
                side = track.position[0]
                tracklist[side].append({"title": clean_text(track.title)})

        for side in sorted(tracklist.keys()):
            album_data["tracklist"][f"Side {side}"] = tracklist[side]

        data.append(album_data)

        time.sleep(1)

    # Save album data to a local JSON file
    with open("album_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    return data

#-ROUTES----------------------------------------------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/discogs")
def discogs():
    album_data = get_collection()

    if "error" in album_data:
        return jsonify(album_data), 400

    return render_template("test_page.html", album_data = album_data)

if __name__ == "__main__":
    app.run(debug = True)

