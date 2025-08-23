-- 外部キー制約を削除してからtarget_company_idカラムを削除

-- 1. 外部キー制約を削除
ALTER TABLE projects DROP CONSTRAINT projects_target_company_id_fkey;

-- 2. target_company_idカラムを削除
ALTER TABLE projects DROP COLUMN target_company_id;

-- 完了確認用クエリ
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'projects' 
AND column_name = 'target_company_id';

-- 中間テーブルの確認
SELECT COUNT(*) as relation_count 
FROM project_target_companies;