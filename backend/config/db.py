import os
from functools import lru_cache

from dotenv import load_dotenv
from mongoengine import connect, disconnect, get_connection
from pymongo.errors import ServerSelectionTimeoutError


load_dotenv()


@lru_cache(maxsize=1)
def connect_mongodb():
    db_name = os.getenv("MONGODB_DB_NAME", "hiresenseai")
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hiresenseai")
    alias = os.getenv("MONGODB_ALIAS", "default")
    timeout_ms = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "3000"))

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
    return connection


def assert_mongodb_ready():
    try:
        connect_mongodb()
        return True, "MongoDB connection healthy"
    except ServerSelectionTimeoutError as exc:
        return False, f"MongoDB unavailable: {exc}"
    except Exception as exc:
        return False, f"MongoDB connection failed: {exc}"
