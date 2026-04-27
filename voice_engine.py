"""
Handles all voice input (microphone -> text) and voice output (text -> speech).
Uses SpeechRecognition for STT and pyttsx3 for offline TTS.
Now includes proper noise handling using error_handler.
"""

import speech_recognition as sr
import pyttsx3
from error_handler import handle_noise_warning

# ── Shared recognizer instance ───────────────────────────────────────────────
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8
recognizer.dynamic_energy_threshold = True

# ── Initial ambient noise calibration (RUN ONCE) ─────────────────────────────
with sr.Microphone() as source:
    print("[Calibrating microphone for ambient noise...]")
    recognizer.adjust_for_ambient_noise(source, duration=1)


# ── TTS engine setup ─────────────────────────────────────────────────────────
def _make_tts_engine():
    engine = pyttsx3.init()
    engine.setProperty("rate", 155)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    for voice in voices:
        if "english" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break

    return engine


_tts_engine = _make_tts_engine()


# ── Public API ────────────────────────────────────────────────────────────────

def speak(text: str) -> None:
    """Convert text to speech and play it through the speakers."""
    global _tts_engine
    print(f"\n[BOT]: {text}")

    try:
        _tts_engine.say(text)
        _tts_engine.runAndWait()
    except RuntimeError:
        # Recreate engine if it crashes
        _tts_engine = _make_tts_engine()
        _tts_engine.say(text)
        _tts_engine.runAndWait()


def listen(timeout: int = 7, phrase_limit: int = 10) -> str:
    """
    Listen from the microphone and return recognised text (lowercase).
    Includes handling for silence, noise, and API issues.
    """
    with sr.Microphone() as source:
        print("[Listening...]")

        try:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit
            )
        except sr.WaitTimeoutError:
            print("[Timeout — no speech detected]")
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"[YOU]: {text}")
        return text.lower().strip()

    except sr.UnknownValueError:
        handle_noise_warning(speak)
        return ""

    except sr.RequestError:
        speak("Voice service is currently unavailable. Please try again.")
        return ""


def listen_for_confirmation() -> bool:
    """Ask for a yes/no answer. Returns True for yes, False for no."""
    for _ in range(2):
        response = listen(timeout=6)

        if any(w in response for w in ["yes", "yeah", "confirm", "correct", "proceed", "ok"]):
            return True

        if any(w in response for w in ["no", "nope", "cancel", "stop", "abort"]):
            return False

        speak("I didn't get that. Please say yes to confirm or no to cancel.")

    return False