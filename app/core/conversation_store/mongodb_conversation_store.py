from datetime import datetime, timezone
from typing import Any

import certifi
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING, MongoClient

from app.core.conversation_store.conversation_store import (
    Conversation,
    ConversationMessage,
    ConversationStore,
)


class MongoDBConversationStore(ConversationStore):

    def __init__(
        self,
        *,
        uri: str,
        db_name: str,
        conversations_collection_name: str = "conversations",
        messages_collection_name: str = "conversation_messages",
        retention_seconds: int = 30 * 24 * 60 * 60,
    ) -> None:
        self._client: MongoClient = MongoClient(uri, tlsCAFile=certifi.where())
        database = self._client[db_name]
        self._conversations = database[conversations_collection_name]
        self._messages = database[messages_collection_name]

        self._conversations.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])
        self._conversations.create_index("updated_at", expireAfterSeconds=retention_seconds)

        self._messages.create_index([("conversation_id", ASCENDING), ("created_at", ASCENDING)])
        self._messages.create_index("created_at", expireAfterSeconds=retention_seconds)

    def create_conversation(self, user_id: str, title: str) -> str:
        now = datetime.now(timezone.utc)
        document = {
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
        }

        result = self._conversations.insert_one(document)

        return str(result.inserted_id)

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        object_id = self._to_object_id(conversation_id)
        if object_id is None:
            return None

        document = self._conversations.find_one({"_id": object_id})

        if document is None:
            return None

        return self._to_conversation(str(document["_id"]), document)

    def list_conversations(self, user_id: str) -> list[Conversation]:
        cursor = self._conversations.find({"user_id": user_id}).sort("updated_at", DESCENDING)

        return [self._to_conversation(str(doc["_id"]), doc) for doc in cursor]

    def append_message(self, conversation_id: str, role: str, content: str) -> None:
        now = datetime.now(timezone.utc)

        self._messages.insert_one(
            {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": now,
            }
        )

        object_id = self._to_object_id(conversation_id)
        if object_id is not None:
            self._conversations.update_one({"_id": object_id}, {"$set": {"updated_at": now}})

    def get_messages(self, conversation_id: str, limit: int) -> list[ConversationMessage]:
        cursor = (
            self._messages.find({"conversation_id": conversation_id})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

        messages = [
            ConversationMessage(
                role=doc["role"],
                content=doc["content"],
                created_at=doc["created_at"],
            )
            for doc in cursor
        ]

        return list(reversed(messages))

    @staticmethod
    def _to_object_id(conversation_id: str) -> ObjectId | None:
        try:
            return ObjectId(conversation_id)
        except InvalidId:
            return None

    @staticmethod
    def _to_conversation(conversation_id: str, document: dict[str, Any]) -> Conversation:
        return Conversation(
            id=conversation_id,
            user_id=document["user_id"],
            title=document["title"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )

    def close(self) -> None:
        self._client.close()
