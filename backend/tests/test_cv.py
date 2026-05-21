import os
import time

import cv2
import numpy as np
import pytest


def test_cv_ml_imports_and_versions():
    import fer
    import mediapipe as mp
    import tensorflow as tf

    assert cv2.__version__ == "4.11.0"
    assert mp.__version__ == "0.10.9"
    assert tf.__version__ == "2.16.1"
    assert hasattr(fer, "FER")


def test_vision_frame_processor_handles_blank_frame():
    from vision.services import VisionFrameProcessor

    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    processor = VisionFrameProcessor()
    result = processor.process_frame(frame)

    assert result["face_detected"] in {True, False}
    assert result["attention"] in {"unknown", "direct", "partial", "away"}


def test_vision_model_clients_are_cached():
    from vision.services import get_emotion_detector, get_face_mesh

    assert get_emotion_detector() is get_emotion_detector()
    assert get_face_mesh() is get_face_mesh()


@pytest.mark.hardware
def test_webcam_access_and_fps_probe():
    if os.getenv("RUN_LIVE_HARDWARE_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_HARDWARE_TESTS=1 to run real webcam validation.")

    capture = cv2.VideoCapture(0)
    try:
        assert capture.isOpened(), "Webcam index 0 is unavailable"
        frames = 0
        started_at = time.perf_counter()
        while time.perf_counter() - started_at < 2.0:
            ok, _frame = capture.read()
            assert ok, "Failed to read webcam frame"
            frames += 1
        fps = frames / max(time.perf_counter() - started_at, 0.001)
        assert fps >= 5, f"Webcam FPS too low: {fps:.2f}"
    finally:
        capture.release()
