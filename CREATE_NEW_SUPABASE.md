# 新しいSupabaseプロジェクト作成手順

## 🆕 パブリックデモ用プロジェクト作成

既存のSupabaseプロジェクトでAPIキーエラーが発生している場合、新しいプロジェクトを作成することをお勧めします。

### Step 1: 新しいプロジェクト作成

1. **[Supabase Dashboard](https://app.supabase.com) にアクセス**
2. **"New Project" をクリック**
3. **プロジェクト設定**:
   - **Name**: `hr-dashboard-public-demo`
   - **Database Password**: 安全なパスワードを設定
   - **Region**: 最寄りの地域を選択 (例: `ap-northeast-1` for Tokyo)
4. **"Create new project" をクリック**

### Step 2: APIキーの取得

プロジェクト作成後（数分かかります）：

1. **"Settings" → "API" をクリック**
2. **以下の情報をコピー**:
   - **Project URL**: `https://xxxxxxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIs...` (長いJWTトークン)

### Step 3: データベーススキーマ作成

1. **"SQL Editor" をクリック**
2. **以下のSQLを実行してテーブルを作成**:

```sql
-- 企業テーブル
CREATE TABLE target_companies (
    target_company_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(255) UNIQUE NOT NULL,
    industry_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 部署テーブル
CREATE TABLE departments (
    department_id BIGSERIAL PRIMARY KEY,
    company_id BIGINT REFERENCES target_companies(target_company_id),
    department_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 優先度テーブル
CREATE TABLE priority_levels (
    priority_id BIGSERIAL PRIMARY KEY,
    priority_name VARCHAR(50) UNIQUE NOT NULL,
    priority_value DECIMAL(3,2) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 担当者テーブル
CREATE TABLE search_assignees (
    assignee_id BIGSERIAL PRIMARY KEY,
    assignee_name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- アプローチ手法テーブル
CREATE TABLE approach_methods (
    method_id BIGSERIAL PRIMARY KEY,
    method_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- コンタクトテーブル
CREATE TABLE contacts (
    contact_id BIGSERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    company_id BIGINT REFERENCES target_companies(target_company_id),
    department_id BIGINT REFERENCES departments(department_id),
    position_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    estimated_age VARCHAR(50),
    screening_status VARCHAR(50) DEFAULT '未実施',
    priority_id BIGINT REFERENCES priority_levels(priority_id),
    assignee_id BIGINT REFERENCES search_assignees(assignee_id),
    profile_memo TEXT,
    comment TEXT,
    skills TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 案件テーブル
CREATE TABLE projects (
    project_id BIGSERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    client_company_id BIGINT REFERENCES target_companies(target_company_id),
    project_description TEXT,
    required_skills TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    location VARCHAR(255),
    employment_type VARCHAR(100),
    status VARCHAR(100) DEFAULT '募集中',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 案件・企業関連テーブル
CREATE TABLE project_target_companies (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(project_id) ON DELETE CASCADE,
    target_company_id BIGINT REFERENCES target_companies(target_company_id),
    department_id BIGINT REFERENCES departments(department_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 4: RLS設定（Row Level Security）

```sql
-- 全テーブルでRLSを有効化
ALTER TABLE target_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE priority_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_assignees ENABLE ROW LEVEL SECURITY;
ALTER TABLE approach_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_target_companies ENABLE ROW LEVEL SECURITY;

-- 匿名ユーザーに全アクセス権を付与（デモ用）
CREATE POLICY "Allow anonymous access" ON target_companies FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON departments FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON priority_levels FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON search_assignees FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON approach_methods FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON contacts FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON projects FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON project_target_companies FOR ALL USING (true);
```

### Step 5: サンプルデータの挿入

```sql
-- サンプルデータを挿入
INSERT INTO target_companies (company_name, industry_type) VALUES
('株式会社テックイノベーション', '情報通信業'),
('グローバル商事株式会社', '卸売業・小売業'),
('未来製造株式会社', '製造業'),
('ヘルスケア株式会社', '医療・福祉業'),
('エデュケーション株式会社', '教育・学習支援業');

INSERT INTO priority_levels (priority_name, priority_value, description) VALUES
('最高', 5.0, '最優先で対応'),
('高', 4.0, '優先的に対応'),
('中', 3.0, '通常対応'),
('低', 2.0, '時間があるときに対応');

INSERT INTO search_assignees (assignee_name) VALUES
('田中太郎'),
('佐藤花子'),
('山田一郎');

INSERT INTO approach_methods (method_name, description) VALUES
('LinkedInメッセージ', 'LinkedIn経由での直接連絡'),
('メール', '企業メールアドレスへの連絡'),
('電話', '直接電話での連絡'),
('紹介', '知人・既存コンタクト経由の紹介');
```

### Step 6: Streamlit Cloud設定更新

1. **Streamlit Cloud管理画面**
2. **アプリ設定 → "Secrets"**
3. **新しいAPIキーで更新**:
```toml
SUPABASE_URL = "https://新しいプロジェクトID.supabase.co"
SUPABASE_ANON_KEY = "新しいanonキー"
```
4. **"Save changes" → "Reboot app"**

これで新しいSupabaseプロジェクトでアプリが動作するはずです！