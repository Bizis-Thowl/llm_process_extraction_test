from pydantic import BaseModel, Field

class KorrektheitResponse(BaseModel):
    ist_korrekt: bool =  Field(..., description="Ob die generierte Antwort korrekt ist oder nicht.")
    begrundung: str = Field(..., description="Die Begründung, warum die generierte Antwort korrekt ist oder nicht.")