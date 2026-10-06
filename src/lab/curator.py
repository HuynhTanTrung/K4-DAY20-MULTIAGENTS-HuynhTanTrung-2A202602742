"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file."""
    from .model import make_model
    from .tasks import ROOT

    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    out_dir = Path(out_dir)

    # 1. Thu thập các lần chạy tác vụ học
    runs = []
    for run_json in sorted(Path(results_dir, source_condition).glob("*/run.json")):
        try:
            r = json.loads(run_json.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("role") != "learn":
            continue
        trace_path = run_json.parent / "trace.md"
        trace = ""
        if trace_path.exists():
            trace = trace_path.read_text(encoding="utf-8", errors="replace")[-6000:]
        failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed")]
        runs.append({"task": r.get("task"), "failed": failed, "trace": trace})

    if not any(run["failed"] for run in runs):
        print("[curator] không có check thất bại ở tác vụ học; bỏ qua.")
        return []

    # 2. Dựng prompt
    blocks = []
    for run in runs:
        if not run["failed"]:
            continue
        lines = [f"TASK: {run['task']}", "FAILED CHECKS:"]
        for name, detail in run["failed"]:
            lines.append(f"- {name}: {detail}")
        if run["trace"]:
            lines.append("TRACE (tail):")
            lines.append(run["trace"])
        blocks.append("\n".join(lines))

    prompt = (
        "Bạn viết SKILL cho một tác tử lập trình và phân tích dữ liệu.\n"
        "Dưới đây là các check thất bại (tên và nhận xét của bot đánh giá) và vết của các lần chạy.\n"
        "Hãy tìm các lỗi QUY TRÌNH chung (không phải đáp án cụ thể) và viết tối đa "
        f"{max_skills} skill ngắn giúp tránh các lỗi đó trên tác vụ MỚI cùng loại.\n\n"
        "Quy tắc:\n"
        "- Skill phải tổng quát: không nêu id tác vụ, không nêu tên tệp riêng của một tác vụ, không nêu đáp án hay con số.\n"
        "- Mỗi skill có frontmatter YAML gồm `name` (chữ thường, gạch ngang) và `description` (một câu: DÙNG KHI NÀO),\n"
        "  sau đó tối đa 40 dòng chỉ dẫn mệnh lệnh (danh sách kiểm tra - checklist - hoạt động tốt).\n"
        "- Định dạng đầu ra, đúng từng ký tự:\n"
        "=== SKILL: <name> ===\n"
        "---\n"
        "name: <name>\n"
        "description: <khi nào dùng>\n"
        "---\n"
        "<nội dung>\n"
        "=== END ===\n\n"
        + "\n\n".join(blocks)
    )

    # 3. Gọi mô hình
    if model is None:
        model = make_model()
    raw = model.invoke(prompt).content
    if isinstance(raw, str):
        reply = raw
    elif isinstance(raw, list):
        # content blocks: ghép tất cả block có 'text'
        reply = "\n".join(
            block.get("text", "") for block in raw
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        reply = str(raw)

    # 4. Parse, validate, ghi file
    written = []
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            print(f"[curator] bỏ qua skill {name!r}: {problems}")
            continue
        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
        written.append(skill_dir / "SKILL.md")

    return written