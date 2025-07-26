from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from yt_dlp import YoutubeDL, cookies
import os
import re

app = Flask(__name__)
CORS(app)

# Directory to save downloaded videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_browser_cookies(browser='chrome'):
    try:
        # Get cookies from Chrome, Firefox, Edge, etc.
        return cookies.cookies_from_browser(browser)
    except Exception as e:
        print("Failed to load browser cookies:", e)
        return None

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    try:
        browser_cookies = get_browser_cookies('chrome')  # Change to 'firefox' or 'edge' if needed

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'cookies': browser_cookies
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = sanitize_filename(info.get("title", "Video"))

        return jsonify({
            "status": "success",
            "title": title,
            "filename": os.path.basename(filename),
            "downloadUrl": f"/downloads/{os.path.basename(filename)}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
