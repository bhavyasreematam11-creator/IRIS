"""Configuration management for IRIS (Intelligent Incident Response System)."""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Base directory for the IRIS project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)


@dataclass(frozen=True)
class ThemeColors:
    """Enterprise Dark Blue SaaS Theme Colors."""
    # Dark Blue Palette
    PRIMARY_BLUE: str = "#3B82F6"      # Electric Blue focal accent
    DEEP_BLUE: str = "#1D4ED8"         # Royal Blue
    LIGHT_BLUE: str = "#172554"        # Dark Blue banner / callout background
    NAVY_BACKGROUND: str = "#0B132B"   # Deep Dark Blue main canvas
    NAVY_SURFACE: str = "#111C3A"      # Dark Blue card surface
    NAVY_SURFACE_HOVER: str = "#162347"# Surface hover state
    NAVY_BORDER: str = "#1E2D54"       # Subtle card & divider border
    
    # Text and Accents
    WHITE: str = "#FFFFFF"
    BACKGROUND: str = "#0B132B"        # Main page background
    SURFACE: str = "#111C3A"           # Standard container surface
    BORDER: str = "#1E2D54"            # Border color
    TEXT: str = "#F8FAFC"              # Crisp white body text
    SECONDARY_TEXT: str = "#94A3B8"    # Muted slate secondary text
    
    # Status alerts
    SUCCESS_GREEN: str = "#10B981"
    WARNING_AMBER: str = "#F59E0B"
    CRITICAL_RED: str = "#EF4444"


@dataclass
class Settings:
    """Application settings with environment variable resolution."""
    # Project paths
    BASE_DIR: Path = BASE_DIR
    DB_PATH: Path = BASE_DIR / os.getenv("IRIS_DATABASE_PATH", "iris.db")
    SAMPLE_INCIDENTS_PATH: Path = BASE_DIR / "examples" / "sample_incidents.json"
    
    # Hindsight Persistent Memory Settings
    HINDSIGHT_BASE_URL: str = os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888").rstrip("/")
    HINDSIGHT_API_KEY: str = os.getenv("HINDSIGHT_API_KEY", "").strip()
    HINDSIGHT_BANK_ID: str = os.getenv("HINDSIGHT_BANK_ID", "iris-incident-memory").strip()
    HINDSIGHT_DEMO_MODE: bool = os.getenv("HINDSIGHT_DEMO_MODE", "false").lower() in ("true", "1", "yes")
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower().strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()
    
    # App Settings
    APP_NAME: str = "IRIS"
    APP_TAGLINE: str = "Turning Past Incidents into Future Intelligence."
    APP_VERSION: str = "v1.0.0"
    APP_ENV: str = os.getenv("IRIS_APP_ENV", "development")

    @classmethod
    def reload(cls) -> "Settings":
        """Reload environment settings dynamically."""
        load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
        return cls()


# Default singleton instance
settings = Settings()
colors = ThemeColors()
