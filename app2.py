from flask import Flask, request, send_file
from kokoro import KPipeline
import soundfile as sf
import os

# Create a Flask web application
app = Flask(__name__)

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
    - Audio file in specified format
    """
    
    # Get text from the URL parameter (required)
    text = request.args.get('text', '')
    if not text:
        return "Please provide text using the 'text' parameter", 400
    
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
        
        # Process the first audio segment (for simplicity)
        for _, _, audio in generator:
            output_path = f"output.{audio_format}"
            sf.write(output_path, audio, 24000)  # 24000 is the sample rate
            print(f"Audio file generated: {output_path}")  # Log the file path
            break
        
        # Return the audio file
        return send_file(output_path, mimetype=f'audio/{audio_format}')
    
    except Exception as e:
        # Log the error
        print(f"Error generating speech: {str(e)}")
        return f"Error generating speech: {str(e)}", 500

# Serve the index.html file
@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080)
