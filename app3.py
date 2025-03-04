from flask import Flask, request, send_file
from kokoro import KPipeline
import soundfile as sf
import io

# Create a Flask web application
app = Flask(__name__)

# Initialize Kokoro pipeline with American English
pipeline = KPipeline(lang_code='a')

@app.route('/tts', methods=['GET'])
def text_to_speech():
    """
    Text-to-Speech API endpoint with in-memory audio handling
    
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
    audio_format = request.args.get('format', 'wav').lower()  # Output format
    
    # Validate audio format
    if audio_format not in ['wav', 'mp3']:
        return "Unsupported audio format. Use 'wav' or 'mp3'.", 400
    
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
            # Create an in-memory bytes buffer
            audio_buffer = io.BytesIO()
            
            # Write audio to the buffer
            sf.write(audio_buffer, audio, 24000, format=audio_format)
            audio_buffer.seek(0)  # Reset buffer position to the beginning
            
            # Determine MIME type based on format
            mimetype = f'audio/{audio_format}'
            
            # Return the in-memory audio file
            return send_file(
                audio_buffer, 
                mimetype=mimetype, 
                as_attachment=True, 
                download_name=f'output.{audio_format}'
            )
        
        # If no audio was generated
        return "No audio generated", 500
    
    except Exception as e:
        # Return any errors
        return f"Error generating speech: {str(e)}", 500

# Add an endpoint to list available voices
@app.route('/voices', methods=['GET'])
def list_voices():
    """
    Lists available voices for the current language
    
    Usage:
    http://localhost:8080/voices
    
    Returns:
    - JSON object with available voices
    """
    # This is a simplification - actual available voices depend on your installation
    voices = {
        "english": ["af_heart", "af_emotional", "af_peaceful"],
        "spanish": ["es_voice1"],
        "french": ["fr_voice1"],
        "hindi": ["hi_voice1"],
        "italian": ["it_voice1"],
        "portuguese": ["pt_voice1"],
        "japanese": ["ja_voice1"],
        "chinese": ["zh_voice1"]
    }
    return voices

# Additional improvements for deployment
if __name__ == '__main__':
    # Use production WSGI server for deployment
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
