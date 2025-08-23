-- ステップ1: project_target_companies テーブルに department_id カラムを追加

ALTER TABLE project_target_companies 
ADD COLUMN department_id BIGINT REFERENCES departments(department_id) ON DELETE SET NULL;

-- インデックス追加（パフォーマンス向上）
CREATE INDEX idx_project_target_companies_department_id 
ON project_target_companies(department_id);

-- 確認
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'project_target_companies' 
ORDER BY ordinal_position;