from flask import Flask, request, jsonify
from flask_cors import CORS
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)
CORS(app)

# Optional: Path to Facebook cookies.txt (exported using Get cookies.txt extension)
COOKIE_FILE = "cookies.txt"  # Make sure this file is in the same directory if needed

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            "format": "best",
            "quiet": True,
            "no_warnings": True,
            "cookiefile": COOKIE_FILE if "facebook" in url else None,
            "skip_download": True,
            "force_generic_extractor": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "url": info["url"],
                "thumbnail": info.get("thumbnail"),
                "ext": info.get("ext"),
                "website": info.get("webpage_url"),
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return "✅ Video Downloader Backend Running"


if __name__ == "__main__":
    app.run(debug=True)