from services.speech.speech_service import SpeechService, SpeechServiceError


class SpeechAnalyzer(SpeechService):
    """Compatibility wrapper for legacy imports."""


SpeechAnalysisError = SpeechServiceError
