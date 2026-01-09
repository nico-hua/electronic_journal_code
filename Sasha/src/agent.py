from langchain_core.language_models import BaseChatModel
from .clarify import clarification_prompt_template, ClarificationResponse
from .filter import filtering_prompt_template, FilteringResponse
from .plan import planning_prompt_template, PlanningResponse
from .implement import implement_prompt_template, ImplementResponse
from .config import ROOM_MAP_DEVICE, DEFAULT_ROOMS
from .api import turn_on, turn_off, open, close, set_temperature, set_speed
import json
import time

class Agent:
    def __init__(
        self,
        llm: BaseChatModel,
        user_location: str
    ):
        self.clarify_chain = clarification_prompt_template | llm
        self.filter_chain = filtering_prompt_template | llm
        self.plan_chain = planning_prompt_template | llm
        self.implement_chain = implement_prompt_template | llm
        self.user_location = user_location
    def run(self):
        user_command = input("Please enter the command and enter 'exit' to exit: ")
        start_time = time.time()
        if user_command != "exit" and user_command != "":
            clarify_res = self.clarify_chain.invoke({
                "user_command": user_command,
                "user_location": self.user_location,
                "devices": ROOM_MAP_DEVICE
            }).content
            if "```json" in clarify_res:
                clarify_res = clarify_res.split("```json")[1].split("```")[0]
            clarify_res = ClarificationResponse(**json.loads(clarify_res))
            print(clarify_res)
            if clarify_res.response == "YES":
                filter_res = self.filter_chain.invoke({
                    "user_command": user_command,
                    "user_location": self.user_location,
                    "devices": ROOM_MAP_DEVICE
                }).content
                if "```json" in filter_res:
                    filter_res = filter_res.split("```json")[1].split("```")[0]
                filter_res = FilteringResponse(**json.loads(filter_res))
                print(filter_res)
                plan_res = self.plan_chain.invoke({
                    "user_command": user_command,
                    "user_location": self.user_location,
                    "devices": filter_res.devices
                }).content
                if "```json" in plan_res:
                    plan_res = plan_res.split("```json")[1].split("```")[0]
                plan_res = PlanningResponse(**json.loads(plan_res))
                print(plan_res)
                implement_res = self.implement_chain.invoke({
                    "plan": plan_res.devices,
                    "user_command": user_command,
                    "user_location": self.user_location,
                    "room_list": DEFAULT_ROOMS
                }).content
                if "```json" in implement_res:
                    implement_res = implement_res.split("```json")[1].split("```")[0]
                implement_res = ImplementResponse(**json.loads(implement_res))
                print(implement_res)
                try:
                    python_code = '\n'.join(implement_res.code)
                    exec(python_code)
                    end_time = time.time()
                    print(f"Total time: {end_time - start_time}")
                except Exception as e:
                    print(e)
                    end_time = time.time()
                    print(f"Total time: {end_time - start_time}")
