#!/bin/bash
# 私有部署：将本目录发布为「仅你自己可见」的 GitHub Pages。
# 前置：已在终端执行 `gh auth login` 并完成授权。
set -e

REPO="ai-wealth-plans"
USER=$(gh api user --jq .login)
echo "当前 GitHub 账号：$USER"

# 1) 创建私有仓库（已存在则忽略）
gh repo create "$REPO" --private --description "AI 财富自由计划 · 私有计划库" 2>/dev/null || echo "仓库已存在，继续…"

# 2) 初始化并提交
git init -q 2>/dev/null || true
git add -A
git commit -q -m "init: AI财富自由计划私有库" 2>/dev/null || echo "无可提交变动"
git branch -M main 2>/dev/null || true

# 3) 关联远程并推送
REMOTE="git@github.com:$USER/$REPO.git"
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main

# 4) 确保仓库为私有 + 启用 Pages（私有仓库的 Pages 仅协作者可见 = 仅你可见）
gh repo edit "$REPO" --visibility private
gh api -X POST repos/$USER/$REPO/pages -f source='{"branch":"main","path":"/"}' \
  && echo "✅ 私有 Pages 已启用" \
  || echo "⚠️ Pages 启用失败，可到仓库 Settings → Pages 手动选择 main 分支根目录"

echo ""
echo "完成。你的私有页面地址（仅登录该 GitHub 账号可见）："
echo "  https://$USER.github.io/$REPO/"
echo "提示：评分与备注保存在你浏览器 localStorage，不会上传，刷新/换设备需用页面'导出/导入'。"
