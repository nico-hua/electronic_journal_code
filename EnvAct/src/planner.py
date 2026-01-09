from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from .mysql import MySQL
from .config import DEFAULT_ROOMS
from .output_parser import AgentOutputParser
from .tools import tools
from datetime import datetime
import json
from pydantic import ValidationError
from langchain_core.language_models import BaseChatModel

class DeviceAction(BaseModel):
    device_type: str = Field(
        description="Type of the device to be controlled, e.g., air_conditioner, light, fan."
    )
    action_name: str = Field(
        description="Specific action to perform on the device, e.g., turn_on, turn_off, set_temperature."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Additional parameters required for the action. "
            "For example: {{'temperature': 26}} for setting air_conditioner temperature, "
            "{{'speed': 2}} for setting fan speed."
        )
    )


class RoomPlan(BaseModel):
    room_name: str = Field(
        description="Name of the room where the actions will be executed, e.g., living_room, bedroom."
    )
    actions: List[DeviceAction] = Field(
        description="List of actions to be applied to devices within this room."
    )


class PlannerResponse(BaseModel):
    plan: List[RoomPlan] = Field(
        description="Overall execution plan, grouped by rooms and the corresponding device actions."
    )

class PlannerRunResult(BaseModel):
    """
    Return type for Planner.run.

    - type='plan': plan contains the parsed execution plan
    - type='reply': message contains the user-facing response
    """
    type: Literal['plan', 'reply']
    plan: Optional[PlannerResponse] = None
    message: Optional[str] = None

planner_template = """
# Role
You are a smart home assistant.
Your task is to understand the user's instructions, call `get_room_info` to check room environment/devices, then generate an execution plan or reply to the user.

## Knowledge
1. Current time: {current_time}
2. The user's current room location: {user_location}
3. Outdoor environment information (context): {context}
4. Names of all rooms in the home: {default_rooms}
5. Device Actions
    - "turn_on" / "turn_off"
        Supported devices: "air_conditioner", "air_purifier", "bath_heater", "cooker_hood", "fan", "gas_stove", "heater", "humidifier", "light", "microwave_oven", "television", "towel_dryer", "washing_machine", "water_heater"
        Parameters: no parameters
    - "open" / "close"
        Supported devices: "window", "door", "curtain"
        Parameters: no parameters
    - "set_temperature"
        Supported devices: "air_conditioner", "bath_heater"
        Parameters: {{"temperature": integer}}
    - "set_speed"
        Supported devices: "fan", "air_conditioner", "cooker_hood"
        Parameters: {{"speed": integer, range: 1–3}}

## Commands
1) get_room_info
Query the environmental and device information of given rooms.
Args:
    "rooms": a list of valid room names
2) finish
Use this to signal that you have generated an execution plan.
Args:
    "response": "the final generated execution plan"
"response" MUST strictly follow the PlannerResponse schema:
{format_instructions}
3) reply_user
Use this **only** when:
    - The user instruction is completely unintelligible,
    - Or it is impossible to infer a feasible action from available information.
Args:
    "response": "a clear and concise message to the user"

## Constraints
1. **Clarification on ambiguous commands**:
   - User instructions are often high-level and may lack specific details such as room or device information. To handle such cases:
     1. **Prioritize using common sense, indoor and outdoor environment data, and available device information** to infer the user's intent.
        - Example: If the user says "It’s too hot," assume they are requesting cooling in a room, especially when the temperature is high. Consider the room's typical usage, the outdoor temperature, and whether cooling devices like air conditioners or fans are available.
     2. **Strive to fulfill the user's request as much as possible** using reasoning from the environment and device data. 
        - **Do not ask the user for confirmation if the intent can be reasonably inferred**. Directly generate an execution plan with the required device actions.
        - Example: If outdoor temperature is high, it is logical to turn on air conditioning rather than opening windows. Execute accordingly.
     3. **Use `reply_user` only as a last resort**: if the user's intent cannot be determined even after applying common sense and environmental/device information.
2. **Room Location Inference**:
   - If the user's instruction clearly mentions a room (e.g., "Turn on the air_conditioner in the living room"), use that room as the target.
   - If no room is explicitly mentioned:
     - Use common sense, environmental/device info, and historical context to infer the target room.
     - If the instruction implies a **global action** like "It's a storm, close the windows," the target room should be **all rooms**, and you should gather environment and device info for all rooms via `get_room_info`.
     - If the instruction cannot be inferred, **default to the user's current room**.
3. **Always call `get_room_info` first**: 
   - Once the target room is identified, call `get_room_info` to gather the environment and device status before generating an execution plan.
4. **Indoor vs Outdoor Environment Differences**:
   - When adjusting temperature:
     - **Outdoor hotter than indoor** → use cooling devices (AC, fan), as opening windows would bring in hot air.
     - **Outdoor cooler than indoor** and difference > 5°C → consider opening windows if they are closed.
     - **Windows already open and indoor still hot** → use cooling devices to lower temperature.
5. **Energy efficiency and device compatibility**: 
   - Prioritize achieving the user's intended result. Energy efficiency should only influence action selection **if multiple valid alternatives exist**.
6. **Device state checks**:
   - Skip actions if devices are already in the desired state (e.g., light already on).
7. **Invalid or unavailable devices**:
   - Provide feedback only if the device does not exist in the target room.
8. **Device Associations and Conflicts**:
   - **Associations**: Operate devices in sequence if needed. Example: Before turning on the air conditioner, ensure windows and doors are closed. Close them first if needed.
   - **Conflicts**: Avoid simultaneous operation of conflicting devices. Example: Do not turn on a fan while the air conditioner is running unless explicitly requested.

## Response Format
- If user's intent can be reasonably inferred: **directly generate execution plan**.
- Only use `reply_user` if the intent is completely unclear.
Only respond in **valid JSON** that can be parsed by Python `json.loads` with the structure:
{{
    "command": {{
        "name": "command name",
        "args": {{
            "arg name": "value"
        }}
    }}
}}
"""

planner_prompt_template = PromptTemplate(
    input_variables=["current_time", "user_location", "context", "default_rooms"],
    template=planner_template,
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=PlannerResponse
        ).get_format_instructions()
    },
)

class Planner():
    def __init__(self, user_location: str, llm: BaseChatModel):
        mysql = MySQL()
        self.system_prompt = planner_prompt_template.format(
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            user_location=user_location,
            context=mysql.get_context(),
            default_rooms=DEFAULT_ROOMS
        )
        self.chat_history_memory = ChatMessageHistory()
        self.chat_history_memory.add_message(SystemMessage(content=self.system_prompt))
        self.llm = llm
        self.output_parser = AgentOutputParser()
        self.tools = {tool.name: tool for tool in tools}

    def reset(self, user_location: Optional[str] = None):
        """
        Reset conversation memory and refresh environment context/time.
        Call this at the beginning of a new user instruction session.
        """
        if user_location is not None:
            self.user_location = user_location
        mysql = MySQL()
        self.system_prompt = planner_prompt_template.format(
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            user_location=getattr(self, "user_location", "unknown"),
            context=mysql.get_context(),
            default_rooms=DEFAULT_ROOMS,
        )
        self.chat_history_memory = ChatMessageHistory()
        self.chat_history_memory.add_message(SystemMessage(content=self.system_prompt))

    def run(self, user_instruction: str, feedback: Optional[str] = None) -> PlannerRunResult:
        self.chat_history_memory.add_message(HumanMessage(content=user_instruction))
        if feedback:
            self.chat_history_memory.add_message(HumanMessage(content=f"[FEEDBACK]\n{feedback}"))
        loop_count = 0
        while True:
            loop_count += 1
            if loop_count > 10:
                print("Max loop reached. Exiting...")
                return PlannerRunResult(type="reply", message="抱歉，我在规划时陷入循环，无法生成可执行计划。你可以换一种说法或提供更多信息。")
            messages = self.chat_history_memory.messages
            assistant_reply = self.llm.invoke(messages).content
            print(assistant_reply)
            self.chat_history_memory.add_message(AIMessage(content=assistant_reply))
            action = self.output_parser.parse(assistant_reply)
            if action.name == "reply_user":
                return PlannerRunResult(type="reply", message=str(action.args.get("response", "")))
            elif action.name == "finish":
                planner_res = action.args["response"]
                if "```json" in planner_res:
                    planner_res = planner_res.split("```json")[1].split("```")[0]
                if isinstance(planner_res, str):
                    planner_res = json.loads(planner_res)
                return PlannerRunResult(type="plan", plan=PlannerResponse(**planner_res))
            elif action.name in self.tools:
                tool = self.tools[action.name]
                try:
                    observation = tool.run(action.args)
                except ValidationError as e:
                    observation = (
                        f"Validation Error in args: {str(e)}, args: {action.args}"
                    )
                except Exception as e:
                    observation = (
                        f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
                    )
                result = f"Command {tool.name} returned: {observation}"
            elif action.name == "ERROR":
                result = f"Error: {action.args}. "
            else:
                result = (
                    f"Unknown command '{action.name}'. "
                    f"Please refer to the 'COMMANDS' list for available "
                    f"commands and only respond in the specified JSON format."
                )
            self.chat_history_memory.add_message(HumanMessage(content=result))