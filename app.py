from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Directory to save downloaded videos
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            # Optional: include cookies if needed
            # 'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "Video")

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
