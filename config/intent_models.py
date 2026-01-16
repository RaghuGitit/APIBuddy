from pydantic import BaseModel, Field
from typing import List


class IntentCandidate(BaseModel):
    intent: str = Field(
        description="One of the allowed intent identifiers"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0 and 1"
    )


class IntentDetectionResult(BaseModel):
    intents: List[IntentCandidate] = Field(
        description="List of detected intents sorted by confidence desc"
    )
