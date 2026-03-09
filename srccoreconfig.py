from dataclasses import dataclass
from typing import Dict, Any
import json
from pathlib import Path

@dataclass
class SystemConfig:
    """System-wide configuration settings."""
    
    # Audio settings
    SAMPLE_RATE: int = 44100
    CHANNELS: int = 2
    BIT_DEPTH: int = 24
    
    # Firebase settings
    FIREBASE_PROJECT_ID: str = "lofi-generator"
    
    # Output settings
    OUTPUT_DIR: Path = Path("output")
    TEMP_DIR: Path = Path("temp")
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'SystemConfig':
        """Load configuration from JSON file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path) as f:
            config_data = json.load(f)
        
        return cls(**config_data)

    def save_to_file(self, config_path: Path) -> None:
        """Save current configuration to JSON file."""
        config_data = {
            key: str(value) if isinstance(value, Path) else value
            for key, value in self.__dict__.items()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)