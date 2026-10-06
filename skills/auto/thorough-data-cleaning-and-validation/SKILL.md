---
name: thorough-data-cleaning-and-validation
description: DÙNG KHI CẦN xử lý, làm sạch dữ liệu thô (CSV, log) và tính toán các chỉ số thống kê.
---
- Kiểm tra và xử lý triệt để các giá trị thiếu, giá trị ngoại lai (outliers) hoặc dữ liệu hỏng theo đúng quy định trong tài liệu mô tả.
- Xử lý chính xác các bản ghi trùng lặp (ví dụ: giữ lại dòng đầu tiên hoặc gộp theo mã định danh) và ghi nhận số lượng đã loại bỏ.
- Chuẩn hóa các trường văn bản (như tên vùng, tên dịch vụ) về dạng chuẩn (chữ thường, thay thế ký tự đặc biệt) để tránh lệch dữ liệu khi tổng hợp.
- Sắp xếp kết quả theo đúng các tiêu chí thứ tự (ví dụ: theo nhóm dịch vụ rồi đến thời gian tăng dần) trước khi xuất tệp.