import azure.cognitiveservices.speech as speechsdk
import sys


# 🔑 Replace this with your Azure Speech key


translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=speech_key,
    region=service_region
)

translation_config.speech_recognition_language = "de-DE"
translation_config.add_target_language("ar")

audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
translator = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config,
    audio_config=audio_config
)

print("⚡ Arabic Real-Time Translation (NO REPETITION)\n")

# --- LCS Algorithm ---
def lcs(a, b):
    dp = [["" for _ in range(len(b)+1)] for _ in range(len(a)+1)]
    for i in range(len(a)):
        for j in range(len(b)):
            if a[i] == b[j]:
                dp[i+1][j+1] = dp[i][j] + " " + a[i] if dp[i][j] else a[i]
            else:
                dp[i+1][j+1] = dp[i][j+1] if len(dp[i][j+1].split()) > len(dp[i+1][j].split()) else dp[i+1][j]
    return dp[-1][-1].strip()

last_text = ""

def handle_recognizing(evt):
    global last_text
    partial = evt.result.translations.get("ar", "").strip()
    if not partial:
        return

    # Tokenize
    old_tokens = last_text.split()
    new_tokens = partial.split()

    # Find shared part with LCS
    shared = lcs(old_tokens, new_tokens).split()

    # Extract only new (delta)
    delta = new_tokens[len(shared):]

    if delta:
        out = " ".join(delta)
        sys.stdout.write(out + " ")
        sys.stdout.flush()

    last_text = partial


def handle_recognized(evt):
    global last_text
    last_text = ""   # reset when final sentence delivered


translator.recognizing.connect(handle_recognizing)
translator.recognized.connect(handle_recognized)

translator.start_continuous_recognition()

try:
    while True:
        pass
except KeyboardInterrupt:
    translator.stop_continuous_recognition()
    print("\n🛑 Stopped.")