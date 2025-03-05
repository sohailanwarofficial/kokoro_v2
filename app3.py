from flask import Flask, request, send_file, jsonify
from kokoro import KPipeline
import soundfile as sf
import os

app = Flask(__name__)
pipeline = KPipeline(lang_code='a')

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text', '')
    if not text:
        return "Please provide text using the 'text' parameter", 400

    voice = request.args.get('voice', 'af_heart')
    speed = float(request.args.get('speed', 1.0))
    audio_format = request.args.get('format', 'wav')

    try:
        generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')

        for _, _, audio in generator:
            filename = f"{text.replace(' ', '_')}.{audio_format}"
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            sf.write(output_path, audio, 24000, format=audio_format.upper())

            return jsonify({"message": "Audio generated", "file_url": f"/fetch_audio/{filename}"})

    except Exception as e:
        return f"Error generating speech: {str(e)}", 500


@app.route('/fetch_audio/<filename>', methods=['GET'])
def fetch_audio(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, mimetype=f'audio/{filename.split(".")[-1]}')
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
