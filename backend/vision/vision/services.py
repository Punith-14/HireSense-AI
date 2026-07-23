from functools import lru_cache

import cv2
import mediapipe as mp
from fer import FER


@lru_cache(maxsize=1)
def get_emotion_detector():
    return FER(mtcnn=False)


@lru_cache(maxsize=1)
def get_face_mesh():
    return mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


class VisionFrameProcessor:
    def __init__(self):
        self.emotion_detector = get_emotion_detector()
        self.face_mesh = get_face_mesh()

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        emotions = self.emotion_detector.detect_emotions(frame)
        mesh = self.face_mesh.process(rgb)
        dominant_emotion = None
        emotion_score = 0.0

        if emotions:
            emotion_map = emotions[0].get("emotions", {})
            if emotion_map:
                dominant_emotion, emotion_score = max(
                    emotion_map.items(), key=lambda item: item[1]
                )

        attention = self._estimate_attention(mesh)
        return {
            "face_detected": bool(emotions or mesh.multi_face_landmarks),
            "dominant_emotion": dominant_emotion,
            "emotion_score": float(emotion_score or 0.0),
            "attention": attention,
        }

    def annotate_frame(self, frame, result):
        status = "face" if result["face_detected"] else "no face"
        emotion = result["dominant_emotion"] or "unknown"
        attention = result["attention"]
        label = f"{status} | emotion: {emotion} | attention: {attention}"
        cv2.putText(
            frame,
            label,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        return frame

    def _estimate_attention(self, mesh_result):
        if not mesh_result.multi_face_landmarks:
            return "unknown"

        landmarks = mesh_result.multi_face_landmarks[0].landmark
        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        eye_center_x = (left_eye.x + right_eye.x) / 2
        offset = abs(nose.x - eye_center_x)

        if offset < 0.035:
            return "direct"
        if offset < 0.07:
            return "partial"
        return "away"
