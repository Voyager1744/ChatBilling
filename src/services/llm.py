from abc import ABC, abstractmethod
from typing import cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from .message import AnswerDTO, QuestionDTO


class LLMService(ABC):
    @abstractmethod
    def execute(self, data: QuestionDTO) -> AnswerDTO:
        raise NotImplementedError


class MistralAIService(LLMService):
    _MESSAGES = [
        ("system", "You are a helpful assistant."),
        (MessagesPlaceholder("history")),
        ("human", "{question}"),
    ]

    def __init__(self, model_name: str, mistral_api_key: str):
        llm = ChatMistralAI(
            model=model_name,
            api_key=mistral_api_key,
        )
        prompt = ChatPromptTemplate.from_messages(self._MESSAGES)
        self._chain = prompt | llm

    async def execute(self, data: QuestionDTO) -> AnswerDTO:
        responce = await self._chain.ainvoke(
            {
                "question": data.text,
                "history": [(message.role, message.text) for message in data.history],
            }
        )
        responce = cast(AnswerDTO, responce)
        return AnswerDTO(
            text=responce.content,
            used_tokens=responce.usage_metadata.get("total_tokens", 0),
        )


class OlamaLLMService(LLMService):
    _MESSAGES = [
        ("system", "You are a helpful assistant."),
        (MessagesPlaceholder("history")),
        ("human", "{question}"),
    ]

    def __init__(self, model_name: str, olama_base_url: str):
        llm = ChatOpenAI(
            model=model_name,
            base_url=f"{olama_base_url}/v1",
        )
        promt = ChatPromptTemplate(self._MESSAGES)
        self._chain = promt | llm

    async def execute(self, data: QuestionDTO) -> AnswerDTO:
        responce = await self._chain.ainvoke(
            {
                "question": data.text,
                "hystory": [(message.role, message.text) for message in data.history],
            }
        )
        responce = cast(AnswerDTO, responce)
        return AnswerDTO(
            text=responce.content,
            used_tokens=responce.usage_metadata.get("total_tokens", 0),
        )
