from flask import Flask, request, send_file
from kokoro import KPipeline
import soundfile as sf
import os

# Create a Flask web application
app = Flask(__name__)

# Initialize Kokoro pipeline with American English
# Language code options:
# 'a' = American English
# 'b' = British English
# 'e' = Spanish (es)
# 'f' = French (fr-fr)
# 'h' = Hindi (hi)
# 'i' = Italian (it)
# 'p' = Brazilian Portuguese (pt-br)
# 'j' = Japanese (requires: pip install misaki[ja])
# 'z' = Mandarin Chinese (requires: pip install misaki[zh])
pipeline = KPipeline(lang_code='a')

@app.route('/tts', methods=['GET'])
def text_to_speech():
    """
    Text-to-Speech API endpoint
    
    Usage:
    http://localhost:8080/tts?text=Hello+world&voice=af_heart&speed=1.0&format=wav
    
    Parameters:
    - text: The text to convert to speech (required)
      Example: text=Hello+world
    
    - voice: The voice to use for synthesis (optional, defaults to af_heart)
      Available voices for English (lang_code='a'):
        - af_heart: Standard voice (default)
      For other languages, check Kokoro documentation for available voices
      Example: voice=af_emotional
    
    - speed: Speech rate multiplier (optional, defaults to 1.0)
      Values > 1.0 increase speed, values < 1.0 slow down speech
      Range: 0.5 to 2.0 recommended
      Example: speed=1.2
    
    - format: Audio format (optional, defaults to wav)
      Options: wav, mp3 (mp3 requires additional libraries)
      Example: format=wav
      
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
    print("Argumetns",voice,speed,audio_format)
    
    # Generate audio using Kokoro TTS
    try:
        generator = pipeline(
            text,             # Text to synthesize
            voice=voice,      # Voice to use
            speed=speed,      # Speed multiplier
            split_pattern=r'\n+'  # Pattern to split text on (default: newlines)
            # Other available options (advanced):
            # pitch=0.0       # Pitch adjustment (-1.0 to 1.0)
            # noise_scale=0.0 # Amount of variation (0.0 to 1.0)
        )
        
        # Process the first audio segment (for simplicity)
        # For longer texts, you might want to combine multiple segments
        for _, _, audio in generator:
            output_path = f"output.{audio_format}"
            sf.write(output_path, audio, 24000)  # 24000 is the sample rate
            break
        
        # Return the audio file
        return send_file(output_path, mimetype=f'audio/{audio_format}')
    
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

if __name__ == '__main__':
    # Run the Flask application
    # host='0.0.0.0' makes the server accessible from other devices on the network
    # port=5000 is the default port for Flask applications
    # debug=False disables debug mode (set to True during development)
    app.run(host='0.0.0.0', port=8080, debug=False)
