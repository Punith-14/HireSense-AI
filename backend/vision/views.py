import base64
import binascii

import cv2
import numpy as np
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from services.confidence_engine import ConfidenceEngine
from vision.services import VisionFrameProcessor


def _decode_frame_from_request(request):
    image_file = request.FILES.get("image_file")
    if image_file:
        data = np.frombuffer(image_file.read(), dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if frame is None:
            return None, "image_file must be a decodable image"
        return frame, None

    image_base64 = (request.data.get("image_base64") or request.data.get("image") or "").strip()
    if image_base64:
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,", 1)[1]
        image_base64 = "".join(image_base64.split())
        try:
            decoded = base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError):
            return None, "image_base64 must be valid base64 data"
        data = np.frombuffer(decoded, dtype=np.uint8)
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if frame is None:
            return None, "image_base64 must decode to an image"
        return frame, None

    return None, "image_file or image_base64 is required"


def _analyze_frame(frame):
    result = VisionFrameProcessor().process_frame(frame)
    confidence = ConfidenceEngine().calculate({}, result)
    return {"status": "ok", "vision": result, "confidence": confidence}


@api_view(["POST"])
def analyze_frame(request):
    frame, error = _decode_frame_from_request(request)
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    return Response(_analyze_frame(frame))


@api_view(["POST"])
def upload_frame(request):
    frame, error = _decode_frame_from_request(request)
    if error:
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

    return Response(_analyze_frame(frame))
