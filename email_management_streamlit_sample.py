"""
メール管理機能のStreamlitサンプルコード
target_companiesテーブルのメール関連カラムを操作
"""

import streamlit as st
import json
import re
from datetime import date, datetime
from supabase import create_client
import pandas as pd

# Supabase接続
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

def display_email_search_patterns_form(target_company_id):
    """メール検索パターンの入力フォーム"""
    st.subheader("📧 メール検索パターン")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('email_search_patterns').eq('target_company_id', target_company_id).execute()
    existing_patterns = []
    if result.data and result.data[0]['email_search_patterns']:
        existing_patterns = result.data[0]['email_search_patterns']
    
    # パターン入力（最大10個）
    patterns = []
    for i in range(10):
        pattern = st.text_input(
            f"パターン {i+1}",
            key=f"email_pattern_{i}",
            value=existing_patterns[i] if i < len(existing_patterns) else "",
            placeholder="例: firstname.lastname@company.com, *@company.com",
            help="*をワイルドカードとして使用可能"
        )
        if pattern:
            patterns.append(pattern)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 パターンを保存", key="save_patterns"):
            save_email_patterns(target_company_id, patterns)
    
    with col2:
        if st.button("🧹 パターンをクリア", key="clear_patterns"):
            save_email_patterns(target_company_id, [])

def display_confirmed_emails_form(target_company_id):
    """確認済みメールアドレスの管理フォーム"""
    st.subheader("✅ 確認済みメールアドレス")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('confirmed_emails').eq('target_company_id', target_company_id).execute()
    existing_emails = []
    if result.data and result.data[0]['confirmed_emails']:
        existing_emails = result.data[0]['confirmed_emails']
    
    # 既存のメール一覧表示
    if existing_emails:
        st.write("### 登録済みメールアドレス")
        df = pd.DataFrame(existing_emails)
        if 'confirmed_date' in df.columns:
            df['confirmed_date'] = pd.to_datetime(df['confirmed_date']).dt.strftime('%Y年%m月%d日')
        st.dataframe(df, use_container_width=True)
        
        # 削除機能
        email_to_delete = st.selectbox("削除するメールアドレス", 
                                     options=["選択してください"] + [e['email'] for e in existing_emails])
        if email_to_delete != "選択してください":
            if st.button("🗑️ 削除", key="delete_confirmed_email"):
                updated_emails = [e for e in existing_emails if e['email'] != email_to_delete]
                save_confirmed_emails(target_company_id, updated_emails)
        
        st.divider()
    
    # 新規追加フォーム
    st.write("### 新しいメールアドレスを追加")
    
    col1, col2 = st.columns(2)
    with col1:
        new_email = st.text_input("メールアドレス", placeholder="tanaka@example.com")
        new_name = st.text_input("氏名", placeholder="田中太郎")
        new_department = st.text_input("部署", placeholder="営業部")
    
    with col2:
        new_position = st.text_input("役職", placeholder="部長")
        confirmation_method = st.selectbox("確認方法", 
                                         ["LinkedIn", "企業HP", "名刺交換", "電話確認", "その他"])
        confirmed_date = st.date_input("確認日", value=date.today())
    
    if st.button("➕ メールアドレスを追加", key="add_confirmed_email"):
        if new_email and new_name:
            if re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
                new_entry = {
                    "email": new_email,
                    "name": new_name,
                    "department": new_department,
                    "position": new_position,
                    "confirmed_date": confirmed_date.isoformat(),
                    "confirmation_method": confirmation_method
                }
                updated_emails = existing_emails + [new_entry]
                save_confirmed_emails(target_company_id, updated_emails)
            else:
                st.error("有効なメールアドレスを入力してください")
        else:
            st.error("メールアドレスと氏名は必須です")

def display_misdelivery_emails_form(target_company_id):
    """誤送信履歴の管理フォーム"""
    st.subheader("❌ 誤送信履歴")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('misdelivery_emails').eq('target_company_id', target_company_id).execute()
    existing_misdelivery = []
    if result.data and result.data[0]['misdelivery_emails']:
        existing_misdelivery = result.data[0]['misdelivery_emails']
    
    # 既存の誤送信履歴表示
    if existing_misdelivery:
        st.write("### 誤送信履歴")
        df = pd.DataFrame(existing_misdelivery)
        if 'sent_date' in df.columns:
            df['sent_date'] = pd.to_datetime(df['sent_date']).dt.strftime('%Y年%m月%d日')
        st.dataframe(df, use_container_width=True)
        st.divider()
    
    # 新規追加フォーム
    st.write("### 誤送信記録を追加")
    
    col1, col2 = st.columns(2)
    with col1:
        wrong_email = st.text_input("誤送信先メールアドレス", placeholder="wrong@example.com")
        sent_date = st.date_input("送信日", value=date.today())
    
    with col2:
        reason = st.selectbox("理由", 
                            ["同姓同名の別人", "退職済み", "部署間違い", "会社間違い", "その他"])
        memo = st.text_area("詳細メモ", placeholder="詳細な状況を記録...")
    
    if st.button("➕ 誤送信記録を追加", key="add_misdelivery"):
        if wrong_email:
            new_entry = {
                "email": wrong_email,
                "sent_date": sent_date.isoformat(),
                "reason": reason,
                "memo": memo
            }
            updated_misdelivery = existing_misdelivery + [new_entry]
            save_misdelivery_emails(target_company_id, updated_misdelivery)
        else:
            st.error("メールアドレスは必須です")

def display_email_search_memo_form(target_company_id):
    """メール検索メモの入力フォーム"""
    st.subheader("📝 メール検索メモ")
    
    # 既存データの取得
    result = supabase.table('target_companies').select('email_search_memo').eq('target_company_id', target_company_id).execute()
    existing_memo = ""
    if result.data and result.data[0]['email_search_memo']:
        existing_memo = result.data[0]['email_search_memo']
    
    memo = st.text_area(
        "メモ", 
        value=existing_memo,
        height=150,
        placeholder="メール検索に関する備考やメモを記録...\n\n例：\n- コーポレートサイトで命名規則を確認済み\n- HR部門は別ドメインを使用\n- 外国人スタッフは英語名を使用"
    )
    
    if st.button("💾 メモを保存", key="save_memo"):
        save_email_search_memo(target_company_id, memo)

# 保存関数群
def save_email_patterns(target_company_id, patterns):
    """メール検索パターンを保存"""
    try:
        result = supabase.table('target_companies').update({
            'email_search_patterns': patterns if patterns else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success(f"✅ {len(patterns)}件のパターンを保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")

def save_confirmed_emails(target_company_id, emails):
    """確認済みメールアドレスを保存"""
    try:
        result = supabase.table('target_companies').update({
            'confirmed_emails': emails if emails else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success(f"✅ {len(emails)}件のメールアドレスを保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")

def save_misdelivery_emails(target_company_id, emails):
    """誤送信履歴を保存"""
    try:
        result = supabase.table('target_companies').update({
            'misdelivery_emails': emails if emails else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success(f"✅ {len(emails)}件の誤送信記録を保存しました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")

def save_email_search_memo(target_company_id, memo):
    """メール検索メモを保存"""
    try:
        result = supabase.table('target_companies').update({
            'email_search_memo': memo if memo else None
        }).eq('target_company_id', target_company_id).execute()
        
        st.success("✅ メモを保存しました")
    except Exception as e:
        st.error(f"❌ 保存中にエラーが発生しました: {str(e)}")

# メイン関数
def main():
    st.title("📧 企業メール管理システム")
    
    # 案件とターゲット企業の選択
    col1, col2 = st.columns(2)
    
    with col1:
        # 案件データを取得
        projects_result = supabase.table('projects').select('project_id, project_name').order('project_name').execute()
        project_options = {"選択してください": None}
        if projects_result.data:
            for p in projects_result.data:
                project_options[p['project_name']] = p['project_id']
        
        selected_project_name = st.selectbox(
            "📋 案件を選択",
            options=list(project_options.keys()),
            key="project_selector"
        )
        selected_project_id = project_options[selected_project_name]
    
    with col2:
        # 選択された案件に紐づくターゲット企業を取得
        target_company_id = None
        if selected_project_id:
            # project_target_companiesから該当案件のターゲット企業を取得
            target_result = supabase.table('project_target_companies').select(
                'target_company_id, target_companies(company_name)'
            ).eq('project_id', selected_project_id).execute()
            
            company_options = {"選択してください": None}
            if target_result.data:
                for t in target_result.data:
                    if t.get('target_companies'):
                        company_name = t['target_companies']['company_name']
                        company_options[company_name] = t['target_company_id']
            
            selected_company_name = st.selectbox(
                "🏢 ターゲット企業を選択",
                options=list(company_options.keys()),
                key="company_selector",
                disabled=False
            )
            target_company_id = company_options[selected_company_name]
        else:
            st.selectbox(
                "🏢 ターゲット企業を選択",
                options=["先に案件を選択してください"],
                key="company_selector",
                disabled=True
            )
    
    # ターゲット企業が選択されている場合のみ各機能を表示
    if target_company_id:
        # タブで機能を分割
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 検索パターン", "✅ 確認済みメール", "❌ 誤送信履歴", "📝 メモ"])
        
        with tab1:
            display_email_search_patterns_form(target_company_id)
        
        with tab2:
            display_confirmed_emails_form(target_company_id)
        
        with tab3:
            display_misdelivery_emails_form(target_company_id)
        
        with tab4:
            display_email_search_memo_form(target_company_id)
    else:
        st.info("📌 案件とターゲット企業を選択してください")

if __name__ == "__main__":
    main()