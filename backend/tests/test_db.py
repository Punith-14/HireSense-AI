import pytest
from mongoengine import NotUniqueError, disconnect


def test_mongodb_connection_healthy(mongo_ready):
    assert mongo_ready is True


def test_user_unique_email_prevents_duplicates(qa_email, mongo_ready):
    from utils.mongo_documents import UserProfile

    UserProfile(email=qa_email, full_name="QA One").save()
    duplicate = UserProfile(email=qa_email, full_name="QA Two")

    with pytest.raises(NotUniqueError):
        duplicate.save()

    assert UserProfile.objects(email=qa_email).count() == 1


def test_persistence_survives_reconnect(qa_email, mongo_ready):
    from config.db import connect_mongodb
    from utils.mongo_documents import UserProfile

    user = UserProfile(email=qa_email, full_name="Persistent QA").save()
    user_id = user.id

    disconnect(alias="default")
    connect_mongodb.cache_clear()
    connect_mongodb()

    restored = UserProfile.objects.get(id=user_id)
    assert restored.email == qa_email
    assert restored.full_name == "Persistent QA"


def test_required_collection_indexes_exist(mongo_ready):
    from utils.mongo_documents import Interview, InterviewSession, Report, UserProfile

    collections = [UserProfile, InterviewSession, Interview, Report]
    for document in collections:
        document.ensure_indexes()
        index_names = document._get_collection().index_information().keys()
        assert "_id_" in index_names
        assert len(index_names) >= 2
