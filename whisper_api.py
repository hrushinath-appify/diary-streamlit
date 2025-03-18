import os
import whisper

# Ensure FFmpeg is in PATH
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

# Load Whisper model once (avoids repeated downloads)
model = whisper.load_model("base")

def transcribe_audio(audio_file):
    """Transcribes an audio file using Whisper AI."""
    result = model.transcribe(audio_file)
    return result['text']
