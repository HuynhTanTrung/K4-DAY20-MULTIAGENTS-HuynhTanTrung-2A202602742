"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau)."""
    return [
        {
            "name": "explorer",
            "description": (
                "Dùng khi cần khảo sát codebase, đọc README/docstring, "
                "tìm file hoặc mẫu dữ liệu mà chưa rõ vị trí. "
                "Subagent này chỉ đọc và báo cáo sự thật, không sửa file."
            ),
            "system_prompt": (
                "Bạn là explorer. Nhiệm vụ: đọc README, docstring, mẫu dữ liệu, "
                "tìm file và nội dung liên quan. Chỉ báo cáo sự thật quan sát được, "
                "kèm đường dẫn và trích dẫn ngắn. Không sửa, không tạo file."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Dùng khi đã xác định được thay đổi cần làm và cần thực thi: "
                "sửa/tạo file, chạy test hoặc script, rồi báo cáo kết quả."
            ),
            "system_prompt": (
                "Bạn là implementer. Nhiệm vụ: thực hiện thay đổi theo yêu cầu, "
                "chạy test hoặc script liên quan, và báo cáo chính xác: "
                "file đã sửa, lệnh đã chạy, kết quả (exit code, output chính), "
                "lỗi còn tồn tại nếu có. Không tự mở rộng phạm vi."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Dùng sau khi implementer hoàn tất, khi cần kiểm tra độc lập "
                "kết quả theo đề bài và các trường hợp biên trước khi kết luận."
            ),
            "system_prompt": (
                "Bạn là reviewer. Nhiệm vụ: kiểm tra độc lập kết quả theo đề bài "
                "và các trường hợp biên. Chỉ đọc và chạy kiểm tra; không sửa file. "
                "Báo cáo: check nào đạt/không đạt, bằng chứng cụ thể, rủi ro còn lại."
            ),
        },
    ]
