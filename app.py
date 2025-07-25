from flask import Flask, request, jsonify, send_from_directory
from yt_dlp import YoutubeDL
import os
import re

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Helper function to sanitize filename
def slugify(value):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', value)

@app.route("/api/download", methods=["POST"])
def download_video():
    url = request.json.get("url")
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title).80s.%(ext)s",
            "format": "best",
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename = os.path.basename(filename)
            safe_filename = slugify(filename)

            # Rename the file safely
            old_path = os.path.join(DOWNLOAD_FOLDER, filename)
            new_path = os.path.join(DOWNLOAD_FOLDER, safe_filename)
            os.rename(old_path, new_path)

        return jsonify({
            "status": "success",
            "filename": safe_filename,
            "title": info.get("title", "Downloaded Video")
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/downloads/<path:filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(debug=True)