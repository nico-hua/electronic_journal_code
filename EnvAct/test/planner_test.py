from src.planner import Planner
from src.model import llm

planner = Planner(user_location="livingroom", llm=llm)
res = planner.run("讲个冷笑话")
print(res)