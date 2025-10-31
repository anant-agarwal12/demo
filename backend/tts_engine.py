import pyttsx3
import os
from datetime import datetime
import threading

class TTSEngine:
    def __init__(self, storage_path: str = "storage/tts"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self._lock = threading.Lock()
    
    def synthesize(self, text: str) -> str:
        """
        Synthesize text to speech and save as WAV file.
        Returns the relative path to the generated audio file.
        """
        with self._lock:
            try:
                engine = pyttsx3.init()
                
                # Configure voice properties
                engine.setProperty('rate', 150)  # Speed of speech
                engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                
                # Generate filename
                timestamp = int(datetime.now().timestamp() * 1000)
                filename = f"tts_{timestamp}.wav"
                filepath = os.path.join(self.storage_path, filename)
                
                # Save to file
                engine.save_to_file(text, filepath)
                engine.runAndWait()
                
                # Return relative path for API response
                return f"static/tts/{filename}"
            except Exception as e:
                print(f"TTS Error: {e}")
                return None
    
    def cleanup_old_files(self, max_age_seconds: int = 86400):
        """Delete TTS files older than max_age_seconds (default 24 hours)"""
        try:
            now = datetime.now().timestamp()
            for filename in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
        except Exception as e:
            print(f"TTS cleanup error: {e}")
