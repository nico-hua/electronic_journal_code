from .planner import DeviceAction, RoomPlan
from collections import defaultdict
from .mysql import MySQL
from .api import turn_off, turn_on, set_temperature, set_speed, open as api_open, close as api_close
import threading
import time
import json
from pathlib import Path

class Ruler:
    def __init__(self):
        self.graph = defaultdict(list)
        self.indegree = defaultdict(int)
        self.lock = threading.Lock()
        self.exec_log = []
        self.rule_map = self.load_rule_map("rule_map.json")

    def load_rule_map(self, filename):
        try:
            path = Path(__file__).resolve().parent / filename
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            rule_map = {}
            for k, v in raw.items():
                parts = [p.strip() for p in k.split(",")]
                if len(parts) != 2 or not parts[0] or not parts[1]:
                    raise ValueError(f"Invalid rule_map key: {k!r}, expected 'device_type, action_name'")
                rule_map[(parts[0], parts[1])] = v
            return rule_map
        except FileNotFoundError:
            print(f"{filename} does not exist")
            return {}
        except json.JSONDecodeError:
            print(f"{filename} is not a valid JSON file")
            return {}

    def build_execution_plan(self, room_plan: RoomPlan):
        """
        构建执行性计划
        """
        self.room = room_plan.room_name
        self.actions = room_plan.actions
        # 检查环境条件
        self.check_environment_conditions()
        for action in self.actions:
            self.build_dependency(action) 

    def check_environment_conditions(self):
        """
        检查环境条件
        """
        actions_to_remove = []
        # 遍历所有动作，检查它们的环境条件是否满足
        for action in self.actions:
            action_key = (action.device_type, action.action_name)
            environment_conditions = self.rule_map.get(action_key, {}).get("environment_conditions", [])
            for environment_condition in environment_conditions:
                state_type = environment_condition.get("state_type")
                field = environment_condition.get("field")
                operator = environment_condition.get("operator")
                right_value = environment_condition.get("right")
                mysql = MySQL()
                current_value = mysql.get_env_state(state_type, self.room, field)
                if current_value is None:
                    # 如果无法获取当前值，则跳过此条件检查
                    continue
                if operator == ">":
                    if not (float(current_value) > float(right_value)):
                        actions_to_remove.append(action)
                        break
                elif operator == "<":
                    if not (float(current_value) < float(right_value)):
                        actions_to_remove.append(action)
                        break
                elif operator == ">=":
                    if not (float(current_value) >= float(right_value)):
                        actions_to_remove.append(action)
                        break
                elif operator == "<=":
                    if not (float(current_value) <= float(right_value)):
                        actions_to_remove.append(action)
                        break
                elif operator == "=":
                    if not (float(current_value) == float(right_value)):
                        actions_to_remove.append(action)
                        break
                elif operator == "!=":
                    if not (float(current_value) != float(right_value)):
                        actions_to_remove.append(action)
                        break
        # 从 actions 中移除不满足条件的动作
        self.actions = [action for action in self.actions if action not in actions_to_remove]

    def build_dependency(self, device_action: DeviceAction):
        """
        递归构建执行动作拓扑图
        """
        device_action_str = device_action.model_dump_json()
        # 如果已经存在，说明已经构建过
        if device_action_str in self.graph:
            return
        action_key = (device_action.device_type, device_action.action_name)
        device_conditions = self.rule_map[action_key].get("device_conditions", [])
        # 前置条件为空，说明没有依赖
        if not device_conditions:
            self.graph[device_action_str] = []
            self.indegree[device_action_str] = 0
            return
        else:
            # 检查前置条件是否满足
            flag = True
            for device_condition in device_conditions:
                condition = device_condition.get("condition")
                device_type = condition.get("device_type")
                field = condition.get("field")
                target_value = condition.get("target")
                mysql = MySQL()
                current_value = mysql.get_status(device_type, self.room, field)
                if current_value == None:
                    continue
                # 如果不满足则加入
                elif str(current_value) != str(target_value):
                    flag = False
                    action_dict = device_condition.get("action")
                    device_type = action_dict.get("device_type")
                    action_name = action_dict.get("action_name")
                    pre_action = DeviceAction(device_type=device_type, action_name=action_name)
                    self.graph[device_action_str].append(pre_action.model_dump_json())
                    self.indegree[device_action_str] += 1
                    # 递归构建
                    self.build_dependency(pre_action)
            if flag:
                self.graph[device_action_str] = []
                self.indegree[device_action_str] = 0

    def execute_plan(self) -> tuple[str, list]:
        """
        多线程执行执行动作拓扑图
        """
        while True:
            zero_indegree_keys = [key for key, degree in self.indegree.items() if degree == 0]
            if not zero_indegree_keys:
                break
            threads = []
            results = []
            # 对每个入度为 0 的设备动作，创建一个线程来执行
            for key in zero_indegree_keys:
                thread = threading.Thread(target=self.execute_action, args=(key, results))
                threads.append(thread)
                thread.start()
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            # 校验是否都执行成功
            for result in results:
                if result != "success":
                    return result, list(self.exec_log)
        return "success", list(self.exec_log)
                
    def execute_action(self, key: str, results: list):
        """
        执行设备动作
        """
        device_action = DeviceAction.model_validate_json(key)
        device_type = device_action.device_type
        action_name = device_action.action_name
        parameters = device_action.parameters or {}
        # 1) Call the (mocked) device API
        if action_name == "turn_on":
            api_message = turn_on(device_type, self.room)
        elif action_name == "turn_off":
            api_message = turn_off(device_type, self.room)
        elif action_name == "open":
            api_message = api_open(device_type, self.room)
        elif action_name == "close":
            api_message = api_close(device_type, self.room)
        elif action_name == "set_temperature":
            api_message = set_temperature(device_type, self.room, int(parameters.get("temperature")))
        elif action_name == "set_speed":
            api_message = set_speed(device_type, self.room, int(parameters.get("speed")))
        if api_message != "success":
            # API level failure (invalid device/room/action/etc.)
            log_entry = {
                "ts": time.time(),
                "room": self.room,
                "device_type": device_type,
                "action_name": action_name,
                "parameters": parameters,
                "stage": "api",
                "status": "failed",
                "api_message": api_message,
            }
            with self.lock:
                self.exec_log.append(log_entry)
            results.append(api_message)
            return
        # 2) Validate the device state after a configured latency
        action_key = (device_type, action_name)
        validation = self.rule_map.get(action_key, {}).get("validation", {}) or {}
        latency = float(validation.get("latency", 0.1))
        field = validation.get("field", "status")
        target_value = validation.get("target")
        time.sleep(latency)
        mysql = MySQL()
        current_value = mysql.get_status(device_type, self.room, field)
        if str(current_value) == str(target_value):
            result = "success"
            self.update_graph_and_indegree(key)
            status = "success"
        else:
            result = f"{device_type} {action_name} in the {self.room} failed"
            status = "failed"
        log_entry = {
            "ts": time.time(),
            "room": self.room,
            "device_type": device_type,
            "action_name": action_name,
            "parameters": parameters,
            "stage": "validation",
            "status": status,
            "api_message": api_message,
            "validation": {
                "field": field,
                "expected": target_value,
                "actual": current_value,
                "latency": latency,
            },
        }
        with self.lock:
            self.exec_log.append(log_entry)
        results.append(result)
        return
    
    def update_graph_and_indegree(self, key: str):
        """
        更新 graph 和 indegree
        """
        with self.lock:
            # 从 indegree 和 graph 中删除
            if key in self.graph:
                del self.graph[key]  
            if key in self.indegree:
                del self.indegree[key]
            # 更新 graph 和 indegree 中其他动作的依赖关系
            for dependency_key, dependencies in self.graph.items():
                if key in dependencies:
                    dependencies.remove(key)
                    self.indegree[dependency_key] -= 1