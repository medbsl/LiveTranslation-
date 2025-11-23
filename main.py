import azure.cognitiveservices.speech as speechsdk
from subtitle_window import SubtitleWindow
import threading
from queue import Queue
import configparser

# -------- global vars to fix long sentence issue --------
cleared = False
last_partial = ""

# ---------------------------------------------------------
config = configparser.ConfigParser()
config.read("Settings.ini")

speech_key = config["azure"]["key"]
service_region = config["azure"]["region"]

queue = Queue()

auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["de-DE", "ar-EG", "ar-SA", "ar-AE"]
)

translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=speech_key,
    region=service_region
)

translation_config.add_target_language("ar")
translation_config.add_target_language("de")

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

translator = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config,
    audio_config=audio_config,
    auto_detect_source_language_config=auto_detect
)

print("\n⚡ REAL-TIME Interpreter (German ↔ Arabic)\n")

# ----------- on-clear callback -----------

def on_clear():
    global cleared
    cleared = True

# ----------- recognizer event -----------

def handle_recognizing(evt):
    global cleared, last_partial

    detected_lang = evt.result.properties.get(
        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
    )

    original_text = evt.result.text.strip()
    translations = evt.result.translations

    if detected_lang == "de-DE":
        translated_text = translations.get("ar", "")
        L1, L2 = "DE", "AR"
    else:
        translated_text = translations.get("de", "")
        L1, L2 = "AR", "DE"

    # ---- skip repeated long text after clearing ----
    if cleared:
        if original_text == last_partial:
            return      # ignore duplicates
        cleared = False  # now accept new text

    last_partial = original_text

    queue.put((
        f"{L1}: {original_text}",
        f"{L2}: {translated_text}"
    ))

translator.recognizing.connect(handle_recognizing)

# ----------- run recognizer in thread -----------

def recognizer_thread():
    translator.start_continuous_recognition_async().get()

threading.Thread(target=recognizer_thread, daemon=True).start()

# ----------- START UI -----------

win = SubtitleWindow(queue)
win.run()