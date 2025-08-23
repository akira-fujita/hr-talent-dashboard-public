#!/bin/bash
# パブリックリポジトリセットアップスクリプト

echo "🚀 HR Talent Dashboard - パブリックリポジトリセットアップ"
echo "=================================================="

# ユーザー情報の取得
read -p "GitHubユーザー名を入力してください: " GITHUB_USERNAME
read -p "新しいリポジトリ名を入力してください (デフォルト: hr-talent-dashboard-public): " REPO_NAME
REPO_NAME=${REPO_NAME:-hr-talent-dashboard-public}

echo ""
echo "📋 設定内容:"
echo "  GitHub Username: $GITHUB_USERNAME"
echo "  Repository Name: $REPO_NAME"
echo "  Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

read -p "この設定で続行しますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ セットアップを中止しました"
    exit 1
fi

echo "🔧 パブリックリポジトリの準備中..."

# 新しいディレクトリを作成
TEMP_DIR="../${REPO_NAME}-temp"
cp -r . "$TEMP_DIR"
cd "$TEMP_DIR"

# 不要なファイルを削除
echo "🧹 不要なファイルを削除中..."
rm -rf .git
rm -rf venv/
rm -rf __pycache__/
rm -rf .DS_Store
rm -rf notion_import/
rm -f setup_public_repo.sh

# Gitリポジトリを初期化
echo "📦 新しいGitリポジトリを初期化中..."
git init
git add .
git commit -m "Initial commit: HR Talent Dashboard (Public Demo Version)

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# リモートリポジトリを追加
echo "🔗 リモートリポジトリを追加中..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "📝 次のステップ:"
echo "1. GitHubで新しいパブリックリポジトリを作成:"
echo "   https://github.com/new"
echo "   Repository name: $REPO_NAME"
echo "   Visibility: Public"
echo ""
echo "2. 以下のコマンドでプッシュ:"
echo "   cd $TEMP_DIR"
echo "   git push -u origin main"
echo ""
echo "3. Streamlit Cloudでデプロイ:"
echo "   https://share.streamlit.io/"
echo "   Repository: $GITHUB_USERNAME/$REPO_NAME"
echo "   Main file: app.py"
echo ""
echo "🌟 完了後、README.mdのデモURLを更新してください"