'''
Thiết lập cấu hình gửi request và nhận kết quả từ model
Cung cấp interface chung generate_json(), tự chọn backend.
'''

import json
import re
from models import config


class ModelClient:
    # Khởi tạo backend dựa vào models/config.py
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or config.PLANNER_MODEL
        self.backend_name = config.MODEL_BACKEND.lower()

        if self.backend_name == "api":
            from models.backends.api import APIBackend
            self.backend = APIBackend(self.model_name)

        elif self.backend_name == "huggingface":
            from models.backends.huggingface import HuggingFaceBackend
            self.backend = HuggingFaceBackend(self.model_name)

        else:
            raise ValueError(
                f"Backend không được hỗ trợ: {self.backend_name}"
            )

    # Chuẩn hóa nội dung JSON nhận từ các backend
    @staticmethod
    def parse_json(raw_output: str) -> dict:
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            raw_output,
            flags=re.DOTALL,
        ).strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                cleaned,
            ).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model không trả về JSON hợp lệ:\n{cleaned}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("Model output phải là JSON object.")

        return data

    # Sinh JSON qua backend được cấu hình
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = config.DEFAULT_MAX_TOKENS,
        temperature: float = config.DEFAULT_TEMPERATURE,
    ) -> dict:
        raw_output = self.backend.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=True,
        )

        return self.parse_json(raw_output)

    # Sinh text thông thường cho Answer Generator
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = config.DEFAULT_MAX_TOKENS,
        temperature: float = config.DEFAULT_TEMPERATURE,
    ) -> str:
        return self.backend.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            json_mode=False,
        )
