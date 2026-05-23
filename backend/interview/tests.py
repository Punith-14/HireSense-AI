from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class InterviewAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch("interview.services.interview_router.generate_technical_question")
    def test_generate_technical_question(self, mock_generate):
        mock_generate.return_value = "Mock technical question"

        response = self.client.post(
            "/api/generate-question/",
            {
                "interview_type": "technical",
                "role": "Java Developer",
                "difficulty": "medium"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "technical")
        self.assertEqual(response.data["question"], "Mock technical question")
        mock_generate.assert_called_once_with("Java Developer", "medium")

    @patch("interview.services.interview_router.generate_hr_question")
    def test_generate_hr_question(self, mock_generate):
        mock_generate.return_value = "Mock HR question"

        response = self.client.post(
            "/api/generate-question/",
            {
                "interview_type": "hr",
                "role": "Java Developer"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "hr")
        self.assertEqual(response.data["question"], "Mock HR question")
        mock_generate.assert_called_once_with("Java Developer")

    @patch("interview.services.interview_router.generate_behavioral_question")
    def test_generate_behavioral_question(self, mock_generate):
        mock_generate.return_value = "Mock behavioral question"

        response = self.client.post(
            "/api/generate-question/",
            {
                "interview_type": "behavioral",
                "topic": "leadership"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "behavioral")
        self.assertEqual(response.data["question"], "Mock behavioral question")
        mock_generate.assert_called_once_with("leadership")

    @patch("interview.services.interview_router.evaluate_answer")
    def test_evaluate_technical_response(self, mock_evaluate):
        mock_evaluate.return_value = {
            "technical_score": 80,
            "communication_score": 75,
            "feedback": "Good answer",
            "followup_question": "Mock follow-up"
        }

        response = self.client.post(
            "/api/evaluate-response/",
            {
                "interview_type": "technical",
                "question": "What is polymorphism?",
                "answer": "It allows many forms."
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "technical")
        self.assertEqual(response.data["next_difficulty"], "hard")
        self.assertEqual(response.data["result"]["technical_score"], 80)
        mock_evaluate.assert_called_once_with(
            "What is polymorphism?",
            "It allows many forms."
        )

    @patch("interview.services.interview_router.evaluate_hr_answer")
    def test_evaluate_hr_response(self, mock_evaluate):
        mock_evaluate.return_value = {
            "communication_score": 85,
            "confidence_score": 80,
            "feedback": "Confident answer",
            "followup_question": "Mock HR follow-up"
        }

        response = self.client.post(
            "/api/evaluate-response/",
            {
                "interview_type": "hr",
                "question": "Tell me about yourself.",
                "answer": "I am a Java developer."
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "hr")
        self.assertEqual(response.data["result"]["confidence_score"], 80)
        mock_evaluate.assert_called_once_with(
            "Tell me about yourself.",
            "I am a Java developer."
        )

    @patch("interview.services.interview_router.evaluate_behavioral_answer")
    def test_evaluate_behavioral_response(self, mock_evaluate):
        mock_evaluate.return_value = {
            "teamwork_score": 78,
            "leadership_score": 82,
            "communication_score": 80,
            "feedback": "Strong STAR structure",
            "followup_question": "Mock behavioral follow-up"
        }

        response = self.client.post(
            "/api/evaluate-response/",
            {
                "interview_type": "behavioral",
                "question": "Tell me about a leadership challenge.",
                "answer": "I led a team during a deadline."
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["interview_type"], "behavioral")
        self.assertEqual(response.data["result"]["leadership_score"], 82)
        mock_evaluate.assert_called_once_with(
            "Tell me about a leadership challenge.",
            "I led a team during a deadline."
        )

    def test_invalid_interview_type_returns_error(self):
        response = self.client.post(
            "/api/generate-question/",
            {"interview_type": "managerial"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Invalid interview_type")

    def test_evaluate_response_requires_question_and_answer(self):
        response = self.client.post(
            "/api/evaluate-response/",
            {"interview_type": "technical"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "question and answer are required"
        )
