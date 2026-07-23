try:
    import cv2
    import numpy as np
    from vision.services import VisionFrameProcessor
except ImportError:
    cv2 = None
    np = None
    VisionFrameProcessor = None

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from services.confidence_engine import ConfidenceEngine


@api_view(["POST"])
def analyze_frame(request):
    if cv2 is None:
        return Response({"error": "Vision dependencies (OpenCV/TensorFlow) are not installed."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    image_file = request.FILES.get("image_file")
    if not image_file:
        return Response({"error": "image_file is required"}, status=status.HTTP_400_BAD_REQUEST)

    data = np.frombuffer(image_file.read(), dtype=np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if frame is None:
        return Response({"error": "image_file must be a decodable image"}, status=status.HTTP_400_BAD_REQUEST)

    result = VisionFrameProcessor().process_frame(frame)
    confidence = ConfidenceEngine().calculate({}, result)
    return Response({"status": "ok", "vision": result, "confidence": confidence})
