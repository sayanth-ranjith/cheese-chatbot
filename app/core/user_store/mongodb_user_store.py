from datetime import datetime, timezone
from typing import Any

import certifi
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, MongoClient

from app.core.user_store.user_store import User, UserStore


class MongoDBUserStore(UserStore):

    def __init__(
        self,
        *,
        uri: str,
        db_name: str,
        collection_name: str = "users",
    ) -> None:
        self._client: MongoClient = MongoClient(uri, tlsCAFile=certifi.where())
        self._collection = self._client[db_name][collection_name]
        self._collection.create_index([("email", ASCENDING)], unique=True)

    def create(self, email: str, hashed_password: str) -> User:
        document = {
            "email": email,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc),
        }

        result = self._collection.insert_one(document)

        return self._to_user(str(result.inserted_id), document)

    def get_by_email(self, email: str) -> User | None:
        document = self._collection.find_one({"email": email})

        if document is None:
            return None

        return self._to_user(str(document["_id"]), document)

    def get_by_id(self, user_id: str) -> User | None:
        try:
            object_id = ObjectId(user_id)
        except InvalidId:
            return None

        document = self._collection.find_one({"_id": object_id})

        if document is None:
            return None

        return self._to_user(str(document["_id"]), document)

    @staticmethod
    def _to_user(user_id: str, document: dict[str, Any]) -> User:
        return User(
            id=user_id,
            email=document["email"],
            hashed_password=document["hashed_password"],
            created_at=document["created_at"],
        )

    def close(self) -> None:
        self._client.close()
