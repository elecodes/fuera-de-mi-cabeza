from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        ...
