from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

class ClarificationResponse(BaseModel):
    response: str = Field(
        description="Answer by YES or NO if the task is possible or the query can be answered"
    )
    explanation: str = Field(
        description="Return an explanation of the response to the user"
    )

clarification_template = """
You are an AI that controls a smart home.
You will be provided with a set of home appliances and an instruction.
Respond, IN ONE WORD, whether it is possible to successfully carry out the instruction using the following devices.

HOME APPLIANCES: {devices}

USER LOCATION: {user_location}

USER COMMAND: {user_command}


{format_instructions}
"""

clarification_prompt_template = PromptTemplate(
    input_variables=[
        "devices",
        "user_location",
        "user_command",
    ],
    template=clarification_template,
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=ClarificationResponse
        ).get_format_instructions()
    },
)