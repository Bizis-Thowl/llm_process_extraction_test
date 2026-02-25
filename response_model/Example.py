from pydantic import BaseModel, Field

class ExampleResponse(BaseModel):

    name: str = Field(..., description="The name of the capital")
    reason: str = Field(..., description="The reason why you think it is the capital")