"""
キーワード検索履歴管理のStreamlitサンプルコード
companiesテーブルのkeyword_searches (JSONB)カラムを操作
"""

import streamlit as st
import json
from datetime import date
from supabase import create_client

# Supabase接続（実際のapp.pyで使用する場合は既存の関数を利用）
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

def display_keyword_search_form(target_company_id):
    """キーワード検索履歴の入力フォームを表示"""
    st.subheader("🔍 キーワード検索履歴")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('keyword_searches').eq('target_company_id', target_company_id).execute()
    existing_searches = []
    if result.data and result.data[0]['keyword_searches']:
        existing_searches = result.data[0]['keyword_searches']
    
    # 5回分の入力フォーム
    keyword_searches = []
    
    for i in range(1, 6):
        st.write(f"### 検索 {i}")
        col1, col2, col3 = st.columns([2, 3, 1])
        
        # 既存データがあれば初期値として設定
        existing_data = next((s for s in existing_searches if s.get('search_number') == i), {})
        
        with col1:
            search_date = st.date_input(
                f"実施日",
                key=f"keyword_date_{i}",
                value=date.fromisoformat(existing_data['date']) if existing_data.get('date') else None,
                help="検索を実施した日付"
            )
        
        with col2:
            keyword = st.text_input(
                f"検索キーワード",
                key=f"keyword_text_{i}",
                value=existing_data.get('keyword', ''),
                placeholder="例: AI エンジニア 東京",
                help="使用した検索キーワード"
            )
        
        with col3:
            if existing_data:
                st.write("✅ 登録済")
        
        # データが入力されていれば配列に追加
        if search_date and keyword:
            keyword_searches.append({
                "date": search_date.isoformat(),
                "keyword": keyword,
                "search_number": i
            })
    
    # 保存ボタン
    if st.button("💾 検索履歴を保存", type="primary"):
        save_keyword_searches(target_company_id, keyword_searches)

def save_keyword_searches(target_company_id, keyword_searches):
    """キーワード検索履歴をデータベースに保存"""
    try:
        # JSONBカラムに保存
        result = supabase.table('target_companies').update({
            'keyword_searches': keyword_searches if keyword_searches else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success(f"✅ {len(keyword_searches)}件の検索履歴を保存しました")
        return True
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")
        return False

def display_keyword_search_summary(target_company_id):
    """キーワード検索履歴のサマリーを表示"""
    result = supabase.table('target_companies').select('keyword_searches').eq('target_company_id', target_company_id).execute()
    
    if result.data and result.data[0]['keyword_searches']:
        searches = result.data[0]['keyword_searches']
        
        st.metric("検索実施回数", f"{len(searches)} / 5 回")
        
        # 履歴をテーブルで表示
        if searches:
            import pandas as pd
            df = pd.DataFrame(searches)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y年%m月%d日')
            df = df.rename(columns={
                'search_number': '検索回',
                'date': '実施日',
                'keyword': '使用キーワード'
            })
            st.dataframe(df[['検索回', '実施日', '使用キーワード']], use_container_width=True)
    else:
        st.info("キーワード検索履歴はまだ登録されていません")

# 使用例（実際のapp.pyに組み込む場合）
def main():
    st.title("企業管理 - キーワード検索履歴")
    
    # 企業選択（実際はセレクトボックスなどで選択）
    target_company_id = st.number_input("企業ID", min_value=1, value=1)
    
    tab1, tab2 = st.tabs(["📝 編集", "📊 サマリー"])
    
    with tab1:
        display_keyword_search_form(target_company_id)
    
    with tab2:
        display_keyword_search_summary(target_company_id)

if __name__ == "__main__":
    main()