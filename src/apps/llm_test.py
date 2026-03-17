import asyncio
import os
from src.services.llm import MistralAIService
from src.services.message import QuestionDTO

mistral_key = os.getenv("MISTRAL_KEY")


async def main():
    llm = MistralAIService(
        model_name="mistral-small-latest", mistral_api_key=mistral_key
    )
    question = QuestionDTO(text="Hi, how are you?", history=[])
    result = await llm.execute(question)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
