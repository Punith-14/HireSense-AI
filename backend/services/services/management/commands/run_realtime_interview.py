import os
import tempfile
import wave

import numpy as np
from django.core.management.base import BaseCommand, CommandError

from services.ai.interview_engine import InterviewEngine
from services.speech.speech_service import SpeechService
from vision.services import VisionFrameProcessor


class Command(BaseCommand):
    help = "Run a realtime interview loop with optional webcam and microphone capture."

    def add_arguments(self, parser):
        parser.add_argument("--role", default="Python Developer")
        parser.add_argument("--mode", default="technical")
        parser.add_argument("--turns", type=int, default=3)
        parser.add_argument("--camera", type=int, default=0)
        parser.add_argument("--audio-seconds", type=float, default=12.0)
        parser.add_argument("--sample-rate", type=int, default=16000)
        parser.add_argument("--no-audio", action="store_true")
        parser.add_argument("--no-camera", action="store_true")

    def handle(self, *args, **options):
        engine = InterviewEngine()
        speech = SpeechService()
        capture = None
        processor = None

        if not options["no_camera"]:
            try:
                import cv2
            except ImportError as exc:
                raise CommandError("OpenCV is required for webcam capture.") from exc
            capture = cv2.VideoCapture(options["camera"])
            if not capture.isOpened():
                self.stdout.write("Webcam unavailable. Continuing without vision metrics.")
                capture = None
            else:
                processor = VisionFrameProcessor()

        result = engine.start(options["role"], options["mode"])
        session_id = result["session_id"]
        self.stdout.write(f"Session: {session_id}")
        self.stdout.write(f"Q1: {result['question']['question']}")

        try:
            for _ in range(options["turns"]):
                answer_text, speech_metrics = self._capture_answer(
                    speech, options["audio_seconds"], options["sample_rate"], options["no_audio"]
                )
                if not answer_text:
                    self.stdout.write("Empty answer received. Stopping.")
                    break

                vision_metrics = {}
                if capture and processor:
                    ok, frame = capture.read()
                    if ok:
                        vision_metrics = processor.process_frame(frame)

                response = engine.answer(
                    session_id,
                    answer_text,
                    speech_metrics=speech_metrics,
                    vision_metrics=vision_metrics,
                )
                evaluation = response["evaluation"]
                self.stdout.write(
                    "Scores: "
                    f"technical={evaluation['technical_score']} "
                    f"communication={evaluation['communication_score']} "
                    f"confidence={evaluation['confidence_score']} "
                    f"hesitation={evaluation['hesitation_score']}"
                )
                self.stdout.write(f"Next: {response['next_question']['question']}")
        finally:
            if capture:
                capture.release()

        report = engine.report(session_id)
        self.stdout.write(self.style.SUCCESS(f"Report generated: {report['report_id']}"))

    def _capture_answer(self, speech, audio_seconds, sample_rate, no_audio):
        if no_audio:
            answer = input("Answer text: ").strip()
            return answer, speech.analyze_text(answer)

        try:
            import sounddevice as sd
        except ImportError:
            self.stdout.write("sounddevice unavailable. Falling back to text input.")
            answer = input("Answer text: ").strip()
            return answer, speech.analyze_text(answer)

        frames = int(audio_seconds * sample_rate)
        self.stdout.write(f"Recording audio for {audio_seconds:.1f}s...")
        try:
            audio = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()
        except Exception:
            self.stdout.write("Microphone capture failed. Falling back to text input.")
            answer = input("Answer text: ").strip()
            return answer, speech.analyze_text(answer)

        wav_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                wav_path = temp_file.name
            with wave.open(wav_path, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(np.asarray(audio).tobytes())

            result = speech.transcribe_file(wav_path)
            transcript = (result.get("transcript") or "").strip()
            if transcript:
                return transcript, result.get("metrics", {})
            self.stdout.write("Transcription unavailable. Please type your answer.")
        finally:
            if wav_path:
                try:
                    os.remove(wav_path)
                except OSError:
                    pass

        answer = input("Answer text: ").strip()
        return answer, speech.analyze_text(answer)
