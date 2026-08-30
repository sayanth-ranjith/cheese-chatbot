# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Cheese Chatbot is a RAG (Retrieval-Augmented Generation) assistant for the **CheeseRetry** Java library. It retrieves relevant chunks from a knowledge base (CheeseRetry's README + Javadoc HTML) and grounds LLM answers in that context, rather than relying on the model's pre-trained knowledge.

Tech stack: FastAPI, LangChain, Groq (LLM), Jina (embeddings), MongoDB Atlas + Atlas Vector Search (vector store), Python 3.13, `uv` for dependency management.

This is a personal learning project (first AI project for the author) built incrementally with Claude Code's assistance — expect the codebase to still be evolving rather than fully "finished" (e.g. no dedup on re-ingestion).

## Commands

```bash
# Install dependencies
uv sync

# Run the API (must be run from repo root; app entrypoint is app/main.py, not a root main.py)
uv run uvicorn app.main:app --reload

# Run the full test suite (use `python -m pytest`, NOT bare `pytest` —
# bare pytest fails with "ModuleNotFoundError: No module named 'app'"
# because it doesn't add the repo root to sys.path the way `python -m` does)
uv run python -m pytest -q

# Run a single test file / test
uv run python -m pytest tests/core/service/test_chat_service.py -q
uv run python -m pytest tests/core/service/test_chat_service.py::TestAsk::test_grounds_answer_in_retrieved_context_and_returns_sources -q

# Lint / type-check
uv run ruff check .
uv run mypy app

# Add a dependency (this project uses uv, not bare pip — a bare `pip install`
# installs into a different environment than the one uvicorn/pytest actually run from)
uv add <package>
```

**Known issue:** `tests/core/embedding_model/test_jina_embedding_model.py` is a leftover manual smoke-test script (module-level code, not `pytest` test functions) that was accidentally placed under `tests/` with a `test_` filename. It fails at collection time (`ValueError: Jina API key must not be empty`, or `ModuleNotFoundError` under bare `pytest`) because it instantiates `JinaEmbeddingModel(api_key="")` at import time. This is pre-existing and unrelated to real regressions — if it errors during collection, that's expected; don't waste time debugging it as a real test failure.

## Environment

Settings load from `.env` via `pydantic-settings` (`app/core/config.py`). These are **required** (the app fails to start without them — no defaults):
- `GROQ_API_KEY`
- `JINA_API_KEY`
- `MONGODB_URI`
- `JWT_SECRET_KEY` — generate with e.g. `openssl rand -hex 32`

Optional, with defaults: `GROQ_MODEL` (`openai/gpt-oss-120b`), `JINA_MODEL` (`jina-embeddings-v3`), `KNOWLEDGE_BASE_DIR` (`app/knowledge_base`), `CHUNK_SIZE` (1000), `CHUNK_OVERLAP` (200), `MONGODB_DB_NAME` (`cheese_chatbot`), `MONGODB_COLLECTION` (`kb_chunks`), `MONGODB_VECTOR_INDEX` (`kb_vector_index`), `RETRIEVAL_TOP_K` (5), `MONGODB_USERS_COLLECTION` (`users`), `MONGODB_CONVERSATIONS_COLLECTION` (`conversations`), `MONGODB_MESSAGES_COLLECTION` (`conversation_messages`), `BCRYPT_ROUNDS` (12), `JWT_ALGORITHM` (`HS256`), `JWT_EXPIRES_MINUTES` (10080, 7 days), `CONVERSATION_RETENTION_DAYS` (30), `CONVERSATION_HISTORY_LIMIT` (10).

This app has no offline/mocked mode for its external dependencies — it talks to real Groq, Jina, and MongoDB Atlas services. There is no local Mongo fallback; Atlas Vector Search specifically requires an Atlas-hosted cluster (a plain local `mongod` doesn't support `$vectorSearch`).

## Architecture

**Abstraction + DI pattern.** Nearly every external integration point is an `ABC` in `app/core/<area>/<area>.py` (e.g. `DocumentLoader`, `EmbeddingModel`, `VectorStore`, `LanguageModel`, `DocumentSplitter`), with one or more concrete implementations alongside it (`JinaEmbeddingModel`, `MongoDBVectorStore`, `GroqLanguageModel`, `MarkdownDirectoryDocumentLoader`, `HtmlDirectoryDocumentLoader`, `CharacterDocumentSplitter`). Each area has a matching `app/core/<area>_config.py` (or wiring lives in `knowledge_base_config.py`/`chat_config.py`) that provides FastAPI `Depends`-based DI, typically with `@lru_cache` singleton factories (`get_embedding_model`, `get_vector_store`, `get_language_model`, etc.). Services (`app/core/service/*.py`) receive these abstractions through their constructors and orchestrate the actual workflow. Routers (`app/api/v1/*.py`) are thin — they just depend on a `*ServiceDependency` type alias and call one method.

When adding a new implementation of an existing abstraction (e.g. swapping the vector store or LLM provider), implement the ABC and wire a new factory function in the relevant `*_config.py` — no other layer should need to change.

**Two pipelines share the same building blocks:**

1. **Ingestion** (`IngestionService`, triggered via `POST /api/v1/knowledge-base/ingest`): `DocumentLoader.load()` → `DocumentSplitter.split()` → `EmbeddingModel.embed_documents()` → `VectorStore.add_documents()`. The loader is a `CompositeDocumentLoader` combining `MarkdownDirectoryDocumentLoader` and `HtmlDirectoryDocumentLoader`, both scanning `KNOWLEDGE_BASE_DIR` (`app/knowledge_base`, which holds the CheeseRetry README plus generated Javadoc HTML under `output/javadocs`). `HtmlDirectoryDocumentLoader` filters out Javadoc chrome (nav-only pages, `class-use/`, `legal/` license pages) so only real class/package documentation gets embedded. `insert_many` has no dedup — re-running ingestion duplicates existing chunks; clear the `kb_chunks` collection first if you want a clean re-ingest.

2. **Chat / retrieval** (`ChatService`, triggered via `POST /api/v1/ask/cheese`): `RetrievalService` embeds the incoming query (`EmbeddingModel.embed_query`) and runs `VectorStore.similarity_search()` (a MongoDB `$vectorSearch` aggregation against the `kb_vector_index` Atlas Search index on the `embedding` field, cosine similarity, 1024 dims for Jina v3) to get top-k `VectorSearchResult`s. Their `content` is joined into a `context` string that gets injected into `GroqLanguageModel`'s system prompt (`app/core/llm/groq_language_model.py`), so answers are meant to be grounded only in retrieved context; `ChatResponse.sources` lists the originating file names.

**The Atlas Vector Search index is not managed by application code/migrations** — it's a cloud-side resource created once via `pymongo`'s `collection.create_search_index()` (or the Atlas UI's "Search Indexes" tab, which is separate from the regular "Indexes" tab). If retrieval starts returning nothing, check that `kb_vector_index` still exists and is `queryable` on the `kb_chunks` collection before assuming it's an app bug.

**Auth and per-user conversation memory.** Registration/login (`app/api/v1/auth_routers.py`, `AuthService`) issue a 7-day JWT (`JwtTokenService`, PyJWT/HS256, no refresh token) against a `users` collection with a unique index on `email`. Chat auth is **optional, not required**: `POST /api/v1/ask/cheese` still works fully anonymously exactly as before (`conversation_id` stays `null`), but a valid `Authorization: Bearer <jwt>` additionally persists that turn into a named conversation thread (multiple threads per user, ChatGPT-sidebar style — not one rolling history) and feeds recent turns back into the Groq prompt via `LanguageModel.generate(..., history=...)`. The auth dependency (`app/core/auth_config.py`, built on `HTTPBearer(auto_error=False)`) is deliberately asymmetric: a fully absent header falls through to anonymous, but a *present-and-invalid* token 401s rather than silently downgrading — don't "fix" this into always-401-on-missing or always-fall-back-on-invalid, both break the intended behavior. Conversation ownership checks (`ensure_conversation_owned` in `app/core/conversation_store/conversation_store.py`) collapse "conversation doesn't exist" and "belongs to another user" into the same `ConversationNotFoundError` → 404, so a non-owner can't use the response to fingerprint valid conversation ids. Both `conversations` and `conversation_messages` carry a native MongoDB **TTL index** (`CONVERSATION_RETENTION_DAYS`, default 30) — retention is self-maintaining via Mongo's background reaper, there is no cron job or app-level cleanup code to look for.

## Claude x Codex

This project has been actively built with assistance from both Claude and Codex; contributions are co-authored accordingly (see `COAUTHORS.md`).
