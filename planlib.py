#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计划库管理脚本（商业计划书级）。
- plans.json       : 规范数据源（计划对象数组，含市场/投入产出/竞品/挑战/AI初评等）
- plans-data.js    : 由 plans.json 生成的 window.PLANS = [...]（HTML 通过 <script> 加载）
- 头脑风暴计划库.md : 人类可读日志

字段（商业计划书级）：
  positioning 一句话定位 | problem 痛点/机会 | solution 产品与功能(PM+AI视角)
  market 目标市场与受众(类型/人群+规模估算) | model 商业模式与变现
  investment 预期投入(时间/资金/资源) | revenue 预期收益(区间/周期)
  competition 现有市场与竞品 | challenges 关键挑战与风险 | compliance 合规边界
  roadmap 进度计划 | ai_feasibility AI初评可行性(1-5) | ai_priority AI初评优先级(1-5)
  ai_recommend AI初步建议

用法：
  python3 planlib.py init
  python3 planlib.py add <batch.json>     # batch.json: 富含上述字段的对象数组(无需id/batch/created)
"""
import json, sys, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PLANS_JSON = os.path.join(BASE, "plans.json")
PLANS_JS   = os.path.join(BASE, "plans-data.js")
MD_FILE    = os.path.join(BASE, "头脑风暴计划库.md")

ALLOWED_CATEGORIES = [
    "专业·环保AI", "双碳·咨询", "内容·写作", "心理·人文",
    "金融·投资", "社群·内向者", "产品·工具", "学术·IP",
    "投资·理财", "其他·跨界",
]

RICH_FIELDS = ["positioning","problem","solution","market","model","investment",
               "revenue","competition","challenges","compliance","roadmap",
               "ai_feasibility","ai_priority","ai_recommend"]

MD_SECTIONS = [
    ("一句话定位", "positioning"),
    ("痛点与机会", "problem"),
    ("产品与功能（PM+AI视角）", "solution"),
    ("目标市场与受众", "market"),
    ("商业模式与变现", "model"),
    ("预期投入", "investment"),
    ("预期收益", "revenue"),
    ("现有市场与竞品", "competition"),
    ("关键挑战与风险", "challenges"),
    ("合规边界", "compliance"),
    ("进度计划", "roadmap"),
    ("AI初步建议", "ai_recommend"),
]


def load_plans():
    if not os.path.exists(PLANS_JSON):
        return []
    with open(PLANS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_plans(plans):
    with open(PLANS_JSON, "w", encoding="utf-8") as f:
        json.dump(plans, f, ensure_ascii=False, indent=2)


def next_id(plans):
    max_n = 0
    for p in plans:
        try:
            max_n = max(max_n, int(str(p.get("id", "P0")).replace("P", "")))
        except Exception:
            pass
    return f"P{max_n + 1:04d}"


def next_batch(plans):
    return max([p.get("batch", 0) for p in plans], default=-1) + 1


def gen_data_js(plans):
    with open(PLANS_JS, "w", encoding="utf-8") as f:
        f.write("// 由 planlib.py 自动生成，请勿手改。用户评分/备注存于浏览器 localStorage。\n")
        f.write("window.PLANS = ")
        f.write(json.dumps(plans, ensure_ascii=False, indent=2))
        f.write(";\n")


def gen_markdown(plans):
    L = []
    L.append("# 头脑风暴计划库 · AI 财富自由（商业计划书级）\n")
    L.append("> 由 `planlib.py` 依据 `plans.json` 自动重建。每条计划含：定位/痛点/产品功能/市场/商业模式/投入/收益/竞品/挑战/合规/进度/AI初评。\n")
    L.append("> 交互式管理页面见 `index.html`（评分、备注、分类筛选均在本地浏览器完成）。\n")
    cats = {}
    for p in plans:
        cats[p.get("category", "其他·跨界")] = cats.get(p.get("category"), 0) + 1
    L.append(f"\n**总计 {len(plans)} 条计划**，分类分布：")
    for c, n in cats.items():
        L.append(f"- {c}：{n}")
    L.append("")
    for p in plans:
        L.append(f"## 第{p.get('batch')}批 · {p.get('title')} 〔{p.get('id')}〕\n")
        L.append(f"- **分类**：{p.get('category','')} ｜ **创建**：{p.get('created','')} ｜ **AI初评**：可行性 {p.get('ai_feasibility','-')}/5 · 优先级 {p.get('ai_priority','-')}/5\n")
        for label, key in MD_SECTIONS:
            L.append(f"- **{label}**：{p.get(key,'')}\n")
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def plan_block_md(p):
    L = [f"### {p['id']} ｜ {p['title']}"]
    L.append(f"- **分类**：{p.get('category','')} ｜ **AI初评**：可行性 {p.get('ai_feasibility','-')}/5 · 优先级 {p.get('ai_priority','-')}/5")
    for label, key in MD_SECTIONS:
        L.append(f"- **{label}**：{p.get(key,'')}")
    return "\n".join(L) + "\n"


def append_markdown(batch, added):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:00")
    header = f"\n---\n\n## 第{batch}批 · 自动头脑风暴（{ts}）\n"
    body = "\n".join(plan_block_md(p) for p in added)
    with open(MD_FILE, "a", encoding="utf-8") as f:
        f.write(header + "\n" + body + "\n")


def cmd_init():
    plans = load_plans()
    gen_data_js(plans)
    gen_markdown(plans)
    print(f"init done: {len(plans)} plans -> {PLANS_JS} + {MD_FILE}")


def cmd_add(batchfile):
    with open(batchfile, "r", encoding="utf-8") as f:
        new_raw = json.load(f)
    if not isinstance(new_raw, list):
        new_raw = [new_raw]
    plans = load_plans()
    batch = next_batch(plans)
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    added = []
    for item in new_raw:
        cat = item.get("category", "其他·跨界")
        if cat not in ALLOWED_CATEGORIES:
            cat = "其他·跨界"
        p = {
            "id": next_id(plans + added),
            "batch": batch,
            "category": cat,
            "title": item.get("title", "未命名计划"),
            "created": ts,
        }
        for k in RICH_FIELDS:
            p[k] = item.get(k, "")
        # 数值字段规范化
        try:
            p["ai_feasibility"] = int(p["ai_feasibility"])
        except Exception:
            p["ai_feasibility"] = 0
        try:
            p["ai_priority"] = int(p["ai_priority"])
        except Exception:
            p["ai_priority"] = 0
        added.append(p)
    plans.extend(added)
    save_plans(plans)
    gen_data_js(plans)
    append_markdown(batch, added)
    print(f"add done: batch #{batch}, +{len(added)} plans, total {len(plans)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: planlib.py init | add <batch.json>")
        sys.exit(1)
    if sys.argv[1] == "init":
        cmd_init()
    elif sys.argv[1] == "add":
        if len(sys.argv) < 3:
            print("add needs <batch.json>"); sys.exit(1)
        cmd_add(sys.argv[2])
    else:
        print("unknown command:", sys.argv[1]); sys.exit(1)
