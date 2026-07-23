import re

from services.speech.filler_detector import detect_fillers


WORD_PATTERN = re.compile(r"[A-Za-z0-9+#.]+")


def calculate_speech_metrics(text, duration_seconds=0, pause_metrics=None):
    words = WORD_PATTERN.findall(text or "")
    filler_result = detect_fillers(text)
    duration = float(duration_seconds or 0)
    pause_metrics = pause_metrics or {}
    words_per_minute = round((len(words) / duration) * 60, 1) if duration > 0 else 0
    pause_count = int(pause_metrics.get("pause_count", 0) or 0)
    pause_duration = float(pause_metrics.get("pause_duration_seconds", 0) or 0)

    hesitation_score = min(
        100,
        filler_result["filler_count"] * 10
        + pause_count * 8
        + pause_duration * 4
        + max(0, 90 - words_per_minute) * 0.25
        + max(0, words_per_minute - 180) * 0.2,
    )
    communication_score = max(
        0,
        min(
            100,
            72
            + min(len(words), 90) * 0.15
            - filler_result["filler_count"] * 4
            - pause_count * 2
            - max(0, pause_duration - 3) * 1.5,
        ),
    )

    return {
        "word_count": len(words),
        "filler_count": filler_result["filler_count"],
        "fillers": filler_result["fillers"],
        "pause_count": pause_count,
        "pause_duration_seconds": round(pause_duration, 2),
        "duration_seconds": round(duration, 2),
        "words_per_minute": words_per_minute,
        "hesitation_score": round(hesitation_score),
        "communication_score": round(communication_score),
    }
