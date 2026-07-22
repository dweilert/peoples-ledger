from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .privacy import assert_no_household_financial_data


@dataclass(frozen=True)
class AIRequest:
    task: str
    prompt: str
    source_refs: list[str]


@dataclass(frozen=True)
class AIResponse:
    provider: str
    model: str
    text: str
    source_refs: list[str]


class AIProvider(Protocol):
    name: str
    model: str

    def complete(self, request: AIRequest) -> AIResponse:
        ...


class ProviderNeutralAIAdapter:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    def complete(self, request: AIRequest) -> AIResponse:
        assert_no_household_financial_data(request.__dict__)
        return self.provider.complete(request)


class DeterministicTCJAProvider:
    name = "deterministic-test-double"
    model = "tcja-poc-v1"

    def complete(self, request: AIRequest) -> AIResponse:
        assert_no_household_financial_data(request.__dict__)
        text = (
            "The TCJA analysis unit identifies the SALT deduction cap as a provision "
            "with distributional effects that vary by geography and itemization status. "
            "The POC records evidence and uncertainty but does not run household-level "
            "tax calculations."
        )
        return AIResponse(provider=self.name, model=self.model, text=text, source_refs=request.source_refs)
