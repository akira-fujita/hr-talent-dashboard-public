# HR Talent Dashboard 

## 🎯 プロジェクト概要

**HR人材コンタクト管理 & 案件管理システム (デモ版)**

このシステムは、HR業界における人材コンタクト情報と求人案件を効率的に管理し、
人材と案件のマッチングを支援するWebアプリケーションです。

> **📍 重要**: この版はデモ・学習目的のパブリックリポジトリです。実際のSupabaseデータベースに接続し、リアルタイムでデータ操作を体験できます。

### 🔗 データベース接続
- **データベース**: Supabase (PostgreSQL)
- **機能**: 完全なCRUD操作、リアルタイム更新
- **データ**: デモ用サンプルデータ（定期的にリセット）

## 🌐 デモサイト

[**📱 ライブデモを見る**](https://akira-fujita-test-hr-dashboard-app-2rwmjj.streamlit.app) *(Streamlit Cloudでホスト)*

*現在サンプルデータモードで動作中 - 全ての機能をお試しいただけます*

### 主な機能
- 📊 **ダッシュボード**: KPI表示、可視化分析
- 👥 **コンタクト管理**: 人材情報の一覧表示、検索、編集、削除
- 🎯 **案件管理**: 求人案件の管理、人材アサイン状況の追跡
- 📝 **新規登録**: コンタクト・案件情報の新規追加
- ⚙️ **マスタ管理**: 企業・部署・優先度・アプローチ手法の管理

### 技術スタック
- **フロントエンド**: Streamlit
- **バックエンド**: Python
- **データベース**: Supabase (PostgreSQL)
- **可視化**: Plotly

## 🗄️ データベース構造

### 📋 テーブル一覧
1. **companies** - 企業情報
2. **departments** - 部署情報
3. **contacts** - 人材コンタクト情報
4. **projects** - 求人案件情報
5. **project_assignments** - 案件・人材アサイン情報
6. **priority_levels** - 優先度マスタ
7. **search_assignees** - 検索担当者マスタ
8. **approach_methods** - アプローチ手法マスタ
9. **contact_approaches** - アプローチ履歴
10. **addresses** - 住所情報
11. **contacts_detail** - コンタクト詳細ビュー

## 🚀 セットアップ

### 前提条件
- Python 3.8以上
- Supabaseアカウント

### ローカル開発環境
```bash
# リポジトリクローン
git clone <repository-url>
cd hr-talent-dashboard

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージインストール
pip install -r requirements.txt

# Streamlitでアプリ起動
streamlit run app.py
```

### 環境設定
`.streamlit/secrets.toml`ファイルを作成し、Supabase接続情報を設定：
```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

## ☁️ Streamlit Cloudデプロイ

### 1. リポジトリの準備
- このリポジトリは既にStreamlit Cloud対応済みです
- `requirements.txt`, `.streamlit/config.toml`が設定済み

### 2. Streamlit Cloudでのデプロイ手順
1. [Streamlit Cloud](https://share.streamlit.io/) にアクセス
2. GitHubアカウントでサインイン
3. "New app" をクリック
4. リポジトリを選択: `hr-talent-dashboard`
5. ブランチを選択: `main` または `demo`
6. Main file path: `app.py`
7. "Deploy!" をクリック

### 3. 環境変数の設定
デプロイ後、アプリ設定画面の "Secrets" タブで以下を設定：
```toml
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

### 4. アプリの再起動
- 設定変更後、"Reboot app" でアプリを再起動
- 数分でアプリが利用可能になります

## 📊 データベース詳細

詳細なER図とテーブル仕様書については以下を参照：
- [ER図](database_er_diagram.md)
- データベース仕様書（アプリ内の「📋 DB仕様書」ページ）

## 🔄 最新の変更履歴

### v2.0 - 案件管理機能追加
- 案件管理テーブル（projects, project_assignments）の追加
- 部署管理テーブル（departments）の追加  
- 企業業種のENUM型対応（industry_type）
- 案件管理UIの実装
- データベース設計の正規化

### v1.0 - 基本システム
- コンタクト管理機能
- マスタデータ管理
- 複数アプローチ履歴対応
- 住所情報管理