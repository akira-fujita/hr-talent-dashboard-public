# 公開リポジトリ同期セットアップガイド

## 🎯 目的

`gip-japan/hr-talent-dashboard` (プライベート) → `akira-fujita/hr-talent-dashboard-public` (パブリック) への効率的な同期

## 🚀 セットアップ方法

### 方法1: GitHub Actions (完全自動化)

#### 1. GitHub Personal Access Token作成

1. [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. "Generate new token (classic)" をクリック
3. 設定:
   - **Note**: `hr-dashboard-public-sync`
   - **Expiration**: `No expiration` or 長期間
   - **Scopes**: `repo` (full control)
4. トークンをコピー（後で使用）

#### 2. メインリポジトリでSecret設定

1. `gip-japan/hr-talent-dashboard` → Settings → Secrets and variables → Actions
2. "New repository secret" をクリック
3. 追加:
   - **Name**: `PUBLIC_REPO_TOKEN`
   - **Value**: 上記で作成したPersonal Access Token

#### 3. 自動同期の動作

- **mainブランチ**または**demoブランチ**にプッシュ
- **手動実行**: Actions タブから "Sync to Public Repository" を実行
- **タグプッシュ**: `v1.0.0` などのタグでリリースも作成

### 方法2: 手動スクリプト実行

#### セットアップ

```bash
# Git エイリアス設定
./setup-git-aliases.sh
```

#### 使用方法

```bash
# 基本的な同期
./sync-to-public.sh

# または Git エイリアス使用
git sync-public

# 開発フロー (コミット→同期オプション)
git dev-commit "新機能を追加"

# プッシュと同期をセット
git push-and-sync
```

### 方法3: VSCode統合 (推奨)

#### 1. VSCode Tasks設定

`.vscode/tasks.json`に追加：

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Sync to Public Repository",
            "type": "shell",
            "command": "./sync-to-public.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "options": {
                "cwd": "${workspaceFolder}"
            }
        }
    ]
}
```

#### 2. 使用方法

- `Ctrl+Shift+P` → "Tasks: Run Task" → "Sync to Public Repository"
- またはコマンドパレットで "sync" と入力

## 🔄 推奨開発フロー

### 日常の開発

1. **メインリポジトリで開発**
```bash
cd /Users/akira.fujita/Documents/GitHub/hr-talent-dashboard
# 通常の開発作業
git add .
git commit -m "新機能追加"
git push origin main
```

2. **公開リポジトリに同期** (以下から選択)
```bash
# 方法A: 手動スクリプト
./sync-to-public.sh

# 方法B: Git エイリアス
git sync-public

# 方法C: GitHub Actions (自動)
# プッシュ後、自動で同期される
```

### 大きな変更・リリース時

1. **機能ブランチで開発**
```bash
git checkout -b feature/new-functionality
# 開発作業
git commit -m "大きな機能を追加"
```

2. **メインブランチにマージ**
```bash
git checkout main
git merge feature/new-functionality
git push origin main
```

3. **タグ付きリリース**
```bash
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
# GitHub Actionsが自動でリリースを作成
```

## 🔒 除外ファイル

以下のファイルは公開リポジトリに同期されません：

- `.streamlit/secrets.toml` (機密情報)
- `venv/` (仮想環境)
- `__pycache__/` (キャッシュ)
- `.DS_Store` (macOS)
- `notion_import/` (プライベートデータ)
- `sync-to-public.sh` (同期スクリプト自体)

## 🔧 トラブルシューティング

### 同期が失敗する場合

1. **権限確認**:
```bash
# Personal Access Tokenの確認
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

2. **公開リポジトリの状態確認**:
```bash
cd ../hr-talent-dashboard-public-temp
git status
git log --oneline -5
```

3. **手動での強制同期**:
```bash
# 公開リポジトリをリセット
cd ../hr-talent-dashboard-public-temp
git fetch origin
git reset --hard origin/main

# 再同期
cd ../hr-talent-dashboard
./sync-to-public.sh
```

## 📊 同期確認方法

1. **GitHub**: コミット履歴が両リポジトリで同期されているか確認
2. **Streamlit Cloud**: デプロイが自動で更新されるか確認
3. **デモサイト**: 機能が正常に動作するか確認