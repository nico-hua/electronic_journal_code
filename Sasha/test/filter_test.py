from src.filter import FilteringResponse, filtering_prompt_template
from src.model import llm
from src.config import ROOM_MAP_DEVICE
import json

chain = filtering_prompt_template | llm
filter_res = chain.invoke({
    "user_command": "屋内太热了",
    "user_location": "livingroom",
    "devices": ROOM_MAP_DEVICE
}).content
if "```json" in filter_res:
    filter_res = filter_res.split("```json")[1].split("```")[0]
res = FilteringResponse(**json.loads(filter_res))
print(res)