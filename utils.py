import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
class ChatHistory:
    def __init__(self, history_dir: Path, max_messages: int = 50):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.max_messages = max_messages
        self.messages: List[Dict[str, Any]] = []
    def add_message(self, role: str, content: str, timestamp: str = None) -> None:
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp
        }
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    def get_messages(self) -> List[Dict[str, str]]:
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    def get_display_messages(self) -> List[Dict[str, Any]]:
        return self.messages
    def save_session(self, filename: str = None) -> str:
        if filename is None:
            filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.history_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)
        return str(filepath)
    def clear(self) -> None:
        self.messages = []
    def load_session(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            self.messages = json.load(f)