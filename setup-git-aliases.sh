#!/bin/bash
# Git エイリアス設定スクリプト

echo "⚙️ Git エイリアスを設定中..."

# 公開リポジトリ同期用のエイリアス
git config alias.sync-public '!f() { 
    echo "🔄 公開リポジトリに同期中..."; 
    bash ./sync-to-public.sh; 
}; f'

# 開発フロー用のエイリアス
git config alias.dev-commit '!f() { 
    git add . && 
    git commit -m "$1" && 
    echo "✅ コミット完了。公開リポジトリに同期しますか？" && 
    read -p "同期する (y/N): " -n 1 -r && 
    echo && 
    if [[ $REPLY =~ ^[Yy]$ ]]; then 
        git sync-public; 
    fi; 
}; f'

# プッシュと同期のセット
git config alias.push-and-sync '!f() { 
    git push origin $(git branch --show-current) && 
    git sync-public; 
}; f'

echo "✅ Git エイリアス設定完了！"
echo ""
echo "📋 使用可能なコマンド:"
echo "  git sync-public     - 公開リポジトリに同期"
echo "  git dev-commit 'メッセージ' - コミット後に同期オプション"
echo "  git push-and-sync   - プッシュ後に自動同期"
echo ""
echo "例:"
echo "  git dev-commit 'Add new feature'"
echo "  git push-and-sync"