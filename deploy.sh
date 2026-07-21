#!/bin/bash
# 部署到 GitHub Pages（需先 `gh auth login`）。
# 说明：免费 GitHub 账户仅支持“公开仓库”的 Pages。本脚本创建公开仓库并启用 Pages，
# 得到「任何人可访问」的渲染页（链接公开）。若需私有渲染页，请先升级 GitHub Pro。
set -e
REPO="ai-wealth-plans"
USER=$(gh api user --jq .login)
echo "账号：$USER"
gh repo create "$REPO" --public --description "AI 财富自由计划 · 计划库" 2>/dev/null || echo "仓库已存在，继续"
git init -q 2>/dev/null || true
git add -A
git commit -q -m "init: AI财富自由计划" 2>/dev/null || echo "无可提交变动"
git branch -M main 2>/dev/null || true
REMOTE="https://github.com/$USER/$REPO.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main
gh repo edit "$REPO" --visibility public
gh api -X POST repos/$USER/$REPO/pages -f source='{"branch":"main","path":"/"}' \
  && echo "✅ Pages 已启用：https://$USER.github.io/$REPO/" \
  || echo "⚠️ Pages 启用失败，可到仓库 Settings → Pages 手动选择 main 分支根目录"
