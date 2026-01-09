from pydantic import BaseModel, Field
from typing import List
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

class ImplementResponse(BaseModel):
    code: List[str] = Field(
        description="The Python code that will execute the required actions based on the plan."
    )

implement_template = """
You are a developer who generates executable Python code based on a given smart home control plan.
The plan contains device names and actions to perform on those devices.

PLAN: {plan}

USER_LOCATION: {user_location}

USER_COMMAND: {user_command}

ROOM_LIST: {room_list}

Generate the Python code that will execute the required actions based on the plan.

Generate executable Python code that performs the actions from the plan using these functions:
- turn_on(device_type, room)
- turn_off(device_type, room)
- open(device_type, room)
- close(device_type, room)
- set_temperature(device_type, room, temperature)  # temperature is an integer
- set_speed(device_type, room, speed)  # speed must be in [1, 2, 3]

Your code should directly map the actions in the plan to the appropriate function calls.
For example, if a device is 'on', use turn_on; if it's 'off', use turn_off; 'open' for open, 'closed' for close.

In the generated code, the `room` parameter should be inferred from the `USER_COMMAND` where possible.
If the room cannot be inferred from the command, use the `USER_LOCATION`.
Ensure that the room names used in the code are from the `ROOM_LIST`.


Return only the Python code.

{format_instructions}
"""

implement_prompt_template = PromptTemplate(
    input_variables=["plan", "user_location", "user_command", "room_list"],
    template=implement_template,
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=ImplementResponse
        ).get_format_instructions()
    },
)
