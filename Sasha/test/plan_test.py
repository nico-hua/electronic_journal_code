from src.plan import planning_prompt_template, PlanningResponse
from src.model import llm
import json

chain = planning_prompt_template | llm
plan_res = chain.invoke({
    "user_command": "屋内太热了",
    "user_location": "livingroom",
    "devices": ['air_conditioner', 'fan', 'window', 'door', 'curtain', 'air_purifier', 'humidifier']
}).content
if "```json" in plan_res:
    plan_res = plan_res.split("```json")[1].split("```")[0]
res = PlanningResponse(**json.loads(plan_res))
print(res)