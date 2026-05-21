import os
import uuid

import pytest

os.environ.setdefault("LLM_PROVIDER", "local")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient(HTTP_HOST="127.0.0.1")


@pytest.fixture
def qa_email():
    return f"qa-{uuid.uuid4().hex[:12]}@hiresense.test"


@pytest.fixture
def mongo_ready():
    from config.db import assert_mongodb_ready

    ok, message = assert_mongodb_ready()
    assert ok, message
    return True
