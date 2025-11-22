import azure.cognitiveservices.speech as speechsdk
from subtitle_window import SubtitleWindow

# ----------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------


win = SubtitleWindow()

# Auto-detect speech (German ↔ Arabic)
auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["de-DE", "ar-EG"]
)

translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=speech_key,
    region=service_region
)

translation_config.add_target_language("ar")   # German → Arabic
translation_config.add_target_language("de")   # Arabic → German

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

translator = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config,
    audio_config=audio_config,
    auto_detect_source_language_config=auto_detect
)

print("\n⚡ REAL-TIME Interpreter (German ↔ Arabic)\n")

last_original = ""
last_translated = ""

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

    # Extract ONLY new part (live-diff)
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

    win.update(
        f"{label_original}: {original_text}",
        f"{label_translated}: {translated_text}"
    )

    last_original = original_text
    last_translated = translated_text


def handle_recognized(evt):
    global last_original, last_translated
    last_original = ""
    last_translated = ""

translator.recognizing.connect(handle_recognizing)
translator.recognized.connect(handle_recognized)

translator.start_continuous_recognition()
win.run()
translator.stop_continuous_recognition()