from src.ruler import Ruler
from src.planner import RoomPlan, DeviceAction

# action1 = DeviceAction(device_type="air_conditioner", action_name="set_temperature", parameters={"temperature": 25})
# action2 = DeviceAction(device_type="air_conditioner", action_name="set_speed", parameters={"speed": 2})
# room_plan = RoomPlan(room_name="livingroom", actions=[action1, action2])
# ruler = Ruler()
# ruler.build_execution_plan(room_plan)
# print(ruler.graph)
# print(ruler.indegree)

action1 = DeviceAction(device_type="window", action_name="open", parameters=None)
action2 = DeviceAction(device_type="cooker_hood", action_name="turn_on", parameters=None)
room_plan = RoomPlan(room_name="kitchen", actions=[action1, action2])
ruler = Ruler()
ruler.build_execution_plan(room_plan)
print(ruler.graph)
print(ruler.indegree)