import os
import uuid

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, resources={r"/*":{"origin":"*"}})


@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)


def generate_room():
    return "room-"+ str(uuid.uuid4())[:8]

@app.route("/getToken")
def get_token():
    name = request.args.get("name","guest")
    language = request.args.get("language", "en")
    room = request.args.get("room", generate_room())
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ['LIVEKIT_API_SECRET']

    grants = VideoGrants(room_join=True, room=room)
    token = (
        AccessToken(api_key, api_secret)
        .with_identity(name)
        .with_grants(grants)
        .with_attributes({"language": language})
    )
    return jsonify({
        "token": token.to_jwt(),
        "room": room,
        "identity": name
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
