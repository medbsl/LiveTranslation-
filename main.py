import azure.cognitiveservices.speech as speechsdk
from subtitle_window import SubtitleWindow

from queue import Queue
import threading
import configparser



# ----------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------

config = configparser.ConfigParser()
config.read("Settings.ini")

speech_key = config["azure"]["key"]
service_region = config["azure"]["region"]




queue = Queue()

last_original = ""
last_translated = ""

def reset_recognizer_memory():
    """Called when the subtitle window clears due to overflow."""
    global last_original, last_translated
    last_original = ""
    last_translated = ""


# -------------------------------
# Azure Speech Setup
# -------------------------------
auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["de-DE", "ar-EG"]
)

translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=speech_key,
    region=service_region
)

translation_config.add_target_language("ar")   # DE → AR
translation_config.add_target_language("de")   # AR → DE

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

translator = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config,
    audio_config=audio_config,
    auto_detect_source_language_config=auto_detect
)

print("\n⚡ REAL-TIME Interpreter (German ↔ Arabic)\n")


# -------------------------------
# Callbacks
# -------------------------------
def handle_recognizing(evt):
    global last_original, last_translated

    detected_lang = evt.result.properties.get(
        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
    )

    original_text = evt.result.text.strip()
    translations = evt.result.translations

    if detected_lang == "de-DE":
        translated_text = translations.get("ar", "").strip()
        label_original, label_translated = "DE", "AR"
    else:
        translated_text = translations.get("de", "").strip()
        label_original, label_translated = "AR", "DE"

    # New fresh block to send to UI
    queue.put((
        f"{label_original}: {original_text}",
        f"{label_translated}: {translated_text}"
    ))

    new_original = (
        original_text[len(last_original):]
        if original_text.startswith(last_original)
        else original_text
    )

    new_translated = (
        translated_text[len(last_translated):]
        if translated_text.startswith(last_translated)
        else translated_text
    )


def handle_recognized(evt):
    """When Azure finalizes a phrase, reset memory."""
    global last_original, last_translated
    last_original = ""
    last_translated = ""


translator.recognizing.connect(handle_recognizing)
translator.recognized.connect(handle_recognized)


# -------------------------------
# Recognizer Thread
# -------------------------------
def recognizer_thread():
    translator.start_continuous_recognition_async().get()


threading.Thread(target=recognizer_thread, daemon=True).start()


# -------------------------------
# Start UI
# -------------------------------
win = SubtitleWindow(queue, reset_recognizer_memory)
win.run()