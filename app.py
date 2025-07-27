from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    # Redirect Facebook URLs to external site
    if "facebook.com" in url or "fb.watch" in url:
        return jsonify({
            "status": "redirect",
            "redirect_url": f"https://www.savefrom.net/{url}"
        }), 200

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "Video")

        return jsonify({
            "status": "success",
            "title": title,
            "filename": os.path.basename(filename)
        })

    except Exception as e:
        error_msg = str(e)

        # Friendly error for broken extractors
        if "facebook" in error_msg.lower():
            return jsonify({
                "status": "error",
                "message": "Facebook videos are not currently supported. Please use SaveFrom.net or fbdown.net."
            }), 500

        return jsonify({
            "status": "error",
            "message": f"Download failed: {error_msg}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)