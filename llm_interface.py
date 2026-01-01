from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLM 제공자 추상 클래스 - 모델 교체 용이성을 위한 Strategy Pattern"""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """비동기로 답변 생성"""
        pass


class OllamaClient(LLMProvider):
    """Ollama 로컬 LLM 클라이언트"""

    def __init__(self, model_name: str = "qwen2.5-coder:14b"):
        from ollama import AsyncClient
        self.model_name = model_name
        self.client = AsyncClient()

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ]
        )
        return response['message']['content']
