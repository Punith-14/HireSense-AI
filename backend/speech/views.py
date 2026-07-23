from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from services.speech.speech_service import SpeechService


@api_view(["POST"])
def transcribe(request):
    audio_file = request.FILES.get("audio_file")
    text = (request.data.get("text") or "").strip()
    duration_seconds = float(request.data.get("duration_seconds") or 0)

    service = SpeechService()
    if audio_file:
        result = service.transcribe_uploaded_file(audio_file)
        http_status = status.HTTP_200_OK if result["status"] == "ok" else status.HTTP_422_UNPROCESSABLE_ENTITY
        return Response(result, status=http_status)

    if text:
        return Response(
            {
                "status": "ok",
                "provider": "text_metrics_only",
                "transcript": text,
                "metrics": service.analyze_text(text, duration_seconds),
                "errors": [],
            }
        )

    return Response({"error": "audio_file or text is required"}, status=status.HTTP_400_BAD_REQUEST)
