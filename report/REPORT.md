# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên          | Mã sinh viên | Phần đóng góp |
| --------------- | ------------ | ------------- |
| Huỳnh Tấn Trung | 2A202602742  |               |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): subagents đạt điểm tác vụ học cao hơn baseline nhờ tách pha khảo sát – thực thi – kiểm chứng, giúp phát hiện lỗi nhóm D và nhóm E. Chi phí token sẽ cao hơn đáng kể — Anthropic ghi nhận hệ đa tác tử tốn ~15× token so với hội thoại thường
- H2 (skills-auto so với baseline): skills-auto cải thiện điểm tác vụ học, chủ yếu ở các check nhóm E, vì curator sinh skill từ chính các lỗi baseline (đọc RULE, chuyển đổi đơn vị, kiểm tra metadata). Theo SkillsBench, skill do mô hình tự sinh trung bình không có lợi, nên kỳ vọng cải thiện nhỏ và có thể không đạt ý nghĩa thống kê
- H3 (tác vụ học so với tác vụ đánh giá): Skill sinh từ tác vụ học giúp tác vụ học nhiều hơn tác vụ đánh giá, do quá khớp (overfitting). SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới. Kỳ vọng: skills-auto cải thiện điểm learn nhưng không cải thiện (hoặc kém hơn) điểm eval

## 3. Làm quen Deep Agents (Phần 0.3)

1. Công cụ mặc định: ls, read_file, write_file, edit_file, delete, glob, grep, execute, task. Chạy lệnh: execute
2. Subagent general-purpose: đa dụng, nghiên cứu/tìm kiếm/thực thi tác vụ nhiều bước, có tất cả công cụ như tác tử chính. Nó không thấy ngữ cảnh tác tử chính, mỗi lần gọi là stateless, chỉ nhận prompt và trả báo cáo cuối
3. task: "Launch multiple agents concurrently when their tasks are independent..."

   execute: "Use absolute paths and avoid cd so the working directory stays stable..."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ                | Check thất bại                | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết)                                                      |
| --------------------- | ----------------------------- | -------------- | ------------------------------------------------------------------------------------------------- |
| code-learn (baseline) | tất cả 10 check               | G              | `GraphRecursionError: Recursion limit of 60 reached` — `tool_calls=0`, trace rỗng                 |
| code-learn (baseline) | tests_not_modified            | A              | `the original files in tests/ must not be modified` — tác tử không đọc quy ước "không sửa tests/" |
| code-learn (baseline) | parse_price_all_formats       | D              | `wrong for: ['$1,299.50', '(12.00)', '$1,000,000.00']`                                            |
| code-learn (baseline) | other_caller_fixed            | D              | `to_csv_row returned '<InvalidOperation>'`                                                        |
| code-learn (baseline) | discount_rounds_half_up       | D              | `wrong for: [('10.05', 10, '9.05'), ('0.05', 50, '0.03'), ('2.665', 0, '2.67')]`                  |
| code-learn (baseline) | low_stock_follows_docstring   | A              | `low_stock returned ['b', 'A', 'c']` — không theo docstring                                       |
| code-learn (baseline) | csv_quoting_follows_docstring | A              | `to_csv_row returned 'Desk, large "oak",10.00,2'` — không theo docstring                          |
| code-learn (baseline) | rule_type_hints               | E              | `RULE: every public function ... has type annotations`                                            |
| code-learn (baseline) | rule_regression_tests         | E              | `RULE: add tests/test_regressions.py ... (at least 3)`                                            |
| code-learn (baseline) | rule_changelog                | E              | `RULE: record each fix in CHANGELOG.md under '## Unreleased'`                                     |
| data-learn (baseline) | north_q1_orders               | D              | `north_q1_orders: wrong value (got 13)`                                                           |
| data-learn (baseline) | rule_money_in_cents           | E              | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).`            |
| data-learn (baseline) | rule_meta_block               | E              | `RULE: answer.json has an object meta = {...}`                                                    |
| data-learn (baseline) | rule_clean_csv                | E              | `RULE: write workspace/clean.csv with header order_id,timestamp_utc,region,amount_cents...`       |
| logs-learn (baseline) | rule_service_names            | E              | `RULE: service names in the output are lower-case with '-' replaced by '_'`                       |
| logs-learn (baseline) | rule_sorted_errors            | E              | `RULE: errors is sorted by service, then by timestamp_utc, ascending.`                            |
| logs-learn (baseline) | rule_schema_header            | E              | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".`            |

Nhận xét: Nhóm E chiếm đa số (9/17 lỗi) — tác tử bỏ qua quy ước Acme không có trong đề. Nhóm D đứng thứ hai (4/17) — sai định dạng/rounding. Nhóm A có 3 lỗi ở code-learn. Riêng code-learn baseline có 1 lỗi G ở lần chạy đầu, nhưng run.json sau đó cho thấy 10 check thực tế đều fail — nghĩa là lần chạy lại không có lỗi G. Check kỹ thuật đạt: data-learn 4/5, logs-learn 6/6, code-learn 0/7 — bằng chứng phủ định cho A–D chỉ đúng một phần. Skill có thể phòng ngừa nhóm E nếu description nêu rõ quy ước Acme và tác tử chịu đọc SKILL.md; ở baseline skills_read=0 nên không có skill nào can thiệp

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): explorer (đọc và báo cáo, không sửa), implementer (thực hiện và chạy test), reviewer (kiểm tra độc lập theo đề và trường hợp biên, không sửa). Mục đích: tách pha khảo sát – thực thi – kiểm chứng và có bước đối chiếu độc lập
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0): code-learn = 7, data-learn = 7, logs-learn = 4. Cả ba tác vụ đều có giao việc. Tuy nhiên trace baseline/data-learn cho thấy subagent được gọi là general-purpose (mặc định của Deep Agents), không phải subagent tự định nghĩa — cần đọc trace.md của điều kiện subagents để xác nhận
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): lời giao việc ở baseline/data-learn đủ bước tính và định dạng file nhưng thiếu quy ước Acme (cents, meta, clean.csv) — nguyên nhân trực tiếp của 3 lỗi nhóm E. Tác tử chính có đọc lại workspace/answer.json sau khi subagent trả về, đúng SUBAGENTS_NOTE, nhưng chỉ kiểm tra tồn tại, không đối chiếu nội dung
- Ảnh hưởng đến token và thời gian: subagents tokens.total là 1.194.496 (code-learn), 291.026 (data-learn), 866.250 (logs-learn). So với baseline: data-learn subagents rẻ hơn ~3× (291k so với 884k), nhưng code-learn và logs-learn đắt hơn. Đa tác tử không nhất quán về chi phí — cần đối chiếu điểm số ở mục 7 để kết luận có đáng không

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill                                      | Tổng quát hay riêng cho tác vụ học?                                                                                                 | Đúng hay sai (nêu chỗ sai nếu có)                                                                                                                                                                                     | Độ dài, `description` và `skills_read` ở Phần 3.4                                                                                                    |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| adhere-to-strict-rules-and-metadata        | Tổng quát — nói về quy trình đọc RULE, chuyển đổi đơn vị tiền tệ, metadata, kiểm tra output. Không nêu id tác vụ hay tên tệp riêng. | Đúng. Khớp với các lỗi nhóm E ở baseline (`rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv`, `rule_schema_header`). Không có hướng dẫn gây hại.                                                              | Body 4 dòng. `description` tiếng Việt: "DÙNG KHI CẦN tạo tệp cấu hình đầu ra hoặc tuân thủ các quy tắc định dạng/metadata nghiêm ngặt trong đề bài." |
| comprehensive-bug-fixing-and-documentation | Tổng quát — nói về type hints, không sửa test gốc, viết regression tests, cập nhật changelog. Không nêu tên hàm hay lỗi cụ thể.     | Đúng. Khớp với `rule_type_hints`, `rule_regression_tests`, `rule_changelog`, `tests_not_modified` ở `code-learn`. Không có hướng dẫn gây hại.                                                                         | Body 4 dòng. `description` tiếng Việt: "DÙNG KHI CẦN sửa lỗi mã nguồn, thêm bài kiểm tra hồi quy và cập nhật nhật ký thay đổi (changelog)."          |
| thorough-data-cleaning-and-validation      | Tổng quát — nói về xử lý giá trị thiếu/ngoại lai, trùng lặp, chuẩn hóa text, sắp xếp output. Không nêu tên cột hay file cụ thể.     | Đúng một phần. Có 1 lỗi nhỏ: dòng 1 nói "giữ lại dòng đầu tiên" — nhưng ở `data-learn`, quy tắc là giữ **một** dòng mỗi `order_id`, không nhất thiết là dòng đầu tiên. Không gây hại nhưng không chính xác tuyệt đối. | Body 4 dòng. `description` tiếng Việt: "DÙNG KHI CẦN xử lý, làm sạch dữ liệu thô (CSV, log) và tính toán các chỉ số thống kê."                       |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
| Task                              | baseline | subagents | skills-auto |
| --------------------------------- | -------- | --------- | ----------- |
| code-learn                        | 2/10     | 5/10      | 0/10        |
| data-learn                        | 4/8      | 4/8       | 0/8         |
| logs-learn                        | 6/9      | 6/9       | 6/9         |
| code-eval                         | 0/11     | 0/11      | 0/11        |
| data-eval                         | 0/9      | 0/9       | 0/9         |
| logs-eval                         | 0/10     | 0/10      | 0/10        |
| **Mean score - learning tasks**   | 0.46     | 0.56      | 0.22        |
| **Mean score - evaluation tasks** | 0.00     | 0.00      | 0.00        |
| **Mean tokens per run**           | 373,346  | 2,704,127 | 205,281     |
| **Runs that read a skill**        | 0/6      | 0/6       | 0/6         |



condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      0/18         0/12         187,032      0/3
baseline      learn    12/18         0/9          559,660      0/3
subagents     eval      0/18         0/12       4,484,190      0/3
subagents     learn    15/18         0/9          924,064      0/3
skills-auto   eval      0/18         0/12         207,589      0/3
skills-auto   learn     6/18         0/9          202,973      0/3
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
   subagents cải thiện điểm tác vụ học (0.46 → 0.56), nhờ code-learn tăng từ 2/10 lên 5/10. skills-auto giảm điểm học (0.46 → 0.22) — code-learn và data-learn đều về 0/… Không điều kiện nào cải thiện điểm tác vụ đánh giá (đều 0.00). Không có điều kiện nào "cải thiện học nhưng không cải thiện đánh giá" — ngược lại, skills-auto giảm cả hai, dấu hiệu skill không được dùng nhưng SKILLS_NOTE vẫn gây ảnh hưởng tiêu cực lên prompt

2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
   Check kỹ thuật: subagents 15/18 > baseline 12/18 > skills-auto 6/18. Check quy ước (rule\_\*): 0/9 ở mọi điều kiện — skill không giúp check quy ước mới nào, vì skills_read = 0 trên tất cả các lần chạy. Đây là bằng chứng phủ định cho H2

3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
   logs-learn đạt 6/9 ở cả ba điều kiện — tác tử xử lý được format log phức tạp bất kể skill, nhờ BASE_PROMPT đã đủ. data-learn đạt 4/8 ở baseline và subagents nhưng 0/8 ở skills-auto — nghi ngờ skill thorough-data-cleaning-and-validation chứa hướng dẫn gây hại ("giữ lại dòng đầu tiên"), nhưng vì skills_read = 0, cần xem trace.md để xác định nguyên nhân thực tế

4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
   subagents tốn trung bình 2.704.127 token/lần — 7.2× baseline (373.346). skills-auto rẻ nhất (205.281). Theo điểm trên mỗi token: baseline hiệu quả nhất trên tác vụ học; subagents đắt gấp 7× nhưng chỉ tăng +0.10 điểm học — không đáng chi phí trong thí nghiệm này. Đa tác tử không hiệu quả về chi phí

5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
   Không có rò rỉ (skill không nhắc eval markers; validate_skill đã chặn). Không có bằng chứng quá khớp vì skills_read = 0 — tác tử không đọc skill nên không thể áp dụng. Ngược lại, skills-auto giảm điểm học, nghi ngờ SKILLS_NOTE thêm vào prompt gây phân tâm mà không có skill nào được đọc

6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?
   Không có số liệu so sánh cùng bộ skill trước/sau đóng băng (mỗi cấu hình chỉ chạy một lần). Chênh lệch giữa các điều kiện (0.46 vs 0.56 vs 0.22) có thể nằm trong nhiễu mô hình — cần ít nhất 2–3 lần chạy mỗi cấu hình để kết luận chắc chắn

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Mỗi cấu hình chỉ chạy một lần — không đủ để tách tín hiệu khỏi nhiễu mô hình. Chênh lệch 0.46 vs 0.56 có thể không có ý nghĩa thống kê
2. Chỉ 3 tác vụ mỗi vai trò — mẫu nhỏ, một tác vụ thay đổi lớn (như code-learn 2/10 → 5/10) chi phối toàn bộ trung bình
3. skills_read = 0 trên mọi điều kiện — không thể kết luận về tác động của skill lên hành vi tác tử; kết quả skills-auto giảm điểm có thể do SKILLS_NOTE thêm vào prompt mà không có skill nào được đọc
4. Chỉ một mô hình (gemini-3.5-flash-lite) — kết quả không khái quát cho mô hình mạnh hơn
5. Hai test test_02_agent.py fail trên Windows do lệnh Unix (which, cat, ls); môi trường khác có thể cho kết quả khác

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.
> subagents cải thiện nhẹ điểm tác vụ học (0.46 → 0.56) nhưng tốn 7.2× token — không đáng chi phí. skills-auto giảm điểm học (0.46 → 0.22) và không cải thiện điểm đánh giá; skills_read = 0 cho thấy skill không được tác tử sử dụng, nên đây không phải bằng chứng chống lại self-evolving mà là bằng chứng về vấn đề kích hoạt skill. Không điều kiện nào cải thiện điểm tác vụ đánh giá (đều 0.00). Đề xuất: chạy lại mỗi cấu hình 3 lần, cải thiện description của skill (viết tiếng Anh, mở rộng tình huống kích hoạt) và kiểm tra vì sao skills_read = 0

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  pytest tests/test_02_agent.py
  pytest tests/test_03_runner.py
  pytest tests/test_04_curator.py
  python -m lab.runner --condition baseline --tasks learn
  python -m lab.runner --condition baseline --tasks eval
  python -m lab.runner --condition subagents --tasks learn
  python -m lab.runner --condition subagents --tasks eval
  python -m lab.runner --condition skills-auto --tasks all
  python -m lab.curator
  python scripts/check_breakdown.py
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
