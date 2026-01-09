from src.clarify import clarification_prompt_template, ClarificationResponse
from src.model import llm
from src.config import ROOM_MAP_DEVICE
import json

chain = clarification_prompt_template | llm
content = chain.invoke({
    "user_command": "turn on the television",
    "user_location": "livingroom",
    "devices": ROOM_MAP_DEVICE
}).content
if "```json" in content:
    content = content.split("```json")[1].split("```")[0]
res = ClarificationResponse(**json.loads(content))
print(res)