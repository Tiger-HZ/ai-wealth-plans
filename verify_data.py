#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署前数据校验守卫。
任何向仓库推送计划数据前都必须先通过本脚本，失败则以非0退出，
从而阻止"坏数据/缺字段/JS语法错误"回灌到线上造成白屏或空列表。

校验项：
  1. plans-data.js 能被当作 JS 解析，且 window.PLANS 为数组；
  2. 每份计划都含 created 字段（排序依赖，缺失会运行时崩溃）；
  3. 每份计划含全部 DEEP_FIELDS 关键字段（允许为空串，但键必须存在）；
  4. ai_feasibility / ai_priority 为 1-5 整数；
  5. index.html 内联脚本通过 node --check（语法层面拦截白屏元凶）。
用法：
  python3 verify_data.py
退出码：0=通过，1=不通过（应中止推送）
"""
import json, re, sys, os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
PLANS_JS = os.path.join(BASE, "plans-data.js")
INDEX_HTML = os.path.join(BASE, "index.html")

try:
    import planlib
    DEEP_FIELDS = planlib.DEEP_FIELDS
except Exception:
    DEEP_FIELDS = ["positioning","executive","background","market","competition",
                   "product","ai_tech","model","financials","roadmap","team","risks",
                   "metrics","evaluation","sources","ai_feasibility","ai_priority","ai_recommend"]


def extract_plans():
    with open(PLANS_JS, encoding="utf-8") as f:
        t = f.read()
    m = re.search(r"window\.PLANS\s*=\s*(\[.*\])\s*;?\s*$", t, re.S)
    if not m:
        raise ValueError("plans-data.js 未找到 window.PLANS = [...]")
    return json.loads(m.group(1))


def check_inline_js():
    html = open(INDEX_HTML, encoding="utf-8").read()
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    if not scripts:
        raise ValueError("index.html 无内联脚本")
    s = scripts[-1]  # 主逻辑脚本
    import tempfile, os as _os
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
        tf.write(s); p = tf.name
    r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
    _os.unlink(p)
    if r.returncode != 0:
        raise ValueError("index.html 内联脚本语法错误: " + r.stderr.strip())
    return True


def main():
    errors = []
    try:
        plans = extract_plans()
    except Exception as e:
        print("❌ 数据解析失败:", e)
        return 1

    if not isinstance(plans, list) or len(plans) == 0:
        print("❌ 计划数据为空或非数组")
        return 1

    for i, p in enumerate(plans):
        pid = p.get("id", f"#{i}")
        if not p.get("created"):
            errors.append(f"{pid}: 缺少 created 字段（排序会运行时崩溃）")
        for k in DEEP_FIELDS:
            if k not in p:
                errors.append(f"{pid}: 缺少字段 {k}")
        try:
            af = int(p.get("ai_feasibility", 0)); ap = int(p.get("ai_priority", 0))
            if not (1 <= af <= 5): errors.append(f"{pid}: ai_feasibility={af} 超出1-5")
            if not (1 <= ap <= 5): errors.append(f"{pid}: ai_priority={ap} 超出1-5")
        except Exception:
            errors.append(f"{pid}: ai_feasibility/ai_priority 非整数")

    try:
        check_inline_js()
    except Exception as e:
        errors.append("页面JS: " + str(e))

    if errors:
        print(f"❌ 校验未通过，发现 {len(errors)} 个问题：")
        for e in errors[:30]:
            print("   -", e)
        return 1

    print(f"✅ 校验通过：{len(plans)} 份计划，字段完整，页面JS语法OK。可安全部署。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
