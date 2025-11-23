import azure.cognitiveservices.speech as speechsdk
from subtitle_window import SubtitleWindow
import threading
from queue import Queue
import configparser
import deepl  # <---- NEW

# -------- global vars to fix long sentence issue --------
cleared = False
last_partial = ""

# ---------------------------------------------------------
config = configparser.ConfigParser()
config.read("Settings.ini")

speech_key = config["azure"]["key"]
service_region = config["azure"]["region"]

DEEPL_KEY = config["deepl"]["key"]
deepl_translator = deepl.Translator(DEEPL_KEY)

queue = Queue()

auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["de-DE", "ar-EG", "ar-SA", "ar-AE"]
)

speech_config = speechsdk.SpeechConfig(
    subscription=speech_key,
    region=service_region
)

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    auto_detect_source_language_config=auto_detect,
    audio_config=audio_config
)

print("\n⚡ REAL-TIME Interpreter (German ↔ Arabic via DeepL)\n")

# ----------- on-clear callback -----------
def on_clear():
    global cleared
    cleared = True

# ----------- recognizer event -----------
def handle_recognizing(evt):
    global cleared, last_partial

    detected_lang_result = evt.result.properties.get(
        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
    )
    if not detected_lang_result:
        return

    # detected language code:
    detected_lang = detected_lang_result.lower()

    original_text = evt.result.text.strip()
    if original_text == "":
        return

    # ---- skip repeated long text after clearing ----
    if cleared:
        if original_text == last_partial:
            return
        cleared = False

    last_partial = original_text

    # -------- DETECT LANGUAGE --------
    if detected_lang.startswith("de"):
        src = "DE"
        tgt = "AR"
        target_lang_code = "ar"
    else:
        src = "AR"
        tgt = "DE"
        target_lang_code = "de"

    # -------- DEEPL TRANSLATION --------
    try:
        translated_text = deepl_translator.translate_text(
            original_text,
            target_lang=target_lang_code
        ).text
    except Exception as e:
        translated_text = f"[DeepL error: {e}]"

    # -------- PUSH TO WINDOW --------
    queue.put((
        f"{src}: {original_text}",
        f"{tgt}: {translated_text}"
    ))


recognizer.recognizing.connect(handle_recognizing)

# ----------- run recognizer in thread -----------
def recognizer_thread():
    recognizer.start_continuous_recognition_async().get()

threading.Thread(target=recognizer_thread, daemon=True).start()

# ----------- START UI -----------
win = SubtitleWindow(queue)
win.run()
