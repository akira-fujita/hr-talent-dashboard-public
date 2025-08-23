-- プロジェクトとターゲット企業の多対多関係を実現するための中間テーブル作成
-- 1. 中間テーブル project_target_companies を作成
CREATE TABLE project_target_companies (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    target_company_id BIGINT NOT NULL REFERENCES target_companies(target_company_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, target_company_id)
);

-- インデックス作成（パフォーマンス向上のため）
CREATE INDEX idx_project_target_companies_project_id ON project_target_companies(project_id);
CREATE INDEX idx_project_target_companies_target_company_id ON project_target_companies(target_company_id);

-- 2. 既存のprojectsテーブルのtarget_company_idからデータを移行
-- 既存データがあれば中間テーブルに移行
INSERT INTO project_target_companies (project_id, target_company_id)
SELECT project_id, target_company_id 
FROM projects 
WHERE target_company_id IS NOT NULL;

-- 3. 外部キー制約を削除してからtarget_company_idカラムを削除
-- 既存の外部キー制約を確認
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f' 
AND conrelid = 'projects'::regclass
AND confrelid = 'target_companies'::regclass;

-- 外部キー制約を削除（制約名は実際の名前に置き換えてください）
-- ALTER TABLE projects DROP CONSTRAINT projects_target_company_id_fkey;

-- 4. target_company_idカラムを削除
-- ALTER TABLE projects DROP COLUMN target_company_id;

-- 注意: 上記の ALTER TABLE コマンドは実際の制約名を確認してから実行してください