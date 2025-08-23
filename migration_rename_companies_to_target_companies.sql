-- companiesテーブルをtarget_companiesにリネーム
-- このテーブルは検索対象となる企業を管理するため、より明確な名前に変更

-- 1. テーブル名の変更
ALTER TABLE companies RENAME TO target_companies;

-- 2. プライマリキーカラム名の変更（company_id → target_company_id）
ALTER TABLE target_companies RENAME COLUMN company_id TO target_company_id;

-- 3. シーケンス名の変更
ALTER SEQUENCE companies_company_id_seq RENAME TO target_companies_target_company_id_seq;

-- 4. テーブルコメントの追加/更新
COMMENT ON TABLE target_companies IS '検索対象企業マスタテーブル - タレント検索の対象となる企業情報を管理';

-- 5. カラムコメントの更新（主要なカラムのみ）
COMMENT ON COLUMN target_companies.target_company_id IS '検索対象企業ID（プライマリキー）';
COMMENT ON COLUMN target_companies.company_name IS '検索対象企業名';

-- 6. 外部キー制約がある他のテーブルの更新
-- contactsテーブルの外部キー制約を更新
ALTER TABLE contacts DROP CONSTRAINT IF EXISTS contacts_company_id_fkey;
ALTER TABLE contacts RENAME COLUMN company_id TO target_company_id;
ALTER TABLE contacts 
    ADD CONSTRAINT contacts_target_company_id_fkey 
    FOREIGN KEY (target_company_id) 
    REFERENCES target_companies(target_company_id);

-- projectsテーブルの外部キー制約を更新（もし存在する場合）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_company_id_fkey;
        ALTER TABLE projects RENAME COLUMN company_id TO target_company_id;
        ALTER TABLE projects 
            ADD CONSTRAINT projects_target_company_id_fkey 
            FOREIGN KEY (target_company_id) 
            REFERENCES target_companies(target_company_id);
    END IF;
END $$;

-- 7. インデックス名の更新（もし存在する場合）
ALTER INDEX IF EXISTS idx_companies_company_name RENAME TO idx_target_companies_company_name;
ALTER INDEX IF EXISTS idx_companies_created_at RENAME TO idx_target_companies_created_at;

-- 8. 確認用クエリ（コメントアウト）
-- SELECT table_name, column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'target_companies' 
-- ORDER BY ordinal_position;

-- 9. 関連テーブルの確認（コメントアウト）
-- SELECT 
--     tc.table_name, 
--     kcu.column_name, 
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name 
-- FROM information_schema.table_constraints AS tc 
-- JOIN information_schema.key_column_usage AS kcu
--     ON tc.constraint_name = kcu.constraint_name
-- JOIN information_schema.constraint_column_usage AS ccu
--     ON ccu.constraint_name = tc.constraint_name
-- WHERE tc.constraint_type = 'FOREIGN KEY' 
--     AND ccu.table_name = 'target_companies';