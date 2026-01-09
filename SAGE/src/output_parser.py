import json
import re
from abc import abstractmethod
from typing import Dict, NamedTuple
from langchain_core.output_parsers import BaseOutputParser

class AgentAction(NamedTuple):
    """
    Action returned by AgentOutputParser.
    """

    name: str
    args: Dict

class BaseAgentOutputParser(BaseOutputParser):
    """
    Base Output parser for Agent.
    """

    @abstractmethod
    def parse(self, text: str) -> AgentAction:
        """Return AgentAction"""


class AgentOutputParser(BaseAgentOutputParser):
    """Output parser for Agent."""

    def parse(self, text: str) -> AgentAction:
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(text, strict=False)
        except json.JSONDecodeError:
            return AgentAction(
                name="ERROR",
                args={"error": f"Could not parse invalid json: {text}"},
            )
        try:
            return AgentAction(
                name=parsed["command"]["name"],
                args=parsed["command"]["args"],
            )
        except (KeyError, TypeError):
            # If the command is null or incomplete, return an erroneous tool
            return AgentAction(
                name="ERROR", args={"error": f"Incomplete command args: {parsed}"}
            )