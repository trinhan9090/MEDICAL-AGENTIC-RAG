
from restriction_rules.pre_planner_rules import route_question
from pipeline.response_handler import handle_restriction
from planner.planner import QwenPlanner


class Orchestrator:
    def __init__(self, planner=None):
        self.planner = planner

    def process(self, query: str) -> dict:
        # Bước 1: Kiểm tra rule-based trước khi gọi LLM.
        screening = route_question(query)

        action = screening["action"]

        # Các trường hợp không cần gọi Planner.
        if action not in {"pass", "review"}:
            return handle_restriction(
                reason=screening["reason"],
                source="pre_planner_rules",
            )

        # Bước 2: Planner kiểm tra ngữ nghĩa và lập kế hoạch.
        if self.planner is None:
            self.planner = QwenPlanner()

        plan = self.planner.plan(
            query,
            screening=screening,
        )

        # Planner quyết định từ chối.
        if plan["route"] == "reject":
            return handle_restriction(
                reason=plan["reason"],
                source="qwen_planner",
            )

        # Bước 3: Chuẩn bị query cho Retriever.
        # Giai đoạn hiện tại chỉ test routing, chưa retrieval.
        all_queries = list(dict.fromkeys(
            [query.strip(), *plan["retrieval_queries"]]
        ))

        return {
            "route": "retrieve",
            "plan": plan,
            "queries": all_queries,
            "retrieval_allowed": True,
        }
