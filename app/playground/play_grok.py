import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()

    model = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
    )

    messages = [
        SystemMessage(
            content=(
                "You are an assistant that explains Java retry concepts "
                "clearly and accurately."
            )
        ),
        HumanMessage(
            content="Explain exponential backoff in simple terms."
        ),
    ]

    response = await model.ainvoke(messages)

    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())