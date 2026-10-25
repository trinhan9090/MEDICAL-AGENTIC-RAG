'''
Thực hiện inference qua API.
'''

from openai import OpenAI
from models import config


class APIBackend:
    # Khởi tạo API client và đọc khóa bảo mật
    def __init__(self, model_name: str):
        if not config.SECRET_KEY_PATH.is_file():
            raise FileNotFoundError(
                f"Không tìm thấy API key: {config.SECRET_KEY_PATH}"
            )

        api_key = config.SECRET_KEY_PATH.read_text(
            encoding="utf-8"
        ).strip()

        if not api_key:
            raise ValueError("File secret_key đang trống.")

        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key,
            base_url=config.API_BASE_URL,
            timeout=config.API_TIMEOUT,
            max_retries=config.API_MAX_RETRIES,
        )

    # Gửi prompt và trả về nội dung phản hồi dạng text
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> str:
        request = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            config.API_TOKEN_PARAMETER: max_tokens,
        }

        if json_mode and config.API_JSON_MODE:
            request["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(
            **request
        )

        if not response.choices:
            raise ValueError("API không trả về completion.")

        choice = response.choices[0]

        if choice.finish_reason == "length":
            raise ValueError(
                "Model đạt giới hạn token trước khi hoàn thành."
            )

        if choice.finish_reason == "content_filter":
            raise ValueError(
                "Phản hồi đã bị bộ lọc nội dung chặn."
            )

        content = choice.message.content

        if not content:
            raise ValueError("API không trả về nội dung.")

        return content
