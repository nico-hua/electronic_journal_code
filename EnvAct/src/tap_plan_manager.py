from threading import Thread
import json
import time
from .planner import PlannerResponse, Condition, RoomPlan
from .mysql import MySQL
from typing import List, Dict, Any
from datetime import datetime
import threading
from .ruler import Ruler
import os

class TapPlanManager:
    def __init__(self, filename="tap_plans.json"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(current_dir, filename)
        self.tap_plans: List[PlannerResponse] = self.load_plans_from_file()
        self.running = True
        self.check_interval = 60
        self.thread = Thread(target=self.run_polling, daemon=True)
        self.thread.start()

    def load_plans_from_file(self) -> List[PlannerResponse]:
        try:
            with open(self.filename, "r", encoding="utf-8") as json_file:
                file_content = json_file.read().strip()
            # 1. 处理真正的空文件
            if not file_content:
                return []
            # 2. 尝试解析
            raw_data = json.loads(file_content)
            # 3. 确保解析出来的是列表（因为你的逻辑是 list）
            if not isinstance(raw_data, list):
                print(f"警告: {self.filename} 格式错误（根元素不是列表）。重置为空。")
                return []
            return [PlannerResponse.model_validate(plan) for plan in raw_data]
        except FileNotFoundError:
            # 文件不存在，返回空列表
            return []
        except json.JSONDecodeError as e:
            # 【关键修复】捕获 JSON 解析错误（如文件只有一半、乱码等）
            print(f"警告: 读取 {self.filename} 失败，文件内容已损坏或格式不正确。错误信息: {e}")
            print("系统将自动使用空计划列表启动。")
            return []
        
    def save_plans_to_file(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump([plan.to_dict() for plan in self.tap_plans], file, ensure_ascii=False, indent=2)

    def add_plan(self, plan: PlannerResponse):
        self.tap_plans.append(plan)
        self.save_plans_to_file()

    def remove_plan(self, plan: PlannerResponse):
        self.tap_plans.remove(plan)
        self.save_plans_to_file()

    def run_polling(self):
        while self.running:
            time.sleep(self.check_interval)
            self.check_and_execute_plans()

    def check_and_execute_plans(self):
        for plan in self.tap_plans:
            print("开始检查计划...")
            print(plan)
            conditions_met = True
            for condition in plan.conditions:
                if not self.check_condition(condition):
                    conditions_met = False
                    break
            if conditions_met:
                print(f"计划已满足条件，开始执行...")
                print(plan)
                self.execute_plan(plan)

    def check_condition(self, condition: Condition) -> bool:
        left = condition.left
        op = condition.op
        right = condition.right
        if left == "current_time":
            current_time = datetime.now().strftime("%H:%M")
            if op == ">" or op == ">=":
                return current_time > right
            elif op == "<" or op == "<=":
                return current_time < right
            elif op == "=":
                return current_time == right
            elif op == "!=":
                return current_time != right
        else:
            room, field = left.split(".", 1)
            mysql = MySQL()
            current_value = mysql.get_env_state(field, room, field)
            if op == ">":
                return float(current_value) > float(right)
            elif op == "<":
                return float(current_value) < float(right)
            elif op == ">=":
                return float(current_value) >= float(right)
            elif op == "<=":
                return float(current_value) <= float(right)
            elif op == "=":
                return float(current_value) == float(right)
            elif op == "!=":
                return float(current_value) != float(right)
            
    def _process_room_plan(self, room_plan: RoomPlan, results: List[Dict[str, Any]]):
        """Build constrained plan and execute for one room (thread worker)."""
        ruler = Ruler()
        build_start_time = time.time()
        print("开始构建执行动作拓扑图")
        ruler.build_execution_plan(room_plan)
        build_end_time = time.time()
        print("执行动作拓扑图构建完成")
        print(ruler.graph)
        print(ruler.indegree)
        print("开始执行计划")
        status, exec_log = ruler.execute_plan()
        results.append(
            {
                "room": room_plan.room_name,
                "status": status,
                "exec_log": exec_log,
                "build_time_s": build_end_time - build_start_time,
                "graph": dict(ruler.graph),
                "indegree": dict(ruler.indegree)
            }
        )
        print("计划执行完毕")
        print(results)

    def _execute_multi_room_plan(self, plan: PlannerResponse) -> List[Dict[str, Any]]:
        threads: List[threading.Thread] = []
        results: List[Dict[str, Any]] = []
        for room_plan in plan.plan:
            thread = threading.Thread(
                target=self._process_room_plan,
                args=(room_plan, results),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        return results
        
    def execute_plan(self, plan: PlannerResponse):
        self._execute_multi_room_plan(plan)