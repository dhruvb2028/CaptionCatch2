from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def extract_video_id(youtube_url):
    parsed = urlparse(youtube_url)
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed.query).get('v', [None])[0]
    elif parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    return None

@app.route('/')
def home():
    return render_template('index.htm')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    video_url = data.get('url')
    video_id = extract_video_id(video_url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ''
        for i, entry in enumerate(transcript_list):
            text = entry['text'].replace('\n', ' ')
            transcript += text
            if i + 1 < len(transcript_list):
                gap = transcript_list[i + 1]['start'] - (entry['start'] + entry['duration'])
                if gap > 1.5:
                    transcript += ' ....  '
                else:
                    transcript += ' '
        return jsonify({'transcript': transcript})
    except (TranscriptsDisabled, NoTranscriptFound):
        return jsonify({'error': 'Transcript not available for this video'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
