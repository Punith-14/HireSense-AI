import os
from functools import lru_cache

from dotenv import load_dotenv
from mongoengine import connect, disconnect, get_connection
from pymongo.errors import ServerSelectionTimeoutError


load_dotenv()


@lru_cache(maxsize=1)
def connect_mongodb():
    db_name = (
        os.getenv("MONGO_DB_NAME")
        or os.getenv("MONGODB_DB_NAME")
        or "hiresense_ai"
    )
    uri = (
        os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URI")
        or f"mongodb://localhost:27017/{db_name}"
    )
    alias = os.getenv("MONGO_ALIAS") or os.getenv("MONGODB_ALIAS") or "default"
    timeout_ms = int(
        os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS")
        or os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS")
        or "3000"
    )

    try:
        existing = get_connection(alias=alias)
        existing.admin.command("ping")
        return existing
    except Exception:
        disconnect(alias=alias)

    connection = connect(
        db=db_name,
        host=uri,
        alias=alias,
        serverSelectionTimeoutMS=timeout_ms,
        uuidRepresentation="standard",
    )
    connection.admin.command("ping")
    _ensure_indexes()
    return connection


def assert_mongodb_ready():
    try:
        connect_mongodb()
        return True, "MongoDB connection healthy"
    except ServerSelectionTimeoutError as exc:
        return False, f"MongoDB unavailable: {exc}"
    except Exception as exc:
        return False, f"MongoDB connection failed: {exc}"


def _ensure_indexes():
    from utils.mongo_documents import Interview, InterviewSession, Report, UserProfile

    for document in (UserProfile, InterviewSession, Interview, Report):
        document.ensure_indexes()
