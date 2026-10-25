
import json
from models.client import ModelClient
from models.config import PLANNER_MODEL
from planner.planner_api import QwenPlanner

# Khởi tạo và kiểm thử Planner
model = ModelClient(model_name=PLANNER_MODEL)
planner = QwenPlanner(model=model)

query = (
    "What are the recommended approaches for managing cardiovascular risk in patients with type 2 diabetes?"
)

result = planner.plan(query)

print(json.dumps(result, indent=2, ensure_ascii=False))
