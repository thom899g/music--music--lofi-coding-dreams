from typing import Optional, Tuple, Dict
import numpy as np
import sounddevice as sd
import logging
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
import wave
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 24
    target_lufs: float = -14.0
    base_bpm: float = 75.0

class LofiGenerator:
    """
    Core audio generation system for lo-fi music creation.
    Handles synthesis, mixing, and output optimization.
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self._initialize_firebase()
        self._validate_resources()
        self.output_path = Path("output")
        self.output_path.mkdir(exist_ok=True)
        
    def _initialize_firebase(self) -> None:
        """Initialize Firebase connection with error handling."""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("firebase-credentials.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            logger.info("Firebase initialization successful")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise RuntimeError("Database connection required for operation")

    def _validate_resources(self) -> None:
        """Validate all required resources and samples exist."""
        required_paths = [
            Path("resources/samples/keys"),
            Path("resources/samples/nature"),
            Path("resources/samples/synth")
        ]
        
        for path in required_paths:
            if not path.exists():
                logger.error(f"Required resource path missing: {path}")
                raise FileNotFoundError(f"Missing required resource: {path}")

    def generate_base_melody(self, duration_seconds: float) -> np.ndarray:
        """Generate base synthesizer melody using pure synthesis."""
        try:
            samples = int(duration_seconds * self.config.sample_rate)
            t = np.linspace(0, duration_seconds, samples)
            
            # Generate a simple sine wave melody
            frequency = 440.0  # A4 note
            melody = 0.5 * np.sin(2 * np.pi * frequency * t)
            
            # Add harmonics for richer sound
            melody += 0.3 * np.sin(4 * np.pi * frequency * t)
            melody += 0.2 * np.sin(6 * np.pi * frequency * t)
            
            return melody
        except Exception as e:
            logger.error(f"Melody generation failed: {str(e)}")
            raise

    def save_track(self, audio_data: np.ndarray, filename: str) -> Path:
        """Save the generated audio to a WAV file."""
        try:
            output_file = self.output_path / f"{filename}.wav"
            with wave.open(str(output_file), 'wb') as wav_file:
                wav_file.setnchannels(self.config.channels)
                wav_file.setsampwidth(self.config.bit_depth // 8)
                wav_file.setframerate(self.config.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            logger.info(f"Successfully saved audio to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to save audio file: {str(e)}")
            raise

    def generate_track(self, duration: float = 180.0) -> Path:
        """Generate a complete lo-fi track with all components."""
        try:
            # Generate base melody
            melody = self.generate_base_melody(duration)
            
            # Add effects and processing
            processed_audio = self._process_audio(melody)
            
            # Save and return path
            return self.save_track(processed_audio, f"lofi_track_{int(duration)}")
        except Exception as e:
            logger.error(f"Track generation failed: {str(e)}")
            raise

    def _process_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply audio processing effects."""
        try:
            # Normalize
            audio = audio / np.max(np.abs(audio))
            
            # Apply soft clipping for warmth
            audio = np.tanh(audio)
            
            return audio
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise