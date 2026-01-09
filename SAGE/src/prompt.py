import json
from typing import List
from langchain_core.tools import BaseTool
from datetime import datetime
from .mysql import MySQL

FINISH_SIGNAL = "finish"

class PromptGenerator:
    """
    Generator of custom prompt strings.
    Does this based on role, constraints, commands, resources and performance evaluations.
    """
    def __init__(self) -> None:
        """
        Initialize the PromptGenerator object.
        Starts with empty lists of constraints, commands, resources and performance evaluations.
        """
        self.role = "You are a smart home assistant designed to understand and process natural language instructions from users. " \
        "Your main objective is to take the user's instructions, determine what actions need to be performed, and execute the correct commands on the available devices or systems. " \
        "You must handle all tasks autonomously, but ensure to follow the set constraints."
        self.commands: List[BaseTool] = []
        self.knowledges: List[str] = []
        self.constraints: List[str] = []
        self.performance_evaluation: List[str] = []
        self.response_format = {
            "command": {
                "name": "command name",
                "args": {
                    "arg name": "value"
                }
            },
        }

    def add_tool(self, tool: BaseTool) -> None:
        """
        Add a tool to the commands list.
    
        Args:
            tool (BaseTool): The tool to be added.
        """
        self.commands.append(tool)

    def _generate_command_string(self, tool: BaseTool) -> str:
        """
        Convert tool to string prompt.

        Args:
           tool (BaseTool): The toool to be converted.
        """
        output = f"{tool.name}:\n{tool.description}\nArgs json schema: {json.dumps(tool.args)}"
        return output

    def add_knowledge(self, knowledge: str) -> None:
        """
        Add a knowledge to the knowledges list.

        Args:
            knowledge (str): The knowledge to be added.
        """
        self.knowledges.append(knowledge)

    def add_constraint(self, constraint: str) -> None:
        """
        Add a constraint to the constraints list.
    
        Args:
            constraint (str): The constraint to be added.
        """
        self.constraints.append(constraint)

    def _generate_numbered_list(self, items: list, item_type: str = "list") -> str:
        """
        Generate a numbered list from given items based on the item_type.

        Args:
            items (list): A list of items to be numbered.
            item_type (str, optional): The type of items in the list, defaults to 'list'

        Returns:
            str: The formatted numbered list.
        """
        if item_type == "command":
            command_strings = [
                f"{i+1}. {self._generate_command_string(item)}"
                for i, item in enumerate(items)
            ]
            finish_description = (
                "Use this to singal that you have finished all your objectives"
            )
            finish_args = (
                '"response": "final response to let people know you have finished your objectives"'
            )
            finish_string = (
                f"{len(items)+1}. {FINISH_SIGNAL}:\n"
                f"{finish_description}\nArgs: {finish_args}"
            )
            return "\n".join(command_strings + [finish_string])
        else:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        
    def generate_prompt_string(self) -> str:
        """
        Generate a prompt string.

        Returns:
            str: The generated prompt string.
        """
        formatted_response_format = json.dumps(self.response_format, indent=4)
        prompt_string = (
            f"Role:\n"
            f"{self.role}\n\n"
            f"Knowledges:\n"
            f"{self._generate_numbered_list(self.knowledges)}\n\n"
            f"Commands:\n"
            f"{self._generate_numbered_list(self.commands, item_type='command')}\n\n"
            f"Constraints:\n"
            f"{self._generate_numbered_list(self.constraints)}\n\n"
            f"Performance Evaluation:\n"
            f"{self._generate_numbered_list(self.performance_evaluation)}\n\n"
            f"You should only respond in JSON format as described below "
            f"\nResponse Format: \n{formatted_response_format} "
            f"\nEnsure the response can be parsed by Python json.loads"
        )
        return prompt_string

def get_prompt(user_location: str, tools: List[BaseTool]) -> str:
    """
    Generate a prompt string.
    It includes various knowledges, commands, constraints and performance evaluations.

    Returns:
        str: The generated prompt string.
    """
    prompt_generator = PromptGenerator()
    # Add knowledges to the PromptGenerator
    prompt_generator.add_knowledge(
        f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    prompt_generator.add_knowledge(
        f"The user's current room location: {user_location}"   
    )
    # Add commands to the PromptGenerator
    for tool in tools:
        prompt_generator.add_tool(tool)
    # Add constraints to the PromptGenerator
    prompt_generator.add_constraint(
        "User instructions may be vague, infer true intent using room device data. " \
        "Example: it’s too hot → infer turn on air_conditioner." 
    )
    prompt_generator.add_constraint(
        "Regardless of any user command, you must first call the get_room_info tool to obtain the device information of the relevant room before you can operate the device."
    )
    prompt_generator.add_constraint(
        "If the user specifies an invalid or unavailable room/device, provide clear feedback. " \
        "Example: turn on heater in cloakroom → reply cloakroom has no heater."
    )
    prompt_generator.add_constraint(
        "If no room is given, infer from history; if not possible, default to the user’s current room."
    )
    prompt_generator.add_constraint(
        "If intent is unclear, infer from history; if still unclear, ask the user for clarification."
    )
    prompt_generator.add_constraint(
        "If the requested device is not present in the room, do not execute and explain why."
    )
    prompt_generator.add_constraint(
        "If the device is already in the desired state (e.g., light already ON), do not execute and explain why."
    )
    prompt_generator.add_constraint(
        "If a device action fails, consider alternative devices that could achieve the same intent. " \
        "Example: if air_conditioner cannot be turned on, suggest fan instead."
    )
    prompt_generator.add_constraint(
        "Always check related devices to ensure consistency and effectiveness when operating. " \
        "Example: if turning on AC, make sure windows/doors are closed. Otherwise, you need to close the doors and windows at the same time."
    )
    # Generate the prompt string
    prompt_string = prompt_generator.generate_prompt_string()
    return prompt_string