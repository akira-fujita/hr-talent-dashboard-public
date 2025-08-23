# HR Talent Dashboard - Streamlit Cloud デプロイガイド

## 🚀 デプロイ手順

### 1. GitHubリポジトリの準備
1. このプロジェクトをGitHubにプッシュ
2. リポジトリをPublicに設定（またはStreamlit CloudからアクセスできるようにPrivate設定）

### 2. Streamlit Cloudでのデプロイ
1. [Streamlit Cloud](https://streamlit.io/cloud)にアクセス
2. GitHubアカウントでサインイン
3. "New app"をクリック
4. 以下の情報を入力：
   - Repository: `hr-talent-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
5. "Deploy"をクリック

### 3. 環境変数の設定（不要）
**注意**: 現在のバージョンはデモ版としてサンプルデータのみで動作するため、環境変数の設定は不要です。

## 📋 現在の設定

### デモ版の特徴
- データベース接続: **無効化済み**
- データソース: **サンプルデータのみ**
- 認証: **不要**

### 利用可能な機能
- ✅ コンタクト管理（50名のサンプルデータ）
- ✅ 案件管理（10件のサンプル案件）
- ✅ データインポート（メモリ上でのみ処理）
- ✅ マスタ管理（サンプルマスタデータ）

### 非表示機能
- ❌ ダッシュボード
- ❌ DB仕様書

## 🔧 カスタマイズ

### 本番環境への切り替え
本番環境で使用する場合は、以下の変更が必要です：

1. `app.py`の53行目を変更：
```python
# デモ版
supabase = None  # init_supabase()

# 本番版
supabase = init_supabase()
```

2. Streamlit Cloudで環境変数を設定：
   - `SUPABASE_URL`: SupabaseプロジェクトのURL
   - `SUPABASE_ANON_KEY`: Supabaseの匿名キー

3. メニューの復元（必要に応じて）：
```python
pages = {
    "🏠 ダッシュボード": "dashboard",
    "👥 コンタクト管理": "contacts",
    "🎯 案件管理": "projects",
    "📥 データインポート": "import",
    "⚙️ マスタ管理": "masters",
    "📋 DB仕様書": "specifications"
}
```

## 📱 アクセス方法
デプロイ完了後、以下のURLでアクセスできます：
```
https://[your-app-name].streamlit.app
```

## 🆘 トラブルシューティング

### よくある問題と解決方法

1. **デプロイが失敗する**
   - `requirements.txt`が正しいか確認
   - Pythonバージョンが3.8以上か確認

2. **アプリが起動しない**
   - `app.py`がリポジトリのルートにあるか確認
   - インポートエラーがないか確認

3. **データが表示されない**
   - ブラウザのキャッシュをクリア
   - ページをリロード

## 📝 注意事項
- このデモ版はサンプルデータのみで動作します
- データは永続化されません（リロードで初期化）
- 同時接続数には制限があります（Streamlit Cloudの無料プラン）

## 🔗 関連リンク
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [GitHub Repository](https://github.com/your-username/hr-talent-dashboard)