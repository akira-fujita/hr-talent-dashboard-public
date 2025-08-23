# パブリックリポジトリでのデプロイガイド

## 🚀 パブリック版リポジトリ作成手順

### 1. 新しいパブリックリポジトリの作成

1. **GitHubで新しいリポジトリを作成**:
   - Repository name: `hr-talent-dashboard-public` (または任意の名前)
   - Visibility: **Public** を選択
   - Initialize with README: チェックしない

2. **ローカルでリモートを追加**:
```bash
# 現在のディレクトリで新しいリモートを追加
git remote add public https://github.com/YOUR_USERNAME/hr-talent-dashboard-public.git

# または、新しいディレクトリにクローンして作業
git clone . ../hr-talent-dashboard-public
cd ../hr-talent-dashboard-public
git remote set-url origin https://github.com/YOUR_USERNAME/hr-talent-dashboard-public.git
```

### 2. 機密情報のチェック

パブリック公開前に以下を確認してください：

#### ✅ 安全に公開できるもの
- アプリケーションコード (`app.py`)
- 設定ファイル (`.streamlit/config.toml`)
- 依存関係 (`requirements.txt`)
- ドキュメント (README.md等)
- サンプルデータ生成コード

#### ❌ 公開してはいけないもの
- `.streamlit/secrets.toml` (既に.gitignoreで保護済み)
- 実際のデータベース接続情報
- APIキー・認証情報

### 3. パブリック版への調整

#### app.pyの調整 (必要に応じて)
```python
# デモモードの有効化
DEMO_MODE = True  # パブリック版では常にサンプルデータを使用

def init_supabase():
    try:
        if DEMO_MODE:
            return None  # サンプルデータのみ使用
        # ... 既存のコード
    except:
        return None
```

#### README.mdの更新
- デモ版であることを明記
- 実際のデータベース接続手順を追加

### 4. Streamlit Cloudでのデプロイ

1. **[Streamlit Cloud](https://share.streamlit.io/) にアクセス**
2. **"New app" をクリック**
3. **パブリックリポジトリを選択**:
   - Repository: `YOUR_USERNAME/hr-talent-dashboard-public`
   - Branch: `main`
   - Main file path: `app.py`
4. **環境変数設定 (Secrets タブ)**:
```toml
# Supabaseを使用する場合
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-supabase-anon-key"

# デモモードの場合は設定不要
```

### 5. デプロイ後の確認

- アプリが正常に起動することを確認
- サンプルデータが表示されることを確認
- 全ての機能が動作することを確認

## 📝 注意事項

1. **データベース接続**: パブリック版では実際のデータベースへの接続を避け、サンプルデータを使用することを推奨
2. **ライセンス**: 適切なライセンスファイルを追加
3. **セキュリティ**: 機密情報が含まれていないことを再度確認
4. **ドキュメント**: 使用方法やセットアップ手順を明確に記載

## 🔗 関連リンク

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [GitHub Public Repository Best Practices](https://docs.github.com/en/repositories)