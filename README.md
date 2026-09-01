# 🧀 Cheese Chatbot

Checkout - https://cheese-chatbot-ui.vercel.app/

Cheese Chatbot is a work-in-progress AI assistant built to help developers understand and use the **CheeseRetry** library.

The chatbot uses a Retrieval-Augmented Generation (RAG) architecture, where it retrieves relevant information from a knowledge base containing CheeseRetry documentation, source code, and examples before generating responses. This helps provide answers that are grounded in the library rather than relying solely on the language model's pre-trained knowledge.

## Features

- Answer frequently asked questions about CheeseRetry
- Explain APIs and configuration
- Understand Java code snippets and provide guidance
- Generate usage examples
- Retrieve answers directly from the CheeseRetry knowledge base
- User accounts (JWT-based) with persistent, multi-thread conversation history — chat still works anonymously too, memory just isn't saved without logging in

## Planned Features

- Tavily-backed web search for questions outside the knowledge base

## Tech Stack

- FastAPI
- LangChain
- Groq (LLM)
- Jina (embeddings)
- MongoDB Atlas + Atlas Vector Search (knowledge base / vector store)
- Tavily (planned)
- Python

## Project Status

🚧 This project is currently under active development.

It is my first AI project, and I'm building it to learn modern AI engineering concepts such as RAG, vector databases, embeddings, prompt engineering, and agentic workflows while creating something genuinely useful for CheeseRetry users.

## Development

This project is being built with the assistance of Claude Code.

### Run the API

From the repository root, start the FastAPI application with:

```powershell
uvicorn app.main:app --reload
```

The `app.` prefix is required because the ASGI entry point is located at
`app/main.py`, rather than at a root-level `main.py`.

## Deployment

This repo includes a `render.yaml` blueprint for deploying to [Render](https://render.com)'s free web service tier.

1. In Render, click **New > Blueprint** and point it at this repository (or use the button below).
2. Render will read `render.yaml` and provision a free web service automatically.
3. Set the required secrets in the Render dashboard (they're intentionally left blank in `render.yaml`):
   - `GROQ_API_KEY`
   - `JINA_API_KEY`
   - `MONGODB_URI`
   - `JWT_SECRET_KEY`
4. Deploy. The service starts with `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sayanth-ranjith/cheese-chatbot)

**Note:** Render's free tier spins the service down after ~15 minutes of inactivity; the next request will take 30-50s to cold-start.

## Claude x Codex

Claude and Codex have been actively contributing too lol as always.
Claude has co authored so has codex too.
