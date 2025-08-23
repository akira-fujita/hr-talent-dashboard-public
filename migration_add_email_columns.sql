-- target_companiesテーブルにメール関連カラムを追加

-- 1. メール検索パターンカラムを追加（JSONB型）
ALTER TABLE target_companies ADD COLUMN email_search_patterns JSONB;

-- 2. 確認済みメールアドレスカラムを追加（JSONB型）
ALTER TABLE target_companies ADD COLUMN confirmed_emails JSONB;

-- 3. 誤送信履歴カラムを追加（JSONB型）
ALTER TABLE target_companies ADD COLUMN misdelivery_emails JSONB;

-- 4. メール検索メモカラムを追加（TEXT型）
ALTER TABLE target_companies ADD COLUMN email_search_memo TEXT;

-- 5. カラムにコメントを追加
COMMENT ON COLUMN target_companies.email_search_patterns IS 'メール検索パターン（配列形式）- 例: ["firstname.lastname@*", "*@company.com", "info@*"]';

COMMENT ON COLUMN target_companies.confirmed_emails IS '確認済みメールアドレス（配列形式）- 例: [{"email": "tanaka@example.com", "name": "田中太郎", "confirmed_date": "2024-01-15", "department": "営業部"}]';

COMMENT ON COLUMN target_companies.misdelivery_emails IS '誤送信履歴（配列形式）- 例: [{"email": "wrong@example.com", "sent_date": "2024-01-10", "reason": "同姓同名の別人", "memo": "退職済み"}]';

COMMENT ON COLUMN target_companies.email_search_memo IS 'メール検索の備考・メモ（自由記述）';

-- 6. JSONBカラムにインデックスを作成（検索パフォーマンス向上）
-- 確認済みメールアドレスでの検索用
CREATE INDEX idx_target_companies_confirmed_emails_gin ON target_companies USING GIN (confirmed_emails);

-- 誤送信履歴での検索用
CREATE INDEX idx_target_companies_misdelivery_emails_gin ON target_companies USING GIN (misdelivery_emails);

-- メール検索パターンでの検索用
CREATE INDEX idx_target_companies_email_search_patterns_gin ON target_companies USING GIN (email_search_patterns);

-- 7. サンプルデータの構造例（コメントアウト）
-- 
-- email_search_patterns例:
-- [
--   "firstname.lastname@company.com",
--   "f.lastname@company.com", 
--   "firstname@company.com",
--   "*@company.com"
-- ]
--
-- confirmed_emails例:
-- [
--   {
--     "email": "tanaka.taro@example.com",
--     "name": "田中太郎",
--     "department": "営業部",
--     "position": "部長",
--     "confirmed_date": "2024-01-15",
--     "confirmation_method": "LinkedIn経由"
--   },
--   {
--     "email": "sato.hanako@example.com", 
--     "name": "佐藤花子",
--     "department": "開発部",
--     "position": "エンジニア",
--     "confirmed_date": "2024-01-20",
--     "confirmation_method": "企業HP経由"
--   }
-- ]
--
-- misdelivery_emails例:
-- [
--   {
--     "email": "tanaka@wrong-company.com",
--     "sent_date": "2024-01-10", 
--     "reason": "同姓同名の別人",
--     "memo": "同じ業界の別会社の田中さんに送信してしまった"
--   },
--   {
--     "email": "old.employee@example.com",
--     "sent_date": "2024-01-12",
--     "reason": "退職済み", 
--     "memo": "昨年退職、現在は別会社"
--   }
-- ]

-- 8. サンプルデータの挿入（コメントアウト）
-- UPDATE target_companies 
-- SET 
--   email_search_patterns = '["firstname.lastname@example.com", "*@example.com"]',
--   email_search_memo = 'コーポレートサイトで命名規則を確認済み'
-- WHERE target_company_id = 1;