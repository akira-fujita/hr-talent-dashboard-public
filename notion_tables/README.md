# Notionテーブル用CSVファイル

このフォルダには、各テーブルの定義をNotion DatabaseとしてインポートできるCSVファイルが含まれています。

## 📂 ファイル一覧

### メインテーブル
- `target_companies_schema.csv` - 🏢 検索対象企業テーブル
- `contacts_schema.csv` - 👥 コンタクト情報テーブル  
- `projects_schema.csv` - 📂 プロジェクト情報テーブル

### マスターテーブル
- `departments_schema.csv` - 🏬 部署マスタテーブル
- `priority_levels_schema.csv` - ⭐ 優先度レベルテーブル
- `search_assignees_schema.csv` - 👤 検索担当者テーブル
- `approach_methods_schema.csv` - 📞 アプローチ手法テーブル

## 🔧 Notionでの使用方法

1. **新規Databaseを作成**
   - Notionページで `/database` と入力
   - 「New database - Table」を選択

2. **CSVファイルをインポート**
   - Database右上の「...」メニューから「Import」を選択
   - 対応するCSVファイルをアップロード

3. **カラムタイプの調整**（必要に応じて）
   - TEXT → Multi-line text
   - DATE → Date
   - JSONB → Text（JSONデータ用）

## 📋 各CSVファイルのカラム構成

すべてのCSVファイルには以下のカラムが含まれています：
- **カラム名**: データベースのフィールド名
- **データ型**: PostgreSQLでのデータ型
- **制約**: PRIMARY KEY, FOREIGN KEY, NOT NULL等
- **NULL許可**: YES/NO
- **デフォルト値**: デフォルト設定値
- **説明**: カラムの用途説明

## 💡 活用のヒント

- **テーブル関係の可視化**: NotionのRelation機能で外部キーを設定
- **フィルタリング**: データ型や制約でフィルタして分析
- **検索**: 特定のカラムや説明文での検索が可能
- **ビュー作成**: 用途別にビューを作成してテーブル設計を整理