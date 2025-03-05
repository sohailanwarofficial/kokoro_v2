from flask import Flask, request, send_from_directory, jsonify, url_for
from kokoro import KPipeline
import soundfile as sf
import os

# Create a Flask web application
app = Flask(__name__)

# Directory to store generated audio files
OUTPUT_DIR = "output"  # Ensure it's "output" (relative path) instead of "/output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize Kokoro pipeline with American English
pipeline = KPipeline(lang_code='a')

@app.route('/tts', methods=['GET'])
def text_to_speech():
    """
    Text-to-Speech API endpoint
    
    Usage:
    http://localhost:8080/tts?text=Hello+world&voice=af_heart&speed=1.0&format=wav
    
    Parameters:
    - text: The text to convert to speech (required)
    - voice: The voice to use for synthesis (optional, defaults to af_heart)
    - speed: Speech rate multiplier (optional, defaults to 1.0)
    - format: Audio format (optional, defaults to wav)
      
    Returns:
    - JSON response with audio file URL
    """
    
    # Get text from the URL parameter (required)
    text = request.args.get('text', '')
    if not text:
        return jsonify({"error": "Please provide text using the 'text' parameter"}), 400
    
    # Get optional parameters with defaults
    voice = request.args.get('voice', 'af_heart')  # Voice selection
    speed = float(request.args.get('speed', 1.0))  # Speech rate
    audio_format = request.args.get('format', 'wav')  # Output format
    
    # Generate audio using Kokoro TTS
    try:
        generator = pipeline(
            text,             # Text to synthesize
            voice=voice,      # Voice to use
            speed=speed,      # Speed multiplier
            split_pattern=r'\n+'  # Pattern to split text on (default: newlines)
        )
        
        # Process the first audio segment
        for _, _, audio in generator:
            output_filename = f"output.{audio_format}"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            sf.write(output_path, audio, 24000)  # Save with 24kHz sample rate
            print(f"Audio file generated: {output_path}")  # Log the file path
            break
        
        # Generate the file URL
        file_url = url_for('get_audio', filename=output_filename, _external=True)
        return jsonify({'file_url': file_url})
    
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return jsonify({"error": f"Error generating speech: {str(e)}"}), 500

# Route to serve audio files directly from "output/" directory
@app.route('/output/<filename>')
def get_audio(filename):
    """Serve saved audio files from the /output directory."""
    return send_from_directory(OUTPUT_DIR, filename, mimetype='audio/*')

# Serve the index.html file
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080)
