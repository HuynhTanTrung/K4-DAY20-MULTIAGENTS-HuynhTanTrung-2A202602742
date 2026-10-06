---
name: comprehensive-bug-fixing-and-documentation
description: DÙNG KHI CẦN sửa lỗi mã nguồn, thêm bài kiểm tra hồi quy và cập nhật nhật ký thay đổi (changelog).
---
- Đảm bảo tuân thủ tuyệt đối quy tắc không chỉnh sửa các tệp kiểm tra gốc (nếu có yêu cầu), chỉ được phép thêm tệp kiểm tra mới.
- Thêm chú thích kiểu dữ liệu (type hints) đầy đủ cho tất cả các tham số và giá trị trả về của mọi hàm công khai (public function).
- Viết tệp kiểm tra hồi quy riêng biệt (ví dụ: `tests/test_regressions.py`) với ít nhất một hàm kiểm tra cho mỗi lỗi đã được sửa.
- Cập nhật tệp `CHANGELOG.md` dưới tiêu đề quy định (ví dụ: `## Unreleased`) với các mục ghi chú dạng gạch đầu dòng rõ ràng cho từng bản sửa lỗi.