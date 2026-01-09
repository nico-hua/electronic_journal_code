from src.planner import Planner
from src.model import llm

planner = Planner(user_location="livingroom", llm=llm)
res = planner.run(user_instruction="下午两点后，如果温度大于30度就给室内降温")
print(res)