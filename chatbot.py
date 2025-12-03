import logging
from typing import Generator
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
genai.configure(api_key=GEMINI_API_KEY)
class GeminiChatBot:
    def __init__(self):
        self.model = genai.GenerativeModel(
            GEMINI_MODEL,
        )
        self.chat_history = []
    def responder(self, texto: str) -> str:
        try:
            self.chat_history.append({"role": "user", "content": texto})
            messages = []
            for msg in self.chat_history:
                role = "user" if msg["role"] == "user" else "model"
                messages.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=GEMINI_MAX_TOKENS,
                ),
            )
            respuesta = response.text.strip()
            self.chat_history.append({"role": "assistant", "content": respuesta})
            logger.info(f"✓ Response generated successfully")
            return respuesta
        except Exception as blocked_error:
            if "BlockedPromptException" in str(type(blocked_error)):
                error_msg = "Esta consulta fue bloqueada por políticas de seguridad."
                logger.warning(f"Blocked prompt: {texto}")
                return error_msg
            raise
        except Exception as e:
            error_msg = f"Error: No pude procesar tu solicitud. {str(e)}"
            logger.error(f"Error generating response: {str(e)}")
            return error_msg
    def responder_stream(self, texto: str) -> Generator[str, None, None]:
        try:
            self.chat_history.append({"role": "user", "content": texto})
            messages = []
            for msg in self.chat_history:
                role = "user" if msg["role"] == "user" else "model"
                messages.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=GEMINI_MAX_TOKENS,
                ),
                stream=True,
            )
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            self.chat_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            error_msg = f"Error en streaming: {str(e)}"
            logger.error(error_msg)
            yield error_msg
    def clear_history(self) -> None:
        self.chat_history = []
        logger.info("Chat history cleared")
    def get_history(self) -> list:
        return self.chat_history
_chatbot_instance = None
def get_chatbot() -> GeminiChatBot:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = GeminiChatBot()
    return _chatbot_instance
def responder(texto: str) -> str:
    return get_chatbot().responder(texto)
def responder_stream(texto: str) -> Generator[str, None, None]:
    return get_chatbot().responder_stream(texto)