import audioop
import wave


def detect_pauses_wav(path, silence_threshold=450, min_pause_ms=550, chunk_ms=30):
    try:
        with wave.open(path, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            sample_width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()
            frame_count = wav_file.getnframes()
            duration_seconds = frame_count / float(sample_rate or 1)
            chunk_frames = max(1, int(sample_rate * chunk_ms / 1000))
            min_pause_chunks = max(1, int(min_pause_ms / chunk_ms))
            pauses = []
            current_silent_chunks = 0
            chunk_index = 0

            while True:
                data = wav_file.readframes(chunk_frames)
                if not data:
                    break
                if channels > 1:
                    data = audioop.tomono(data, sample_width, 0.5, 0.5)
                rms = audioop.rms(data, sample_width)
                if rms < silence_threshold:
                    current_silent_chunks += 1
                else:
                    if current_silent_chunks >= min_pause_chunks:
                        end_ms = chunk_index * chunk_ms
                        start_ms = end_ms - current_silent_chunks * chunk_ms
                        pauses.append({"start_ms": start_ms, "end_ms": end_ms})
                    current_silent_chunks = 0
                chunk_index += 1

            if current_silent_chunks >= min_pause_chunks:
                end_ms = chunk_index * chunk_ms
                start_ms = end_ms - current_silent_chunks * chunk_ms
                pauses.append({"start_ms": start_ms, "end_ms": end_ms})

        pause_duration = sum((pause["end_ms"] - pause["start_ms"]) for pause in pauses) / 1000
        return {
            "pause_count": len(pauses),
            "pause_duration_seconds": round(pause_duration, 2),
            "duration_seconds": round(duration_seconds, 2),
            "pauses": pauses,
        }
    except (OSError, wave.Error, audioop.error, ZeroDivisionError):
        return {"pause_count": 0, "pause_duration_seconds": 0, "duration_seconds": 0, "pauses": []}
