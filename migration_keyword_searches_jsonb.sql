-- keyword_searchedカラムをkeyword_searchesという名前のJSONB型に変更
-- 既存のdate型データを移行

-- 1. 新しいJSONBカラムを追加
ALTER TABLE companies ADD COLUMN keyword_searches JSONB;

-- 2. 既存のデータを移行（既存のdate型データがある場合、1回目の検索として移行）
UPDATE companies 
SET keyword_searches = 
    CASE 
        WHEN keyword_searched IS NOT NULL THEN 
            jsonb_build_array(
                jsonb_build_object(
                    'date', keyword_searched::text,
                    'keyword', '移行前データ（キーワード不明）',
                    'search_number', 1
                )
            )
        ELSE NULL
    END;

-- 3. 古いカラムを削除
ALTER TABLE companies DROP COLUMN keyword_searched;

-- 4. カラムにコメントを追加
COMMENT ON COLUMN companies.keyword_searches IS 'キーワード検索履歴（最大5回分）- JSON形式: [{"date": "YYYY-MM-DD", "keyword": "検索キーワード", "search_number": 1-5}]';

-- 5. サンプルデータの説明（コメント）
-- 使用例:
-- [
--   {"date": "2024-01-15", "keyword": "AI エンジニア 東京", "search_number": 1},
--   {"date": "2024-01-20", "keyword": "機械学習 新卒 2024", "search_number": 2},
--   {"date": "2024-01-25", "keyword": "Python データサイエンティスト", "search_number": 3}
-- ]