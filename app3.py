from flask import Flask, request, send_file, jsonify, after_this_request
import logging
import soundfile as sf
import tempfile
import os
from kokoro import KPipeline

# Initialize Flask app
app = Flask(_name_)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Kokoro pipeline with American English
try:
    logging.info("Initializing Kokoro TTS pipeline...")
    pipeline = KPipeline(lang_code='a')
    logging.info("Kokoro TTS pipeline initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Kokoro pipeline: {e}")
    pipeline = None

@app.route('/tts', methods=['GET'])
def text_to_speech():
    """
    Converts text to speech using Kokoro TTS
    """
    logging.info("Received TTS request.")
    if pipeline is None:
        logging.error("Kokoro TTS pipeline is not initialized.")
        return jsonify({"error": "Kokoro TTS pipeline not initialized"}), 500
    
    # Get text input
    text = request.args.get('text', '').strip()
    if not text:
        logging.warning("No text provided in request.")
        return jsonify({"error": "Please provide text using the 'text' parameter"}), 400
    
    # Get optional parameters
    voice = request.args.get('voice', 'af_heart')  # Default voice
    speed = float(request.args.get('speed', 1.0))  # Speech speed
    audio_format = request.args.get('format', 'wav').lower()  # Audio format
    
    logging.info(f"Processing TTS request: text='{text}', voice='{voice}', speed={speed}, format='{audio_format}'")
    
    # Validate format
    if audio_format not in ['wav', 'mp3']:
        logging.warning("Invalid format provided.")
        return jsonify({"error": "Invalid format. Use 'wav' or 'mp3'"}), 400
    
    try:
        logging.info("Generating speech using Kokoro pipeline...")
        generator = pipeline(
            text=text,
            voice=voice,
            speed=speed,
            split_pattern=r'\n+'  # Split text by newlines
        )
        
        # Generate and save the first audio segment
        for _, _, audio in generator:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_format}") as temp_audio:
                output_path = temp_audio.name
                logging.info(f"Saving generated speech to temporary file: {output_path}")
                sf.write(output_path, audio, 24000)  # Save audio with a 24k sample rate
            break
        
        logging.info("Speech generation completed successfully.")
        
        # Ensure the file is deleted AFTER the response is sent
        response = send_file(output_path, mimetype=f'audio/{audio_format}', as_attachment=True, download_name=f"speech_output.{audio_format}")
                
        logging.info("Sending generated speech file for download.")
        return response
    
    except Exception as e:
        logging.error(f"Error generating speech: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """
    Lists available voices for the current language
    """
    logging.info("Fetching available voices.")
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
    logging.info("Available voices fetched successfully.")
    return jsonify(voices)

if _name_ == '_main_':
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=8080, debug=False)
