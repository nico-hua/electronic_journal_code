from pydantic import BaseModel, Field
from typing import Dict
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

class PlanningResponse(BaseModel):
    devices: Dict = Field(
        description="Return a diff json file that follows the structure of FILTERED DEVICES and specifies which values of the dictionary should be changed to best accomplish the USER COMMAND."
    )

planning_template = """
You are an AI that controls a smart home.
You will be provided with a set of home appliances and an instruction.
Your job is to figure out how to use the set of home appliances to execute the instruction.

FILTERED DEVICES: {devices}

USER LOCATION: {user_location}

USER COMMAND: {user_command}


Return a json file that follows the structure of FILTERED DEVICES. Change the values of the
dictionary to best accomplish the USER COMMAND.

{format_instructions}
"""

planning_prompt_template = PromptTemplate(
    input_variables=["devices", "user_location", "user_command"],
    template=planning_template,
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=PlanningResponse
        ).get_format_instructions()
    },
)
