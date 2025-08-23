-- target_companiesテーブルに企業URLカラムを追加

-- 1. company_urlカラムを追加
ALTER TABLE target_companies ADD COLUMN company_url VARCHAR(500);

-- 2. カラムにコメントを追加
COMMENT ON COLUMN target_companies.company_url IS '企業の公式ウェブサイトURL';

-- 3. URLの形式チェック制約を追加（オプション）
-- HTTPまたはHTTPSで始まるURLのみ許可
ALTER TABLE target_companies 
ADD CONSTRAINT check_company_url_format 
CHECK (
    company_url IS NULL 
    OR company_url ~ '^https?://.*'
);

-- 4. インデックスの作成（URLでの検索を高速化）
CREATE INDEX idx_target_companies_company_url ON target_companies(company_url);

-- 5. サンプルデータ更新（コメントアウト）
-- UPDATE target_companies SET company_url = 'https://example.com' WHERE target_company_id = 1;
-- UPDATE target_companies SET company_url = 'https://sample-company.co.jp' WHERE target_company_id = 2;