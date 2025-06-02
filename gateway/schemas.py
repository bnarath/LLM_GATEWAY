"""Pydantic request/response schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union


class InputSchema(BaseModel):
    models: Optional[Union[str, List[str]]] = None
    prompt: str


class SingleModelOutput(BaseModel):
    name: str
    output: Optional[str] = None  # Optional should always accompany a default
    score: Optional[float] = Field(ge=0, le=1)  # Optional but if provided a float [0,1]
    reason: Optional[str] = None


class OutputSchema(BaseModel):
    response: str
    quality_score: float = Field(ge=0, le=1)
    reason_of_score: str
    model_used: str
    all_models_considered_with_scores: List[SingleModelOutput]


if __name__ == "__main__":
    # Test
    print(
        InputSchema(
            models=[
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-2.0-flash-001",
                "gpt-4o-mini",
            ],
            prompt="How Ukrain conduct drone attack in Russia?",
        ),
    )

    print(
        SingleModelOutput(
            name="gemini-2.0-flash",
            output="I don't know",
            score=0.1,
            reason="Model doesn't answer but honest",
        )
    )

    print(
        OutputSchema(
            response="I don't know",
            quality_score=0.1,
            reason_of_score="Model doesn't answer but honest",
            model_used="gemini-2.0-flash",
            all_models_considered_with_scores=[
                SingleModelOutput(
                    name="gemini-2.0-flash",
                    output="I don't know",
                    score=0.1,
                    reason="Model doesn't answer but honest",
                )
            ],
        )
    )
