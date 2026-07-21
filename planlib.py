#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计划库管理脚本（深度计划书级）。
字段（深度计划书级，单份目标 ≥5000 中文字）：
  positioning 一句话定位 | executive 执行摘要 | background 背景与机会(痛点)
  market 市场规模与受众(细分+数据+TAM/SAM/SOM) | competition 竞品与现有市场
  product 产品与功能详述(PM视角,模块/PRD) | ai_tech 技术与AI实现(AI专家视角)
  model 商业模式与变现(定价/单位经济) | financials 营收预测与投入
  roadmap 里程碑与路线图 | team 团队与资源 | risks 风险与合规
  metrics 关键成功指标 | evaluation AI评估与建议 | sources 数据来源/参考
  ai_feasibility AI初评可行性(1-5) | ai_priority AI初评优先级(1-5) | ai_recommend AI建议
用法：
  python3 planlib.py init
  python3 planlib.py add <batch.json>   # batch.json: 富含上述字段的对象数组(无需id/batch/created)
  python3 planlib.py check               # 统计每份字数，检查深度
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

DEEP_FIELDS = ["positioning","executive","background","market","competition","product",
               "ai_tech","model","financials","roadmap","team","risks","metrics",
               "evaluation","sources","ai_feasibility","ai_priority","ai_recommend"]

MD_SECTIONS = [
    ("一句话定位", "positioning"),
    ("执行摘要", "executive"),
    ("背景与机会（痛点）", "background"),
    ("市场规模与受众", "market"),
    ("竞品与现有市场", "competition"),
    ("产品与功能详述（PM视角）", "product"),
    ("技术与AI实现（AI专家视角）", "ai_tech"),
    ("商业模式与变现", "model"),
    ("营收预测与投入", "financials"),
    ("里程碑与路线图", "roadmap"),
    ("团队与资源", "team"),
    ("风险与合规", "risks"),
    ("关键成功指标", "metrics"),
    ("AI评估与建议", "evaluation"),
    ("数据来源/参考", "sources"),
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
    L.append("# 头脑风暴计划库 · AI 财富自由（深度计划书级）\n")
    L.append("> 由 `planlib.py` 依据 `plans.json` 自动重建。每条计划为完整商业计划书（定位/执行摘要/市场/竞品/产品/技术/商业模式/财务/路线图/风险/AI评估）。\n")
    L.append("> 交互式浅色页面见 `index.html`（点击计划弹出全文；评分、备注存于本地浏览器）。\n")
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
            L.append(f"\n### {label}\n{p.get(key,'')}\n")
    with open(MD_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def plan_block_md(p):
    L = [f"### {p['id']} ｜ {p['title']}",
         f"- **分类**：{p.get('category','')} ｜ **AI初评**：可行性 {p.get('ai_feasibility','-')}/5 · 优先级 {p.get('ai_priority','-')}/5"]
    for label, key in MD_SECTIONS:
        L.append(f"\n### {label}\n{p.get(key,'')}")
    return "\n".join(L) + "\n"


def append_markdown(batch, added):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:00")
    header = f"\n---\n\n## 第{batch}批 · 深度计划（{ts}）\n"
    body = "\n".join(plan_block_md(p) for p in added)
    with open(MD_FILE, "a", encoding="utf-8") as f:
        f.write(header + "\n" + body + "\n")


def char_count(p):
    return sum(len(str(p.get(k, ""))) for k in DEEP_FIELDS)


def cmd_init():
    plans = load_plans()
    gen_data_js(plans)
    gen_markdown(plans)
    print(f"init done: {len(plans)} plans -> {PLANS_JS} + {MD_FILE}")


def cmd_check():
    plans = load_plans()
    print(f"共 {len(plans)} 条；字数统计：")
    for p in plans:
        n = char_count(p)
        flag = "✅" if n >= 4000 else "⚠️浅"
        print(f"  {p.get('id')} {p.get('title')[:18]:<20} 约{n}字 {flag}")


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
        for k in DEEP_FIELDS:
            p[k] = item.get(k, "")
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
        print("usage: planlib.py init | add <batch.json> | check")
        sys.exit(1)
    if sys.argv[1] == "init":
        cmd_init()
    elif sys.argv[1] == "add":
        if len(sys.argv) < 3:
            print("add needs <batch.json>"); sys.exit(1)
        cmd_add(sys.argv[2])
    elif sys.argv[1] == "check":
        cmd_check()
    else:
        print("unknown command:", sys.argv[1]); sys.exit(1)
