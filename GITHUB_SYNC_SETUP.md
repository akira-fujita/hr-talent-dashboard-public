# GitHub同期セットアップガイド

## 問題: `fatal: could not read Password for 'https://github.com': No such device or address`

この問題は、GitHubのPersonal Access Token (PAT)が正しく設定されていないために発生します。

## 解決方法

### 1. Personal Access Token (PAT) を作成

1. GitHub にログイン → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" をクリック
3. 以下の権限を選択：
   - `repo` (フル権限)
   - `workflow` (GitHub Actions用)
4. トークンをコピー（再表示できないため注意）

### 2. ローカル環境での設定

以下のいずれかの方法を選択：

#### 方法A: 環境変数で設定
```bash
export GITHUB_TOKEN=your_personal_access_token_here
./sync-to-public.sh
```

#### 方法B: SSH認証に変更
```bash
cd /Users/akira.fujita/Documents/GitHub/hr-talent-dashboard-public-temp
git remote set-url origin git@github.com:akira-fujita/hr-talent-dashboard-public.git
```

#### 方法C: 認証情報を保存
```bash
git config --global credential.helper store
git push origin main  # 初回のみユーザー名とPATを入力
```

### 3. GitHub Actions での設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定：

- Secret name: `GITHUB_TOKEN`
- Secret value: 作成したPersonal Access Token

### 4. 確認方法

```bash
./sync-to-public.sh
```

正常に動作すれば以下が表示されます：
```
✅ GITHUB_TOKEN環境変数が設定されています
✅ プッシュ成功！
✅ 同期完了！
```

## トラブルシューティング

### Token権限不足
- `repo`権限が必要
- Organization の場合は `write:org` も必要

### SSH Key 未設定
方法Bを選択した場合、SSH Keyの設定が必要：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # GitHubに追加
```

### 2FA有効時
- パスワードの代わりにPersonal Access Tokenを使用
- GitHub Appトークンは使用不可（権限が異なるため）