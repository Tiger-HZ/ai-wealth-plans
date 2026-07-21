#!/bin/bash
# 私有部署到 GitHub（需先 `gh auth login`）。
# 重要：免费 GitHub 账户仅支持“公开仓库”的 Pages；私有仓库 Pages 需 GitHub Pro/Team。
# 因此本脚本把仓库设为私有并推送，作为「固定、私有、带版本历史」的计划数据源；
# 交互页面请在本地双击 index.html 打开（完全私有，评分存浏览器本地）。
set -e
REPO="ai-wealth-plans"
USER=$(gh api user --jq .login)
echo "账号：$USER"
gh repo create "$REPO" --private --description "AI 财富自由计划 · 私有计划库" 2>/dev/null || echo "仓库已存在，继续"
git init -q 2>/dev/null || true
git add -A
git commit -q -m "init: AI财富自由计划私有库" 2>/dev/null || echo "无可提交变动"
git branch -M main 2>/dev/null || true
REMOTE="https://github.com/$USER/$REPO.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main
gh repo edit "$REPO" --visibility private
echo "✅ 私有仓库已推送：https://github.com/$USER/$REPO"
echo "交互页面：本地双击 index.html（评分/备注仅存你浏览器，不外传）。"
echo ""
echo "想要『渲染后的固定网页』二选一（需你确认）："
echo "  A. 私有渲染页：升级 GitHub Pro 后执行"
echo "     gh api -X POST repos/$USER/$REPO/pages -f source='{\"branch\":\"main\",\"path\":\"/\"}'"
echo "  B. 公开渲染页：将下方 private 改为 false 后再跑本脚本（链接任何人可见）"
