from pydantic import BaseModel, Field

class Record(BaseModel):
    id: str = Field(default="")
    name: str = Field(default="")
    description: str = Field(default="")
    type: str = Field(default="")
    default: bool = Field(default=False)
    data: dict = Field(default_factory=dict)