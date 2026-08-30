# app/core/user_config.py

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.core.user_store.mongodb_user_store import MongoDBUserStore
from app.core.user_store.user_store import UserStore


@lru_cache
def get_user_store() -> UserStore:
    settings: Settings = get_settings()

    return MongoDBUserStore(
        uri=settings.mongodb_uri.get_secret_value(),
        db_name=settings.mongodb_db_name,
        collection_name=settings.mongodb_users_collection,
    )
