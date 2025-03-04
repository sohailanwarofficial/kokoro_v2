from flask import Flask, request, send_file
from kokoro import KPipeline
import soundfile as sf
import io

app = Flask(__name__)
pipeline = KPipeline(lang_code='a')

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
            buffer = io.BytesIO()
            sf.write(buffer, audio, 24000, format=audio_format.upper())  # Save directly to buffer
            buffer.seek(0)  # Reset buffer position

            return send_file(
                buffer,
                mimetype=f'audio/{audio_format}',
                as_attachment=True,
                download_name=f"speech.{audio_format}"
            )

    except Exception as e:
        return f"Error generating speech: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
