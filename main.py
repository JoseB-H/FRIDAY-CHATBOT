import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import queue
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import queue
import threading
from PIL import Image
import logging
from datetime import datetime
from chatbot import responder, get_chatbot
from config import (
    APP_TITLE, APP_TAGLINE, APP_VERSION, APP_WIDTH, APP_HEIGHT,
    SPEECH_RATE, SPEECH_ENABLED, COLOR_BG_PRIMARY, COLOR_BG_SECONDARY,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_SUCCESS, COLOR_ERROR
)
from utils import ChatHistory
logger = logging.getLogger(__name__)
chat_history = ChatHistory("historial")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
class FridayApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} — {APP_TAGLINE}")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(800, 600)
        self.configure(fg_color=COLOR_BG_PRIMARY)
        self.attributes("-alpha", 0.0)
        self.is_loading = False
        self.recognizer = sr.Recognizer()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._load_assets()
        self._build_ui()
        self.after(100, self._fade_in)
    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(20, self._fade_in)
    def _load_assets(self):
        try:
            self.avatar_friday = ctk.CTkImage(Image.open("assets/avatar_friday.png"), size=(40, 40))
            self.avatar_user = ctk.CTkImage(Image.open("assets/avatar_user.png"), size=(40, 40))
        except Exception as e:
            logger.error(f"Error loading assets: {e}")
            self.avatar_friday = None
            self.avatar_user = None
    def _build_ui(self):
        main_container = ctk.CTkFrame(self, fg_color=COLOR_BG_PRIMARY, corner_radius=0)
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        self._build_header(main_container)
        self._build_chat_area(main_container)
        self._build_input_section(main_container)
        self._build_footer(main_container)
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color=COLOR_BG_SECONDARY, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        title = ctk.CTkLabel(
            title_frame,
            text=APP_TITLE,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_ACCENT
        )
        title.pack(side="left")
        version = ctk.CTkLabel(
            title_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=COLOR_TEXT_SECONDARY
        )
        version.pack(side="left", padx=(8, 0))
        tagline = ctk.CTkLabel(
            header,
            text=APP_TAGLINE,
            font=ctk.CTkFont(size=11),
            text_color=COLOR_TEXT_SECONDARY
        )
        tagline.grid(row=0, column=1, sticky="e", padx=20, pady=15)
        self.status_label = ctk.CTkLabel(
            header,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_SUCCESS
        )
        self.status_label.grid(row=0, column=2, padx=20, pady=15)
    def _build_chat_area(self, parent):
        self.chat_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            label_text=""
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.add_message("assistant", "Hola. Soy FRIDAY, tu asistente IA con voz integrada. Estoy aquí para ayudarte con preguntas, análisis, escritura y mucho más.")
    def add_message(self, role, text, animate=False):
        is_user = role == "user"
        avatar = self.avatar_user if is_user else self.avatar_friday
        name = "TÚ" if is_user else "FRIDAY"
        align = "e" if is_user else "w"
        bubble_color = COLOR_ACCENT if is_user else COLOR_BG_SECONDARY
        text_color = "white" if is_user else COLOR_TEXT_PRIMARY
        row_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=10, padx=5)
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(side="right" if is_user else "left", anchor=align)
        if not is_user and avatar:
            avatar_label = ctk.CTkLabel(content_frame, text="", image=avatar)
            avatar_label.pack(side="left", padx=(0, 10), anchor="n")
        bubble_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        bubble_container.pack(side="left")
        timestamp = datetime.now().strftime("%H:%M")
        header_text = f"{name} • {timestamp}"
        header = ctk.CTkLabel(
            bubble_container, 
            text=header_text, 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        header.pack(anchor="w" if not is_user else "e", pady=(0, 2))
        bubble = ctk.CTkFrame(bubble_container, fg_color=bubble_color, corner_radius=12)
        bubble.pack(anchor="w" if not is_user else "e")
        message_label = ctk.CTkLabel(
            bubble,
            text=text if not animate else "",
            font=ctk.CTkFont(size=13),
            text_color=text_color,
            wraplength=500,  
            justify="left"
        )
        message_label.pack(padx=15, pady=10)
        if is_user and avatar:
            avatar_label = ctk.CTkLabel(content_frame, text="", image=avatar)
            avatar_label.pack(side="left", padx=(10, 0), anchor="n")
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        if animate:
            self._animate_text(message_label, text)
    def _animate_text(self, label, full_text, index=0):
        if index < len(full_text):
            current_text = full_text[:index+1]
            label.configure(text=current_text)
            delay = 10 if len(full_text) > 100 else 20
            self.after(delay, lambda: self._animate_text(label, full_text, index+1))
        else:
            self.chat_frame._parent_canvas.yview_moveto(1.0)
    def _build_input_section(self, parent):
        input_frame = ctk.CTkFrame(parent, fg_color=COLOR_BG_SECONDARY, corner_radius=8)
        input_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)
        self.entrada = ctk.CTkEntry(
            input_frame,
            placeholder_text="Escribe tu mensaje aquí... (Presiona Enter o haz clic en Enviar)",
            fg_color=COLOR_BG_PRIMARY,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_ACCENT,
            border_width=1,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        self.entrada.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.entrada.bind("<Return>", self._on_enter_pressed)
        self.entrada.focus_set()
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="e", padx=10, pady=(0, 10))
        self.btn_send = ctk.CTkButton(
            button_frame,
            text="Enviar",
            command=self._send_message,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=6,
            height=32,
            width=100
        )
        self.btn_send.pack(side="left", padx=(0, 8))
        btn_clear = ctk.CTkButton(
            button_frame,
            text="Limpiar",
            command=self._clear_chat,
            fg_color=COLOR_BG_PRIMARY,
            hover_color=COLOR_TEXT_SECONDARY,
            text_color=COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=11),
            corner_radius=6,
            height=32,
            width=80,
            border_color=COLOR_ACCENT,
            border_width=1
        )
        btn_clear.pack(side="left", padx=(0, 8))
        self.voice_enabled = True
        self.btn_voice = ctk.CTkButton(
            button_frame,
            text="🔊",
            command=self._toggle_voice,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            height=32,
            width=40
        )
        self.btn_voice.pack(side="left")
        self.btn_mic = ctk.CTkButton(
            button_frame,
            text="🎤",
            command=self._listen_voice,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="white",
            font=ctk.CTkFont(size=12),
            corner_radius=6,
            height=32,
            width=40
        )
        self.btn_mic.pack(side="left", padx=(8, 0))
    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color=COLOR_BG_SECONDARY, corner_radius=0)
        footer.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        footer.grid_columnconfigure(1, weight=1)
        btn_about = ctk.CTkButton(
            footer,
            text="? Acerca de",
            command=self._show_about,
            fg_color="transparent",
            hover_color=COLOR_BG_PRIMARY,
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=9),
            corner_radius=4,
            height=24,
            border_color=COLOR_TEXT_SECONDARY,
            border_width=1
        )
        btn_about.pack(side="left", padx=10, pady=8)
        btn_save = ctk.CTkButton(
            footer,
            text="💾 Guardar",
            command=self._save_history,
            fg_color="transparent",
            hover_color=COLOR_BG_PRIMARY,
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=9),
            corner_radius=4,
            height=24,
            border_color=COLOR_TEXT_SECONDARY,
            border_width=1
        )
        btn_save.pack(side="left", padx=(0, 10))
        self.footer_status = ctk.CTkLabel(
            footer,
            text="Listo",
            font=ctk.CTkFont(size=9),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.footer_status.pack(side="right", padx=10, pady=8)
    def _on_enter_pressed(self, event):
        self._send_message()
    def _send_message(self):
        user_input = self.entrada.get().strip()
        if not user_input or self.is_loading:
            return
        self.is_loading = True
        self.btn_send.configure(state="disabled", text="Procesando...")
        self.entrada.delete(0, "end")
        self.entrada.configure(state="disabled")
        self.add_message("user", user_input)
        self.footer_status.configure(text="FRIDAY está respondiendo...")
        self.status_label.configure(text_color=COLOR_ACCENT)
        thread = threading.Thread(target=self._get_response, args=(user_input,))
        thread.daemon = True
        thread.start()
    def _get_response(self, user_input):
        try:
            respuesta = responder(user_input)
            self.after(0, lambda: self.add_message("assistant", respuesta, animate=True))
            chat_history.add_message("user", user_input)
            chat_history.add_message("assistant", respuesta)
            if self.voice_enabled and SPEECH_ENABLED:
                tts_thread = threading.Thread(target=self._speak_text, args=(respuesta,), daemon=True)
                tts_thread.start()
            self.footer_status.configure(text=f"Respuesta enviada • {len(chat_history.get_messages())//2} mensajes")
            self.status_label.configure(text_color=COLOR_SUCCESS)
        except Exception as e:
            self.after(0, lambda: self.add_message("assistant", f"ERROR: {str(e)}"))
            self.status_label.configure(text_color=COLOR_ERROR)
            self.footer_status.configure(text="Error en la respuesta")
        finally:
            self.is_loading = False
            self.btn_send.configure(state="normal", text="Enviar")
            self.entrada.configure(state="normal")
            self.entrada.focus_set()
    def _speak_text(self, text: str):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", SPEECH_RATE)
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.error(f"TTS error: {str(e)}")
    def _listen_voice(self):
        if self.is_loading:
            return
        self.footer_status.configure(text="Escuchando...")
        self.btn_mic.configure(fg_color=COLOR_SUCCESS)
        thread = threading.Thread(target=self._process_voice_input)
        thread.daemon = True
        thread.start()
    def _process_voice_input(self):
        q = queue.Queue()
        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))
        try:
            fs = 16000  
            seconds = 10  
            silence_threshold = 500  
            silence_duration = 1.5  
            recorded_frames = []
            silent_chunks = 0
            has_speech = False
            with sd.RawInputStream(samplerate=fs, blocksize=8000, device=None, dtype='int16',
                                   channels=1, callback=callback):
                start_time = datetime.now()
                while (datetime.now() - start_time).total_seconds() < seconds:
                    data = q.get()
                    recorded_frames.append(data)
                    audio_chunk = np.frombuffer(data, dtype=np.int16)
                    if np.max(np.abs(audio_chunk)) > silence_threshold:
                        silent_chunks = 0
                        has_speech = True
                    else:
                        silent_chunks += 1
                    if has_speech and silent_chunks > (silence_duration * (fs / 8000)):
                        break
            if not has_speech:
                self.after(0, lambda: self._on_voice_error("No se detectó voz"))
                return
            raw_data = b''.join(recorded_frames)
            audio_data = sr.AudioData(raw_data, fs, 2) 
            text = self.recognizer.recognize_google(audio_data, language="es-ES")
            self.after(0, lambda: self._on_voice_recognized(text))
        except sr.UnknownValueError:
            self.after(0, lambda: self._on_voice_error("No se entendió el audio"))
        except sr.RequestError as e:
            self.after(0, lambda: self._on_voice_error(f"Error de servicio: {e}"))
        except Exception as e:
            self.after(0, lambda: self._on_voice_error(f"Error: {str(e)}"))
    def _on_voice_recognized(self, text):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, text)
        self.btn_mic.configure(fg_color=COLOR_ACCENT)
        self.footer_status.configure(text="Voz reconocida")
        self._send_message()
    def _on_voice_error(self, message):
        self.btn_mic.configure(fg_color=COLOR_ACCENT)
        self.footer_status.configure(text=message)
        messagebox.showwarning("Reconocimiento de voz", message)
    def _clear_chat(self):
        if messagebox.askyesno("Confirmar", "¿Deseas limpiar todo el historial de chat?"):
            for widget in self.chat_frame.winfo_children():
                widget.destroy()
            self.add_message("assistant", "Historial limpiado. Comenzando nueva conversación.")
            chat_history.clear()
            get_chatbot().clear_history()
            self.footer_status.configure(text="Historial limpiado")
    def _toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        color = COLOR_SUCCESS if self.voice_enabled else COLOR_TEXT_SECONDARY
        self.btn_voice.configure(fg_color=color)
    def _save_history(self):
        try:
            filepath = chat_history.save_session()
            messagebox.showinfo("Guardado", f"Conversación guardada en:\n{filepath}")
            self.footer_status.configure(text=f"Guardado en: {filepath.split('/')[-1]}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
    def _show_about(self):
        messagebox.showinfo("Acerca de FRIDAY", about_text)
if __name__ == "__main__":
    app = FridayApp()
    app.mainloop()