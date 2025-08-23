"""
その他検索履歴管理のStreamlitサンプルコード
companiesテーブルのother_searches (JSONB)カラムを操作
"""

import streamlit as st
import json
from datetime import date
from supabase import create_client
import pandas as pd

# Supabase接続（実際のapp.pyで使用する場合は既存の関数を利用）
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

# 検索手法の選択肢
SEARCH_METHODS = [
    "",  # 空の選択肢
    "Wantedly検索",
    "Green検索",
    "ビズリーチ検索",
    "Indeed検索",
    "リクナビ検索",
    "マイナビ検索",
    "Twitter/X検索",
    "Facebook検索",
    "LinkedIn追加検索",
    "業界データベース検索",
    "イベント参加者リスト",
    "紹介・リファラル",
    "その他（自由入力）"
]

def display_other_search_form(target_company_id):
    """その他検索履歴の入力フォームを表示"""
    st.subheader("🔍 その他検索履歴")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('other_searches').eq('target_company_id', target_company_id).execute()
    existing_searches = []
    if result.data and result.data[0]['other_searches']:
        existing_searches = result.data[0]['other_searches']
    
    # 3回分の入力フォーム
    other_searches = []
    
    for i in range(1, 4):
        st.write(f"### その他検索 {i}")
        col1, col2, col3 = st.columns([2, 3, 1])
        
        # 既存データがあれば初期値として設定
        existing_data = next((s for s in existing_searches if s.get('search_number') == i), {})
        
        with col1:
            search_date = st.date_input(
                f"実施日",
                key=f"other_date_{i}",
                value=date.fromisoformat(existing_data['date']) if existing_data.get('date') else None,
                help="検索を実施した日付"
            )
        
        with col2:
            # プリセットから選択または自由入力
            selected_method = st.selectbox(
                f"検索手法",
                options=SEARCH_METHODS,
                key=f"other_method_select_{i}",
                index=SEARCH_METHODS.index(existing_data.get('method', '')) 
                      if existing_data.get('method', '') in SEARCH_METHODS else 0,
                help="検索手法を選択"
            )
            
            # 「その他」が選択された場合は自由入力欄を表示
            if selected_method == "その他（自由入力）":
                custom_method = st.text_input(
                    "検索手法を入力",
                    key=f"other_method_custom_{i}",
                    placeholder="例: 独自データベース検索",
                    value=existing_data.get('method', '') if existing_data.get('method', '') not in SEARCH_METHODS else ''
                )
                method = custom_method if custom_method else None
            else:
                method = selected_method if selected_method else None
        
        with col3:
            if existing_data:
                st.write("✅ 登録済")
        
        # データが入力されていれば配列に追加
        if search_date and method:
            other_searches.append({
                "date": search_date.isoformat(),
                "method": method,
                "search_number": i
            })
    
    # 保存ボタン
    if st.button("💾 その他検索履歴を保存", type="primary", key="save_other_searches"):
        save_other_searches(target_company_id, other_searches)

def save_other_searches(target_company_id, other_searches):
    """その他検索履歴をデータベースに保存"""
    try:
        # JSONBカラムに保存
        result = supabase.table('target_companies').update({
            'other_searches': other_searches if other_searches else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success(f"✅ {len(other_searches)}件のその他検索履歴を保存しました")
        return True
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")
        return False

def display_other_search_summary(target_company_id):
    """その他検索履歴のサマリーを表示"""
    result = supabase.table('target_companies').select('other_searches').eq('target_company_id', target_company_id).execute()
    
    if result.data and result.data[0]['other_searches']:
        searches = result.data[0]['other_searches']
        
        st.metric("その他検索実施回数", f"{len(searches)} / 3 回")
        
        # 履歴をテーブルで表示
        if searches:
            df = pd.DataFrame(searches)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y年%m月%d日')
            df = df.rename(columns={
                'search_number': '検索回',
                'date': '実施日',
                'method': '検索手法'
            })
            st.dataframe(df[['検索回', '実施日', '検索手法']], use_container_width=True)
    else:
        st.info("その他検索履歴はまだ登録されていません")

def display_combined_search_dashboard(target_company_id):
    """キーワード検索とその他検索を統合したダッシュボード"""
    st.subheader("📊 検索履歴ダッシュボード")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # キーワード検索の状況
        result_kw = supabase.table('target_companies').select('keyword_searches').eq('target_company_id', target_company_id).execute()
        kw_count = len(result_kw.data[0]['keyword_searches']) if result_kw.data and result_kw.data[0]['keyword_searches'] else 0
        st.metric("キーワード検索", f"{kw_count} / 5 回")
        
    with col2:
        # その他検索の状況
        result_other = supabase.table('target_companies').select('other_searches').eq('target_company_id', target_company_id).execute()
        other_count = len(result_other.data[0]['other_searches']) if result_other.data and result_other.data[0]['other_searches'] else 0
        st.metric("その他検索", f"{other_count} / 3 回")
    
    # 全体の進捗
    total_progress = (kw_count + other_count) / 8.0
    st.progress(total_progress)
    st.caption(f"全体進捗: {total_progress:.0%} ({kw_count + other_count} / 8 検索完了)")

# 使用例（実際のapp.pyに組み込む場合）
def main():
    st.title("企業管理 - 検索履歴管理")
    
    # 企業選択（実際はセレクトボックスなどで選択）
    target_company_id = st.number_input("企業ID", min_value=1, value=1)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 キーワード検索", "🔍 その他検索", "📊 サマリー", "📈 ダッシュボード"])
    
    with tab1:
        # keyword_searches_streamlit_sample.pyの関数を呼び出す
        st.info("キーワード検索の編集画面")
    
    with tab2:
        display_other_search_form(target_company_id)
    
    with tab3:
        display_other_search_summary(target_company_id)
    
    with tab4:
        display_combined_search_dashboard(target_company_id)

if __name__ == "__main__":
    main()