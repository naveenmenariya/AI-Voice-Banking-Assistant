"""
Handles Voice KYC (audio recording) and Video KYC (webcam recording).
Files are saved locally under the recordings/ directory.
"""

import os
import time
import wave

import cv2
import sounddevice as sd

# ── Config ────────────────────────────────────────────────────────────────────
RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), "recordings")
AUDIO_FILENAME = "kyc_audio.wav"
VIDEO_FILENAME = "kyc_video.avi"

AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_DURATION = 6
VIDEO_DURATION = 8
VIDEO_FPS = 20.0
VIDEO_RESOLUTION = (640, 480)


def _ensure_dir():
    os.makedirs(RECORDINGS_DIR, exist_ok=True)


# ── Audio KYC ─────────────────────────────────────────────────────────────────

def record_audio_kyc(speak, duration: int = AUDIO_DURATION) -> str:
    _ensure_dir()
    output_path = os.path.join(RECORDINGS_DIR, AUDIO_FILENAME)

    speak(
        "I will now record a short audio clip for identity verification. "
        "Please read the following sentence aloud when prompted: "
        "'My name is on my account and I authorise this transaction.' "
        "Recording starts in 3 seconds."
    )

    for i in range(3, 0, -1):
        print(f"  Starting in {i}...")
        time.sleep(1)

    speak("Recording now. Please speak clearly.")
    print("[REC] Audio recording started...")

    recording = sd.rec(
        int(duration * AUDIO_SAMPLE_RATE),
        samplerate=AUDIO_SAMPLE_RATE,
        channels=AUDIO_CHANNELS,
        dtype="int16"
    )
    sd.wait()

    with wave.open(output_path, "w") as wf:
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(AUDIO_SAMPLE_RATE)
        wf.writeframes(recording.tobytes())

    print(f"[REC] Audio saved → {output_path}")
    speak(
        "Audio recording complete. "
        "Your voice sample has been saved. "
        "KYC audio verification is done."
    )
    return output_path


# ── Video KYC ─────────────────────────────────────────────────────────────────

def record_video_kyc(speak, duration: int = VIDEO_DURATION) -> str:
    _ensure_dir()
    output_path = os.path.join(RECORDINGS_DIR, VIDEO_FILENAME)

    # UX IMPROVEMENT STARTS HERE
    speak(
        "We will now begin video KYC verification. "
        "Your camera will open shortly. "
        "Please make sure you are in a well-lit environment and your face is clearly visible."
    )

    time.sleep(2)

    speak("Please allow camera access if prompted. Preparing to open camera.")
    time.sleep(1)

    # Countdown before camera opens
    for i in range(3, 0, -1):
        speak(f"Opening camera in {i}")
        time.sleep(1)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        speak(
            "I could not access your camera. "
            "Please check your webcam connection or permissions and try again."
        )
        return ""

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(output_path, fourcc, VIDEO_FPS, VIDEO_RESOLUTION)

    speak("Recording will start now. Please look straight at the camera and remain still.")
    print("[REC] Video recording started...")

    start_time = time.time()
    frame_count = 0

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            speak("Camera feed interrupted. Stopping recording.")
            break

        elapsed = time.time() - start_time
        remaining = max(0, duration - elapsed)

        cv2.putText(
            frame,
            f"KYC Recording — {remaining:.1f}s remaining",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            (0, 0, 255), 2
        )

        cv2.putText(
            frame,
            "Dubai Bank — KYC Verification",
            (10, VIDEO_RESOLUTION[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (255, 255, 255), 1
        )

        writer.write(frame)
        cv2.imshow("Kentiq AI — KYC Recording (press Q to abort)", frame)

        frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            speak("KYC recording aborted by user.")
            break

    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    print(f"[REC] Video saved → {output_path} ({frame_count} frames)")

    speak(
        "Video recording complete. "
        "Your KYC video has been saved securely. "
        "Identity verification is now complete."
    )

    return output_path


# ── Voice-integrated handler ──────────────────────────────────────────────────

def handle_kyc(speak, listen) -> None:
    speak(
        "Starting KYC verification. "
        "Would you like audio KYC or video KYC? "
        "Say audio or video."
    )

    choice = listen(timeout=8) or ""

    if "audio" in choice:
        record_audio_kyc(speak)

    elif "video" in choice:
        record_video_kyc(speak)

    else:
        speak("I did not clearly understand your choice. Proceeding with audio KYC.")
        record_audio_kyc(speak)