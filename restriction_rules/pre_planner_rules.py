# restriction_rules/pre_planner_rules.py
'''
Định nghĩa các từ khóa nhạy cảm. Cần được xem xét
'''
import re
import unicodedata


def normalize(text: str) -> str:
    return re.sub(
        r"\s+", " ",
        unicodedata.normalize("NFC", text).casefold()
    ).strip()


# 1. Nhận diện đối tượng và tình huống y tế
MINOR_WORDS = re.compile(
    r"\b(?:trẻ em|trẻ nhỏ|em bé|bé nhà|con nhỏ|cháu bé|"
    r"nhi khoa|con tôi|con em|my child|pediatric)\b"
)
AGE = re.compile(r"\b(\d{1,3})\s*(?:tuổi|years? old)\b")
TREATMENT = re.compile(
    r"\b(?:liều|insulin|thuốc|tiêm|điều trị|phác đồ|"
    r"dose|medication|treatment)\b"
)

CURRENT_PREGNANCY = re.compile(
    r"\b(?:đang|hiện đang|hiện|i am|i'm)\s+"
    r"(?:mang thai|có thai|mang bầu|có bầu|pregnant)"
    r"|(?:mang thai|có thai|thai)\s+\d{1,2}\s*tuần"
)

PREGNANCY_NEGATION = re.compile(
    r"\b(?:không|chưa)\s+(?:mang thai|có thai|mang bầu|có bầu)"
    r"|\bnot pregnant\b"
)

# 2. Nhận diện yêu cầu cá nhân hóa
FIRST_PERSON = re.compile(
    r"\b(?:tôi|mình|em|bố tôi|mẹ tôi|chồng tôi|vợ tôi|"
    r"con tôi|con em|i|my|me)\b"
)

PERSONAL_DOSE = re.compile(
    r"(?:tiêm|uống|dùng|take|inject)\s+"
    r"(?:chính xác\s+)?(?:bao nhiêu|mấy|how much|how many)"
    r"|(?:tính|chỉnh|tăng|giảm|cho|adjust|calculate)\s+"
    r"(?:giúp\s+)?(?:tôi\s+|mình\s+|em\s+)?liều"
)

# 3. Nhận diện yêu cầu dữ liệu ngoài KB tĩnh
PRICE = re.compile(
    r"\b(?:giá thuốc|giá bán|giá tiền|bao nhiêu tiền|"
    r"chi phí|price|cost)\b"
)
NOW = re.compile(
    r"\b(?:hôm nay|hiện nay|hiện tại|bây giờ|"
    r"nhà thuốc|today|current|now|pharmacy)\b"
)

CURRENCY_CLAIM = re.compile(
    r"(?:xác nhận|khẳng định|bảo đảm|đảm bảo|chắc chắn|"
    r"confirm|guarantee|verify)[^.?!]*"
    r"(?:hiện hành|còn hiệu lực|mới nhất|năm 20\d\d|"
    r"still valid|latest|up.to.date)"
)

# 4. Dấu hiệu cấp cứu rõ ràng
EMERGENCY = re.compile(
    r"(?:đau ngực|chest pain)[^.?!]{0,60}"
    r"(?:khó thở|vã mồ hôi|shortness of breath)"
    r"|(?:khó thở|vã mồ hôi)[^.?!]{0,60}"
    r"(?:đau ngực|chest pain)"
    r"|(?:bất tỉnh|không thở|unconscious|not breathing)"
)

# 5. Phát hiện nỗ lực can thiệp hướng dẫn
OVERRIDE = re.compile(
    r"bỏ qua[^.?!:]*?(?:chú thích|tài liệu|ghi chú|"
    r"điều kiện|hướng dẫn|quy tắc)"
    r"|ignore (?:the )?(?:footnotes|evidence|instructions|rules)",
    re.I
)


def route_question(question: str) -> dict:
    text = normalize(question)

    # Nhận diện người dưới 18 tuổi
    minor = (
        bool(MINOR_WORDS.search(text))
        or any(int(age) < 18 for age in AGE.findall(text))
    )

    treatment = bool(TREATMENT.search(text))
    personal = bool(FIRST_PERSON.search(text))

    pregnancy = (
        bool(CURRENT_PREGNANCY.search(text))
        and not bool(PREGNANCY_NEGATION.search(text))
    )

    checks = [
        ("urgent_safety", bool(EMERGENCY.search(text))),
        ("pediatric_treatment", minor and treatment),
        ("current_pregnancy", pregnancy),
        ("personal_dose",
         personal and bool(PERSONAL_DOSE.search(text))),
        ("current_price",
         bool(PRICE.search(text) and NOW.search(text))),
        ("currency_confirmation",
         bool(CURRENCY_CLAIM.search(text))),
    ]

    matched = [name for name, hit in checks if hit]

    # Chỉ quyết định sớm khi có tín hiệu rõ ràng.
    # Các trường hợp nhạy cảm còn lại chuyển cho Planner.

    # các loại từ khóa thuộc EMERGENCY
    if "urgent_safety" in matched:
        action = "urgent_safety"
        reason = "urgent_safety"

    # các loại từ khóa thuộc PERSONAL_DOSE
    elif "personal_dose" in matched:
        action = "reject"
        reason = "personal_dose"

    # các loại từ khóa thuộc PRICE và NOW
    elif "current_price" in matched:
        action = "unsupported_capability"
        reason = "current_price"

    # các loại từ khóa thuộc CURRENCY_CLAIM
    elif "currency_confirmation" in matched:
        action = "unsupported_capability"
        reason = "currency_confirmation"

    # các loại từ khóa thuộc MINOR, PREGNANCY và TREATMENT
    elif matched:
        action = "review"
        reason = matched[0]

    # KHÔNG CÓ TỪ KHÓA NÀO NHẠY CẢM
    else:
        action = "pass"
        reason = None

    return {
        "action": action,
        "reason": reason,
        "matched": matched,
        "override_attempt": bool(OVERRIDE.search(text)),
        "method": "keyword_policy_heuristic_v2"
    }