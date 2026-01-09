from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

class FilteringResponse(BaseModel):
    devices: list[str] = Field(
        description="A list that contains the devices that can potentially accomplish the task"
    )

filtering_template = """
You are an AI that controls a smart home.
You will be provided with a set of home appliances and an instruction.
Extract the names of the devices that are relevant to execute the instruction

APPLIANCE LIST: {devices}

USER LOCATION: {user_location}

USER COMMAND: {user_command}


Respond by returning a subset of the devices under APPLIANCE LIST
{format_instructions}
"""

filtering_prompt_template = PromptTemplate(
    input_variables=["devices", "user_location", "user_command"],
    template=filtering_template,
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=FilteringResponse
        ).get_format_instructions()
    },
)