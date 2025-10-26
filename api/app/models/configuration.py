from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str = Field(default="")
    type: str = Field(default="string")
    description: str = Field(default="")
    required: bool = Field(default=True)


class ToolConfiguration(BaseModel):
    name: str = Field(default="")
    description: str = Field(default="")
    parameters: list[ToolParameter] = Field(default_factory=list)

    def convert_function_params(self) -> dict:
        """Convert parameters to a dictionary suitable for function calls."""
        return {
            "type": "object",
            "properties": {
                p.name: {
                    "type": p.type,
                    "description": (
                        p.description if p.description else "No Description"
                    ),
                }
                for p in self.parameters
            },
            "required": [p.name for p in self.parameters if p.required],
        }


class Configuration(BaseModel):
    id: str = Field(default="")
    name: str = Field(default="")
    content: str = Field(default="")
    default: bool = Field(default=False)
    tools: list[ToolConfiguration] = Field(default_factory=list)
