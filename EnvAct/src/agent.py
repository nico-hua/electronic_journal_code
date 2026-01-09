from langchain_core.language_models import BaseChatModel
import time
import json
from typing import Any, Dict, List, Optional
from src.planner import Planner, RoomPlan, PlannerResponse, PlannerRunResult
from src.ruler import Ruler
import threading

class Agent:
    """Smart-home Agent with Plan -> Constrain -> Execute -> Feedback loop."""
    def __init__(self, user_location: str, llm: BaseChatModel):
        self.user_location = user_location
        self.llm = llm
        self.planner = Planner(user_location, llm)

    def _process_room_plan(self, room_plan: RoomPlan, results: List[Dict[str, Any]]):
        """Build constrained plan and execute for one room (thread worker)."""
        ruler = Ruler()
        build_start_time = time.time()
        ruler.build_execution_plan(room_plan)
        build_end_time = time.time()
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
    
    def _format_feedback_for_replan(
        self,
        user_instruction: str,
        last_plan: Optional[PlannerResponse],
        execution_results: List[Dict[str, Any]],
        max_log_chars: int = 8000,
    ) -> str:
        failures = [r for r in execution_results if r.get("status") != "success"]
        combined_log = []
        for r in execution_results:
            combined_log.extend(r.get("exec_log") or [])

        payload = {
            "original_user_instruction": user_instruction,
            "failed_rooms": [
                {"room": f.get("room"), "reason": f.get("status")} for f in failures
            ],
            "last_plan": last_plan.model_dump() if last_plan else None,
            "execution_log": combined_log,
            "requirements": [
                "Please generate a revised execution plan that can complete the user's intent.",
                "You may choose alternative devices/actions if the original ones fail.",
                "If no feasible alternative exists, call reply_user with a concise explanation and any actionable suggestions (e.g., manual steps or missing capability).",
            ],
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if len(text) > max_log_chars:
            # keep the tail (usually contains the failure) and the head (schema)
            head = text[: int(max_log_chars * 0.6)]
            tail = text[-int(max_log_chars * 0.4) :]
            text = head + "\n... (log truncated) ...\n" + tail
        return text

    def run(self, max_iterations: int = 3):
        """
        Start a continuous interactive loop.

        - For each user instruction, plan and execute.
        - If execution fails, feed the execution log back to the planner and retry, up to max_iterations.
        """
        while True:
            instruction = input("Please enter the command and enter 'exit' to exit: ")
            if instruction.lower() == "exit":
                print("Exiting...")
                break
            if not instruction:
                continue
            total_start_time = time.time()
            last_plan: Optional[PlannerResponse] = None
            feedback: Optional[str] = None
            for attempt in range(1, max_iterations + 1):
                # fresh context each attempt (time/context/devices may have changed)
                self.planner.reset(self.user_location)
                attempt_instruction = instruction
                if feedback:
                    attempt_instruction = (
                        instruction
                        + "\n\n# Previous execution feedback (for replanning)\n"
                        + feedback
                    )
                plan_start_time = time.time()
                plan_res: PlannerRunResult = self.planner.run(attempt_instruction)
                plan_end_time = time.time()
                print(f"执行计划生成耗时：{plan_end_time - plan_start_time}秒")
                if plan_res.type == "reply":
                    # Planner decided it cannot produce a feasible plan
                    if plan_res.message:
                        print(plan_res.message)
                    break
                if not plan_res.plan:
                    print("规划器未返回可执行计划。\n")
                    break
                last_plan = plan_res.plan
                # Execute (multi-room in parallel)
                exec_start_time = time.time()
                execution_results = self._execute_multi_room_plan(last_plan)
                exec_end_time = time.time()
                # Print per-room summary
                for r in execution_results:
                    print(
                        f"[{r.get('room')}] build={r.get('build_time_s'):.3f}s, status={r.get('status')}"
                    )
                all_success = all(r.get("status") == "success" for r in execution_results)
                if all_success:
                    print(f"✅ 执行成功，用时：{exec_end_time - exec_start_time} 秒")
                    break
                # Failed: prepare feedback and retry
                failures = [r for r in execution_results if r.get("status") != "success"]
                for f in failures:
                    print(f"❌ 失败：room={f.get('room')} reason={f.get('status')}")
                if attempt < max_iterations:
                    feedback = self._format_feedback_for_replan(
                        user_instruction=instruction,
                        last_plan=last_plan,
                        execution_results=execution_results,
                    )
                    print(f"准备重新规划（attempt {attempt + 1}/{max_iterations}）...\n")
                else:
                    # Last attempt failed: tell user and stop retrying
                    print(
                        "已达到最大迭代次数，仍未能成功执行。你可以尝试：\n"
                        "- 换一种更具体的说法（房间/设备/目标值）\n"
                        "- 检查设备是否在线/可控，或在环境表征中补充设备能力\n"
                    )
            total_end_time = time.time()
            print(f"总共用时: {total_end_time - total_start_time} 秒\n")
