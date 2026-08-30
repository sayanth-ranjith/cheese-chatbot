from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.core.abstract.LanguageModel import ConversationTurn, LanguageModel

CHEESE_ASSISTANT_SYSTEM_PROMPT = """
You are Cheese Assssistant, a technical aistant for developers using
the CheeseRetry Java library.

Your responsibilities:
- Explain Java retry concepts clearly and accurately.
- Explain CheeseRetry functionality only from the supplied context.
- Never invent CheeseRetry classes, methods, configuration, or behavior.
- Clearly state when the available information is insufficient.
- Prefer concise explanations with practical Java examples when relevant.

Context:
{context}
""".strip()

class GroqLanguageModel(LanguageModel):
    
    def __init__(self, *, api_key: SecretStr, model_name: str, temperature: float = 0):

        #Create the template
        prompt = self._create_prompt()

        #Model definition
        model = ChatGroq(
            api_key=api_key,
            model=model_name,
            temperature=temperature,
        )

        #Chain
        self._chain = prompt | model | StrOutputParser()


    async def generate(
        self,
        message: str,
        context: str = "",
        history: list[ConversationTurn] | None = None,
    ) -> str:
        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Message must not be empty")

        return await self._chain.ainvoke(
            {
                "message": cleaned_message,
                "context": context.strip() or "No relevant context was found.",
                "history": self._to_langchain_messages(history or []),
            }
        )

    @staticmethod
    def _to_langchain_messages(history: list[ConversationTurn]) -> list[BaseMessage]:
        messages: list[BaseMessage] = []

        for turn in history:
            if turn.role == "assistant":
                messages.append(AIMessage(content=turn.content))
            else:
                messages.append(HumanMessage(content=turn.content))

        return messages

    @staticmethod
    def _create_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                ("system", CHEESE_ASSISTANT_SYSTEM_PROMPT),
                MessagesPlaceholder("history"),
                ("human", "{message}"),
            ]
        )