# データベース詳細テーブル定義

## 1. target_companies (検索対象企業) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| target_company_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('target_companies_target_company_id_seq'::regclass) | 企業ID（自動採番） |
| company_name | VARCHAR(255) | NOT NULL | NOT NULL | - | 企業名 |
| company_url | VARCHAR(500) | URL形式チェック | YES | - | 企業の公式ウェブサイトURL |
| email_searched | DATE | - | YES | - | メール検索実施日 |
| linkedin_searched | DATE | - | YES | - | LinkedIn検索実施日 |
| homepage_searched | DATE | - | YES | - | ホームページ検索実施日 |
| eight_search | DATE | - | YES | - | Eight検索実施日 |
| keyword_searches | JSONB | - | YES | - | キーワード検索履歴（最大5回分）|
| other_searches | JSONB | - | YES | - | その他検索履歴（最大3回分） |
| email_search_patterns | JSONB | - | YES | - | メール検索パターン配列 |
| confirmed_emails | JSONB | - | YES | - | 確認済みメールアドレス情報 |
| misdelivery_emails | JSONB | - | YES | - | 誤送信履歴 |
| email_search_memo | TEXT | - | YES | - | メール検索の備考・メモ |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 4 件

---

## 2. contacts (コンタクト情報) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| contact_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('contacts_contact_id_seq'::regclass) | コンタクトID（自動採番） |
| target_company_id | BIGINT | FOREIGN KEY | NOT NULL | - | 所属企業ID（target_companies参照） |
| full_name | VARCHAR(255) | NOT NULL | NOT NULL | - | フルネーム |
| last_name | VARCHAR(100) | - | YES | - | 姓 |
| first_name | VARCHAR(100) | - | YES | - | 名 |
| furigana | VARCHAR(255) | - | YES | - | ふりがな（フル） |
| furigana_last_name | VARCHAR(100) | - | YES | - | 姓（ふりがな） |
| furigana_first_name | VARCHAR(100) | - | YES | - | 名（ふりがな） |
| department_name | VARCHAR(255) | - | YES | - | 部署名 |
| position_name | VARCHAR(255) | - | YES | - | 役職名 |
| estimated_age | VARCHAR(50) | - | YES | - | 推定年齢 |
| profile | TEXT | - | YES | - | プロフィール |
| url | VARCHAR(500) | URL形式 | YES | - | プロフィールURL |
| screening_status | VARCHAR(100) | - | YES | - | スクリーニングステータス |
| primary_screening_comment | TEXT | - | YES | - | 一次スクリーニングコメント |
| priority_id | BIGINT | FOREIGN KEY | YES | - | 優先度ID（priority_levels参照） |
| name_search_key | VARCHAR(255) | - | YES | - | 名前検索キー |
| work_comment | TEXT | - | YES | - | 業務コメント |
| search_assignee_id | BIGINT | FOREIGN KEY | YES | - | 検索担当者ID（search_assignees参照） |
| search_date | DATE | - | YES | - | 検索実施日 |
| email_trial_history | TEXT | - | YES | - | メール送信履歴 |
| scrutiny_memo | TEXT | - | YES | - | 精査メモ |
| department_id | BIGINT | FOREIGN KEY | YES | - | 部署ID（departments参照） |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 4 件

---

## 3. projects (プロジェクト情報) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| project_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('projects_project_id_seq'::regclass) | プロジェクトID（自動採番） |
| project_name | VARCHAR(255) | NOT NULL | NOT NULL | - | プロジェクト名 |
| target_company_id | BIGINT | FOREIGN KEY | NOT NULL | - | 対象企業ID（target_companies参照） |
| client_company_id | BIGINT | FOREIGN KEY | YES | - | 依頼元企業ID（client_companies参照） |
| department_id | BIGINT | FOREIGN KEY | YES | - | 部署ID（departments参照） |
| project_status | VARCHAR(100) | - | YES | - | プロジェクトステータス |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 0 件

---

## 4. client_companies (依頼元企業) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| client_company_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('client_companies_client_company_id_seq'::regclass) | 依頼元企業ID（自動採番） |
| company_name | VARCHAR(255) | NOT NULL | NOT NULL | - | 依頼元企業名 |
| company_url | VARCHAR(500) | URL形式チェック | YES | - | 依頼元企業の公式ウェブサイトURL |
| contact_person | VARCHAR(255) | - | YES | - | 担当者名 |
| contact_email | VARCHAR(255) | - | YES | - | 担当者メールアドレス |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 4 件

---

## 5. departments (部署マスタ) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| department_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('departments_department_id_seq'::regclass) | 部署ID（自動採番） |
| department_name | VARCHAR(255) | NOT NULL | NOT NULL | - | 部署名 |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 0 件

---

## 5. priority_levels (優先度レベル) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| priority_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('priority_levels_priority_id_seq'::regclass) | 優先度ID（自動採番） |
| priority_name | VARCHAR(100) | NOT NULL | NOT NULL | - | 優先度名 |
| priority_value | NUMERIC(3,1) | NOT NULL | NOT NULL | - | 優先度値（1.0-5.0） |
| description | TEXT | - | YES | - | 優先度の説明 |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |

**レコード数:** 5 件

---

## 6. search_assignees (検索担当者) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| assignee_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('search_assignees_assignee_id_seq'::regclass) | 担当者ID（自動採番） |
| assignee_name | VARCHAR(255) | NOT NULL | NOT NULL | - | 担当者名 |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 更新日時 |

**レコード数:** 4 件

---

## 7. approach_methods (アプローチ手法) テーブル定義

| カラム名 | データ型 | 制約 | NULL許可 | デフォルト値 | 説明 |
|----------|----------|------|----------|--------------|------|
| method_id | BIGSERIAL | PRIMARY KEY | NOT NULL | nextval('approach_methods_method_id_seq'::regclass) | 手法ID（自動採番） |
| method_name | VARCHAR(255) | NOT NULL | NOT NULL | - | アプローチ手法名 |
| description | TEXT | - | YES | - | 手法の説明 |
| created_at | TIMESTAMP | DEFAULT | YES | CURRENT_TIMESTAMP | 作成日時 |

**レコード数:** 5 件

---

## 外部キー制約

### target_companies テーブル
- `check_company_url_format`: company_url が HTTP/HTTPS形式である

### contacts テーブル
- `contacts_target_company_id_fkey`: target_company_id → target_companies(target_company_id)
- `contacts_priority_id_fkey`: priority_id → priority_levels(priority_id)  
- `contacts_search_assignee_id_fkey`: search_assignee_id → search_assignees(assignee_id)
- `contacts_department_id_fkey`: department_id → departments(department_id)

### projects テーブル
- `projects_target_company_id_fkey`: target_company_id → target_companies(target_company_id)
- `projects_client_company_id_fkey`: client_company_id → client_companies(client_company_id)
- `projects_department_id_fkey`: department_id → departments(department_id)

### client_companies テーブル
- `check_company_url_format`: company_url が HTTP/HTTPS形式である

---

## インデックス

### target_companies テーブル
- `idx_target_companies_company_url`: company_url（URL検索用）
- `idx_target_companies_confirmed_emails_gin`: confirmed_emails（JSONB検索用）
- `idx_target_companies_misdelivery_emails_gin`: misdelivery_emails（JSONB検索用）
- `idx_target_companies_email_search_patterns_gin`: email_search_patterns（JSONB検索用）

---

## JSONB カラムの詳細構造

### keyword_searches（キーワード検索履歴）
```json
[
  {
    "date": "2024-01-15",
    "keyword": "AI エンジニア 東京",
    "search_number": 1
  }
]
```

### other_searches（その他検索履歴）
```json
[
  {
    "date": "2024-02-01", 
    "method": "Wantedly検索",
    "search_number": 1
  }
]
```

### email_search_patterns（メール検索パターン）
```json
[
  "firstname.lastname@company.com",
  "f.lastname@company.com",
  "*@company.com"
]
```

### confirmed_emails（確認済みメール）
```json
[
  {
    "email": "tanaka@example.com",
    "name": "田中太郎",
    "department": "営業部", 
    "position": "部長",
    "confirmed_date": "2024-01-15",
    "confirmation_method": "LinkedIn"
  }
]
```

### misdelivery_emails（誤送信履歴）
```json
[
  {
    "email": "wrong@example.com",
    "sent_date": "2024-01-10",
    "reason": "同姓同名の別人",
    "memo": "別会社に送信してしまった"
  }
]
```