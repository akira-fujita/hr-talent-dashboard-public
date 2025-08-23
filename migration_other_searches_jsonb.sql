-- その他検索用のJSONBカラムを追加（最大3回分）
-- 各検索には日付と検索手法を記録

-- 1. 新しいJSONBカラムを追加
ALTER TABLE companies ADD COLUMN other_searches JSONB;

-- 2. カラムにコメントを追加
COMMENT ON COLUMN companies.other_searches IS 'その他検索履歴（最大3回分）- JSON形式: [{"date": "YYYY-MM-DD", "method": "検索手法", "search_number": 1-3}]';

-- 3. サンプルデータの説明（コメント）
-- 使用例:
-- [
--   {"date": "2024-02-01", "method": "Wantedly検索", "search_number": 1},
--   {"date": "2024-02-05", "method": "Green検索", "search_number": 2},
--   {"date": "2024-02-10", "method": "ビズリーチ検索", "search_number": 3}
-- ]
--
-- その他の検索手法例:
-- - SNS検索（Twitter/X、Facebook等）
-- - 求人サイト検索（Indeed、リクナビ、マイナビ等）
-- - 業界特化型プラットフォーム検索
-- - 企業データベース検索（東京商工リサーチ、帝国データバンク等）
-- - イベント・セミナー参加者リスト検索
-- - 紹介・リファラル検索
-- - その他自由記述