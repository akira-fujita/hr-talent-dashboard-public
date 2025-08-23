# パブリックデモ用Supabase設定ガイド

## 🔐 セキュリティ設定

### 1. Row Level Security (RLS) の有効化

すべてのテーブルでRLSを有効にし、匿名ユーザーでも安全にアクセスできるようにします。

```sql
-- 全テーブルでRLSを有効化
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE target_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE priority_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_assignees ENABLE ROW LEVEL SECURITY;
ALTER TABLE approach_methods ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_target_companies ENABLE ROW LEVEL SECURITY;

-- 匿名ユーザーに読み取り・書き込み権限を付与（デモ用）
CREATE POLICY "Allow anonymous access" ON contacts FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON projects FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON target_companies FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON departments FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON priority_levels FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON search_assignees FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON approach_methods FOR ALL USING (true);
CREATE POLICY "Allow anonymous access" ON project_target_companies FOR ALL USING (true);
```

### 2. データベース制限設定

```sql
-- データ量制限（必要に応じて）
-- 例: contactsテーブルの最大レコード数を1000件に制限
CREATE OR REPLACE FUNCTION limit_contacts_count()
RETURNS trigger AS $$
BEGIN
  IF (SELECT COUNT(*) FROM contacts) >= 1000 THEN
    RAISE EXCEPTION 'Maximum number of contacts reached (1000)';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contacts_count_limit
  BEFORE INSERT ON contacts
  FOR EACH ROW EXECUTE FUNCTION limit_contacts_count();
```

## 🎯 デモデータの準備

### 1. サンプルデータの投入

```sql
-- 企業マスタデータ
INSERT INTO target_companies (company_name, industry_type) VALUES
('株式会社テックイノベーション', '情報通信業'),
('グローバル商事株式会社', '卸売業・小売業'),
('未来製造株式会社', '製造業'),
('ヘルスケア株式会社', '医療・福祉業'),
('エデュケーション株式会社', '教育・学習支援業');

-- 優先度マスタ
INSERT INTO priority_levels (priority_name, priority_value, description) VALUES
('最高', 5.0, '最優先で対応'),
('高', 4.0, '優先的に対応'),
('中', 3.0, '通常対応'),
('低', 2.0, '時間があるときに対応');

-- 担当者マスタ
INSERT INTO search_assignees (assignee_name) VALUES
('田中太郎'),
('佐藤花子'),
('山田一郎');
```

## 🚀 Streamlit Cloud設定

### 1. Secrets設定

Streamlit Cloud管理画面の "Secrets" タブで以下を設定：

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

### 2. アプリ再起動

設定後、"Reboot app" でアプリを再起動してください。

## ⚠️ 注意事項

1. **データのリセット**: デモ用なので定期的にデータをリセットする場合があります
2. **利用制限**: Supabaseの無料プランの制限内で運用
3. **責任**: デモ目的での利用に留め、機密情報は入力しないでください

## 📈 監視とメンテナンス

- Supabaseダッシュボードでアクセス状況を監視
- 必要に応じてデータクリーンアップを実施
- パフォーマンス問題があれば制限を調整