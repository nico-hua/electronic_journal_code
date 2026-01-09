from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
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

class Condition(BaseModel):
    """
    A single condition expression.

    Example:
      left="livingroom.temperature", op=">", right=30
      left="context.temperature", op="<", right=25
      left="time.hour", op="=", right=23
    """
    left: str = Field(
        description="Left operand. e.g., 'livingroom.temperature', 'context.temperature', 'current_time'."
    )
    op: Literal[">", "<", "=", "!="] = Field(
        description="Operator for the condition: one of '>', '<', '=', '!='."
    )
    right: Union[int, float, str, bool] = Field(
        description="Right operand. Usually a number for env values, or string/bool if needed."
    )


class PlannerResponse(BaseModel):
    type: Literal["tap", "instant"] = Field(
        description="Indicates the type of plan. If 'tap', it's a TAP plan (waiting for conditions); if 'instant', it's an instant action."
    )
    conditions: List[Condition] = Field(
        default_factory=list,
        description=(
            "List of conditions to trigger the plan. "
            "If type='tap', ALL conditions should be satisfied before executing (AND semantics). "
            "If type='instant', this list should be empty."
        ),
    )
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
5. Supported Device Actions
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
Use this ONLY when generating a feasible plan is impossible, including but not limited to:
    - The user instruction is completely unintelligible (intent cannot be inferred).
    - Required device is missing in the target room(s) and there is no reasonable substitute device.
    - The requested goal is not achievable under the supported actions (e.g., asking for unsupported action_name).
    - Device is explicitly reported as broken/faulty and there is no safe alternative plan.
    - Required condition attribute is unavailable (e.g., user asks for CO2 but no CO2 sensor/field exists), and you cannot infer safely.
When replying, clearly state the blocking reason and, if possible, provide actionable guidance (what to change / what information is missing).
Args:
    "response": "a clear and concise message to the user"

## Core Rules
### A) Instant vs TAP (type + conditions) Classification
Your output plan MUST set PlannerResponse.type as:
- "instant": the user wants immediate execution now.
- "tap": the user defines a trigger/condition; actions execute only when conditions become true.
Classify as "tap" when the instruction contains conditional/trigger semantics such as:
- “当/如果/只要/一旦 … 就 …”
- “温度大于/小于/等于/不等于 … 时 …”
- “到了某个时间/在某个时间段 …”
- “每次/每当 … 发生时 …”
- “保持/监测/超过阈值再执行 …”
Classify as "instant" when the instruction is a direct imperative without waiting semantics, such as:
- “打开/关闭/调到/把…设为…/现在/立刻/帮我…”
### B) Condition Representation (for TAP)
When type="tap":
- PlannerResponse.conditions MUST be a non-empty list.
- Each condition MUST be structured as: {{left, op, right}}
- Supported ops: >, <, =, !=
- Multiple conditions follow AND semantics (ALL must be true).
Recommended left operand patterns:
1) Room environment: "<room>.<metric>"
   metric examples: temperature, humidity, brightness, noise, air_quality, uv_index
   e.g., "livingroom.temperature"
2) Outdoor/context: "context.<metric>"
   e.g., "context.temperature"
3) Time: only use "current_time"
   - Compare current_time with a "HH:MM" string (24-hour).
   - Example: left="current_time", op=">", right="18:00"
When type="instant":
- PlannerResponse.conditions MUST be an empty list [].
### C) Execution Plan Feasibility & reply_user Boundary
You must attempt to produce a feasible plan whenever possible:
- If the requested device is missing, consider substitutes with similar effect (e.g., no AC -> fan; no fan -> open window when outdoor cooler).
- If partial fulfillment is possible, output the best-effort plan and avoid reply_user.
Use reply_user only when no safe, reasonable, and supported plan exists.
### D) Room Target Inference
- If a room is mentioned explicitly, treat it as target.
- If no room is mentioned:
  - If the instruction implies global action (e.g., “暴风雨把所有窗户关上”), target all rooms and call get_room_info for all rooms.
  - Otherwise default to user's current room.
### E) Always call get_room_info first
Once target room(s) are determined, always call get_room_info to fetch current environment & device status BEFORE finishing a plan.
### F) Device state checks
Skip actions that are already in the desired state (e.g., light already on).

## Response Format (STRICT)
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