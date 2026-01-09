from src.ruler import Ruler
from src.planner import RoomPlan, DeviceAction

action1 = DeviceAction(device_type="air_conditioner", action_name="set_temperature", parameters={"temperature": 25})
action2 = DeviceAction(device_type="air_conditioner", action_name="set_speed", parameters={"speed": 2})
room_plan = RoomPlan(room_name="livingroom", actions=[action1, action2])
ruler = Ruler()
ruler.build_execution_plan(room_plan)
print(ruler.graph)
print(ruler.indegree)