'''
Chọn backend, model và các tham số.
Mô hình nào, ở đâu, cấu hình như thế nào?
Khi đổi mô hình thì chỉ cần thay đổi ở đây
'''

from pathlib import Path

# Đường dẫn cấu hình
MODEL_DIR = Path(__file__).resolve().parent
SECRET_KEY_PATH = MODEL_DIR / "secret_key"
HF_CACHE_DIR = MODEL_DIR / "hf_cache"

# Backend mặc định: "api" hoặc "huggingface"
MODEL_BACKEND = "huggingface"

# Model sử dụng cho từng thành phần
PLANNER_MODEL = (
    r"D:\1_TaiLieuHocTap\2627\DuAn_KhoaLuan"
    r"\Demo_Nhan\DACNTT\models\weights\qwen3-1.7b"
) # model cho agent planner
EVALUATOR_MODEL = PLANNER_MODEL # model cho agent đánh giá
GENERATOR_MODEL = PLANNER_MODEL # model cho agent generator

# Cấu hình API
API_BASE_URL = "https://api.miraiapi.com/v1"
API_TIMEOUT = 120.0
API_MAX_RETRIES = 2
API_JSON_MODE = True

# Tùy chọn tương thích với API provider
API_TOKEN_PARAMETER = "max_tokens"

# Cấu hình Hugging Face
HF_DEVICE_MAP = "auto"
HF_DTYPE = "auto"
HF_TRUST_REMOTE_CODE = False
HF_ENABLE_THINKING = False

# Thông số riêng cho Planner
PLANNER_MAX_TOKENS = 512
PLANNER_TEMPERATURE = 0.0

# Thông số mặc định cho các tác vụ khác
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.0
