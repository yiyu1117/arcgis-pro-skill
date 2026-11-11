# 核对 SKILL.md「工具签名速查」章节中的 arcpy 调用
# 用法: "{python}" verify_sigs.py
# 返回码: 0 = 全部调用都能在 arcpy 中找到; 1 = 存在找不到的调用 / 找不到速查表章节
import inspect
import re
import sys
from pathlib import Path

import arcpy

SKILL = Path(__file__).with_name("SKILL.md")
SECTION_START = "## 工具签名速查"
SECTION_END = "## 错误处理"
CALL_RE = re.compile(r"arcpy\.([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(")

# 非工具调用：辅助类，不参与工具签名核对
SKIP = {
    ("sa", "RemapValue"),
}


def signature_text(fn) -> str:
    """优先用 inspect.signature；失败时回退到 doc 的签名或参数行。"""
    try:
        sig = str(inspect.signature(fn))
        if sig not in ("(*args, **kwargs)", "()"):
            return sig
    except (TypeError, ValueError):
        pass

    lines = (fn.__doc__ or "").strip().splitlines()
    if not lines:
        return "(无 doc)"
    first = lines[0].strip()
    params = [line.strip() for line in lines if line.strip().startswith(":param")]
    if params:
        return f"{first} | {'; '.join(params)}"
    return first


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = SKILL.read_text(encoding="utf-8")
    start = text.find(SECTION_START)
    end = text.find(SECTION_END, start + 1) if start != -1 else -1
    if start == -1 or end == -1:
        print(f"找不到「{SECTION_START}」到「{SECTION_END}」章节")
        return 1

    section = text[start:end]
    calls = []
    seen = set()
    for match in CALL_RE.finditer(section):
        key = (match.group(1), match.group(2))
        if key in SKIP or key in seen:
            continue
        seen.add(key)
        calls.append(key)

    print(f"核对 {SKILL.name} 速查表：共 {len(calls)} 个 arcpy 调用\n")

    missing = []
    for module, func in calls:
        mod = getattr(arcpy, module, None)
        fn = getattr(mod, func, None) if mod is not None else None
        if fn is None:
            print(f"[MISSING] arcpy.{module}.{func}")
            missing.append(f"arcpy.{module}.{func}")
            continue
        print(f"arcpy.{module}.{func}: {signature_text(fn)}")

    print()
    if missing:
        print(f"失败：{len(missing)} 个调用在 arcpy 中不存在：")
        for item in missing:
            print(f"  - {item}")
        return 1

    print("全部调用均可解析。请对照上面的真实签名，人工核对 SKILL.md 中的参数名与顺序。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
