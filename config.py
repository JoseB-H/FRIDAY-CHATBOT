import os
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "YOUR_API_KEY_HERE"
)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 2048
APP_TITLE = "FRIDAY"
APP_TAGLINE = "Asistente de IA · Powered by Google Gemini"
APP_VERSION = "2.0"
APP_WIDTH = 900
APP_HEIGHT = 700
SPEECH_RATE = 170
SPEECH_ENABLED = True
HISTORY_DIR = Path(__file__).parent / "historial"
HISTORY_MAX_MESSAGES = 50
COLOR_BG_PRIMARY = "#09090b" 
COLOR_BG_SECONDARY = "#18181b" 
COLOR_ACCENT = "#3b82f6" 
COLOR_ACCENT_HOVER = "#2563eb" 
COLOR_TEXT_PRIMARY = "#f4f4f5" 
COLOR_TEXT_SECONDARY = "#a1a1aa" 
COLOR_SUCCESS = "#10b981" 
COLOR_WARNING = "#f59e0b" 
COLOR_ERROR = "#ef4444" 
HISTORY_DIR.mkdir(exist_ok=True)