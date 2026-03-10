from pydantic import BaseModel, Field

class SubQuestionWithAnswer(BaseModel):
    
    question: str = Field(..., description="Die Frage, die beantwortet werden soll")
    
    answer: str = Field(..., description="Die Antwort auf die Frage")
    
class SubQuestion(BaseModel):
    
    question: str = Field(..., description="Die Frage, die beantwortet werden soll")
    