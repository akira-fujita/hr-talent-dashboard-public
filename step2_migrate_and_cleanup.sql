-- ステップ2: データ移行とクリーンアップ

-- 既存データをマイグレーション（projects の target_department_id から移行）
UPDATE project_target_companies 
SET department_id = (
    SELECT target_department_id 
    FROM projects 
    WHERE projects.project_id = project_target_companies.project_id
)
WHERE EXISTS (
    SELECT 1 FROM projects 
    WHERE projects.project_id = project_target_companies.project_id 
    AND projects.target_department_id IS NOT NULL
);

-- projects テーブルから target_department_id を削除
ALTER TABLE projects DROP COLUMN target_department_id;

-- 確認クエリ
SELECT 
    ptc.id,
    ptc.project_id,
    ptc.target_company_id,
    ptc.department_id,
    tc.company_name,
    d.department_name
FROM project_target_companies ptc
LEFT JOIN target_companies tc ON ptc.target_company_id = tc.target_company_id
LEFT JOIN departments d ON ptc.department_id = d.department_id
LIMIT 5;

-- 制約確認（企業と部署の整合性）
SELECT 
    ptc.id,
    tc.company_name,
    d.department_name,
    d.company_id as dept_company_id,
    ptc.target_company_id as ptc_company_id,
    CASE 
        WHEN ptc.department_id IS NULL THEN 'OK (部署なし)'
        WHEN d.company_id = ptc.target_company_id THEN 'OK'
        ELSE 'NG (企業・部署不整合)'
    END as consistency_check
FROM project_target_companies ptc
LEFT JOIN target_companies tc ON ptc.target_company_id = tc.target_company_id
LEFT JOIN departments d ON ptc.department_id = d.department_id;