
"""
Xử lý các phản hồi khi câu hỏi không được chuyển sang retrieval.

Không gọi LLM, không sử dụng Knowledge Base.
Tất cả thông báo được định nghĩa sẵn để dễ kiểm thử.
"""

RESPONSE_MESSAGES = {
    "urgent_medical_symptoms": (
        "Các triệu chứng bạn mô tả có thể cần được đánh giá "
        "y tế khẩn cấp. Nếu bạn đang ở Việt Nam, hãy gọi 115; "
        "nếu ở Hoa Kỳ, hãy gọi 911; hoặc liên hệ số cấp cứu "
        "địa phương ngay. Không nên chờ hệ thống AI "
        "đưa ra chẩn đoán."
    ),

    "personalized_medication_dose": (
        "Tôi không thể xác định hoặc điều chỉnh liều thuốc "
        "cá nhân dựa trên thông tin hiện có. Bạn nên liên hệ "
        "bác sĩ điều trị hoặc cơ sở khám chữa bệnh gần nhất. "
        "Không tự ý tăng, giảm hoặc ngừng thuốc."
    ),

    "unsupported_current_price": (
        "Hệ thống hiện không có dữ liệu giá thuốc hoặc "
        "dịch vụ y tế theo thời gian thực. Bạn nên kiểm tra "
        "trực tiếp với nhà thuốc hoặc cơ sở y tế để biết "
        "giá được cập nhật."
    ),

    "unsupported_guideline_validity": (
        "Hệ thống không thể xác nhận chắc chắn hướng dẫn "
        "y khoa này còn hiệu lực tại thời điểm hiện tại. "
        "Bạn nên kiểm tra văn bản gốc, các quyết định "
        "sửa đổi hoặc thay thế trên cổng thông tin "
        "chính thức của Bộ Y tế."
    ),

    "unsupported_pediatric_treatment": (
        "Hệ thống chưa hỗ trợ đưa ra quyết định điều trị "
        "cá nhân cho trẻ em. Bạn nên tham khảo ý kiến "
        "bác sĩ nhi khoa hoặc cơ sở y tế phù hợp."
    ),

    "unsupported_current_pregnancy_treatment": (
        "Hệ thống chưa hỗ trợ đưa ra quyết định điều trị "
        "cá nhân trong thai kỳ. Bạn nên liên hệ bác sĩ "
        "sản khoa hoặc bác sĩ đang theo dõi thai kỳ."
    ),

    "unsafe_personalized_treatment": (
        "Hệ thống không thể đưa ra quyết định điều trị "
        "cá nhân thay cho bác sĩ. Bạn nên đến cơ sở "
        "khám chữa bệnh để được đánh giá."
    ),

    "out_of_domain": (
        "Câu hỏi này nằm ngoài phạm vi hỗ trợ của hệ thống "
        "hỏi đáp y tế."
    ),
}


# Đồng nhất reason code giữa Pre-Planner và Planner.
REASON_ALIASES = {
    "urgent_safety": "urgent_medical_symptoms",
    "personal_dose": "personalized_medication_dose",
    "current_price": "unsupported_current_price",
    "currency_confirmation": "unsupported_guideline_validity",
}


def handle_restriction(reason: str, source: str) -> dict:
    # Chuẩn hóa reason code trước khi chọn thông báo.
    canonical_reason = REASON_ALIASES.get(reason, reason)

    if canonical_reason not in RESPONSE_MESSAGES:
        raise ValueError(
            f"Unknown restriction reason: {reason}"
        )

    return {
        "route": "urgent_safety"
        if canonical_reason == "urgent_medical_symptoms"
        else "reject",
        "reason": canonical_reason,
        "response": RESPONSE_MESSAGES[canonical_reason],
        "decision_source": source,
        "retrieval_allowed": False,
    }
