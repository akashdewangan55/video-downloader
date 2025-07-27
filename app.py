from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"status": "error", "message": "URL is required"}), 400

    try:
        # Facebook Video → SnapSave
        if "facebook.com" in url or "fb.watch" in url:
            snap_response = requests.post(
                "https://snapsave.app/action.php?lang=en",
                data={"url": url}
            )
            if snap_response.status_code == 200 and "url" in snap_response.text:
                return jsonify({
                    "status": "success",
                    "source": "snapsave",
                    "html": snap_response.text
                })
            else:
                return jsonify({"status": "error", "message": "SnapSave failed"}), 500

        # YouTube Video → Y2Mate Unofficial API
        elif "youtube.com" in url or "youtu.be" in url:
            api_url = "https://api.vevioz.com/api/button/mp3/"  # or /mp4/
            response = requests.get(f"{api_url}{url}")
            if response.status_code == 200:
                return jsonify({
                    "status": "success",
                    "source": "y2mate",
                    "html": response.text
                })
            else:
                return jsonify({"status": "error", "message": "Y2Mate failed"}), 500

        else:
            return jsonify({"status": "error", "message": "Unsupported URL"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)