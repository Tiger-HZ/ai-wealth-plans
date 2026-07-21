#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日推送：汇总当天新增计划，按分类统计并给出关注建议，追加到 每日推送.md。"""
import json, os, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PLANS_JSON = os.path.join(BASE, "plans.json")
MD = os.path.join(BASE, "每日推送.md")
TZ = "Asia/Shanghai"

def main():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(PLANS_JSON, encoding="utf-8") as f:
        plans = json.load(f)
    new = [p for p in plans if p.get("created", "").startswith(today)]
    lines = []
    lines.append(f"\n---\n\n## 📅 {today} 每日推送\n")
    if not new:
        lines.append("今日暂无新增计划（头脑风暴任务仍在运行，明天见）。\n")
        with open(MD, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("daily digest: no new plans")
        return

    by_cat = {}
    for p in new:
        by_cat.setdefault(p.get("category", "其他·跨界"), []).append(p)
    lines.append(f"今日新增 **{len(new)}** 条计划。分类分布：")
    for c, ps in by_cat.items():
        lines.append(f"- {c}：{len(ps)} 条")

    lines.append("\n### 今日新增清单")
    for p in new:
        lines.append(f"- `{p['id']}` 〔{p['category']}〕 **{p['title']}** — {p.get('goal','')[:60]}")

    # 关注建议：从不同分类各取1条，最多3条
    picks = []
    seen = set()
    for c, ps in by_cat.items():
        if c not in seen:
            picks.append(ps[0]); seen.add(c)
        if len(picks) >= 3:
            break
    if picks:
        lines.append("\n### 💡 今日建议关注（跨分类抽样）")
        for p in picks:
            lines.append(f"- `{p['id']}` {p['title']}：{p.get('goal','')}")

    lines.append(f"\n> 打开 `index.html` 给它们打分与备注；完整计划见 `头脑风暴计划库.md`。")
    with open(MD, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"daily digest done: +{len(new)} plans -> {MD}")

if __name__ == "__main__":
    main()
