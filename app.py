from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Video Downloader Backend is running!"

@app.route("/api/download", methods=["POST"])
def download_video():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"status": "error", "message": "Missing video URL"}), 400

    try:
        filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join("downloads", filename)

        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title", "Video")

        download_url = f"https://video-downloader-n7xr.onrender.com/downloads/{filename}"

        return jsonify({
            "status": "success",
            "title": title,
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    app.run(host="0.0.0.0", port=5000)
