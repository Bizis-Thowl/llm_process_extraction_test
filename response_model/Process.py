from pydantic import BaseModel, Field

class ProcessResponse(BaseModel):

    answer: str = Field(..., description="Antwort auf die Frage")
    reason: str = Field(..., description="Begründung, wie Deine Antwort zustande kommt.")