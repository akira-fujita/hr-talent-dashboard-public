# トラブルシューティングガイド

## 🔧 Supabase接続エラーの解決方法

### エラー: "Invalid API key"

**症状**: 
```
データベース接続エラー: {'message': 'JSON could not be generated', 'code': 401...}
```

**原因と解決法**:

#### 1. APIキーの形式が間違っている

**確認方法**:
- Streamlit Cloud Secrets の `SUPABASE_ANON_KEY` を確認
- 正しいキーは `eyJ` で始まる長い文字列

**修正方法**:
1. [Supabase Dashboard](https://app.supabase.com) にアクセス
2. プロジェクト → Settings → API
3. "anon public" キーをコピー
4. Streamlit Cloud Secrets を更新

#### 2. プロジェクトが一時停止している

**確認方法**:
- Supabaseダッシュボードでプロジェクト状態を確認
- "Project paused" などの表示がないかチェック

**修正方法**:
- プロジェクトを再開
- または新しいプロジェクトを作成

### 代替案: サンプルデータモードで実行

Supabase接続に問題がある場合、アプリは自動的にサンプルデータモードで動作します：

```
🎯 デモモード: このアプリはサンプルデータで動作しています
```

**サンプルデータモードの特徴**:
- ✅ 全ての機能が利用可能
- ✅ データの作成・編集・削除が可能
- ✅ リアルタイム更新（ブラウザセッション内）
- ❌ データの永続化なし（リロードで初期化）

## 🔄 デバッグ手順

### 1. Streamlit Cloud ログの確認

1. Streamlit Cloud管理画面
2. アプリ選択 → "Logs" タブ
3. エラーメッセージを確認

### 2. 段階的テスト

**Step 1**: Secrets設定確認
```python
# アプリの最初にデバッグ情報を表示
st.write("SUPABASE_URL exists:", "SUPABASE_URL" in st.secrets)
st.write("SUPABASE_ANON_KEY exists:", "SUPABASE_ANON_KEY" in st.secrets)
```

**Step 2**: 接続テスト
```python
# 簡単な接続テスト
try:
    response = supabase.table('priority_levels').select('*').limit(1).execute()
    st.success("✅ Supabase接続成功")
except Exception as e:
    st.error(f"❌ Supabase接続失敗: {e}")
```

### 3. よくある問題

| 問題 | 症状 | 解決法 |
|------|------|---------|
| APIキー期限切れ | 401 Unauthorized | 新しいキーを生成・設定 |
| プロジェクト一時停止 | 接続タイムアウト | プロジェクトを再開 |
| Secrets設定ミス | Key not found | 設定を再確認・修正 |
| RLS設定問題 | 403 Forbidden | RLSポリシーを確認 |

## 📞 サポート

問題が解決しない場合:

1. **GitHub Issues**: リポジトリのIssuesで報告
2. **Supabase Support**: [Supabase Discord](https://discord.supabase.com)
3. **Streamlit Support**: [Streamlit Community](https://discuss.streamlit.io)

## 🎯 推奨: 新しいデモ用プロジェクト作成

最も確実な解決法として、新しいSupabaseプロジェクトの作成をお勧めします：

1. **新しいプロジェクト作成**:
   - プロジェクト名: `hr-dashboard-demo`
   - Region: 最寄りの地域を選択

2. **データベーススキーマの設定**:
   - `SUPABASE_PUBLIC_SETUP.md`の手順を実行

3. **APIキーの取得と設定**:
   - 新しいプロジェクトのAPIキーを使用
   - Streamlit Cloud Secretsを更新