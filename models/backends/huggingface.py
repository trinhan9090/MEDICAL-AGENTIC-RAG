'''
Tải và chạy model từ Hugging Face.
'''


import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)
from models import config



class HuggingFaceBackend:
    # Khởi tạo model từ Hugging Face Hub hoặc cache session
    def __init__(self, model_name: str):
        self.model_name = model_name

        cache_dir = (
            str(config.HF_CACHE_DIR)
            if config.HF_CACHE_DIR is not None
            else None
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=config.HF_TRUST_REMOTE_CODE,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            device_map=config.HF_DEVICE_MAP,
            dtype=config.HF_DTYPE,
            trust_remote_code=config.HF_TRUST_REMOTE_CODE,
        )

        self.model.eval()

    # Sinh phản hồi sử dụng chat template của model
    @torch.inference_mode()
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> str:
        if json_mode:
            system_prompt += (
                "\nReturn exactly one valid JSON object. "
                "Do not include Markdown or explanatory text."
            )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        template_kwargs = {}

        if "qwen3" in self.model_name.lower():
            template_kwargs["enable_thinking"] = (
                config.HF_ENABLE_THINKING
            )

        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            **template_kwargs,
        )

        device = self.model.get_input_embeddings().weight.device
        inputs = inputs.to(device)

        do_sample = temperature > 0

        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
        }

        if do_sample:
            generation_kwargs["temperature"] = temperature

        outputs = self.model.generate(
            **inputs,
            **generation_kwargs,
        )

        generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]
        
        response = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        )
        
        # Phát hiện phản hồi có thể bị cắt do giới hạn token
        if len(generated_ids) >= max_tokens:
            if generated_ids[-1].item() not in (
                self.model.generation_config.eos_token_id
                if isinstance(
                    self.model.generation_config.eos_token_id, list
                )
                else [self.model.generation_config.eos_token_id]
            ):
                raise ValueError(
                    "Hugging Face model đạt giới hạn output tokens."
                )

        content = self.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        ).strip()

        if not content:
            raise ValueError(
                "Hugging Face model không trả về nội dung."
            )

        return content
