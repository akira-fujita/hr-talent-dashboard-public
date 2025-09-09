import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np
from supabase import create_client


# URLパラメータ管理用のヘルパー関数
def get_url_param(key, default=""):
    """URLパラメータから値を取得するヘルパー関数"""
    return st.query_params.get(key, default)


def set_url_param(key, value):
    """URLパラメータを設定するヘルパー関数"""
    if value and value != "" and value != "すべて":
        st.query_params[key] = str(value)
    else:
        # 空の値や「すべて」の場合はパラメータを削除
        if key in st.query_params:
            del st.query_params[key]


def get_selectbox_index(options, default_value):
    """selectboxのデフォルトインデックスを取得するヘルパー関数"""
    try:
        if default_value and default_value in options:
            return options.index(default_value)
    except (ValueError, AttributeError):
        pass
    return 0


# ページ設定
st.set_page_config(
    page_title="HR Talent Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stMetric > label {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    .stMetric > div {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# Supabase接続
@st.cache_resource
def init_supabase():
    """Supabaseクライアントを初期化"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase接続エラー: {str(e)}")
        # サンプルデータにフォールバック
        return None


supabase = init_supabase()


# データ取得関数
@st.cache_data(ttl=300)
def fetch_contacts():
    """プロジェクトコンタクトデータを取得"""
    if supabase is None:
        # Supabase接続失敗時はサンプルデータを使用
        return generate_sample_data()
    
    try:
        # target_companies, priority_levels, search_assigneesの関連データも含めて取得
        # 正しい外部キー制約名を使用
        response = supabase.table('contacts').select(
            '*, target_companies!contacts_target_company_id_fkey(company_name), ' + 
            'priority_levels!project_contacts_priority_id_fkey(priority_name, priority_value), ' + 
            'search_assignees!project_contacts_search_assignee_id_fkey(assignee_name)'
        ).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # HR Dashboardに合わせてカラム名を調整
            if not df.empty:
                column_mapping = {
                    'full_name': 'name',
                    'last_name': 'last_name',
                    'first_name': 'first_name',
                    # 'company_name': 'company',  # target_companies関連で処理
                    'department_name': 'department',
                    'position_name': 'position'
                }
                
                # 存在するカラムのみマッピング
                for old_col, new_col in column_mapping.items():
                    if old_col in df.columns:
                        df = df.rename(columns={old_col: new_col})
                
                # target_companies関連データの処理
                if 'target_companies' in df.columns:
                    df['company'] = df['target_companies'].apply(lambda x: x['company_name'] if x else 'Unknown')
                    df['company_name'] = df['target_companies'].apply(lambda x: x['company_name'] if x else 'Unknown')
                
                # priority_levels関連データの処理
                if 'priority_levels' in df.columns:
                    df['priority_name'] = df['priority_levels'].apply(lambda x: x['priority_name'] if x else None)
                    df['priority_value'] = df['priority_levels'].apply(lambda x: x['priority_value'] if x else None)
                
                # search_assignees関連データの処理
                if 'search_assignees' in df.columns:
                    df['search_assignee'] = df['search_assignees'].apply(lambda x: x['assignee_name'] if x else None)
                
                # contactsテーブルの物理カラムのみを使用
                # 追加の計算カラムやダミーデータは生成しない
                
                return df
            else:
                return generate_sample_data()
        else:
            # データが空の場合はサンプルデータを使用
            return generate_sample_data()
    except Exception as e:
        st.warning(f"データベース接続エラー: {str(e)} - サンプルデータを使用します")
        return generate_sample_data()


# サンプルデータ生成関数（フォールバック用）
def generate_sample_data():
    """サンプルデータを生成（contactsテーブルの物理カラムのみ）"""
    np.random.seed(42)
    
    # プロフィール情報（2件のみ詳細設定）
    profiles = [
        # 1件目: 詳細なプロフィール
        "10年間のJava開発経験を持つシステムエンジニア。金融系システムの設計・開発に従事し、Spring Boot、MySQL、AWSを使った大規模システム開発をリード。最近はマイクロサービス化プロジェクトを担当。TOEIC 850点。",
        # 2件目: 詳細なプロフィール  
        "マーケティング戦略コンサルタント。BtoBマーケティング専門で、製造業・IT業界での実績多数。デジタルマーケティング、SEO・SEM、MA導入支援が得意分野。Google Analytics、Salesforce認定資格保持。",
        # 3-30件目: プロフィールなし
        * ([None] * 28)
    ]
    
    # コメント情報（2件のみ詳細設定）
    comments = [
        # 1件目
        "技術力が高く、チームリーダーとしての経験も豊富。金融業界の知識も深い。次回面談でアーキテクト案件を提案予定。",
        # 2件目  
        "戦略的思考力に優れ、クライアントとの折衝能力も高い。BtoB領域でのマーケティング自動化プロジェクトでの起用を検討中。",
        # 3-30件目: コメントなし
        * ([None] * 28)
    ]
    
    # スキル情報（2件のみ詳細設定）
    skills = [
        # 1件目
        "Java, Spring Boot, MySQL, AWS, Docker, Kubernetes, マイクロサービス, システム設計, プロジェクトマネジメント",
        # 2件目
        "マーケティング戦略, デジタルマーケティング, SEO/SEM, MA導入, Google Analytics, Salesforce, データ分析, BtoBマーケティング",
        # 3-30件目: スキルなし
        * ([None] * 28)
    ]
    
    # 職歴情報（2件のみ詳細設定）
    work_histories = [
        # 1件目
        "2019-現在: 株式会社テックソリューション シニアエンジニア\n2015-2019: 金融システム開発会社 システムエンジニア\n2012-2015: ITベンダー プログラマー",
        # 2件目
        "2020-現在: マーケティングコンサル会社 シニアコンサルタント\n2017-2020: 大手広告代理店 マーケティングプランナー\n2014-2017: IT企業 マーケティング担当",
        # 3-30件目: 職歴なし
        * ([None] * 28)
    ]
    
    # プロジェクトアサインメントで使用される実際の名前
    assignment_names = ['山田 太郎', '佐藤 花子', '田中 次郎', '鈴木 一郎']
    assignment_last_names = ['山田', '佐藤', '田中', '鈴木']
    assignment_first_names = ['太郎', '花子', '次郎', '一郎']
    assignment_furigana = ['ヤマダ タロウ', 'サトウ ハナコ', 'タナカ ジロウ', 'スズキ イチロウ']
    assignment_furigana_last = ['ヤマダ', 'サトウ', 'タナカ', 'スズキ']
    assignment_furigana_first = ['タロウ', 'ハナコ', 'ジロウ', 'イチロウ']
    
    # 最初の4件はプロジェクトアサインメントと一致させ、残りは従来通り
    full_names = assignment_names + [f'山田 太郎{i}' for i in range(5, 31)]
    last_names = assignment_last_names + [f'山田{i}' for i in range(5, 31)]
    first_names = assignment_first_names + [f'太郎{i}' for i in range(5, 31)]
    furiganas = assignment_furigana + [f'ヤマダ タロウ{i}' for i in range(5, 31)]
    furigana_lasts = assignment_furigana_last + [f'ヤマダ{i}' for i in range(5, 31)]
    furigana_firsts = assignment_furigana_first + [f'タロウ{i}' for i in range(5, 31)]
    
    # contactsテーブルの実際の物理カラムに基づいたサンプルデータ
    contacts = pd.DataFrame({
        'contact_id': range(1, 31),
        'full_name': full_names,
        'last_name': last_names,
        'first_name': first_names,
        'furigana': furiganas,
        'furigana_last_name': furigana_lasts,
        'furigana_first_name': furigana_firsts,
        'estimated_age': np.random.choice(['20代', '30代', '40代', '50代'], 30),
        'company_name': ['Demo Company サンプル'] * 30,  # サンプルデータ識別用
        'department_name': np.random.choice(['開発部', '営業部', 'マーケティング部', '人事部', '経理部'], 30),
        'position_name': np.random.choice(['部長', '課長', 'マネージャー', '主任', 'スタッフ'], 30),
        'priority_name': np.random.choice(['高', '中', '低'], 30),
        'screening_status': np.random.choice(['精査済み', None], 30),
        'search_date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'created_at': pd.date_range('2024-01-01', periods=30, freq='D'),
        'updated_at': pd.date_range('2024-01-01', periods=30, freq='D'),
        # 全文検索テスト用の詳細カラム
        'profile': profiles,
        'comments': comments,
        'skills': skills,
        'work_history': work_histories
    })
    
    return contacts


def generate_sample_projects():
    """案件管理用サンプルデータを生成"""
    np.random.seed(42)
    
    # サンプル案件データ
    sample_projects = pd.DataFrame({
        'project_id': range(1, 11),
        'project_name': [
            'システム開発案件（金融）',
            'マーケティング戦略コンサル',
            'データ分析システム構築',
            '人事制度改革プロジェクト',
            'ECサイト リニューアル',
            'AI導入コンサルティング',
            'セキュリティ強化プロジェクト',
            '業務効率化システム導入',
            'クラウド移行支援',
            'デジタル変革コンサル'
        ],
        'company_name': [
            'デモ金融株式会社',
            'サンプル商事',
            'テスト製造業',
            'Demo HR Solutions',
            'Sample E-commerce',
            'テストIT企業',
            'Demo Security Corp',
            'サンプル物流',
            'Test Cloud Systems',
            'Demo DX Consulting'
        ],
        'company_id': range(101, 111),  # メール管理で使用するcompany_id
        'department_name': [
            'システム開発部',
            'マーケティング部',
            'データ分析部',
            '人事部',
            'EC事業部',
            'AI開発部',
            'セキュリティ部',
            '業務改善部',
            'インフラ部',
            'DX推進部'
        ],
        'status': np.random.choice(['OPEN', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED'], 10),
        'contract_start_date': pd.date_range('2024-01-01', periods=10, freq='M').strftime('%Y-%m-%d'),
        'contract_end_date': pd.date_range('2024-06-01', periods=10, freq='M').strftime('%Y-%m-%d'),
        'required_headcount': np.random.randint(1, 5, 10),
        'co_manager': np.random.choice(['田中CO', '佐藤CO', '山田CO', '鈴木CO'], 10),
        're_manager': np.random.choice(['高橋RE', '渡辺RE', '伊藤RE', '中村RE'], 10),
        'job_description': [
            '金融システムの設計・開発業務',
            'マーケティング戦略の立案・実行支援',
            'ビッグデータ分析基盤の構築',
            '人事制度の見直しと新制度設計',
            'ECサイトのUI/UX改善とシステム更新',
            'AI技術導入の企画・実装支援',
            'セキュリティ監査と対策実装',
            '業務プロセス改善とシステム導入',
            'オンプレミスからクラウドへの移行',
            'デジタル変革戦略の策定・実行'
        ],
        'requirements': [
            'Java, Spring Boot経験3年以上',
            'マーケティング戦略経験5年以上',
            'Python, SQL, 統計学の知識',
            '人事制度設計経験3年以上',
            'React, Node.js, AWS経験',
            'Python, 機械学習の実務経験',
            'セキュリティ監査資格保持者',
            'BPR経験、システム導入経験',
            'AWS, Azure, GCP いずれかの経験',
            'DX推進、戦略コンサル経験'
        ],
        'employment_type': np.random.choice(['正社員', '契約社員', '業務委託', 'フリーランス'], 10),
        'position_level': np.random.choice(['シニア', 'マネージャー', 'ディレクター', 'エキスパート'], 10),
        'work_location': np.random.choice(['東京都千代田区', '東京都新宿区', '東京都港区', 'リモート可'], 10),
        'min_age': np.random.randint(25, 35, 10),
        'max_age': np.random.randint(40, 55, 10),
        'education_requirement': np.random.choice(['大卒以上', '専門卒以上', '高卒以上', '不問'], 10),
        'required_qualifications': [
            'Oracle認定Java資格',
            'マーケティング検定1級',
            '統計検定2級以上',
            '人事検定資格',
            'AWS認定資格',
            'G検定、E資格',
            'CISSP、CEH',
            'PMP、ITコーディネータ',
            'AWS SAA、Azure Architect',
            '中小企業診断士'
        ],
        'job_classification': np.random.choice(['001 専門的・技術的職業', '002 管理的職業', '003 事務的職業'], 10),
        'priority_name': np.random.choice(['最高', '高', '中', '低'], 10),
        'priority_value': np.random.choice([5, 4, 3, 2], 10),
        'created_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    return sample_projects


def generate_sample_project_assignments():
    """人材アサイン用サンプルデータを生成"""
    np.random.seed(42)
    
    # サンプル人材アサインデータ
    sample_assignments = pd.DataFrame({
        'assignment_id': range(1, 16),
        'project_id': [1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9, 9, 10, 10, 2],
        'contact_id': [1, 2, 3, 1, 4, 2, 3, 4, 1, 2, 3, 4, 1, 2, 4],
        'assignment_status': [
            'ASSIGNED', 'CANDIDATE', 'ASSIGNED', 'INTERVIEW', 'ASSIGNED',
            'COMPLETED', 'ASSIGNED', 'CANDIDATE', 'INTERVIEW', 'ASSIGNED',
            'CANDIDATE', 'REJECTED', 'ASSIGNED', 'CANDIDATE', 'COMPLETED'
        ],
        'created_at': pd.date_range('2024-01-15', periods=15, freq='W').strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': pd.date_range('2024-01-15', periods=15, freq='W').strftime('%Y-%m-%d %H:%M:%S'),
        
        # 関連データ（JOINされた情報として表示用）
        'project_name': [
            'システム開発案件（金融）', 'システム開発案件（金融）', 'マーケティング戦略コンサル',
            'データ分析システム構築', 'データ分析システム構築', '人事制度改革プロジェクト',
            'ECサイト リニューアル', 'AI導入コンサルティング', 'セキュリティ強化プロジェクト',
            '業務効率化システム導入', 'クラウド移行支援', 'クラウド移行支援',
            'デジタル変革コンサル', 'デジタル変革コンサル', 'マーケティング戦略コンサル'
        ],
        'contact_name': [
            '山田 太郎', '佐藤 花子', '田中 次郎', '山田 太郎', '鈴木 一郎',
            '佐藤 花子', '田中 次郎', '鈴木 一郎', '山田 太郎', '佐藤 花子',
            '田中 次郎', '鈴木 一郎', '山田 太郎', '佐藤 花子', '鈴木 一郎'
        ],
        'company_name': [
            'デモ金融株式会社', 'デモ金融株式会社', 'サンプル商事',
            'テスト製造業', 'テスト製造業', 'Demo HR Solutions',
            'Sample E-commerce', 'テストIT企業', 'Demo Security Corp',
            'サンプル物流', 'Test Cloud Systems', 'Test Cloud Systems',
            'Demo DX Consulting', 'Demo DX Consulting', 'サンプル商事'
        ],
        'contact_company': [
            'テクノロジー株式会社', 'イノベーション企業', 'デジタル・ソリューションズ',
            'テクノロジー株式会社', 'グローバル・システムズ', 'イノベーション企業',
            'デジタル・ソリューションズ', 'グローバル・システムズ', 'テクノロジー株式会社',
            'イノベーション企業', 'デジタル・ソリューションズ', 'グローバル・システムズ',
            'テクノロジー株式会社', 'イノベーション企業', 'グローバル・システムズ'
        ],
        'contact_position': [
            'シニアエンジニア', 'マーケティングマネージャー', 'データサイエンティスト',
            'シニアエンジニア', 'プロジェクトマネージャー', 'マーケティングマネージャー',
            'データサイエンティスト', 'プロジェクトマネージャー', 'シニアエンジニア',
            'マーケティングマネージャー', 'データサイエンティスト', 'プロジェクトマネージャー',
            'シニアエンジニア', 'マーケティングマネージャー', 'プロジェクトマネージャー'
        ]
    })
    
    return sample_assignments


# データ操作関数
def insert_contact(contact_data):
    """新規コンタクトを挿入"""
    if supabase is None:
        return None
    response = supabase.table('contacts').insert(contact_data).execute()
    return response


def update_contact(contact_id, update_data):
    """コンタクト情報を更新"""
    if supabase is None:
        return None
    response = supabase.table('contacts').update(update_data).eq('contact_id', contact_id).execute()
    return response


def delete_contact(contact_id):
    """コンタクトを削除"""
    if supabase is None:
        return None
    response = supabase.table('contacts').delete().eq('contact_id', contact_id).execute()
    return response


@st.cache_data(ttl=300)
def fetch_master_data():
    """マスターデータを取得"""
    if supabase is None:
        return {}
    
    masters = {}
    # 統一企業マスタを含む全テーブル
    tables = ['companies', 'target_companies', 'client_companies', 'projects', 'search_assignees', 'priority_levels', 'approach_methods']
    
    for table in tables:
        try:
            response = supabase.table(table).select('*').execute()
            masters[table] = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            masters[table] = pd.DataFrame()
    
    # キー名の統一（コンタクト管理機能との互換性のため）
    masters['priorities'] = masters.get('priority_levels', pd.DataFrame())
    
    return masters


def insert_master_data(table_name, data):
    """マスターデータを挿入"""
    if supabase is None:
        return None
    response = supabase.table(table_name).insert(data).execute()
    return response


def fetch_contact_approaches(contact_id):
    """指定されたコンタクトのアプローチ履歴を取得"""
    if supabase is None:
        return pd.DataFrame()
    
    try:
        # アプローチ履歴を取得（approach_methodsとJOIN）
        response = supabase.table('contact_approaches')\
            .select('*, approach_methods(method_name)')\
            .eq('contact_id', contact_id)\
            .order('approach_order')\
            .execute()
        
        if response.data:
            approaches_data = []
            for approach in response.data:
                approaches_data.append({
                    'approach_id': approach['approach_id'],
                    'approach_date': approach['approach_date'],
                    'approach_method_id': approach['approach_method_id'],
                    'method_name': approach['approach_methods']['method_name'] if approach['approach_methods'] else 'N/A',
                    'approach_order': approach['approach_order']
                })
            return pd.DataFrame(approaches_data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"アプローチ履歴取得エラー: {str(e)}")
        return pd.DataFrame()


def fetch_project_assignments_for_contact(contact_id):
    """指定されたコンタクトの案件アサイン履歴を取得"""
    if supabase is None:
        return pd.DataFrame()
    
    try:
        # 案件アサイン履歴を取得（projectsとJOIN）
        response = supabase.table('project_assignments')\
            .select('*, projects(project_name, project_target_companies(target_companies(company_name)))')\
            .eq('contact_id', contact_id)\
            .order('created_at', desc=True)\
            .execute()
        
        if response.data:
            assignments_data = []
            for assignment in response.data:
                project_info = assignment.get('projects', {})
                company_info = project_info.get('target_companies', {}) if project_info else {}
                
                assignments_data.append({
                    'assignment_id': assignment['assignment_id'],
                    'project_id': assignment['project_id'],
                    'project_name': project_info.get('project_name', 'N/A') if project_info else 'N/A',
                    'company_name': company_info.get('company_name', 'N/A') if company_info else 'N/A',
                    'assignment_status': assignment['assignment_status'],
                    'created_at': assignment.get('created_at')
                })
            return pd.DataFrame(assignments_data)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"案件アサイン履歴取得エラー: {str(e)}")
        return pd.DataFrame()


def main():
    st.title("👥 HR Talent Dashboard")
    st.text("version 0.5")
    
    
    # URLクエリパラメータから現在のページを取得
    query_params = st.query_params
    
    # サイドバーナビゲーション
    st.sidebar.title("📊 メニュー")
    st.sidebar.markdown("---")
    
    pages = {
        # "🏠 ダッシュボード": "dashboard",
        "👥 コンタクト管理": "contacts",
        "🎯 案件管理": "projects",
        "🤝 人材マッチング": "matching",
        # "🔍 検索進捗": "search_progress",
        # "🎯 キーワード検索": "keyword_search",
        "📧 メール管理": "email_management",
        # "🏢 企業管理": "company_management",
        "📥 データインポート": "import",
        "⚙️ マスタ管理": "masters",
        # "📋 DB仕様書": "specifications"
    }
    
    # URLパラメータからページを取得、なければデフォルト
    default_page_key = query_params.get("page", "contacts")
    default_page_name = next((name for name, key in pages.items() if key == default_page_key), "👥 コンタクト管理")
    
    selected_page = st.sidebar.radio("ページを選択", list(pages.keys()), index=list(pages.keys()).index(default_page_name))
    page_key = pages[selected_page]
    
    # URLパラメータを更新
    if query_params.get("page") != page_key:
        st.query_params.update({"page": page_key})
    
    # ページが案件管理以外に変更された場合、案件編集関連のセッション状態をクリア
    if 'current_page_key' not in st.session_state:
        st.session_state.current_page_key = page_key
    elif st.session_state.current_page_key != page_key:
        if st.session_state.current_page_key == "projects" and page_key != "projects":
            # 案件管理から他のページに移動した場合、編集状態をクリア
            clear_project_editing_state()
        st.session_state.current_page_key = page_key
    
    # サンプルデータ使用オプション
    use_sample_data = st.sidebar.checkbox("🎯 サンプルデータを使用", value=True, help="実際のデータが少ない場合に有効にしてください")
    
    # データ更新ボタン
    if st.sidebar.button("🔄 データ更新", use_container_width=True):
        st.cache_data.clear()
        st.sidebar.success("データを更新しました")
        st.rerun()
    
    # ページルーティング
    if page_key == "dashboard":
        show_dashboard(use_sample_data)
    elif page_key == "contacts":
        show_contacts()
    elif page_key == "projects":
        show_projects(use_sample_data)
    elif page_key == "matching":
        show_matching()
    elif page_key == "search_progress":
        show_search_progress()
    elif page_key == "keyword_search":
        show_keyword_search()
    elif page_key == "email_management":
        show_email_management()
    elif page_key == "company_management":
        show_company_management()
    elif page_key == "import":
        show_data_import()
    elif page_key == "masters":
        show_masters()
    elif page_key == "specifications":
        show_specifications()


# 人材紹介会社向けKPIデータ取得関数群
@st.cache_data(ttl=300)
def fetch_recruitment_kpis():
    """人材紹介会社のKPIデータを取得"""
    if supabase is None:
        # サンプルデータを返す
        return generate_sample_recruitment_kpis()
    
    try:
        # 案件データ取得（新しい多対多関係対応）
        projects_response = supabase.table('projects').select(
            '*, client_companies(company_name), project_assignments(assignment_id, assignment_status, contact_id), project_target_companies(id, target_companies(target_company_id, company_name), department_name, priority_levels(priority_id, priority_name, priority_value))'
        ).execute()
        
        # コンタクトデータ取得
        contacts_response = supabase.table('contacts').select(
            '*, target_companies!contacts_target_company_id_fkey(company_name), project_assignments(project_id, assignment_status)'
        ).execute()
        
        # アプローチデータ取得
        approaches_response = supabase.table('contact_approaches').select(
            '*, approach_methods(method_name), contacts(full_name)'
        ).execute()
        
        # 担当者データ取得
        assignees_response = supabase.table('search_assignees').select('*').execute()
        
        return {
            'projects': pd.DataFrame(projects_response.data) if projects_response.data else pd.DataFrame(),
            'contacts': pd.DataFrame(contacts_response.data) if contacts_response.data else pd.DataFrame(),
            'approaches': pd.DataFrame(approaches_response.data) if approaches_response.data else pd.DataFrame(),
            'assignees': pd.DataFrame(assignees_response.data) if assignees_response.data else pd.DataFrame()
        }
    except Exception as e:
        st.warning(f"KPIデータ取得エラー: {str(e)} - サンプルデータを使用します")
        return generate_sample_recruitment_kpis()


def generate_sample_recruitment_kpis():
    """人材紹介会社向けサンプルKPIデータを生成（実データベースとの整合性を保つ）"""
    np.random.seed(42)
    
    # 実際のデータベースから企業とコンタクトデータを取得
    actual_companies = []
    actual_contacts = []
    
    if supabase is not None:
        try:
            # 企業データ取得
            companies_response = supabase.table('target_companies').select('target_company_id, company_name').execute()
            if companies_response.data:
                actual_companies = companies_response.data
            
            # コンタクトデータ取得
            contacts_response = supabase.table('contacts').select(
                'contact_id, full_name, screening_status, target_company_id, target_companies!contacts_target_company_id_fkey(company_name)'
            ).execute()
            if contacts_response.data:
                actual_contacts = contacts_response.data
        except Exception as e:
            st.warning(f"実データ取得エラー: {str(e)} - フォールバックデータを使用")
    
    # フォールバックまたは取得したデータに基づく設定
    if actual_companies:
        company_names = [comp['company_name'] for comp in actual_companies]
    else:
        company_names = ['株式会社サンプル', 'テクノロジー株式会社', 'グローバル商事', 'GIP株式会社']
    
    if actual_contacts:
        contact_data = [(c['contact_id'], c['full_name'], c.get('screening_status', '未実施'),
                        c.get('target_companies', {}).get('company_name', '不明') if c.get('target_companies') else '不明') 
                       for c in actual_contacts]
    else:
        contact_data = [
            (1, '山田太郎', '未実施', '株式会社サンプル'),
            (2, '佐藤花子', '実施済み', '株式会社サンプル'),
            (3, '田中次郎', '実施中', 'テクノロジー株式会社'),
            (4, '鈴木三郎', '未実施', 'グローバル商事')
        ]
    
    # リアルな案件名
    project_names = [
        'システムエンジニア（金融系）', 'データサイエンティスト', 'プロダクトマネージャー',
        'UI/UXデザイナー', 'セールスマネージャー', 'マーケティングスペシャリスト',
        '人事担当者', '経理・財務担当', 'プロジェクトマネージャー', 'ITコンサルタント'
    ]
    
    # 実際の企業データに基づいて案件データを生成
    num_projects = min(len(project_names), len(company_names) * 3)  # 企業数に応じた案件数
    projects = pd.DataFrame({
        'project_id': range(1, num_projects + 1),
        'project_name': project_names[:num_projects],
        'status': np.random.choice(['OPEN', 'CLOSED', 'PENDING'], num_projects, p=[0.6, 0.25, 0.15]),
        'required_headcount': np.random.randint(1, 4, num_projects),
        'target_companies': [{'company_name': company_names[i % len(company_names)]} for i in range(num_projects)],
        'co_manager': np.random.choice(['田中CO', '佐藤CO', '山田CO', '鈴木CO'], num_projects),
        're_manager': np.random.choice(['高橋RE', '渡辺RE', '中村RE', '小林RE'], num_projects),
        'created_at': pd.date_range('2024-01-01', '2024-12-31', periods=num_projects)
    })
    
    # 実際のコンタクトIDに基づいてアサインデータを生成
    actual_contact_ids = [c[0] for c in contact_data]
    project_assignments_data = []
    for project_id in range(1, num_projects + 1):
        # 各案件に1-3人の候補者をアサイン（実際のcontact_idを使用）
        num_candidates = min(np.random.randint(1, 4), len(actual_contact_ids))
        selected_contacts = np.random.choice(actual_contact_ids, num_candidates, replace=False)
        for contact_id in selected_contacts:
            assignment_status = np.random.choice(
                ['候補', '選考中', '成約', '辞退', '見送り'],
                p=[0.3, 0.25, 0.15, 0.2, 0.1]
            )
            project_assignments_data.append({
                'assignment_id': len(project_assignments_data) + 1,
                'project_id': project_id,
                'assignment_status': assignment_status,
                'contact_id': contact_id
            })
    
    # プロジェクトに割り当て情報を追加
    projects['project_assignments'] = projects['project_id'].apply(
        lambda pid: [a for a in project_assignments_data if a['project_id'] == pid]
    )
    
    # 実際のコンタクトデータを使用
    contacts = pd.DataFrame({
        'contact_id': [c[0] for c in contact_data],
        'full_name': [c[1] for c in contact_data],
        'screening_status': [c[2] for c in contact_data],
        'target_companies': [{'company_name': c[3]} for c in contact_data],
        'created_at': pd.date_range('2024-01-01', '2024-12-31', periods=len(contact_data))
    })
    
    # コンタクトごとのプロジェクトアサイン情報を追加
    contacts['project_assignments'] = contacts['contact_id'].apply(
        lambda cid: [a for a in project_assignments_data if a['contact_id'] == cid]
    )
    
    # より現実的なアプローチデータ（過去1年間）
    approaches_data = []
    approach_methods = ['電話', 'メール', 'LinkedIn', '紹介', 'スカウト', '直接コンタクト']
    
    # 実際のコンタクトIDに対してアプローチを生成
    for contact_id in actual_contact_ids:
        # 候補者あたり1-5回のアプローチ
        num_approaches = np.random.randint(1, 6)
        base_date = pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365))
        
        # 実際のコンタクト名を取得
        contact_name = next((c[1] for c in contact_data if c[0] == contact_id), 'Unknown')
        
        for approach_order in range(1, num_approaches + 1):
            # アプローチ間隔は1-30日
            approach_date = base_date + pd.Timedelta(days=np.random.randint(0, 30) * approach_order)
            if approach_date <= pd.Timestamp('2024-12-31'):
                approaches_data.append({
                    'approach_id': len(approaches_data) + 1,
                    'contact_id': contact_id,
                    'approach_date': approach_date,
                    'approach_order': approach_order,
                    'approach_methods': {'method_name': np.random.choice(approach_methods)},
                    'contacts': {'full_name': contact_name}
                })
    
    approaches = pd.DataFrame(approaches_data)
    
    # 担当者データ（CO/RE分離）
    assignees = pd.DataFrame({
        'assignee_id': range(1, 9),
        'assignee_name': ['田中CO', '佐藤CO', '山田CO', '鈴木CO', '高橋RE', '渡辺RE', '中村RE', '小林RE'],
        'role': ['CO', 'CO', 'CO', 'CO', 'RE', 'RE', 'RE', 'RE']
    })
    
    return {
        'projects': projects,
        'contacts': contacts,
        'approaches': approaches,
        'assignees': assignees
    }


def show_dashboard(use_sample_data=False):
    st.subheader("📊 人材紹介ダッシュボード")
    
    # KPIデータ取得
    if use_sample_data:
        kpi_data = generate_sample_recruitment_kpis()
    else:
        kpi_data = fetch_recruitment_kpis()
    projects_df = kpi_data['projects']
    contacts_df = kpi_data['contacts']
    approaches_df = kpi_data['approaches']
    
    # データソース表示
    if use_sample_data:
        st.info(f"🎯 サンプルデータを表示中（案件{len(projects_df)}件、候補者{len(contacts_df)}人）")
    elif not projects_df.empty and 'project_name' in projects_df.columns:
        st.success(f"✅ データベース接続中（案件{len(projects_df)}件、候補者{len(contacts_df)}人）")
    else:
        st.warning("⚠️ データが見つかりません。サンプルデータを使用するには左側のチェックボックスを有効にしてください")
    
    # 🎯 案件管理KPIセクション
    st.markdown("### 🎯 案件管理KPI")
    
    # デバッグ情報を表示
    if st.sidebar.checkbox("🐛 デバッグ情報を表示"):
        st.write("**デバッグ情報:**")
        st.write(f"projects_df empty: {projects_df.empty}")
        if not projects_df.empty:
            st.write(f"projects_df shape: {projects_df.shape}")
            st.write(f"projects_df columns: {list(projects_df.columns)}")
            st.write("**サンプルデータ:**")
            st.write(projects_df.head(3))
    
    if not projects_df.empty:
        # 案件ステータス集計
        if 'status' in projects_df.columns:
            status_counts = projects_df['status'].value_counts()
        else:
            status_counts = pd.Series()
        
        # 候補者総数・成約数計算
        total_candidates = 0
        total_contracts = 0
        
        if 'project_assignments' in projects_df.columns:
            for assignments in projects_df['project_assignments']:
                if isinstance(assignments, list):
                    total_candidates += len(assignments)
                    total_contracts += len([a for a in assignments if isinstance(a, dict) and a.get('assignment_status') == '成約'])
        
        # 成約率計算
        contract_rate = (total_contracts / total_candidates * 100) if total_candidates > 0 else 0
        
        # KPIメトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔓 OPEN案件", status_counts.get('OPEN', 0))
        
        with col2:
            st.metric("✅ 成約案件", status_counts.get('CLOSED', 0))
        
        with col3:
            st.metric("👥 総候補者数", total_candidates)
        
        with col4:
            st.metric("📈 成約率", f"{contract_rate:.1f}%")
        
        # 案件ステータス・候補者数グラフ
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("案件ステータス分布")
            if not status_counts.empty:
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    color_discrete_map={'OPEN': '#FF6B6B', 'CLOSED': '#4ECDC4', 'PENDING': '#FFE66D'}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("データがありません")
        
        with col2:
            st.subheader("案件別候補者数")
            # 案件別候補者数集計
            project_candidates = []
            for _, row in projects_df.iterrows():
                assignments = row['project_assignments'] if isinstance(row['project_assignments'], list) else []
                candidate_count = len(assignments)
                project_candidates.append({
                    'project_name': row['project_name'],
                    'candidates': candidate_count
                })
            
            if project_candidates:
                candidates_df = pd.DataFrame(project_candidates)
                fig_bar = px.bar(
                    candidates_df.head(10),
                    x='project_name',
                    y='candidates',
                    title="案件別候補者数（TOP10）"
                )
                fig_bar.update_layout(xaxis_title="案件名", yaxis_title="候補者数")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("データがありません")
    else:
        st.warning("案件データが見つかりません")
    
    # 👥 人材・候補者KPIセクション
    st.markdown("### 👥 人材・候補者KPI")
    
    if not contacts_df.empty:
        # スクリーニング状況集計
        if 'screening_status' in contacts_df.columns:
            screening_counts = contacts_df['screening_status'].value_counts()
        else:
            screening_counts = pd.Series()
        
        # アサイン状況集計
        active_candidates = 0
        contracted_candidates = 0
        
        if 'project_assignments' in contacts_df.columns:
            for assignments in contacts_df['project_assignments']:
                if isinstance(assignments, list) and len(assignments) > 0:
                    active_candidates += 1
                    if any(isinstance(a, dict) and a.get('assignment_status') == '成約' for a in assignments):
                        contracted_candidates += 1
        
        # 候補者KPIメトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 総候補者数", len(contacts_df))
        
        with col2:
            st.metric("🎯 アクティブ候補者", active_candidates)
        
        with col3:
            st.metric("✅ 成約済み候補者", contracted_candidates)
        
        with col4:
            candidate_success_rate = (contracted_candidates / len(contacts_df) * 100) if len(contacts_df) > 0 else 0
            st.metric("📊 候補者成約率", f"{candidate_success_rate:.1f}%")
        
        # スクリーニング状況・成約状況グラフ
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("スクリーニング状況")
            if not screening_counts.empty:
                fig_screening = px.bar(
                    x=screening_counts.index,
                    y=screening_counts.values,
                    color=screening_counts.index,
                    color_discrete_map={'未実施': '#FFB6C1', '実施中': '#FFE66D', '実施済み': '#90EE90'}
                )
                fig_screening.update_layout(xaxis_title="スクリーニング状況", yaxis_title="候補者数")
                st.plotly_chart(fig_screening, use_container_width=True)
            else:
                st.info("データがありません")
        
        with col2:
            st.subheader("候補者アサイン状況")
            assignment_status = pd.DataFrame({
                'status': ['アクティブ', '待機中', '成約済み'],
                'count': [active_candidates - contracted_candidates, len(contacts_df) - active_candidates, contracted_candidates]
            })
            
            fig_assignment = px.pie(
                assignment_status,
                values='count',
                names='status',
                color_discrete_map={'アクティブ': '#FF6B6B', '待機中': '#FFE66D', '成約済み': '#4ECDC4'}
            )
            st.plotly_chart(fig_assignment, use_container_width=True)
    else:
        st.warning("候補者データが見つかりません")
    
    # 📞 営業・アプローチKPIセクション
    st.markdown("### 📞 営業・アプローチKPI")
    
    if not approaches_df.empty:
        # アプローチ手法別集計
        method_counts = pd.Series()
        if 'approach_methods' in approaches_df.columns:
            methods = [m['method_name'] if isinstance(m, dict) else str(m) for m in approaches_df['approach_methods']]
            method_counts = pd.Series(methods).value_counts()
        
        # アプローチKPIメトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📞 総アプローチ数", len(approaches_df))
        
        with col2:
            unique_contacts = approaches_df['contact_id'].nunique() if 'contact_id' in approaches_df.columns else 0
            st.metric("👤 アプローチ済み候補者", unique_contacts)
        
        with col3:
            avg_approaches = len(approaches_df) / unique_contacts if unique_contacts > 0 else 0
            st.metric("📈 平均アプローチ回数", f"{avg_approaches:.1f}回")
        
        with col4:
            response_rate = np.random.uniform(15, 35)  # サンプル値
            st.metric("📨 レスポンス率", f"{response_rate:.1f}%")
        
        # アプローチ手法・月次推移グラフ
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("アプローチ手法別実績")
            if not method_counts.empty:
                fig_methods = px.bar(
                    x=method_counts.index,
                    y=method_counts.values,
                    color=method_counts.index
                )
                fig_methods.update_layout(xaxis_title="アプローチ手法", yaxis_title="実施回数")
                st.plotly_chart(fig_methods, use_container_width=True)
            else:
                st.info("データがありません")
        
        with col2:
            st.subheader("月次アプローチ推移")
            if 'approach_date' in approaches_df.columns:
                approaches_df['approach_date'] = pd.to_datetime(approaches_df['approach_date'])
                monthly_approaches = approaches_df.groupby(approaches_df['approach_date'].dt.to_period('M')).size()
                
                if not monthly_approaches.empty:
                    fig_monthly = px.line(
                        x=[str(period) for period in monthly_approaches.index],
                        y=monthly_approaches.values,
                        title="月次アプローチ数推移"
                    )
                    fig_monthly.update_layout(xaxis_title="月", yaxis_title="アプローチ数")
                    st.plotly_chart(fig_monthly, use_container_width=True)
                else:
                    st.info("データがありません")
            else:
                st.info("データがありません")
    else:
        st.warning("アプローチデータが見つかりません")
    
    # 📊 パフォーマンス分析セクション
    st.markdown("### 📊 担当者別パフォーマンス")
    
    if not projects_df.empty and 'co_manager' in projects_df.columns and 'status' in projects_df.columns:
        # CO・RE別成約数集計
        closed_projects = projects_df[projects_df['status'] == 'CLOSED']
        co_performance = closed_projects['co_manager'].value_counts() if not closed_projects.empty else pd.Series()
        re_performance = closed_projects['re_manager'].value_counts() if 're_manager' in closed_projects.columns and not closed_projects.empty else pd.Series()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CO別成約実績")
            if not co_performance.empty:
                fig_co = px.bar(
                    x=co_performance.index,
                    y=co_performance.values,
                    color=co_performance.values,
                    color_continuous_scale='viridis'
                )
                fig_co.update_layout(xaxis_title="CO担当者", yaxis_title="成約数")
                st.plotly_chart(fig_co, use_container_width=True)
            else:
                st.info("成約実績データがありません")
        
        with col2:
            st.subheader("RE別成約実績")
            if not re_performance.empty:
                fig_re = px.bar(
                    x=re_performance.index,
                    y=re_performance.values,
                    color=re_performance.values,
                    color_continuous_scale='plasma'
                )
                fig_re.update_layout(xaxis_title="RE担当者", yaxis_title="成約数")
                st.plotly_chart(fig_re, use_container_width=True)
            else:
                st.info("成約実績データがありません")
    else:
        st.warning("担当者データまたは案件ステータスが見つかりません")


def show_contacts():
    st.subheader("👥 コンタクト管理")
    
    # URLパラメータから特定のコンタクト選択をチェック
    query_params = st.query_params
    url_contact_id = query_params.get("contact_id")
    from_projects = query_params.get("from_projects") == "true"
    
    # 案件管理からの遷移の場合、編集タブに直接移動
    if url_contact_id and from_projects:
        # ナビゲーション パンくずリスト
        st.markdown("### 📍 ナビゲーション")
        nav_col1, nav_col2, nav_col3 = st.columns([2, 1, 2])
        with nav_col1:
            st.info("🎯 案件管理")
        with nav_col2:
            st.markdown("**→**")
        with nav_col3:
            st.success("👥 コンタクト詳細")
        st.markdown("---")
        
        st.session_state.selected_contact_id = int(url_contact_id)
        st.session_state.selected_tab = 2  # 編集タブに移動
    
    # session_stateで選択されたタブを管理
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = 0
    
    # タブで機能分割
    # セッション状態に基づいて表示するコンテンツを決める
    if st.session_state.selected_tab == 2:
        # 編集タブを直接表示
        
        # 案件管理からの遷移の場合、上部に戻るボタンを表示
        if from_projects:
            with st.container():
                back_col1, back_col2 = st.columns([1, 4])
                with back_col1:
                    if st.button("⬅️ 案件管理に戻る", key="top_back_to_projects", type="secondary"):
                        # セッション履歴を使用して戻る
                        if hasattr(st.session_state, 'navigation_history') and st.session_state.navigation_history:
                            back_url = st.session_state.navigation_history.get('from_url', '?page=projects')
                            # navigation_historyはクリアしない（案件一覧画面で復元に使用するため）
                        else:
                            back_url = '?page=projects'
                        
                        # URLを解析して適切なパラメータを設定
                        if 'page=projects' in back_url:
                            st.query_params.clear()
                            st.query_params.update({'page': 'projects'})
                        st.rerun()
                st.markdown("---")
        
        st.success("📝 編集対象が選択されました。編集画面を表示しています...")
        show_contacts_edit()
        
        # 編集後にタブをリセット
        st.markdown("---")
        col_back1, col_back2 = st.columns(2)
        with col_back1:
            if st.button("📋 コンタクト一覧に戻る", key="back_from_edit"):
                st.session_state.selected_tab = 0
                if 'selected_contact_id' in st.session_state:
                    del st.session_state.selected_contact_id
                st.rerun()
        with col_back2:
            if from_projects and st.button("🎯 案件管理に戻る", key="back_to_projects"):
                # セッション履歴を使用して戻る
                if hasattr(st.session_state, 'navigation_history') and st.session_state.navigation_history:
                    back_url = st.session_state.navigation_history.get('from_url', '?page=projects')
                    # navigation_historyはクリアしない（案件一覧画面で復元に使用するため）
                else:
                    back_url = '?page=projects'
                
                # URLを解析して適切なパラメータを設定
                if 'page=projects' in back_url:
                    st.query_params.clear()
                    st.query_params.update({'page': 'projects'})
                st.rerun()
        return
    elif st.session_state.selected_tab == 3:
        # 削除タブを直接表示
        st.warning("🗑️ 削除対象が選択されました。削除画面を表示しています...")
        show_contacts_delete()
        # 削除後にタブをリセット
        if st.button("一覧に戻る", key="back_from_delete"):
            st.session_state.selected_tab = 0
            if 'selected_contact_id' in st.session_state:
                del st.session_state.selected_contact_id
            if 'selected_contact_id_from_list' in st.session_state:
                del st.session_state.selected_contact_id_from_list
            st.rerun()
        return
    
    # 通常のタブ表示
    tab_list = st.tabs(["📋 一覧・検索", "📝 新規登録", "✏️ 詳細編集", "🗑️ 削除"])
    
    # 一覧・検索タブ
    with tab_list[0]:
        show_contacts_list()
    
    # 新規登録タブ
    with tab_list[1]:
        show_contacts_create()
    
    # 詳細編集タブ
    with tab_list[2]:
        show_contacts_edit()
        # 編集後にタブをリセット
        if st.button("一覧に戻る", key="back_from_edit_tab"):
            st.session_state.selected_tab = 0
            if 'selected_contact_id' in st.session_state:
                del st.session_state.selected_contact_id
            if 'selected_contact_id_from_list' in st.session_state:
                del st.session_state.selected_contact_id_from_list
            st.rerun()
    
    # 削除タブ
    with tab_list[3]:
        show_contacts_delete()


def show_contacts_list():
    st.markdown("### 📋 コンタクト一覧・検索")
    
    df = fetch_contacts()
    
    if df.empty:
        st.warning("データが見つかりません。")
        return
    
    # サンプルデータかどうかを判定
    is_sample_data = 'company' in df.columns and df['company'].str.contains('Demo Company サンプル', na=False).any()
    
    if is_sample_data:
        st.info("💡 現在表示されているのはデモ用のサンプルデータです。編集・削除機能を使用するには、「新規登録」タブから実際のデータを登録してください。")
    
    # URLパラメータから初期値を取得
    default_search = get_url_param("contact_search", "")
    default_search_all = get_url_param("contact_search_all", "")
    default_company = get_url_param("contact_company", "すべて")
    default_priority = get_url_param("contact_priority", "すべて")
    default_screening = get_url_param("contact_screening", "すべて")
    default_ap = get_url_param("contact_ap", "すべて")
    
    # 検索機能
    col_search1, col_search2 = st.columns(2)
    
    with col_search1:
        search_text = st.text_input("🔍 氏名・フリガナ検索",
                                   value=default_search,
                                   placeholder="氏名またはフリガナを入力してください...")
        if search_text != default_search:
            set_url_param("contact_search", search_text)
    
    with col_search2:
        search_all_text = st.text_input("🔍 全項目検索",
                                       value=default_search_all,
                                       placeholder="プロフィール、コメント、経歴など全項目から検索...")
        if search_all_text != default_search_all:
            set_url_param("contact_search_all", search_all_text)
    
    # フィルター機能
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'company_name' in df.columns:
            companies = ["すべて"] + sorted(df['company_name'].dropna().unique().tolist())
            selected_company = st.selectbox("企業", companies,
                                          index=get_selectbox_index(companies, default_company))
            set_url_param("contact_company", selected_company)
        else:
            selected_company = "すべて"
    
    with col2:
        if 'priority_name' in df.columns:
            priorities = ["すべて"] + sorted(df['priority_name'].dropna().unique().tolist())
            selected_priority = st.selectbox("優先度", priorities,
                                           index=get_selectbox_index(priorities, default_priority))
            set_url_param("contact_priority", selected_priority)
        else:
            selected_priority = "すべて"
    
    with col3:
        screening_statuses = ["すべて", "精査済み", "未精査"]
        selected_screening = st.selectbox("精査状況", screening_statuses,
                                        index=get_selectbox_index(screening_statuses, default_screening))
        set_url_param("contact_screening", selected_screening)
    
    with col4:
        ap_statuses = ["すべて", "AP済み", "未AP"]
        selected_ap = st.selectbox("AP状況", ap_statuses,
                                  index=get_selectbox_index(ap_statuses, default_ap))
        set_url_param("contact_ap", selected_ap)
    
    # フィルター適用
    filtered_df = df.copy()
    
    # full_nameが存在しない場合、先に生成（検索フィルター適用前に必要）
    if 'full_name' not in filtered_df.columns:
        if 'last_name' in filtered_df.columns and 'first_name' in filtered_df.columns:
            filtered_df['full_name'] = filtered_df['last_name'].fillna('') + ' ' + filtered_df['first_name'].fillna('')
            filtered_df['full_name'] = filtered_df['full_name'].str.strip()
        elif 'name' in filtered_df.columns:
            filtered_df['full_name'] = filtered_df['name']
        else:
            filtered_df['full_name'] = '名前未設定'
    
    # 文字列検索フィルター
    # 氏名・フリガナ検索
    if search_text:
        name_filter = pd.Series(False, index=filtered_df.index)
        
        # 氏名で検索
        if 'full_name' in filtered_df.columns:
            name_filter |= filtered_df['full_name'].str.contains(search_text, case=False, na=False)
        
        # フリガナで検索
        if 'furigana' in filtered_df.columns:
            name_filter |= filtered_df['furigana'].str.contains(search_text, case=False, na=False)
        
        filtered_df = filtered_df[name_filter]
    
    # 全項目検索
    if search_all_text:
        all_filter = pd.Series(False, index=filtered_df.index)
        
        # 検索対象の全カラム（テキスト系）
        search_columns = [
            'full_name', 'furigana', 'company_name', 'department_name', 'position_name',
            'profile', 'comments', 'email', 'phone', 'linkedin_url', 'wantedly_url',
            'other_urls', 'work_history', 'skills', 'certifications', 'education',
            'note', 'screening_status', 'priority_name', 'approach_method',
            'last_contact_date', 'next_action'
        ]
        
        for col in search_columns:
            if col in filtered_df.columns:
                all_filter |= filtered_df[col].astype(str).str.contains(search_all_text, case=False, na=False)
        
        filtered_df = filtered_df[all_filter]
    
    if selected_company != "すべて" and 'company_name' in df.columns:
        filtered_df = filtered_df[filtered_df['company_name'] == selected_company]
    
    if selected_priority != "すべて" and 'priority_name' in df.columns:
        filtered_df = filtered_df[filtered_df['priority_name'] == selected_priority]
    
    if selected_screening == "精査済み" and 'screening_status' in df.columns:
        filtered_df = filtered_df[filtered_df['screening_status'].notna()]
    elif selected_screening == "未精査" and 'screening_status' in df.columns:
        filtered_df = filtered_df[filtered_df['screening_status'].isna()]
    
    st.info(f"表示件数: {len(filtered_df)}件 / 全{len(df)}件")
    
    # 詳細なデータ表示（contactsテーブルの全項目表示）
    if not filtered_df.empty:
        st.markdown("### 📋 詳細データ一覧")
        st.markdown("📌 **行をクリックすると詳細情報が表示されます**")
        
        # contactsテーブルの主要項目を表示（一覧用に表示項目を絞る）
        display_columns = []
        column_config = {}
        
        # 一覧表示用の主要カラムのみ
        list_columns = {
            'contact_id': "ID",
            'full_name': "氏名",
            'furigana': "フリガナ",
            'company_name': "企業名",
            'department_name': "部署",
            'position_name': "役職",
            'priority_name': "優先度",
            'screening_status': "精査状況",
            'search_date': ("検索日", st.column_config.DateColumn("検索日"))
        }
        
        # 重複処理を回避するため、既に処理済みの場合はスキップ
        
        for col_name, config in list_columns.items():
            if col_name in filtered_df.columns:
                display_columns.append(col_name)
                if isinstance(config, tuple):
                    column_config[col_name] = config[1]
                else:
                    column_config[col_name] = config
        
        if display_columns:
            # 選択可能なデータフレームとして表示
            selected_row = st.dataframe(
                filtered_df[display_columns].fillna(''),
                use_container_width=True,
                hide_index=True,
                column_config=column_config,
                height=400,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # 行が選択された場合、詳細情報を表示
            if selected_row and selected_row.selection and selected_row.selection.rows:
                selected_index = selected_row.selection.rows[0]
                selected_contact = filtered_df.iloc[selected_index]
                
                # 選択されたコンタクトIDをsession_stateに保存（他のタブでも使用可能にする）
                if 'contact_id' in selected_contact.index:
                    st.session_state.selected_contact_id_from_list = selected_contact['contact_id']
                
                # 詳細情報表示エリア
                st.markdown("---")
                st.markdown("### 👤 人材詳細情報")
                
                # 基本情報カード
                col_basic1, col_basic2, col_basic3 = st.columns(3)
                
                with col_basic1:
                    st.markdown("#### 📋 基本情報")
                    if 'full_name' in selected_contact.index and pd.notna(selected_contact['full_name']):
                        st.metric("氏名", selected_contact['full_name'])
                    if 'furigana' in selected_contact.index and pd.notna(selected_contact['furigana']):
                        st.text(f"フリガナ: {selected_contact['furigana']}")
                    if 'estimated_age' in selected_contact.index and pd.notna(selected_contact['estimated_age']):
                        st.text(f"推定年齢: {selected_contact['estimated_age']}")
                    if 'birth_date' in selected_contact.index and pd.notna(selected_contact['birth_date']):
                        st.text(f"生年月日: {selected_contact['birth_date']}")
                    if 'actual_age' in selected_contact.index and pd.notna(selected_contact['actual_age']):
                        st.text(f"実年齢: {selected_contact['actual_age']}歳")
                    if 'contact_id' in selected_contact.index:
                        st.text(f"ID: {selected_contact['contact_id']}")
                
                with col_basic2:
                    st.markdown("#### 🏢 所属情報")
                    if 'company_name' in selected_contact.index and pd.notna(selected_contact['company_name']):
                        st.metric("企業名", selected_contact['company_name'])
                    if 'department_name' in selected_contact.index and pd.notna(selected_contact['department_name']):
                        st.text(f"部署: {selected_contact['department_name']}")
                    if 'position_name' in selected_contact.index and pd.notna(selected_contact['position_name']):
                        st.text(f"役職: {selected_contact['position_name']}")
                
                with col_basic3:
                    st.markdown("#### 📊 ステータス")
                    if 'priority_name' in selected_contact.index and pd.notna(selected_contact['priority_name']):
                        priority_color = {
                            '高': '🔴',
                            '中': '🟡',
                            '低': '🔵'
                        }.get(selected_contact['priority_name'], '⚪')
                        st.metric("優先度", f"{priority_color} {selected_contact['priority_name']}")
                    if 'screening_status' in selected_contact.index:
                        status = "✅ 精査済み" if pd.notna(selected_contact['screening_status']) else "⏳ 未精査"
                        st.text(f"精査状況: {status}")
                    if 'search_date' in selected_contact.index and pd.notna(selected_contact['search_date']):
                        st.text(f"検索日: {selected_contact['search_date']}")
                
                # 紐付け案件情報を表示
                if 'contact_id' in selected_contact.index:
                    show_contact_project_assignments(selected_contact['contact_id'])
                
                # 詳細情報タブ
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 プロフィール", "💬 コメント", "📧 コンタクト履歴", "🔗 リンク・検索情報", "📊 全データ"])
                
                with tab1:
                    # プロフィール関連情報を包括的に表示
                    if 'profile' in selected_contact.index and pd.notna(selected_contact['profile']):
                        st.text_area("プロフィール詳細", selected_contact['profile'], height=200, disabled=True)
                    
                    # 職歴・スキル情報
                    col_prof1, col_prof2 = st.columns(2)
                    with col_prof1:
                        if 'career_history' in selected_contact.index and pd.notna(selected_contact['career_history']):
                            st.text_area("職歴", selected_contact['career_history'], height=100, disabled=True)
                        if 'skills' in selected_contact.index and pd.notna(selected_contact['skills']):
                            st.text(f"スキル: {selected_contact['skills']}")
                    with col_prof2:
                        if 'education' in selected_contact.index and pd.notna(selected_contact['education']):
                            st.text_area("学歴", selected_contact['education'], height=100, disabled=True)
                        if 'certifications' in selected_contact.index and pd.notna(selected_contact['certifications']):
                            st.text(f"資格: {selected_contact['certifications']}")
                    
                    if not any(key in selected_contact.index and pd.notna(selected_contact[key]) 
                              for key in ['profile', 'career_history', 'skills', 'education', 'certifications']):
                        st.info("プロフィール情報はありません")
                
                with tab2:
                    # すべてのコメント関連フィールドを表示
                    comment_fields = [
                        ('primary_screening_comment', '一次精査コメント'),
                        ('work_comment', '作業コメント'),
                        ('approach_comment', 'アプローチコメント'),
                        ('interview_comment', '面談コメント'),
                        ('evaluation_comment', '評価コメント'),
                        ('internal_notes', '社内メモ')
                    ]
                    
                    has_comments = False
                    for field, label in comment_fields:
                        if field in selected_contact.index and pd.notna(selected_contact[field]):
                            st.text_area(label, selected_contact[field], height=80, disabled=True)
                            has_comments = True
                    
                    if not has_comments:
                        st.info("コメントはありません")
                
                with tab3:
                    # コンタクト履歴関連の全情報
                    contact_fields = [
                        ('email_trial_history', 'メール履歴'),
                        ('call_history', '電話履歴'),
                        ('meeting_history', '面談履歴'),
                        ('last_contact_date', '最終コンタクト日'),
                        ('next_action_date', '次回アクション予定日'),
                        ('contact_status', 'コンタクトステータス')
                    ]
                    
                    has_contact_info = False
                    for field, label in contact_fields:
                        if field in selected_contact.index and pd.notna(selected_contact[field]):
                            if 'history' in field:
                                st.text_area(label, selected_contact[field], height=100, disabled=True)
                            else:
                                st.text(f"{label}: {selected_contact[field]}")
                            has_contact_info = True
                    
                    if not has_contact_info:
                        st.info("コンタクト履歴はありません")
                
                with tab4:
                    # リンクと検索関連情報
                    col_link1, col_link2 = st.columns(2)
                    with col_link1:
                        st.markdown("**🔗 リンク情報**")
                        if 'url' in selected_contact.index and pd.notna(selected_contact['url']):
                            st.markdown(f"プロフィールURL: [{selected_contact['url']}]({selected_contact['url']})")
                        if 'linkedin_url' in selected_contact.index and pd.notna(selected_contact['linkedin_url']):
                            st.markdown(f"LinkedIn: [{selected_contact['linkedin_url']}]({selected_contact['linkedin_url']})")
                        if 'resume_url' in selected_contact.index and pd.notna(selected_contact['resume_url']):
                            st.markdown(f"履歴書: [{selected_contact['resume_url']}]({selected_contact['resume_url']})")
                    
                    with col_link2:
                        st.markdown("**🔍 検索情報**")
                        if 'name_search_key' in selected_contact.index and pd.notna(selected_contact['name_search_key']):
                            st.text(f"検索キー: {selected_contact['name_search_key']}")
                        # search_assigneeを優先表示（名前）、なければsearch_assignee_id
                        if 'search_assignee' in selected_contact.index and pd.notna(selected_contact['search_assignee']):
                            st.text(f"検索担当者: {selected_contact['search_assignee']}")
                        elif 'search_assignee_id' in selected_contact.index and pd.notna(selected_contact['search_assignee_id']):
                            st.text(f"検索担当者ID: {selected_contact['search_assignee_id']}")
                        if 'search_date' in selected_contact.index and pd.notna(selected_contact['search_date']):
                            st.text(f"検索日: {selected_contact['search_date']}")
                        if 'search_source' in selected_contact.index and pd.notna(selected_contact['search_source']):
                            st.text(f"検索ソース: {selected_contact['search_source']}")
                        if 'search_method' in selected_contact.index and pd.notna(selected_contact['search_method']):
                            st.text(f"検索方法: {selected_contact['search_method']}")
                
                with tab5:
                    # すべてのデータを表形式で表示
                    st.markdown("**📊 登録されている全データ**")
                    
                    # フィールド名の日本語マッピング
                    field_mapping = {
                        'contact_id': 'コンタクトID',
                        'target_company_id': '対象企業ID',
                        'full_name': '氏名',
                        'last_name': '姓',
                        'first_name': '名',
                        'furigana': 'フリガナ',
                        'furigana_last_name': 'フリガナ（姓）',
                        'furigana_first_name': 'フリガナ（名）',
                        'estimated_age': '推定年齢',
                        'profile': 'プロフィール',
                        'url': 'プロフィールURL',
                        'screening_status': '精査状況',
                        'primary_screening_comment': '一次精査コメント',
                        'priority_id': '優先度ID',
                        'priority_name': '優先度',
                        'priority_value': '優先度値',
                        'name_search_key': '検索キー',
                        'work_comment': '作業コメント',
                        'search_assignee_id': '検索担当者ID',
                        'search_assignee': '検索担当者',
                        'search_date': '検索日',
                        'email_trial_history': 'メール履歴',
                        'department_name': '部署名',
                        'department_id': '部署ID',
                        'position_name': '役職名',
                        'company_name': '企業名',
                        'company': '企業',
                        'created_at': '登録日時',
                        'updated_at': '更新日時'
                    }
                    
                    # データを整形して表示
                    all_data = []
                    for key, value in selected_contact.items():
                        if pd.notna(value) and key not in ['target_companies', 'priority_levels', 'search_assignees']:  # 関連テーブルは除外（別途処理済み）
                            # 日付型の場合は文字列に変換
                            if isinstance(value, (pd.Timestamp, datetime, date)):
                                value = str(value)
                            
                            # フィールド名を日本語に変換
                            display_name = field_mapping.get(key, key)
                            
                            all_data.append({
                                'フィールド名': display_name,
                                '内部名': key,
                                '値': str(value)[:200] if len(str(value)) > 200 else str(value)  # 長すぎる場合は切り詰め
                            })
                    
                    if all_data:
                        df_all = pd.DataFrame(all_data)
                        st.dataframe(df_all, use_container_width=True, height=400)
                        
                        # データエクスポートボタン
                        if st.button("📥 全データをCSV形式でダウンロード", key="export_data"):
                            csv = df_all.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="CSVファイルをダウンロード",
                                data=csv,
                                file_name=f"contact_{selected_contact.get('contact_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.info("表示可能なデータがありません")
                
                # システム情報の表示（フッター）
                st.markdown("---")
                col_sys1, col_sys2, col_sys3 = st.columns(3)
                with col_sys1:
                    if 'created_at' in selected_contact.index and pd.notna(selected_contact['created_at']):
                        st.caption(f"登録日時: {selected_contact['created_at']}")
                with col_sys2:
                    if 'updated_at' in selected_contact.index and pd.notna(selected_contact['updated_at']):
                        st.caption(f"更新日時: {selected_contact['updated_at']}")
                with col_sys3:
                    if 'updated_by' in selected_contact.index and pd.notna(selected_contact['updated_by']):
                        st.caption(f"最終更新者: {selected_contact['updated_by']}")
                
                # アクションボタン
                st.markdown("---")
                col_action1, col_action2, col_action3 = st.columns(3)
                with col_action1:
                    if st.button("✏️ この人材を編集", use_container_width=True):
                        # 選択されたコンタクトIDをsession_stateに保存
                        st.session_state.selected_contact_id = selected_contact['contact_id']
                        st.session_state.selected_tab = 2  # 詳細編集タブ（インデックス2）に移動
                        st.rerun()
                with col_action2:
                    if st.button("📋 データをコピー", use_container_width=True):
                        # 選択された人材の全データを文字列に変換
                        contact_text = "\n".join([f"{k}: {v}" for k, v in selected_contact.items() if pd.notna(v)])
                        st.code(contact_text)
                with col_action3:
                    if st.button("🗑️ この人材を削除", use_container_width=True):
                        # 選択されたコンタクトIDをsession_stateに保存
                        st.session_state.selected_contact_id = selected_contact['contact_id']
                        st.session_state.selected_tab = 3  # 削除タブ（インデックス3）に移動
                        st.rerun()
    else:
        st.info("フィルター条件に一致するデータがありません")


def show_add_contact():
    st.subheader("📝 新規コンタクト登録")
    
    masters = fetch_master_data()
    
    with st.form("new_contact_form", clear_on_submit=True):
        st.markdown("### 基本情報")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 企業選択
            if not masters['target_companies'].empty:
                company_options = [""] + masters['target_companies']['company_name'].tolist()
                selected_company = st.selectbox("企業名 *", company_options)
            else:
                selected_company = st.text_input("企業名 *", placeholder="手動入力")
            
            # 姓・名を分けて入力
            col_name1, col_name2 = st.columns(2)
            with col_name1:
                last_name = st.text_input("姓 *", placeholder="山田")
            with col_name2:
                first_name = st.text_input("名 *", placeholder="太郎")
            
            # フリガナも姓・名に分けて入力
            col_furigana1, col_furigana2 = st.columns(2)
            with col_furigana1:
                furigana_last_name = st.text_input("フリガナ（姓）", placeholder="ヤマダ")
            with col_furigana2:
                furigana_first_name = st.text_input("フリガナ（名）", placeholder="タロウ")
            estimated_age = st.text_input("推定年齢", placeholder="30代")
            
            # 生年月日と実年齢
            from datetime import datetime
            min_date = datetime(1900, 1, 1).date()  # 1900年から選択可能
            max_date = date.today()  # 今日まで選択可能
            birth_date = st.date_input("生年月日", value=None, format="YYYY-MM-DD", min_value=min_date, max_value=max_date, key="create_birth_date")
            
            # 生年月日から実年齢を自動計算
            if birth_date:
                today = date.today()
                actual_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                st.text_input("実年齢", value=f"{actual_age}歳", disabled=True)
            else:
                actual_age = None
                st.text_input("実年齢", value="生年月日を選択してください", disabled=True)
        
        with col2:
            # 部署名入力（文字列）
            selected_department = st.text_input("部署名", placeholder="営業部、開発部など")
            
            # 役職入力（文字列）
            selected_position = st.text_input("役職", placeholder="部長、課長、マネージャーなど")
            
            # 優先度選択
            if not masters['priority_levels'].empty:
                priority_options = masters['priority_levels'][['priority_id', 'priority_name']].values.tolist()
                priority_display = [f"{name}" for _, name in priority_options]
                selected_priority_display = st.selectbox("優先度 *", [""] + priority_display)
            else:
                selected_priority_display = st.selectbox("優先度 *", ["", "高", "中", "低"])
        
        st.markdown("### 詳細情報")
        
        col3, col4 = st.columns(2)
        
        with col3:
            profile = st.text_area("プロフィール", height=100)
            url = st.text_input("URL")
        
        with col4:
            work_comment = st.text_area("作業コメント", height=100)
        
        st.markdown("### 作業情報")
        
        col5, col6 = st.columns(2)
        
        with col5:
            # 検索担当者
            if not masters['search_assignees'].empty:
                assignee_options = [""] + masters['search_assignees']['assignee_name'].tolist()
                selected_assignee = st.selectbox("検索担当者", assignee_options)
            else:
                selected_assignee = st.text_input("検索担当者", placeholder="手動入力")
            
            search_date = st.date_input("検索日", value=date.today())
        
        with col6:
            # 複数AP履歴の入力
            st.markdown("**AP履歴（最大3件）**")
            ap_dates = []
            ap_methods = []
            
            for i in range(1, 4):
                with st.expander(f"AP履歴 {i}", expanded=(i == 1)):
                    col_ap1, col_ap2 = st.columns(2)
                    with col_ap1:
                        ap_date = st.date_input(f"AP日{i}", value=None, key=f"new_ap_date_{i}")
                        ap_dates.append(ap_date)
                    
                    with col_ap2:
                        if not masters['approach_methods'].empty:
                            method_options = [""] + masters['approach_methods']['method_name'].tolist()
                            selected_method = st.selectbox(f"AP手法{i}", method_options, key=f"new_method_{i}")
                        else:
                            selected_method = st.text_input(f"AP手法{i}", placeholder="手動入力", key=f"new_method_{i}")
                        ap_methods.append(selected_method)
        
        st.markdown("### 🏢 勤務地情報")
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            postal_code = st.text_input("郵便番号", placeholder="123-4567")
        
        with col8:
            address = st.text_input("勤務地住所", placeholder="東京都渋谷区...")
        
        with col9:
            building_name = st.text_input("勤務地ビル名", placeholder="○○ビル 5F")
        
        submitted = st.form_submit_button("🎯 登録", use_container_width=True, type="primary")
        
        if submitted:
            # バリデーション
            if not last_name or not first_name or not selected_company or not selected_priority_display:
                st.error("姓、名、企業名、優先度は必須項目です。")
                return
            
            try:

                # IDを取得する関数
                def get_id_from_name(df, name_col, name_val, id_col):
                    if not name_val or df.empty:
                        return None
                    result = df[df[name_col] == name_val]
                    return result.iloc[0][id_col] if not result.empty else None
                
                # 各IDを取得
                target_company_id = get_id_from_name(masters['target_companies'], 'company_name', selected_company, 'target_company_id')
                assignee_id = get_id_from_name(masters['search_assignees'], 'assignee_name', selected_assignee, 'assignee_id')
                
                # 優先度IDの取得
                priority_id = None
                if selected_priority_display and not masters['priority_levels'].empty:
                    priority_idx = priority_display.index(selected_priority_display)
                    priority_id = priority_options[priority_idx][0]
                elif selected_priority_display:
                    # マニュアル入力の場合、デフォルト値
                    priority_mapping = {"高": 1, "中": 2, "低": 3}
                    priority_id = priority_mapping.get(selected_priority_display, 2)
                
                # データ準備
                full_name = last_name + first_name  # 姓名を結合してfull_nameも保存
                full_furigana = (furigana_last_name or '') + (furigana_first_name or '') if (furigana_last_name or furigana_first_name) else None
                
                contact_data = {
                    'target_company_id': target_company_id,
                    'full_name': full_name,
                    'last_name': last_name,
                    'first_name': first_name,
                    'furigana': full_furigana,  # 従来の互換性のため結合したフリガナも保存
                    'furigana_last_name': furigana_last_name if furigana_last_name else None,
                    'furigana_first_name': furigana_first_name if furigana_first_name else None,
                    'department_name': selected_department if selected_department else None,
                    'position_name': selected_position if selected_position else None,
                    'estimated_age': estimated_age if estimated_age else None,
                    'birth_date': birth_date.isoformat() if birth_date else None,
                    'actual_age': actual_age if actual_age else None,
                    'profile': profile if profile else None,
                    'url': url if url else None,
                    'work_comment': work_comment if work_comment else None,
                    'search_assignee_id': assignee_id,
                    'search_date': search_date.isoformat() if search_date else None,
                    'priority_id': priority_id
                }
                
                # データ挿入
                response = insert_contact(contact_data)
                if response:
                    contact_id = response.data[0]['contact_id'] if response.data else None
                    
                    # 勤務地情報の挿入
                    if contact_id and (postal_code or address or building_name):
                        work_location_data = {
                            'contact_id': contact_id,
                            'postal_code': postal_code if postal_code else None,
                            'work_address': address if address else None,
                            'building_name': building_name if building_name else None
                        }
                        try:
                            supabase.table('work_locations').insert(work_location_data).execute()
                        except Exception as e:
                            st.warning(f"勤務地情報の登録でエラー: {str(e)}")
                    
                    # AP履歴の挿入（contact_approachesテーブル）
                    if contact_id:
                        for i, (ap_date, ap_method) in enumerate(zip(ap_dates, ap_methods), 1):
                            if ap_date and ap_method:
                                # AP手法IDを取得
                                method_id = get_id_from_name(masters['approach_methods'], 'method_name', ap_method, 'method_id')
                                if method_id:
                                    approach_data = {
                                        'contact_id': contact_id,
                                        'approach_date': ap_date.isoformat(),
                                        'approach_method_id': method_id,
                                        'approach_order': i
                                    }
                                    try:
                                        supabase.table('contact_approaches').insert(approach_data).execute()
                                    except Exception as e:
                                        st.warning(f"AP履歴{i}の登録でエラー: {str(e)}")
                    
                    st.success("✅ コンタクトが正常に登録されました！")
                    st.cache_data.clear()
                else:
                    st.error("❌ 登録に失敗しました")
                
            except Exception as e:
                st.error(f"❌ 登録エラー: {str(e)}")


def show_projects(use_sample_data=False):
    st.subheader("🎯 案件管理")
    
    # session_stateで選択されたタブを管理
    if 'selected_project_tab' not in st.session_state:
        st.session_state.selected_project_tab = 0
    
    # タブで機能分割
    # セッション状態に基づいて表示するコンテンツを決める
    if st.session_state.selected_project_tab == 2:
        # 編集タブを直接表示
        st.success("📝 編集対象が選択されました。編集画面を表示しています...")
        show_projects_edit()
        # 編集後にタブをリセット
        if st.button("一覧に戻る", key="back_from_project_edit"):
            clear_project_editing_state()
            st.session_state.selected_project_tab = 0
            st.rerun()
        return
    elif st.session_state.selected_project_tab == 3:
        # 削除タブを直接表示
        st.warning("🗑️ 削除対象が選択されました。削除画面を表示しています...")
        show_projects_delete()
        # 削除後にタブをリセット
        if st.button("一覧に戻る", key="back_from_project_delete"):
            st.session_state.selected_project_tab = 0
            if 'selected_project_id' in st.session_state:
                del st.session_state.selected_project_id
            st.rerun()
        return
    
    # 通常のタブ表示
    tab_list = st.tabs(["📋 一覧・検索", "📝 新規登録", "✏️ 詳細編集", "🗑️ 削除", "👥 人材アサイン"])
    
    # タブ切り替え時の状態管理を改善
    current_tab = 0  # デフォルトは一覧タブ
    
    # 一覧・検索タブ
    with tab_list[0]:
        show_projects_list(use_sample_data)
    
    # 新規登録タブ
    with tab_list[1]:
        show_projects_create()
    
    # 詳細編集タブ
    with tab_list[2]:
        # タブが切り替わった際の状態確認
        if current_tab != 2:
            # 編集タブに初めて入った時のメッセージ
            if 'current_editing_project_id' not in st.session_state and 'selected_project_id_from_list' not in st.session_state:
                st.info("💡 編集する案件を選択してください。一覧タブで案件を選択してから編集タブをご利用いただくと便利です。")
        show_projects_edit()
    
    # 削除タブ
    with tab_list[3]:
        show_projects_delete()
    
    # 人材アサインタブ
    with tab_list[4]:
        show_project_assignments_tab()


def show_projects_list(use_sample_data=False):
    """案件一覧・検索画面"""
    st.markdown("### 📋 案件一覧・検索")
    
    # URLパラメータから選択状態を取得
    query_params = st.query_params
    
    
    # ナビゲーション履歴から復元すべき状態をチェック
    should_restore_state = False
    restored_project_id = None
    if hasattr(st.session_state, 'navigation_history') and st.session_state.navigation_history:
        nav_history = st.session_state.navigation_history
        default_status = nav_history.get('filter_status', query_params.get("project_status", "すべて"))
        default_company = nav_history.get('filter_company', query_params.get("project_company", "すべて"))
        # 案件管理からの戻りの場合
        if nav_history.get('from_page') == 'projects':
            should_restore_state = True
            restored_project_id = nav_history.get('selected_project_id') or nav_history.get('expanded_project')
            # 復元メッセージは表示しない（ユーザーからの要望により削除）
        # セッション状態に復元フラグを設定
        st.session_state.restore_project_state = should_restore_state
        st.session_state.restored_project_id = restored_project_id
    else:
        default_status = query_params.get("project_status", "すべて")
        default_company = query_params.get("project_company", "すべて")
    
    # プロジェクト一覧を取得
    try:
        projects_query = supabase.table("projects").select("""
            *,
            client_companies(company_name),
            project_target_companies(
                id,
                target_company_id,
                target_companies(company_name),
                department_name
            )
        """).execute()
        
        if projects_query.data:
            projects_df = pd.DataFrame(projects_query.data)
        else:
            projects_df = pd.DataFrame()
    except Exception as e:
        st.error(f"案件データの取得に失敗しました: {e}")
        projects_df = pd.DataFrame()
    
    if not projects_df.empty:
        # サンプルデータかどうかを判定
        is_sample_data = 'company_name' in projects_df.columns and projects_df['company_name'].str.contains('デモ|サンプル|テスト|Demo|Sample|Test', na=False).any()
        
        if is_sample_data:
            st.info("💡 現在表示されているのは案件管理のデモ用サンプルデータです。実際の案件を管理するには、「新規案件」タブから案件を登録してください。")
        
        # フィルター
        col1, col2, col3 = st.columns(3)
        with col1:
            # 案件名検索
            project_name_search = st.text_input("🔍 案件名で検索", placeholder="案件名を入力...", key="project_name_search")
            
        with col2:
            if 'status' in projects_df.columns:
                status_options = ["すべて"] + sorted(projects_df['status'].dropna().unique().tolist())
                # デフォルト値のインデックスを取得
                default_status_index = status_options.index(default_status) if default_status in status_options else 0
                selected_status = st.selectbox("ステータス", status_options, index=default_status_index, key="project_filter_status_select")
                # フィルタ状態を保存
                st.session_state.project_filter_status = selected_status
            else:
                selected_status = "すべて"
        
        with col3:
            if 'project_target_companies' in projects_df.columns:

                # project_target_companiesから企業名を抽出
                def extract_company_names(ptc_list):
                    if not ptc_list or not isinstance(ptc_list, list):
                        return []
                    companies = []
                    for ptc in ptc_list:
                        if ptc.get('target_companies') and ptc['target_companies'].get('company_name'):
                            companies.append(ptc['target_companies']['company_name'])
                    return companies
                
                all_companies = []
                for ptc_list in projects_df['project_target_companies']:
                    all_companies.extend(extract_company_names(ptc_list))
                
                unique_companies = list(set([c for c in all_companies if c]))
                company_options = ["すべて"] + sorted(unique_companies)
                # デフォルト値のインデックスを取得
                default_company_index = company_options.index(default_company) if default_company in company_options else 0
                selected_company = st.selectbox("企業", company_options, index=default_company_index, key="project_filter_company_select")
                # フィルタ状態を保存
                st.session_state.project_filter_company = selected_company
            else:
                selected_company = "すべて"
        
        # URLパラメータを更新
        st.query_params["project_status"] = selected_status
        st.query_params["project_company"] = selected_company
        
        # フィルター適用
        filtered_projects = projects_df.copy()
        
        # 案件名検索フィルター
        if project_name_search:
            if 'project_name' in filtered_projects.columns:
                filtered_projects = filtered_projects[
                    filtered_projects['project_name'].str.contains(project_name_search, case=False, na=False)
                ]
        
        # ステータスフィルター
        if selected_status != "すべて":
            filtered_projects = filtered_projects[filtered_projects['status'] == selected_status]
            
        # 企業フィルター
        if selected_company != "すべて":

            # project_target_companiesから該当する企業を含む案件をフィルター
            def has_company(ptc_list):
                if not ptc_list or not isinstance(ptc_list, list):
                    return False
                for ptc in ptc_list:
                    if ptc.get('target_companies') and ptc['target_companies'].get('company_name') == selected_company:
                        return True
                return False
            
            company_mask = projects_df['project_target_companies'].apply(has_company)
            filtered_projects = filtered_projects[company_mask]
        
        st.info(f"表示件数: {len(filtered_projects)}件 / 全{len(projects_df)}件")
        
        # コンタクト管理と同じパターン：選択可能なテーブル表示
        # 基本情報テーブル表示
        display_columns = ['project_id', 'project_name', 'status', 'contract_start_date', 'contract_end_date', 'required_headcount']
        column_config = {
            'project_id': 'ID',
            'project_name': '案件名',
            'status': 'ステータス',
            'contract_start_date': st.column_config.DateColumn('契約開始日'),
            'contract_end_date': st.column_config.DateColumn('契約終了日'),
            'required_headcount': '必要人数'
        }
        
        # 新しいスキーマ対応: project_target_companies経由で企業名取得
        if 'project_target_companies' in filtered_projects.columns:

            def extract_company_names_for_display(ptc_list):
                if not ptc_list:
                    return ''
                if isinstance(ptc_list, list):
                    companies = []
                    for ptc in ptc_list:
                        if ptc.get('target_companies') and ptc['target_companies'].get('company_name'):
                            companies.append(ptc['target_companies']['company_name'])
                    return ', '.join(companies)
                return ''
            
            filtered_projects['company_name'] = filtered_projects['project_target_companies'].apply(extract_company_names_for_display)
            display_columns.append('company_name')
            column_config['company_name'] = '企業名'
        
        # 新しいスキーマ対応: project_target_companies経由で部署名取得
        if 'project_target_companies' in filtered_projects.columns:

            def extract_companies_and_departments(ptc_list):
                if not ptc_list:
                    return ''
                if isinstance(ptc_list, list):
                    company_dept_list = []
                    for ptc in ptc_list:
                        if ptc.get('target_companies'):
                            company_name = ptc['target_companies'].get('company_name', '不明')
                            dept_name = ptc.get('department_name', '')
                            priority_info = ptc.get('priority_levels', {})
                            priority_name = priority_info.get('priority_name', '') if priority_info else ''
                            priority_value = priority_info.get('priority_value', '') if priority_info else ''
                            
                            # 表示文字列を構築
                            display_parts = [company_name]
                            if dept_name:
                                display_parts.append(f"({dept_name})")
                            if priority_name:
                                display_parts.append(f"[{priority_name}:{priority_value}]")
                            
                            company_dept_list.append(''.join(display_parts))
                    return ', '.join(company_dept_list)
                return ''
            
            filtered_projects['target_companies_list'] = filtered_projects['project_target_companies'].apply(extract_companies_and_departments)
            display_columns.append('target_companies_list')
            column_config['target_companies_list'] = 'ターゲット企業・部署'
        
        available_columns = [col for col in display_columns if col in filtered_projects.columns]
        
        if available_columns:
            # プロジェクト選択オプションを準備
            project_options = ["案件を選択してください..."] + [
                f"{row.get('project_name', 'N/A')} (ID: {row.get('project_id')}) - {row.get('status', 'N/A')}"
                for _, row in filtered_projects.iterrows()
            ]
            
            # デフォルト選択インデックスの決定
            default_index = 0
            
            # 1. 復元対象の案件IDがある場合
            restored_project_id = None
            if (hasattr(st.session_state, 'restore_project_state') and st.session_state.restore_project_state and
                hasattr(st.session_state, 'restored_project_id') and st.session_state.restored_project_id):
                restored_project_id = st.session_state.restored_project_id
                # 復元メッセージは表示しない（ユーザーからの要望により削除）
                
                
                # ナビゲーション履歴からselectboxの選択状態も復元
                if (hasattr(st.session_state, 'navigation_history') and 
                    st.session_state.navigation_history and 
                    'selectbox_selection' in st.session_state.navigation_history):
                    saved_selection = st.session_state.navigation_history['selectbox_selection']
                    if 0 <= saved_selection < len(project_options):
                        default_index = saved_selection
                        st.session_state.project_selector = saved_selection
                else:
                    # fallback: project_idでselectbox選択を復元
                    for i, (_, row) in enumerate(filtered_projects.iterrows(), 1):
                        if str(row.get('project_id')) == str(restored_project_id):
                            default_index = i
                            # session_stateにも設定して永続化
                            st.session_state.project_selector = i
                            break
                        
                # 復元フラグをクリア（一度だけ実行）
                st.session_state.restore_project_state = False
                st.session_state.restored_project_id = None
            
            # 2. session_stateに既存の選択がある場合（ページリロードなど）
            elif hasattr(st.session_state, 'project_selector') and st.session_state.project_selector is not None:
                # 選択されたインデックスが有効な範囲内かチェック
                if 0 <= st.session_state.project_selector < len(project_options):
                    default_index = st.session_state.project_selector
            
            # 単一選択用の選択状態を管理（複数選択から単一選択に変更）
            if 'selected_project_single' not in st.session_state:
                st.session_state.selected_project_single = None
            
            # ページネーション設定
            items_per_page = 20
            total_items = len(filtered_projects)
            total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
            
            # ページ選択
            if total_pages > 1:
                col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
                with col_page2:
                    current_page = st.number_input(
                        f"ページ (1-{total_pages})",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key="project_page_selector"
                    )
            else:
                current_page = 1
            
            # 現在のページのデータを取得
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            page_projects = filtered_projects.iloc[start_idx:end_idx]
            
            # 選択解除ボタン（単一選択のため全選択ボタンは削除）
            col_btn1, col_btn2 = st.columns([1, 3])
            with col_btn1:
                if st.button("選択解除", key="deselect_project"):
                    st.session_state.selected_project_single = None
                    st.rerun()
            with col_btn2:
                if st.session_state.selected_project_single is not None:
                    st.write(f"✅ 選択中: 1件")
                else:
                    st.write("選択なし")
            
            # 案件一覧表示
            st.markdown(f"### 📋 案件一覧 (ページ {current_page}/{total_pages}) {start_idx + 1}-{end_idx}件 / 全{total_items}件")
            
            if not page_projects.empty:
                # カスタムテーブルヘッダー
                header_cols = st.columns([1, 3, 1.5, 2, 1.5, 1.5, 1, 1])
                header_labels = ["選択", "案件名", "ステータス", "会社名", "開始日", "終了日", "必要人数", "ID"]
                
                for i, (col, label) in enumerate(zip(header_cols, header_labels)):
                    with col:
                        st.markdown(f"**{label}**")
                
                st.markdown("---")
                
                # 各行を表示
                for page_idx, (idx, project) in enumerate(page_projects.iterrows()):
                    actual_idx = start_idx + page_idx
                    is_selected = st.session_state.selected_project_single == actual_idx
                    
                    # 行の色付け
                    if is_selected:
                        st.markdown('<div style="background-color: #e6f3ff; padding: 5px; border-radius: 5px; margin: 2px 0;">', unsafe_allow_html=True)
                    
                    row_cols = st.columns([1, 3, 1.5, 2, 1.5, 1.5, 1, 1])
                    
                    with row_cols[0]:
                        if st.button("●" if is_selected else "○", key=f"select_project_{actual_idx}", help="クリックして選択"):
                            if is_selected:
                                st.session_state.selected_project_single = None
                            else:
                                st.session_state.selected_project_single = actual_idx
                            st.rerun()
                    
                    with row_cols[1]:
                        project_name = str(project.get('project_name', 'N/A'))
                        if len(project_name) > 25:
                            st.markdown(f"**{project_name[:25]}...**" if is_selected else f"{project_name[:25]}...")
                        else:
                            st.markdown(f"**{project_name}**" if is_selected else project_name)
                    
                    with row_cols[2]:
                        status = project.get('status', 'N/A')
                        if status == "進行中":
                            st.markdown("🟢 進行中")
                        elif status == "完了":
                            st.markdown("🔵 完了")
                        elif status == "一時停止":
                            st.markdown("🟡 一時停止")
                        else:
                            st.text(status)
                    
                    with row_cols[3]:
                        company_name = str(project.get('company_name', 'N/A'))
                        st.text(company_name[:18] + "..." if len(company_name) > 18 else company_name)
                    
                    with row_cols[4]:
                        start_date = project.get('contract_start_date', '')
                        st.text(start_date[:10] if start_date else '-')
                    
                    with row_cols[5]:
                        end_date = project.get('contract_end_date', '')
                        st.text(end_date[:10] if end_date else '-')
                    
                    with row_cols[6]:
                        required_headcount = project.get('required_headcount', '')
                        if required_headcount not in [None, '', 'N/A']:
                            st.text(f"{required_headcount}名")
                        else:
                            st.text("-")
                    
                    with row_cols[7]:
                        st.text(str(project.get('project_id', 'N/A')))
                    
                    if is_selected:
                        st.markdown('</div>', unsafe_allow_html=True)
                        
            else:
                st.info("表示する案件がありません")
            
            # 選択された案件を取得（単一選択）
            selected_project = None
            if st.session_state.selected_project_single is not None:
                if st.session_state.selected_project_single < len(filtered_projects):
                    selected_project = filtered_projects.iloc[st.session_state.selected_project_single]
            
            # 選択された案件の詳細表示
            if selected_project is not None:
                st.markdown("---")
                st.markdown("### 🎯 選択中案件詳細")
                
                # 案件のIDをsession_stateに保存（既存機能との互換性のため）
                if 'project_id' in selected_project.index:
                    st.session_state.selected_project_id_from_list = selected_project['project_id']
                
                project_name = selected_project.get('project_name', 'N/A')
                status = selected_project.get('status', 'N/A')
                project_id = selected_project.get('project_id', 'N/A')
                
                # 単一選択のためexpanderは不要、直接表示
                st.markdown(f"**📋 {project_name}** - {status} (ID: {project_id})")
                
                # 基本情報カード
                col_basic1, col_basic2, col_basic3 = st.columns(3)
                
                with col_basic1:
                    st.markdown("#### 📋 基本情報")
                    if 'project_name' in selected_project.index and pd.notna(selected_project['project_name']):
                        st.metric("案件名", selected_project['project_name'])
                    if 'status' in selected_project.index and pd.notna(selected_project['status']):
                        st.text(f"ステータス: {selected_project['status']}")
                    if 'required_headcount' in selected_project.index and pd.notna(selected_project['required_headcount']):
                        st.text(f"必要人数: {selected_project['required_headcount']}名")
                    if 'project_id' in selected_project.index:
                        st.text(f"ID: {selected_project['project_id']}")
                
                with col_basic2:
                    st.markdown("#### 🏢 対象企業・契約情報")
                    if 'company_name' in selected_project.index and pd.notna(selected_project['company_name']):
                        st.metric("対象企業", selected_project['company_name'])
                    if 'contract_start_date' in selected_project.index and pd.notna(selected_project['contract_start_date']):
                        st.text(f"契約開始: {selected_project['contract_start_date']}")
                    if 'contract_end_date' in selected_project.index and pd.notna(selected_project['contract_end_date']):
                        st.text(f"契約終了: {selected_project['contract_end_date']}")
                
                with col_basic3:
                    st.markdown("#### 👥 担当者情報")
                    if 'co_manager' in selected_project.index and pd.notna(selected_project['co_manager']):
                        st.text(f"CO担当: {selected_project['co_manager']}")
                    if 're_manager' in selected_project.index and pd.notna(selected_project['re_manager']):
                        st.text(f"RE担当: {selected_project['re_manager']}")
                
                # 候補者情報を表示
                if 'project_id' in selected_project.index:
                    show_project_candidates_summary(selected_project['project_id'], use_sample_data)
                
                # 詳細情報タブ
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 求人内容", "🎯 ターゲット企業・部署", "⚙️ 条件・要件", "📊 全データ", "🔧 編集"])
                
                with tab1:
                    # 求人内容関連情報
                    if 'job_description' in selected_project.index and pd.notna(selected_project['job_description']):
                        st.text_area("職務内容", selected_project['job_description'], height=150, disabled=True)
                    
                    col_job1, col_job2 = st.columns(2)
                    with col_job1:
                        if 'employment_type' in selected_project.index and pd.notna(selected_project['employment_type']):
                            st.text(f"雇用形態: {selected_project['employment_type']}")
                        if 'position_level' in selected_project.index and pd.notna(selected_project['position_level']):
                            st.text(f"ポジションレベル: {selected_project['position_level']}")
                        if 'job_classification' in selected_project.index and pd.notna(selected_project['job_classification']):
                            st.text(f"職種: {selected_project['job_classification']}")
                    
                    with col_job2:
                        if 'work_location' in selected_project.index and pd.notna(selected_project['work_location']):
                            st.text_area("勤務地", selected_project['work_location'], height=80, disabled=True)
                
                with tab2:
                    # ターゲット企業・部署情報
                    if 'project_target_companies' in selected_project.index and selected_project['project_target_companies']:
                        st.markdown("**🎯 対象企業・部署一覧**")
                        ptc_list = selected_project['project_target_companies']
                        if isinstance(ptc_list, list):
                            for i, ptc in enumerate(ptc_list, 1):
                                with st.expander(f"対象企業 {i}"):
                                    if ptc.get('target_companies'):
                                        company_name = ptc['target_companies'].get('company_name', '不明')
                                        dept_name = ptc.get('department_name', '')
                                        if dept_name:
                                            st.text(f"企業名: {company_name}")
                                            st.text(f"部署名: {dept_name}")
                                        else:
                                            st.text(f"企業名: {company_name}")
                    else:
                        st.info("対象企業・部署情報はありません")
                
                with tab3:
                    # 条件・要件情報
                    col_req1, col_req2 = st.columns(2)
                    with col_req1:
                        st.markdown("**👤 人物要件**")
                        if 'min_age' in selected_project.index and pd.notna(selected_project['min_age']):
                            st.text(f"最低年齢: {selected_project['min_age']}歳")
                        if 'max_age' in selected_project.index and pd.notna(selected_project['max_age']):
                            st.text(f"最高年齢: {selected_project['max_age']}歳")
                        if 'education_requirement' in selected_project.index and pd.notna(selected_project['education_requirement']):
                            st.text_area("学歴要件", selected_project['education_requirement'], height=80, disabled=True)
                    
                    with col_req2:
                        st.markdown("**🎯 スキル・資格要件**")
                        if 'requirements' in selected_project.index and pd.notna(selected_project['requirements']):
                            st.text_area("必須要件", selected_project['requirements'], height=80, disabled=True)
                        if 'required_qualifications' in selected_project.index and pd.notna(selected_project['required_qualifications']):
                            st.text_area("必要資格", selected_project['required_qualifications'], height=80, disabled=True)
                
                with tab4:
                    # すべてのデータを表示
                    st.markdown("**📊 登録されている全データ**")
                    
                    # システム情報
                    col_sys1, col_sys2 = st.columns(2)
                    with col_sys1:
                        if 'created_at' in selected_project.index and pd.notna(selected_project['created_at']):
                            st.caption(f"作成日時: {selected_project['created_at']}")
                    with col_sys2:
                        if 'updated_at' in selected_project.index and pd.notna(selected_project['updated_at']):
                            st.caption(f"更新日時: {selected_project['updated_at']}")
                    
                    # 全項目を展開表示
                    for field, value in selected_project.items():
                        # 値が存在するかチェック（配列型を考慮）
                        try:
                            is_valid = (value is not None and 
                                      value != '' and 
                                      str(value).strip() != '' and 
                                      str(value).strip() != 'nan' and
                                      field not in ['created_at', 'updated_at'])
                        except:
                            is_valid = False
                            
                        if is_valid:
                            if isinstance(value, dict):
                                st.json({field: value})
                            elif isinstance(value, list):
                                st.json({field: value})
                            else:
                                st.text(f"{field}: {value}")
                
                with tab5:
                    # 詳細編集タブへのリダイレクト
                    st.markdown("#### ✏️ 案件詳細編集")
                    st.info("💡 詳細な編集機能を使用するには「詳細編集」タブをご利用ください。")
                    
                    col_redirect1, col_redirect2 = st.columns([1, 1])
                    
                    with col_redirect1:
                        if st.button("📝 詳細編集タブで編集", use_container_width=True, type="primary"):
                            # 選択された案件IDを保存
                            st.session_state.selected_project_id_from_list = selected_project['project_id']
                            # 詳細編集タブに切り替え
                            st.session_state.selected_project_tab = 2
                            st.success("✅ 詳細編集タブに移動しています...")
                            st.rerun()
                    
                    with col_redirect2:
                        st.markdown("**選択中の案件:**")
                        st.write(f"🎯 {selected_project.get('project_name', 'N/A')}")
                        st.write(f"📊 ステータス: {selected_project.get('status', 'N/A')}")
                    
                    st.markdown("---")
                    st.markdown("**詳細編集タブでは以下の機能が利用できます：**")
                    st.markdown("""
                    - 🎯 **ターゲット企業・部門・優先度の管理**
                    - 📝 **案件の詳細情報編集** 
                    - 🔄 **リアルタイムでの保存・更新**
                    - 🐛 **デバッグ情報の表示**
                    """)
                
                # アクションボタン
                st.markdown("---")
                col_action1, col_action2, col_action3 = st.columns(3)
                with col_action1:
                    if st.button("✏️ この案件を詳細編集", use_container_width=True):
                        # 選択された案件IDをsession_stateに保存
                        st.session_state.selected_project_id = selected_project['project_id']
                        st.session_state.selected_project_tab = 2  # 詳細編集タブに移動
                        st.rerun()
                with col_action2:
                    if st.button("📋 データをコピー", use_container_width=True):
                        # 選択された案件の全データを文字列に変換
                        project_text = "\n".join([f"{k}: {v}" for k, v in selected_project.items() if pd.notna(v)])
                        st.code(project_text)
                with col_action3:
                    if st.button("🗑️ この案件を削除", use_container_width=True):
                        # 選択された案件IDをsession_stateに保存
                        st.session_state.selected_project_id = selected_project['project_id']
                        st.session_state.selected_project_tab = 3  # 削除タブに移動
                        st.rerun()
        
        else:  # 詳細情報表示
            st.markdown("### 📄 案件詳細情報")
            
            for idx, project in filtered_projects.iterrows():
                project_id = project.get('project_id')
                # セッション状態から復元すべき案件かチェック
                should_expand = False
                if (hasattr(st.session_state, 'restore_project_state') and st.session_state.restore_project_state and 
                    hasattr(st.session_state, 'restored_project_id') and st.session_state.restored_project_id):
                    if str(st.session_state.restored_project_id) == str(project_id):
                        should_expand = True
                
                # 復元対象の案件の場合、アンカーを設定
                if should_expand:
                    st.markdown(f'<div id="project_{project_id}"></div>', unsafe_allow_html=True)
                
                with st.expander(f"🎯 {project.get('project_name', 'N/A')} ({project.get('status', 'N/A')})", expanded=should_expand):
                    
                    # 基本情報
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📋 基本情報")
                        st.text(f"案件ID: {project.get('project_id', 'N/A')}")
                        st.text(f"案件名: {project.get('project_name', 'N/A')}")
                        st.text(f"ステータス: {project.get('status', 'N/A')}")
                        
                        # 優先度表示
                        priority_name = project.get('priority_name', 'N/A')
                        priority_value = project.get('priority_value', 0)
                        if priority_name != 'N/A':
                            # 優先度に応じて色を変更
                            if priority_value >= 4:
                                priority_color = "🔴"
                            elif priority_value >= 3:
                                priority_color = "🟡"
                            else:
                                priority_color = "🟢"
                            st.text(f"優先度: {priority_color} {priority_name}")
                        else:
                            st.text(f"優先度: {priority_name}")
                        
                        # 依頼元企業名とターゲット企業名を分けて表示
                        client_company_name = 'N/A'
                        target_company_name = 'N/A'
                        
                        # client_companiesからの企業名を取得
                        if isinstance(project.get('client_companies'), dict) and project['client_companies']:
                            client_company_name = project['client_companies'].get('company_name', 'N/A')
                        
                        # target_companiesからの企業名を取得（既存のcompany_nameフィールド）
                        if project.get('company_name'):
                            target_company_name = project.get('company_name')
                        
                        st.text(f"依頼元企業: {client_company_name}")
                        st.text(f"ターゲット企業: {target_company_name}")
                        st.text(f"ターゲット部署: {project.get('department_name', 'N/A')}")
                        
                        st.markdown("#### 📅 契約情報")
                        st.text(f"契約開始日: {project.get('contract_start_date', 'N/A')}")
                        st.text(f"契約終了日: {project.get('contract_end_date', 'N/A')}")
                        st.text(f"必要人数: {project.get('required_headcount', 'N/A')}名")
                        
                        st.markdown("#### 👨‍💼 担当者")
                        st.text(f"担当CO: {project.get('co_manager', 'N/A')}")
                        st.text(f"担当RE: {project.get('re_manager', 'N/A')}")
                    
                    with col2:
                        st.markdown("#### 💼 雇用条件")
                        st.text(f"雇用形態: {project.get('employment_type', 'N/A')}")
                        st.text(f"役職レベル: {project.get('position_level', 'N/A')}")
                        st.text(f"勤務地: {project.get('work_location', 'N/A')}")
                        st.text(f"年齢: {project.get('min_age', 'N/A')}歳 〜 {project.get('max_age', 'N/A')}歳")
                        st.text(f"学歴要件: {project.get('education_requirement', 'N/A')}")
                        st.text(f"必要資格: {project.get('required_qualifications', 'N/A')}")
                        st.text(f"職業分類: {project.get('job_classification', 'N/A')}")
                    
                    # 業務内容・要件
                    st.markdown("#### 📝 業務内容")
                    st.text_area("", value=project.get('job_description', ''), height=100, key=f"desc_{project.get('project_id', 'unknown')}", disabled=True)
                    
                    st.markdown("#### 🎯 人材要件")
                    st.text_area("", value=project.get('requirements', ''), height=100, key=f"req_{project.get('project_id', 'unknown')}", disabled=True)
                    
                    # 候補者情報を表示
                    if project_id:
                        show_project_candidates_summary(project_id, use_sample_data)
    else:
        st.info("案件データがありません")
    
    # ナビゲーション履歴のクリア（復元が完了した場合のみ）
    if hasattr(st.session_state, 'navigation_history') and st.session_state.navigation_history:
        # 復元処理が完了していない場合は履歴を保持
        nav_history = st.session_state.navigation_history
        if nav_history.get('from_page') != 'projects' or not nav_history.get('selected_project_id'):
            st.session_state.navigation_history = None

def show_projects_create():
    """新規案件作成画面"""
    st.markdown("### 📝 新規案件作成")
    
    if supabase is None:
        st.warning("データベースに接続されていません。")
        return
    
    # マスターデータ取得
    try:
        companies_response = supabase.table('target_companies').select('*').execute()
        priority_response = supabase.table('priority_levels').select('*').execute()
        
        companies = companies_response.data if companies_response.data else []
        priorities = priority_response.data if priority_response.data else []
        
    except Exception as e:
        st.error(f"マスターデータの取得に失敗しました: {e}")
        return
    
    # 基本情報入力
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("案件名", placeholder="例: システム開発エンジニア募集")
        project_description = st.text_area("案件概要", height=100, placeholder="案件の詳細説明")
        
    with col2:
        employment_type = st.selectbox("雇用形態", ["正社員", "契約社員", "派遣", "業務委託", "アルバイト・パート"])
        salary_range = st.text_input("給与範囲", placeholder="例: 400-600万円")
    
    # ターゲット企業・部門設定
    st.markdown("#### 🎯 ターゲット企業・部門設定")
    
    # 動的に追加できるターゲット設定
    if 'target_companies_list' not in st.session_state:
        st.session_state.target_companies_list = []
    
    # 新しいターゲット追加
    with st.expander("➕ ターゲット企業・部門を追加", expanded=len(st.session_state.target_companies_list) == 0):
        target_col1, target_col2, target_col3, target_col4 = st.columns([3, 3, 2, 1])
        
        with target_col1:
            company_options = [""] + [comp['company_name'] for comp in companies]
            selected_company_name = st.selectbox("企業", company_options, key="new_company")
            
        with target_col2:
            department_name = st.text_input("部門名", key="new_department", placeholder="例: 開発部")
            
        with target_col3:
            priority_options = [""] + [f"{p['priority_name']} ({p['priority_value']})" for p in priorities]
            selected_priority = st.selectbox("優先度", priority_options, key="new_priority")
            
        with target_col4:
            if st.button("追加", key="add_target"):
                if selected_company_name and department_name:
                    # 重複チェック（同じ企業・部門の組み合わせ）
                    duplicate_exists = any(
                        target['company_name'] == selected_company_name and 
                        target['department_name'] == department_name
                        for target in st.session_state.target_companies_list
                    )
                    
                    if duplicate_exists:
                        st.warning(f"「{selected_company_name} - {department_name}」は既に追加されています。")
                    else:
                        # 企業IDを取得
                        selected_company = next((c for c in companies if c['company_name'] == selected_company_name), None)
                        
                        # 優先度の処理（空の場合も許可）
                        priority_id = None
                        priority_name = ''
                        priority_value = ''
                        
                        if selected_priority and selected_priority.strip():
                            priority_info = selected_priority.split(" (")
                            priority_name = priority_info[0]
                            selected_priority_obj = next((p for p in priorities if p['priority_name'] == priority_name), None)
                            if selected_priority_obj:
                                priority_id = selected_priority_obj['priority_id']
                                priority_value = selected_priority_obj['priority_value']
                        
                        target_info = {
                            'company_id': selected_company['target_company_id'],
                            'company_name': selected_company_name,
                            'department_name': department_name,
                            'priority_id': priority_id,
                            'priority_name': priority_name,
                            'priority_value': priority_value
                        }
                        st.session_state.target_companies_list.append(target_info)
                else:
                    st.warning("企業名と部門名を入力してください。")
    
    # 追加されたターゲット一覧表示
    if st.session_state.target_companies_list:
        st.markdown("##### 設定済みターゲット企業・部門")
        
        # 優先度順でソート（空白は最後、priority_valueの降順）
        def sort_key(target):
            priority_value = target.get('priority_value', '')
            if priority_value == '' or priority_value is None:
                return (1, 0)  # 空白は最後（1）、かつ優先度0
            else:
                try:
                    return (0, float(priority_value))  # 優先度ありは最初（0）、値の降順
                except (ValueError, TypeError):
                    return (1, 0)  # 変換できない場合は最後
        
        sorted_targets = sorted(st.session_state.target_companies_list, key=sort_key, reverse=True)
        
        for i, target in enumerate(sorted_targets):
            # 元のインデックスを取得（削除処理のため）
            original_index = st.session_state.target_companies_list.index(target)
            col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
            with col1:
                st.write(f"🏢 {target['company_name']}")
            with col2:
                st.write(f"🏛️ {target['department_name']}")
            with col3:
                priority_display = f"⭐ {target['priority_name']} ({target['priority_value']})" if target['priority_name'] else "⭐ 未設定"
                st.write(priority_display)
            with col4:
                if st.button("削除", key=f"delete_target_{i}"):
                    st.session_state.target_companies_list.pop(original_index)
        
        # 作成ボタン
        st.markdown("---")
        if st.button("案件を作成", type="primary", key="create_project"):
            if project_name and st.session_state.target_companies_list:
                try:
                    # プロジェクト作成
                    project_data = {
                        'project_name': project_name,
                        'project_description': project_description,
                        'employment_type': employment_type,
                        'salary_range': salary_range
                    }
                    
                    project_response = supabase.table('projects').insert(project_data).execute()
                    if project_response.data:
                        project_id = project_response.data[0]['project_id']
                        
                        # ターゲット企業・部門を個別に挿入
                        for target in st.session_state.target_companies_list:
                            target_company_data = {
                                'project_id': int(project_id) if project_id is not None else None,
                                'target_company_id': int(target['company_id']) if target.get('company_id') is not None else None,
                                'department_name': target.get('department_name') if target.get('department_name') else None,
                                'priority_id': int(target['priority_id']) if target.get('priority_id') is not None else None
                            }
                            
                            # 必須フィールドがNoneの場合はスキップ
                            if target_company_data['project_id'] is None or target_company_data['target_company_id'] is None:
                                continue
                                
                            supabase.table('project_target_companies').insert(target_company_data).execute()
                        
                        st.success(f"案件「{project_name}」を作成しました！")
                        # セッション状態をクリア
                        st.session_state.target_companies_list = []
                        st.rerun()
                    else:
                        st.error("案件の作成に失敗しました。")
                        
                except Exception as e:
                    st.error(f"案件作成中にエラーが発生しました: {e}")
            else:
                st.warning("案件名とターゲット企業・部門を設定してください。")
    else:
        st.info("ターゲット企業・部門を追加してください。")

# Removed duplicate functions - using the active implementation below


def show_projects_delete():
    """案件削除機能"""
    st.markdown("### 🗑️ 案件削除")
    st.info("案件削除機能は開発中です。")


def show_project_assignments_tab():
    """人材アサイン管理画面"""
    st.markdown("### 👥 人材アサイン管理")
    st.info("この機能は人材マッチング画面で利用できます。")
    if st.button("🤝 人材マッチング画面を開く"):
        st.markdown("[人材マッチング画面を開く](?page=matching)")


def manage_project_selection_state():
    """案件選択状態を統一管理する関数"""
    # セッション状態キーの定義
    keys = {
        'from_list': 'selected_project_id_from_list',
        'current_editing': 'current_editing_project_id',
        'selected_tab': 'selected_project_tab'
    }
    
    # 優先順位に従って選択すべき案件IDを決定
    selected_id = None
    
    # 1. 一覧からの選択が最優先
    if keys['from_list'] in st.session_state:
        selected_id = st.session_state[keys['from_list']]
        # 使用したのでクリア
        del st.session_state[keys['from_list']]
        # 編集継続用にセット
        st.session_state[keys['current_editing']] = selected_id
    # 2. 現在編集中のIDを使用
    elif keys['current_editing'] in st.session_state:
        selected_id = st.session_state[keys['current_editing']]
    
    return selected_id, keys


def clear_project_editing_state():
    """案件編集関連のセッション状態をクリア"""
    keys_to_clear = [
        'current_editing_project_id',
        'selected_project_id_from_list',
        'selected_project_tab'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def show_projects_edit():
    """案件編集機能"""
    st.markdown("### ✏️ 案件編集")
    
    # 実際のデータベースデータのみを取得
    if supabase is None:
        st.warning("データベースに接続されていません。編集機能を使用するにはSupabase接続が必要です。")
        return
    
    try:
        # 1回のクエリですべてのデータを取得（パフォーマンス改善）
        response = supabase.table('projects').select(
            '*, project_target_companies(id, target_company_id, department_name, priority_id, target_companies(target_company_id, company_name), priority_levels(priority_id, priority_name, priority_value))'
        ).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
        else:
            df = pd.DataFrame()
    except Exception as e:
        st.error(f"データ取得エラー: {str(e)}")
        st.error("Streamlit Cloudでの接続制限により、データ取得に失敗しました。少し待ってから再試行してください。")
        # フォールバック: より少ない情報で基本的なプロジェクトリストを取得
        try:
            st.info("基本情報のみで案件リストを表示します...")
            simple_response = supabase.table('projects').select('project_id, project_name, status').execute()
            if simple_response.data:
                df = pd.DataFrame(simple_response.data)
                # 空のproject_target_companiesを追加
                df['project_target_companies'] = [[] for _ in range(len(df))]
            else:
                df = pd.DataFrame()
        except Exception as fallback_error:
            st.error(f"フォールバック取得も失敗: {str(fallback_error)}")
            df = pd.DataFrame()
    
    if df.empty:
        st.info("データベースに登録された案件がありません。まず「新規案件」タブから案件を追加してください。")
        return
    
    # 統一されたセッション状態管理を使用
    preselected_id, session_keys = manage_project_selection_state()
    
    # 編集対象選択
    project_options = df.apply(lambda row: f"{row.get('project_name', 'N/A')} ({row.get('status', 'N/A')})", axis=1).tolist()
    
    # デフォルトのインデックスを決定
    default_index = 0
    if preselected_id:
        for i, (_, project) in enumerate(df.iterrows()):
            if project.get('project_id') == preselected_id:
                default_index = i
                break
    
    selected_index = st.selectbox("編集する案件を選択してください", range(len(project_options)),
                                  format_func=lambda x: project_options[x],
                                  index=default_index)
    
    if selected_index is not None:
        selected_project = df.iloc[selected_index]
        project_id = selected_project.get('project_id')
        
        # 現在編集中の案件IDを保存
        st.session_state[session_keys['current_editing']] = project_id
        
        masters = fetch_master_data()
        
        st.markdown(f"#### 編集中: {selected_project.get('project_name', 'N/A')}")
        
        # ターゲット企業・部門・優先度管理
        st.markdown("#### 🎯 ターゲット企業・部門・優先度管理")
        
        # 既存のターゲット設定を取得
        existing_targets = []
        if 'project_target_companies' in selected_project and selected_project['project_target_companies']:
            ptc_list = selected_project['project_target_companies']
            if isinstance(ptc_list, list):
                for ptc in ptc_list:
                    if ptc.get('target_companies'):
                        target_info = {
                            'id': ptc.get('id'),
                            'company_id': ptc['target_companies'].get('target_company_id'),
                            'company_name': ptc['target_companies'].get('company_name', ''),
                            'department_name': ptc.get('department_name', ''),
                            'priority_id': ptc.get('priority_levels', {}).get('priority_id') if ptc.get('priority_levels') else None,
                            'priority_name': ptc.get('priority_levels', {}).get('priority_name', '') if ptc.get('priority_levels') else '',
                            'priority_value': ptc.get('priority_levels', {}).get('priority_value', '') if ptc.get('priority_levels') else ''
                        }
                        existing_targets.append(target_info)
        
        # セッション状態で編集中のターゲット一覧を管理
        edit_key = f"edit_target_companies_list_{project_id}"
        db_hash_key = f"db_hash_{project_id}"
        
        # データベース状態のハッシュを生成（より確実な比較のため）
        import json
        current_db_hash = hash(json.dumps(existing_targets, sort_keys=True, default=str))
        
        # 初期化：データベースの状態が変わった場合のみセッション状態をリセット
        if db_hash_key not in st.session_state or st.session_state[db_hash_key] != current_db_hash:
            st.session_state[edit_key] = existing_targets.copy()
            st.session_state[db_hash_key] = current_db_hash
        elif edit_key not in st.session_state:
            st.session_state[edit_key] = existing_targets.copy()
        
        # 新しいターゲット追加
        with st.expander("➕ ターゲット企業・部門を追加/編集"):
            target_col1, target_col2, target_col3, target_col4 = st.columns([3, 3, 2, 1])
            
            # マスターデータ取得
            companies = masters['target_companies'].to_dict('records') if not masters['target_companies'].empty else []
            priority_response = supabase.table('priority_levels').select('*').execute() if supabase else None
            priorities = priority_response.data if priority_response and priority_response.data else []
            
            with target_col1:
                company_options = [""] + [comp['company_name'] for comp in companies]
                selected_company_name = st.selectbox("企業", company_options, key=f"edit_new_company_{project_id}")
                
            with target_col2:
                department_name = st.text_input("部門名", key=f"edit_new_department_{project_id}", placeholder="例: 開発部")
                
            with target_col3:
                priority_options = [""] + [f"{p['priority_name']} ({p['priority_value']})" for p in priorities]
                selected_priority = st.selectbox("優先度", priority_options, key=f"edit_new_priority_{project_id}")
                
            with target_col4:
                if st.button("追加", key=f"edit_add_target_{project_id}"):
                    if selected_company_name and department_name:
                        # 重複チェック（同じ企業・部門の組み合わせ）
                        duplicate_exists = any(
                            target['company_name'] == selected_company_name and 
                            target['department_name'] == department_name
                            for target in st.session_state[edit_key]
                        )
                        
                        if duplicate_exists:
                            st.warning(f"「{selected_company_name} - {department_name}」は既に追加されています。")
                        else:
                            # 企業IDを取得
                            selected_company = next((c for c in companies if c['company_name'] == selected_company_name), None)
                            
                            # 優先度の処理（空の場合も許可）
                            priority_id = None
                            priority_name = ''
                            priority_value = ''
                            
                            if selected_priority and selected_priority.strip():
                                priority_info = selected_priority.split(" (")
                                priority_name = priority_info[0]
                                selected_priority_obj = next((p for p in priorities if p['priority_name'] == priority_name), None)
                                if selected_priority_obj:
                                    priority_id = selected_priority_obj['priority_id']
                                    priority_value = selected_priority_obj['priority_value']
                            
                            target_info = {
                                'id': None,  # 新規追加なのでNone
                                'company_id': selected_company['target_company_id'],
                                'company_name': selected_company_name,
                                'department_name': department_name,
                                'priority_id': priority_id,
                                'priority_name': priority_name,
                                'priority_value': priority_value
                            }
                            st.session_state[edit_key].append(target_info)
                            
                            # 追加と同時にデータベースに保存
                            try:
                                target_company_data = {
                                    'project_id': int(project_id),
                                    'target_company_id': int(target_info['company_id']),
                                    'department_name': target_info['department_name'],
                                    'priority_id': int(target_info['priority_id']) if target_info['priority_id'] is not None else None
                                }
                                
                                insert_response = supabase.table('project_target_companies').insert(target_company_data).execute()
                                if insert_response.data:
                                    # 挿入されたレコードのIDを更新
                                    inserted_id = insert_response.data[0]['id']
                                    st.session_state[edit_key][-1]['id'] = inserted_id
                                    
                                    # DBハッシュを更新
                                    db_hash_key = f"db_hash_{project_id}"
                                    import json
                                    new_db_hash = hash(json.dumps(st.session_state[edit_key], sort_keys=True, default=str))
                                    st.session_state[db_hash_key] = new_db_hash
                                    
                                    st.success(f"✅ 「{selected_company_name} - {department_name}」を追加しました！")
                                else:
                                    st.error("❌ データベースへの保存に失敗しました")
                            except Exception as e:
                                st.error(f"❌ 保存エラー: {str(e)}")
                                # エラーの場合はセッション状態からも削除
                                st.session_state[edit_key].pop()
                    else:
                        st.warning("企業名と部門名を入力してください。")
        
        # デバッグ情報（開発用）
        if st.checkbox("デバッグ情報を表示", key=f"debug_info_{project_id}"):
            st.markdown("**デバッグ情報:**")
            st.write(f"プロジェクトID: {project_id}")
            st.write(f"データベース登録数: {len(existing_targets)}")
            st.write(f"セッション状態の数: {len(st.session_state[edit_key])}")
            st.write(f"現在のDBハッシュ: {current_db_hash}")
            st.write(f"保存されたDBハッシュ: {st.session_state.get(db_hash_key, 'なし')}")
            st.write(f"現在編集中のID: {st.session_state.get(session_keys['current_editing'], 'なし')}")
            st.write(f"一覧から選択されたID: {st.session_state.get(session_keys['from_list'], 'なし')}")
            with st.expander("詳細データ"):
                st.write("データベースから取得:", existing_targets)
                st.write("セッション状態:", st.session_state[edit_key])
                st.write("全セッション状態キー:", [k for k in st.session_state.keys() if str(project_id) in k])
        
        # 設定済みターゲット一覧表示
        if st.session_state[edit_key]:
            st.markdown("##### 設定済みターゲット企業・部門")
            
            # 優先度順でソート（空白は最後、priority_valueの降順）
            def sort_key(target):
                priority_value = target.get('priority_value', '')
                if priority_value == '' or priority_value is None:
                    return (1, 0)  # 空白は最後（1）、かつ優先度0
                else:
                    try:
                        return (0, float(priority_value))  # 優先度ありは最初（0）、値の降順
                    except (ValueError, TypeError):
                        return (1, 0)  # 変換できない場合は最後
            
            sorted_targets = sorted(st.session_state[edit_key], key=sort_key, reverse=True)
            
            for i, target in enumerate(sorted_targets):
                # 元のインデックスを取得（削除処理のため）
                original_index = st.session_state[edit_key].index(target)
                col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
                with col1:
                    st.write(f"🏢 {target['company_name']}")
                with col2:
                    st.write(f"🏛️ {target['department_name']}")
                with col3:
                    priority_display = f"⭐ {target['priority_name']} ({target['priority_value']})" if target['priority_name'] else "⭐ 未設定"
                    st.write(priority_display)
                with col4:
                    if st.button("削除", key=f"edit_delete_target_{project_id}_{i}"):
                        target_to_delete = st.session_state[edit_key][original_index]
                        
                        # データベースからも削除（IDがある場合のみ）
                        if target_to_delete.get('id'):
                            try:
                                supabase.table('project_target_companies').delete().eq('id', target_to_delete['id']).execute()
                                st.success(f"✅ 「{target_to_delete['company_name']} - {target_to_delete['department_name']}」を削除しました！")
                            except Exception as e:
                                st.error(f"❌ 削除エラー: {str(e)}")
                                return  # エラー時は削除を中止
                        
                        # セッション状態から削除
                        st.session_state[edit_key].pop(original_index)
                        
                        # DBハッシュを更新
                        db_hash_key = f"db_hash_{project_id}"
                        import json
                        new_db_hash = hash(json.dumps(st.session_state[edit_key], sort_keys=True, default=str))
                        st.session_state[db_hash_key] = new_db_hash
                        
                        # 編集継続のためセッション状態は維持
                        st.session_state[session_keys['current_editing']] = project_id
                        
                        st.rerun()
        else:
            st.info("ターゲット企業・部門を追加してください。")

        with st.form("edit_project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # 基本情報
                project_name = st.text_input("案件名", value=selected_project.get('project_name', ''))
                
                status = st.selectbox("ステータス", ["OPEN", "CLOSED", "PENDING", "IN_PROGRESS"],
                                    index=["OPEN", "CLOSED", "PENDING", "IN_PROGRESS"].index(selected_project.get('status', 'OPEN')) if selected_project.get('status') in ["OPEN", "CLOSED", "PENDING", "IN_PROGRESS"] else 0)
                
            with col2:
                # 予約スペース（col2は今後必要に応じて使用）
                pass
                
            headcount_value = selected_project.get('required_headcount')
            if pd.isna(headcount_value) or headcount_value is None:
                headcount_value = 1
            required_headcount = st.number_input("必要人数", min_value=1, value=int(headcount_value))
            employment_type = st.selectbox("雇用形態", ["", "正社員", "契約社員", "業務委託", "派遣"],
                                         index=["", "正社員", "契約社員", "業務委託", "派遣"].index(selected_project.get('employment_type', '')) if selected_project.get('employment_type') in ["", "正社員", "契約社員", "業務委託", "派遣"] else 0)
                    
            st.markdown("#### 期間・条件")
            col3, col4 = st.columns(2)
            
            with col3:
                # 契約開始日
                current_start_date = selected_project.get('contract_start_date')
                if current_start_date:
                    try:
                        contract_start_date = st.date_input("契約開始日", value=pd.to_datetime(current_start_date).date())
                    except:
                        contract_start_date = st.date_input("契約開始日", value=None)
                else:
                    contract_start_date = st.date_input("契約開始日", value=None)
                
                co_manager = st.text_input("担当CO", value=selected_project.get('co_manager', ''))
                min_age_value = selected_project.get('min_age')
                if pd.isna(min_age_value) or min_age_value is None:
                    min_age_value = 28
                min_age = st.number_input("年齢下限", min_value=18, max_value=100, value=int(min_age_value))
                
            with col4:
                # 契約終了日
                current_end_date = selected_project.get('contract_end_date')
                if current_end_date:
                    try:
                        contract_end_date = st.date_input("契約終了日", value=pd.to_datetime(current_end_date).date())
                    except:
                        contract_end_date = st.date_input("契約終了日", value=None)
                else:
                    contract_end_date = st.date_input("契約終了日", value=None)
                
                re_manager = st.text_input("担当RE", value=selected_project.get('re_manager', ''))
                max_age_value = selected_project.get('max_age')
                if pd.isna(max_age_value) or max_age_value is None:
                    max_age_value = 50
                max_age = st.number_input("年齢上限", min_value=18, max_value=100, value=int(max_age_value))
            
            st.markdown("#### 詳細情報")
            job_description = st.text_area("業務内容", height=100, value=selected_project.get('job_description', ''))
            requirements = st.text_area("人材要件", height=100, value=selected_project.get('requirements', ''))
            work_location = st.text_input("勤務地", value=selected_project.get('work_location', ''))
            education_requirement = st.text_input("学歴要件", value=selected_project.get('education_requirement', ''))
            
            submitted = st.form_submit_button("🎯 更新", use_container_width=True, type="primary")
            
            if submitted:
                try:

                    # ターゲット企業・部門・優先度の妥当性をチェック
                    if edit_key not in st.session_state or not st.session_state[edit_key]:
                        st.error("ターゲット企業・部門を最低1つ設定してください。")
                        return
                    
                    # projectsテーブルの更新（数値型をint()で変換、None値チェック）
                    update_data = {
                        'project_name': project_name,
                        'status': status,
                        'contract_start_date': contract_start_date.isoformat() if contract_start_date else None,
                        'contract_end_date': contract_end_date.isoformat() if contract_end_date else None,
                        'required_headcount': int(required_headcount) if required_headcount is not None else 1,
                        'co_manager': co_manager if co_manager else None,
                        're_manager': re_manager if re_manager else None,
                        'job_description': job_description if job_description else None,
                        'requirements': requirements if requirements else None,
                        'employment_type': employment_type if employment_type else None,
                        'work_location': work_location if work_location else None,
                        'min_age': int(min_age) if min_age is not None else 18,
                        'max_age': int(max_age) if max_age is not None else 65,
                        'education_requirement': education_requirement if education_requirement else None
                    }
                    
                    # None値を除去
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    # 1. 案件本体を更新
                    response = supabase.table('projects').update(update_data).eq('project_id', project_id).execute()
                    
                    # 2. 既存のproject_target_companies関連付けを削除
                    supabase.table('project_target_companies').delete().eq('project_id', project_id).execute()
                    
                    # 3. 新しいターゲット企業・部門・優先度を挿入
                    target_count = len(st.session_state[edit_key])
                    for target in st.session_state[edit_key]:
                        # None値チェックを追加
                        target_company_data = {
                            'project_id': int(project_id) if project_id is not None else None,
                            'target_company_id': int(target['company_id']) if target.get('company_id') is not None else None,
                            'department_name': target.get('department_name') if target.get('department_name') else None,
                            'priority_id': int(target['priority_id']) if target.get('priority_id') is not None else None
                        }
                        
                        # 必須フィールドがNoneの場合はスキップ
                        if target_company_data['project_id'] is None or target_company_data['target_company_id'] is None:
                            continue
                            
                        supabase.table('project_target_companies').insert(target_company_data).execute()
                    
                    # データベース更新成功時、次回の比較用にDBのハッシュを更新
                    db_hash_key = f"db_hash_{project_id}"
                    import json
                    new_db_hash = hash(json.dumps(st.session_state[edit_key], sort_keys=True, default=str))
                    st.session_state[db_hash_key] = new_db_hash
                    
                    # 編集完了時に編集関連のセッション状態をクリア
                    clear_project_editing_state()
                    
                    st.success(f"✅ 案件が正常に更新されました！（ターゲット設定: {target_count}件）")
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ 更新エラー: {str(e)}")


def show_projects_delete():
    """案件削除機能"""
    st.markdown("### 🗑️ 案件削除")
    
    # 実際のデータベースデータのみを取得
    if supabase is None:
        st.warning("データベースに接続されていません。削除機能を使用するにはSupabase接続が必要です。")
        return
    
    try:
        response = supabase.table('projects').select(
            '*, project_target_companies(id, target_companies(target_company_id, company_name), department_name, priority_levels(priority_id, priority_name, priority_value))'
        ).execute()
        if response.data:
            df = pd.DataFrame(response.data)
        else:
            df = pd.DataFrame()
    except:
        df = pd.DataFrame()
    
    if df.empty:
        st.info("データベースに登録された案件がありません。削除可能なデータがありません。")
        return
    
    st.warning("⚠️ 削除されたデータは復元できません。十分ご注意ください。")
    
    # 削除対象選択
    project_options = df.apply(lambda row: f"{row.get('project_name', 'N/A')} ({row.get('status', 'N/A')})", axis=1).tolist()
    selected_index = st.selectbox("削除する案件を選択してください", range(len(project_options)),
                                  format_func=lambda x: project_options[x])
    
    if selected_index is not None:
        selected_project = df.iloc[selected_index]
        project_id = selected_project.get('project_id')
        
        # 削除対象の詳細表示
        st.markdown("#### 削除対象の詳細")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text(f"案件名: {selected_project.get('project_name', 'N/A')}")
            st.text(f"ステータス: {selected_project.get('status', 'N/A')}")
            st.text(f"企業名: {selected_project.get('company_name', 'N/A')}")
            st.text(f"部署: {selected_project.get('department_name', 'N/A')}")
        
        with col2:
            st.text(f"必要人数: {selected_project.get('required_headcount', 'N/A')}名")
            st.text(f"契約期間: {selected_project.get('contract_start_date', 'N/A')} 〜 {selected_project.get('contract_end_date', 'N/A')}")
            st.text(f"担当CO: {selected_project.get('co_manager', 'N/A')}")
            st.text(f"担当RE: {selected_project.get('re_manager', 'N/A')}")
        
        # 確認チェックボックス
        confirm_delete = st.checkbox("上記の案件を削除することを確認しました")
        
        if confirm_delete:
            if st.button("🗑️ 削除実行", type="primary"):
                try:
                    # 関連データも削除する必要がある場合は先に削除
                    # (外部キー制約により)
                    
                    # まず関連するproject_assignmentsを削除
                    supabase.table('project_assignments').delete().eq('project_id', project_id).execute()
                    
                    # 最後にprojectsテーブルから削除
                    response = supabase.table('projects').delete().eq('project_id', project_id).execute()
                    
                    st.success(f"案件「{selected_project.get('project_name', 'N/A')}」が正常に削除されました")
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 削除エラー: {str(e)}")



def show_masters():
    st.subheader("⚙️ マスタ管理")
    
    masters = fetch_master_data()
    
    # タブで各マスタを管理
    tabs = st.tabs(["🏢 企業", "🏢 部署", "👥 担当者", "🎯 優先度", "📞 AP手法"])
    
    # 企業マスタ
    with tabs[0]:
        st.markdown("### 🏢 企業マスタ")
        
        # 統一企業マスタ（companies）を使用
        companies = masters.get('companies', pd.DataFrame())
        
        if not companies.empty:
            # 企業の役割を取得（project_companiesから）
            try:
                pc_response = supabase.table('project_companies').select('company_id, role').execute()
                company_roles_data = pc_response.data if pc_response.data else []
                
                # 企業IDごとの役割をまとめる
                company_role_map = {}
                for pc in company_roles_data:
                    company_id = pc['company_id']
                    role = pc['role']
                    if company_id not in company_role_map:
                        company_role_map[company_id] = set()
                    company_role_map[company_id].add('ターゲット企業' if role == 'target' else '依頼企業')
                
                # 表示用データを作成
                display_data = []
                for _, company in companies.iterrows():
                    company_id = company['company_id']
                    roles = list(company_role_map.get(company_id, set()))
                    
                    display_data.append({
                        'company_id': company_id,
                        'company_name': company['company_name'],
                        'company_url': company.get('company_url', ''),
                        'contact_person': company.get('contact_person', ''),
                        'contact_email': company.get('contact_email', ''),
                        'company_phone': company.get('company_phone', ''),
                        'company_address': company.get('company_address', ''),
                        'notes': company.get('notes', ''),
                        'email_searched': company.get('email_searched', ''),
                        'linkedin_searched': company.get('linkedin_searched', ''),
                        'homepage_searched': company.get('homepage_searched', ''),
                        'eight_search': company.get('eight_search', ''),
                        'keyword_searches': company.get('keyword_searches', {}),
                        'other_searches': company.get('other_searches', {}),
                        'email_search_patterns': company.get('email_search_patterns', {}),
                        'confirmed_emails': company.get('confirmed_emails', {}),
                        'misdelivery_emails': company.get('misdelivery_emails', {}),
                        'email_search_memo': company.get('email_search_memo', ''),
                        'roles': ', '.join(roles) if roles else '未使用',
                        'created_at': company.get('created_at', ''),
                        'updated_at': company.get('updated_at', '')
                    })
                
                if display_data:
                    df_display = pd.DataFrame(display_data)
                    
                    # 選択可能なデータフレーム表示
                    selected_company = st.dataframe(
                        df_display[['company_name', 'roles', 'company_url', 'email_searched', 'linkedin_searched', 'homepage_searched', 'eight_search', 'contact_person', 'contact_email', 'created_at']],
                        column_config={
                            'company_name': '企業名',
                            'roles': '役割',
                            'company_url': 'URL',
                            'email_searched': st.column_config.DateColumn('メール検索'),
                            'linkedin_searched': st.column_config.DateColumn('LinkedIn検索'),
                            'homepage_searched': st.column_config.DateColumn('HP検索'),
                            'eight_search': st.column_config.DateColumn('Eight検索'),
                            'contact_person': '担当者',
                            'contact_email': 'メール',
                            'created_at': st.column_config.DatetimeColumn('作成日')
                        },
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="single-row"
                    )
            
                    # 選択された企業の編集・削除フォーム
                    if selected_company.selection.rows:
                        selected_idx = selected_company.selection.rows[0]
                        selected_row = df_display.iloc[selected_idx]
                        
                        st.markdown("---")
                        st.markdown("### ✏️ 企業情報編集")
                        
                        with st.form("edit_unified_company"):
                            st.markdown("**基本情報**")
                            col1, col2 = st.columns(2)
                            with col1:
                                edited_name = st.text_input("企業名 *", value=selected_row['company_name'])
                                edited_url = st.text_input("企業URL", value=selected_row.get('company_url', ''))
                                edited_address = st.text_input("住所", value=selected_row.get('company_address', ''))
                            with col2:
                                edited_phone = st.text_input("電話番号", value=selected_row.get('company_phone', ''))
                                edited_contact_person = st.text_input("担当者名", value=selected_row.get('contact_person', ''))
                                edited_contact_email = st.text_input("担当者メール", value=selected_row.get('contact_email', ''))
                            
                            edited_notes = st.text_area("備考", value=selected_row.get('notes', ''), height=100)
                            
                            # 検索関連情報セクション
                            st.markdown("**検索履歴**")
                            col3, col4 = st.columns(2)
                            with col3:
                                edited_email_searched = st.date_input("メール検索日", value=pd.to_datetime(selected_row.get('email_searched')) if selected_row.get('email_searched') else None, format="YYYY-MM-DD")
                                edited_linkedin_searched = st.date_input("LinkedIn検索日", value=pd.to_datetime(selected_row.get('linkedin_searched')) if selected_row.get('linkedin_searched') else None, format="YYYY-MM-DD")
                            with col4:
                                edited_homepage_searched = st.date_input("ホームページ検索日", value=pd.to_datetime(selected_row.get('homepage_searched')) if selected_row.get('homepage_searched') else None, format="YYYY-MM-DD")
                                edited_eight_search = st.date_input("Eight検索日", value=pd.to_datetime(selected_row.get('eight_search')) if selected_row.get('eight_search') else None, format="YYYY-MM-DD")
                            
                            edited_email_search_memo = st.text_area("メール検索メモ", value=selected_row.get('email_search_memo', ''), height=100)
                            
                            form_col1, form_col2 = st.columns(2)
                            with form_col1:
                                if st.form_submit_button("💾 更新", type="primary"):
                                    if edited_name:
                                        try:
                                            update_data = {
                                                'company_name': edited_name,
                                                'company_url': edited_url if edited_url else None,
                                                'company_address': edited_address if edited_address else None,
                                                'company_phone': edited_phone if edited_phone else None,
                                                'contact_person': edited_contact_person if edited_contact_person else None,
                                                'contact_email': edited_contact_email if edited_contact_email else None,
                                                'notes': edited_notes if edited_notes else None,
                                                'email_searched': edited_email_searched.isoformat() if edited_email_searched else None,
                                                'linkedin_searched': edited_linkedin_searched.isoformat() if edited_linkedin_searched else None,
                                                'homepage_searched': edited_homepage_searched.isoformat() if edited_homepage_searched else None,
                                                'eight_search': edited_eight_search.isoformat() if edited_eight_search else None,
                                                'email_search_memo': edited_email_search_memo if edited_email_search_memo else None,
                                                'updated_at': datetime.now().isoformat()
                                            }
                                            
                                            # companiesテーブルを更新
                                            response = supabase.table('companies').update(update_data).eq('company_id', selected_row['company_id']).execute()
                                            
                                            if response.data:
                                                st.success(f"✅ 企業 '{edited_name}' の情報を更新しました")
                                                st.cache_data.clear()
                                                st.rerun()
                                            else:
                                                st.error("❌ 更新に失敗しました")
                                        except Exception as e:
                                            st.error(f"❌ 更新エラー: {str(e)}")
                                    else:
                                        st.error("企業名を入力してください")
                            
                            with form_col2:
                                if st.form_submit_button("🗑️ 削除", type="secondary"):
                                    try:
                                        # 関連データの確認
                                        # コンタクトでの使用確認
                                        contacts_check = supabase.table('contacts').select('contact_id').eq('company_id', selected_row['company_id']).execute()
                                        # プロジェクトでの使用確認
                                        projects_check = supabase.table('project_companies').select('id').eq('company_id', selected_row['company_id']).execute()
                                        
                                        if contacts_check.data or projects_check.data:
                                            error_msg = f"❌ この企業は"
                                            if contacts_check.data:
                                                error_msg += f" {len(contacts_check.data)}件のコンタクト"
                                            if projects_check.data:
                                                if contacts_check.data:
                                                    error_msg += "と"
                                                error_msg += f" {len(projects_check.data)}件のプロジェクト"
                                            error_msg += "で使用されているため削除できません"
                                            st.error(error_msg)
                                        else:
                                            # 削除実行
                                            response = supabase.table('companies').delete().eq('company_id', selected_row['company_id']).execute()
                                            if response.data:
                                                st.success(f"✅ 企業 '{selected_row['company_name']}' を削除しました")
                                                st.cache_data.clear()
                                                st.rerun()
                                            else:
                                                st.error("❌ 削除に失敗しました")
                                    except Exception as e:
                                        st.error(f"❌ 削除エラー: {str(e)}")
                        
                        st.info("💡 削除は関連するコンタクトや案件で使用されていない場合のみ可能です。")
                
                else:
                    st.info("企業マスタにデータがありません。")
            except Exception as e:
                st.error(f"企業情報の取得に失敗しました: {str(e)}")
                st.dataframe(companies, use_container_width=True)
        else:
            st.info("企業マスタにデータがありません。")
        
        # 新規企業追加フォーム
        st.markdown("---")
        st.markdown("### ➕ 新規企業追加")
        with st.form("add_unified_company"):
            st.markdown("**基本情報**")
            col1, col2 = st.columns(2)
            with col1:
                new_company_name = st.text_input("企業名 *", placeholder="例: 株式会社サンプル")
                new_company_url = st.text_input("企業URL", placeholder="https://example.com")
                new_company_address = st.text_input("住所", placeholder="東京都千代田区...")
            with col2:
                new_company_phone = st.text_input("電話番号", placeholder="03-1234-5678")
                new_contact_person = st.text_input("担当者名", placeholder="山田太郎")
                new_contact_email = st.text_input("担当者メール", placeholder="yamada@example.com")
            
            new_notes = st.text_area("備考", placeholder="その他の情報", height=100)
            
            if st.form_submit_button("🏢 企業を追加", type="primary"):
                if new_company_name:
                    try:
                        # 重複チェック
                        existing_check = supabase.table('companies').select('company_id').eq('company_name', new_company_name).execute()
                        if existing_check.data:
                            st.error(f"❌ 企業名 '{new_company_name}' は既に登録されています")
                        else:
                            insert_data = {
                                'company_name': new_company_name,
                                'company_url': new_company_url if new_company_url else None,
                                'company_address': new_company_address if new_company_address else None,
                                'company_phone': new_company_phone if new_company_phone else None,
                                'contact_person': new_contact_person if new_contact_person else None,
                                'contact_email': new_contact_email if new_contact_email else None,
                                'notes': new_notes if new_notes else None,
                                'created_at': datetime.now().isoformat(),
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            response = supabase.table('companies').insert(insert_data).execute()
                            if response.data:
                                st.success(f"✅ 企業 '{new_company_name}' を追加しました")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ 追加に失敗しました")
                    except Exception as e:
                        st.error(f"❌ エラー: {str(e)}")
                else:
                    st.error("企業名を入力してください")
    
    # 部署マスタ
    with tabs[1]:
        st.markdown("### 🏢 部署マスタ")
        
        # 部署マスタは廃止されました
        st.info("📝 部署マスタ機能は廃止されました。\n\n部署情報は各人材のレコードで個別に管理されるようになりました。")
        if False:  # 以下のコードは無効化
            display_data = {}
            if not masters['target_companies'].empty:
                company_dict = masters['target_companies'].set_index('target_company_id')['company_name'].to_dict()
                display_data['company_name'] = display_data['company_id'].map(company_dict)
            
            display_columns = ['department_id', 'company_name', 'department_name', 'is_target_department', 'created_at']
            column_config = {
                'department_id': 'ID',
                'company_name': '企業名',
                'department_name': '部署名',
                'is_target_department': st.column_config.CheckboxColumn('ターゲット部署'),
                'created_at': st.column_config.DatetimeColumn('作成日時')
            }
            
            available_columns = [col for col in display_columns if col in display_data.columns]
            if available_columns:
                st.dataframe(
                    display_data[available_columns].fillna(''),
                    use_container_width=True,
                    column_config=column_config
                )
        else:
            st.info("部署データがありません")
        
        with st.form("add_department"):
            col1, col2, col3 = st.columns(3)
            with col1:
                if not masters['target_companies'].empty:
                    company_options = [""] + masters['target_companies']['company_name'].tolist()
                    selected_company = st.selectbox("企業名 *", company_options)
                else:
                    selected_company = st.text_input("企業名 *", placeholder="手動入力")
            
            with col2:
                department_name = st.text_input("部署名 *")
            
            with col3:
                is_target = st.checkbox("ターゲット部署")
            
            if st.form_submit_button("🏢 部署を追加"):
                if department_name and selected_company:
                    try:
                        # 企業IDを取得
                        target_company_id = None
                        if not masters['target_companies'].empty:
                            company_result = masters['target_companies'][masters['target_companies']['company_name'] == selected_company]
                            target_company_id = company_result.iloc[0]['target_company_id'] if not company_result.empty else None
                        
                        department_data = {
                            'company_id': target_company_id,
                            'department_name': department_name,
                            'is_target_department': is_target
                        }
                        
                        # 部署マスタは廃止：各コンタクトに直接部署名を保存
                        response = None
                        if response:
                            st.success(f"部署 '{department_name}' を追加しました")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("追加に失敗しました")
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
                else:
                    st.error("企業名と部署名を入力してください")
    
    # 検索担当者マスタ
    with tabs[2]:
        st.markdown("### 👥 検索担当者マスタ")
        
        if not masters['search_assignees'].empty:
            st.dataframe(
                masters['search_assignees'][['assignee_id', 'assignee_name', 'created_at']],
                use_container_width=True,
                column_config={
                    "assignee_id": "ID",
                    "assignee_name": "担当者名",
                    "created_at": st.column_config.DatetimeColumn("作成日時")
                }
            )
        else:
            st.info("担当者データがありません")
        
        with st.form("add_assignee"):
            assignee_name = st.text_input("新規担当者名")
            if st.form_submit_button("👥 担当者を追加"):
                if assignee_name:
                    try:
                        response = insert_master_data('search_assignees', {'assignee_name': assignee_name})
                        if response:
                            st.success(f"担当者 '{assignee_name}' を追加しました")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("追加に失敗しました")
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
                else:
                    st.error("担当者名を入力してください")
    
    # 優先度マスタ
    with tabs[3]:
        st.markdown("### 🎯 優先度マスタ")
        
        if not masters['priority_levels'].empty:
            st.dataframe(
                masters['priority_levels'][['priority_id', 'priority_name', 'priority_value', 'description', 'created_at']],
                use_container_width=True,
                column_config={
                    "priority_id": "ID",
                    "priority_name": "優先度名",
                    "priority_value": st.column_config.NumberColumn("優先度値", format="%.2f"),
                    "description": "説明",
                    "created_at": st.column_config.DatetimeColumn("作成日時")
                }
            )
        else:
            st.info("優先度データがありません")
        
        with st.form("add_priority"):
            col1, col2, col3 = st.columns(3)
            with col1:
                priority_name = st.text_input("優先度名")
            with col2:
                priority_value = st.number_input("優先度値", min_value=1.0, max_value=5.0, step=0.1, value=3.0)
            with col3:
                description = st.text_input("説明")
            
            if st.form_submit_button("🎯 優先度を追加"):
                if priority_name:
                    try:
                        response = insert_master_data('priority_levels', {
                            'priority_name': priority_name,
                            'priority_value': priority_value,
                            'description': description if description else None
                        })
                        if response:
                            st.success(f"優先度 '{priority_name}' を追加しました")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("追加に失敗しました")
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
                else:
                    st.error("優先度名を入力してください")
    
    # AP手法マスタ
    with tabs[4]:
        st.markdown("### 📞 AP手法マスタ")
        
        if not masters['approach_methods'].empty:
            st.dataframe(
                masters['approach_methods'][['method_id', 'method_name', 'description', 'created_at']],
                use_container_width=True,
                column_config={
                    "method_id": "ID",
                    "method_name": "手法名",
                    "description": "説明",
                    "created_at": st.column_config.DatetimeColumn("作成日時")
                }
            )
        else:
            st.info("AP手法データがありません")
        
        with st.form("add_method"):
            col1, col2 = st.columns(2)
            with col1:
                method_name = st.text_input("新規AP手法名")
            with col2:
                method_description = st.text_input("説明")
            
            if st.form_submit_button("📞 AP手法を追加"):
                if method_name:
                    try:
                        response = insert_master_data('approach_methods', {
                            'method_name': method_name,
                            'description': method_description if method_description else None
                        })
                        if response:
                            st.success(f"AP手法 '{method_name}' を追加しました")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("追加に失敗しました")
                    except Exception as e:
                        st.error(f"エラー: {str(e)}")
                else:
                    st.error("AP手法名を入力してください")


def show_specifications():
    st.subheader("📋 データベース仕様書（v2.0）")
    
    tabs = st.tabs(["🎯 概要", "📊 ER図", "📋 テーブル仕様", "🔄 データフロー", "🚀 v2.0更新内容"])
    
    # 概要タブ
    with tabs[0]:
        st.markdown("## 🎯 システム概要（v2.0）")
        
        st.markdown("""
        ### HR人材コンタクト管理 & 案件管理システム
        
        **目的**: HR業界における人材コンタクト情報と求人案件を効率的に管理し、人材と案件のマッチングを支援するシステム
        
        **主な機能**:
        - 📊 **ダッシュボード**: KPI表示、可視化分析
        - 👥 **コンタクト管理**: 人材情報の一覧表示、検索、編集、削除  
        - 🎯 **案件管理**: 求人案件の管理、人材アサイン状況の追跡
        - 📝 **新規登録**: コンタクト・案件情報の新規追加
        - ⚙️ **マスタ管理**: 企業・部署・優先度・アプローチ手法の管理
        
        **技術スタック**:
        - **フロントエンド**: Streamlit
        - **バックエンド**: Python  
        - **データベース**: Supabase (PostgreSQL)
        - **可視化**: Plotly
        
        **データベース構造**:
        - **11テーブル**: 正規化されたリレーショナル設計
        - **12外部キー制約**: データ整合性保証
        - **ENUM型対応**: 業種の標準化
        - **時系列管理**: アプローチ履歴・アサイン履歴
        """)
        
        st.markdown("### 📈 システム効果")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **効率化**:
            - 手動管理からの脱却
            - 検索・フィルタ機能
            - リアルタイム更新
            """)
        
        with col2:
            st.markdown("""
            **可視化**:
            - 部署別分析
            - 優先度管理
            - 進捗追跡
            """)
    
    # ER図タブ
    with tabs[1]:
        st.markdown("## 📊 ER図（エンティティ関係図）")
        
        st.markdown("""
        ```
        ┌─────────────────┐    ┌─────────────────┐
        │   companies     │    │   positions     │
        │                 │    │                 │
        │ PK target_company_id   │    │ PK position_id  │
        │    company_name │    │    position_name│
        │    created_at   │    │    created_at   │
        │    updated_at   │    │    updated_at   │
        └─────────────────┘    └─────────────────┘
                                         ▲
                                         │
                              ┌─────────────────┐
                              │ priority_levels │
                              │                 │
                              │ PK priority_id  │
                              │    priority_name│
                              │    priority_value│
                              │ │    description  │            │
                              │ │    created_at   │            │
                              │ └─────────────────┘            │
                              │           ▲                   │
        ┌─────────────────┐   │           │                   │
        │search_assignees │   │           │                   │
        │                 │   │           │ ┌─────────────────┐
        │ PK assignee_id  │   │           │ │ approach_methods│
        │    assignee_name│   │           │ │                 │
        │    created_at   │   │           │ │ PK method_id    │
        │    updated_at   │   │           │ │    method_name  │
        └─────────────────┘   │           │ │    description  │
                ▲             │           │ │    created_at   │
                │             │           │ └─────────────────┘
                │             │           │           ▲
                │             │           │           │
        ┌───────┴─────────────┴───────────┴───────────┴───────┐
        │                    contacts                         │
        │                                                     │
        │ PK contact_id                                       │
        │ FK target_company_id ──────────────────────────────────────┘
        │    department_name
        │    position_name
        │    last_name
        │    first_name
        │ FK priority_id
        │ FK search_assignee_id
        │ FK approach_method_id
        │    full_name
        │    furigana
        │    estimated_age
        │    profile
        │    url
        │    memo
        │    screening_status
        │    name_search_key
        │    work_comment
        │    search_date
        │    email_trial_history
        │    ap_date
        │    created_at
        │    updated_at
        └─────────────────────────────────────────────────────┘
        ```
        """)
        
        st.markdown("### 🔗 リレーション")
        st.markdown("""
        - **companies (1) ↔ (N) contacts**: 企業は複数のコンタクトを持つ
        - **priority_levels (1) ↔ (N) contacts**: 優先度は複数のコンタクトで使用される
        - **search_assignees (1) ↔ (N) contacts**: 担当者は複数のコンタクトを担当
        - **approach_methods (1) ↔ (N) contacts**: AP手法は複数のコンタクトで使用される
        """)
    
    # テーブル仕様タブ
    with tabs[2]:
        st.markdown("## 📋 テーブル仕様")
        
        # メインテーブル
        st.markdown("### 🎯 メインテーブル")
        
        st.markdown("#### contacts（コンタクト）")
        contact_spec = pd.DataFrame([
            ["contact_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "コンタクトID（自動採番）"],
            ["target_company_id", "BIGINT", "FOREIGN KEY", "NULL", "企業ID（companiesテーブル参照）"],
            ["full_name", "VARCHAR(255)", "", "NOT NULL", "氏名"],
            ["furigana", "VARCHAR(255)", "", "NULL", "フリガナ"],
            ["department_name", "VARCHAR(255)", "", "NULL", "部署名（テキスト）"],
            ["position_id", "BIGINT", "FOREIGN KEY", "NULL", "役職ID（positionsテーブル参照）"],
            ["estimated_age", "VARCHAR(20)", "", "NULL", "推定年齢"],
            ["profile", "TEXT", "", "NULL", "プロフィール"],
            ["url", "TEXT", "", "NULL", "URL"],
            ["memo", "TEXT", "", "NULL", "メモ"],
            ["screening_status", "VARCHAR(50)", "", "NULL", "精査状況"],
            ["priority_id", "BIGINT", "FOREIGN KEY", "NULL", "優先度ID（priority_levelsテーブル参照）"],
            ["name_search_key", "VARCHAR(255)", "", "NULL", "名前検索キー"],
            ["work_comment", "TEXT", "", "NULL", "作業コメント"],
            ["search_assignee_id", "BIGINT", "FOREIGN KEY", "NULL", "検索担当者ID（search_assigneesテーブル参照）"],
            ["search_date", "DATE", "", "NULL", "検索日"],
            ["email_trial_history", "TEXT", "", "NULL", "メール履歴"],
            ["ap_date", "DATE", "", "NULL", "AP実施日"],
            ["approach_method_id", "BIGINT", "FOREIGN KEY", "NULL", "AP手法ID（approach_methodsテーブル参照）"],
            ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"],
            ["updated_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "更新日時"]
        ], columns=["カラム名", "型", "制約", "NULL許可", "説明"])
        
        st.dataframe(contact_spec, use_container_width=True, hide_index=True)
        
        # マスターテーブル
        st.markdown("### ⚙️ マスターテーブル")
        
        master_tables = {
            "companies（企業）": [
                ["target_company_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "企業ID（自動採番）"],
                ["company_name", "VARCHAR(255)", "UNIQUE", "NOT NULL", "企業名"],
                ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"],
                ["updated_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "更新日時"]
            ],
            "positions（役職）": [
                ["position_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "役職ID（自動採番）"],
                ["position_name", "VARCHAR(255)", "UNIQUE", "NOT NULL", "役職名"],
                ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"],
                ["updated_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "更新日時"]
            ],
            "search_assignees（検索担当者）": [
                ["assignee_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "担当者ID（自動採番）"],
                ["assignee_name", "VARCHAR(100)", "UNIQUE", "NOT NULL", "担当者名"],
                ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"],
                ["updated_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "更新日時"]
            ],
            "priority_levels（優先度）": [
                ["priority_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "優先度ID（自動採番）"],
                ["priority_name", "VARCHAR(50)", "UNIQUE", "NOT NULL", "優先度名"],
                ["priority_value", "DECIMAL(3,2)", "UNIQUE", "NOT NULL", "優先度値"],
                ["description", "TEXT", "", "NULL", "説明"],
                ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"]
            ],
            "approach_methods（AP手法）": [
                ["method_id", "BIGSERIAL", "PRIMARY KEY", "NOT NULL", "手法ID（自動採番）"],
                ["method_name", "VARCHAR(100)", "UNIQUE", "NOT NULL", "手法名"],
                ["description", "TEXT", "", "NULL", "説明"],
                ["created_at", "TIMESTAMP", "DEFAULT", "NOT NULL", "作成日時"]
            ]
        }
        
        for table_name, spec in master_tables.items():
            st.markdown(f"#### {table_name}")
            df_spec = pd.DataFrame(spec, columns=["カラム名", "型", "制約", "NULL許可", "説明"])
            st.dataframe(df_spec, use_container_width=True, hide_index=True)
        
        # ビュー
        st.markdown("### 👁️ ビュー")
        st.markdown("""
        #### contacts_detail（コンタクト詳細ビュー）
        - **目的**: 正規化されたテーブルを結合して、表示用の非正規化データを提供
        - **結合対象**: contacts + companies + priority_levels + search_assignees + approach_methods
        - **用途**: アプリケーションでの一覧表示、検索、フィルタリング
        """)
    
    # データフロータブ
    with tabs[3]:
        st.markdown("## 🔄 データフロー")
        
        st.markdown("### 📊 ダッシュボード")
        st.markdown("""
        ```
        1. contacts_detail ビューからデータ取得
        2. カラム名マッピング（full_name → name, company_name → company等）
        3. HR分析用カラム生成（salary, performance_score, training_hours等）
        4. フィルタリング（部署、職位）
        5. KPI計算・グラフ生成・テーブル表示
        ```
        """)
        
        st.markdown("### 👥 コンタクト管理")
        st.markdown("""
        ```
        【表示】
        1. contacts_detail ビューからデータ取得
        2. フィルタリング（企業、優先度、精査状況、AP状況）
        3. 一覧表示
        
        【編集】
        1. 対象レコード選択
        2. contacts テーブル UPDATE
        3. キャッシュクリア・画面再読み込み
        
        【削除】
        1. 対象レコード選択
        2. contacts テーブル DELETE
        3. キャッシュクリア・画面再読み込み
        ```
        """)
        
        st.markdown("### 📝 新規登録")
        st.markdown("""
        ```
        1. マスターデータ取得（companies, positions等）
        2. フォーム入力値検証
        3. 各マスターテーブルからID取得
        4. contacts テーブル INSERT
        5. キャッシュクリア
        ```
        """)
        
        st.markdown("### ⚙️ マスタ管理")
        st.markdown("""
        ```
        【企業マスタ】
        companies テーブル INSERT
        
        【担当者マスタ】
        search_assignees テーブル INSERT
        
        【優先度マスタ】
        priority_levels テーブル INSERT
        
        【AP手法マスタ】
        approach_methods テーブル INSERT
        ```
        """)
        
        st.markdown("### 🔧 技術的注意点")
        st.markdown("""
        **キャッシュ戦略**:
        - `@st.cache_data(ttl=300)`: 5分間のデータキャッシュ
        - データ更新時に `st.cache_data.clear()` でキャッシュクリア
        
        **エラーハンドリング**:
        - Supabase接続失敗時はサンプルデータにフォールバック
        - カラム名の動的判定（full_name/name等）
        - 安全なデータアクセス（.get()メソッド使用）
        
        **セキュリティ**:
        - Row Level Security (RLS) 対応
        - APIキー認証
        - SQLインジェクション対策（Supabaseクライアント使用）
        """)
    
    # v2.0更新内容タブ
    with tabs[4]:
        st.markdown("## 🚀 v2.0 更新内容")
        
        st.markdown("### ✅ 新機能・テーブル追加")
        
        new_features = pd.DataFrame([
            ["🎯 案件管理", "projects", "求人案件の詳細管理機能", "案件一覧・新規作成・人材アサイン"],
            ["👥 アサイン管理", "project_assignments", "案件と人材のマッチング", "アサイン状況・履歴追跡"],
            ["🎯 ターゲット企業管理", "project_target_companies", "案件別企業・部門・優先度管理", "企業部門組み合わせに優先度設定"],
            ["🏭 業種分類", "industry_type (ENUM)", "日本標準産業分類対応", "16種類の業種マスタ"],
            ["📊 統合分析", "Dashboard拡張", "案件・人材統合ダッシュボード", "KPI・可視化強化"]
        ], columns=["機能", "テーブル/実装", "説明", "詳細"])
        
        st.dataframe(new_features, use_container_width=True, hide_index=True)
        
        st.markdown("### 🔧 技術的改善")
        
        improvements = pd.DataFrame([
            ["データベース正規化", "部署情報のマスタ化", "企業 → 部署 → 人材の階層構造"],
            ["外部キー制約強化", "12個の外部キー制約", "データ整合性の完全保証"],
            ["タイムスタンプ統一", "timestamp with time zone", "全テーブルでタイムゾーン対応"],
            ["ENUM型導入", "業種の標準化", "データ品質向上・検索性能向上"],
            ["UI/UX改善", "案件管理ページ追加", "直感的な案件・アサイン管理"]
        ], columns=["改善項目", "内容", "効果"])
        
        st.dataframe(improvements, use_container_width=True, hide_index=True)
        
        st.markdown("### 📈 システム効果")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **機能拡張**:
            - 案件管理の一元化
            - 人材マッチング効率化  
            - 部署別分析可能
            - 業種別レポート対応
            """)
        
        with col2:
            st.markdown("""
            **データ品質向上**:
            - 正規化によるデータ重複排除
            - 外部キー制約による整合性保証
            - ENUM型による入力値統制
            - 時系列データ管理強化
            """)
        
        st.markdown("### 🔄 マイグレーション状況")
        
        st.success("✅ v1.0 → v2.0 マイグレーション完了")
        
        migration_status = pd.DataFrame([
            ["✅ 完了", "projects テーブル作成", "求人案件管理"],
            ["✅ 完了", "project_assignments テーブル作成", "案件・人材アサイン"],
            ["✅ 完了", "industry_type ENUM作成", "業種標準化"],
            ["✅ 完了", "外部キー制約追加", "データ整合性強化"],
            ["✅ 完了", "タイムスタンプ型統一", "timezone対応"],
            ["✅ 完了", "システムUI更新", "案件管理画面追加"]
        ], columns=["状況", "作業内容", "説明"])
        
        st.dataframe(migration_status, use_container_width=True, hide_index=True)
        
        st.markdown("### 🚀 今後の拡張予定")
        
        st.info("""
        **Phase 3.0 予定機能**:
        - 📊 高度な分析・レポート機能
        - 🔔 案件・人材マッチング通知システム  
        - 🎯 AIによる人材推薦機能
        - 📱 モバイル対応UI
        - 🔗 外部求人サイト連携API
        - 📈 成約率・稼働率分析ダッシュボード
        """)


def show_contacts_create():
    """新規コンタクト登録機能"""
    st.markdown("### 📝 新規コンタクト登録")
    
    masters = fetch_master_data()
    
    with st.form("create_contact_form", clear_on_submit=True):
        st.markdown("#### 基本情報")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 企業選択
            if not masters['target_companies'].empty:
                company_options = [""] + masters['target_companies']['company_name'].tolist()
                selected_company = st.selectbox("企業名 *", company_options)
                
            else:
                selected_company = st.text_input("企業名 *", placeholder="手動入力")
            
            # 部署名（自由入力）
            selected_department = st.text_input("部署名", placeholder="営業部、開発部など")
            
            # 姓・名を分けて入力
            col_name1, col_name2 = st.columns(2)
            with col_name1:
                last_name = st.text_input("姓 *", placeholder="山田")
            with col_name2:
                first_name = st.text_input("名 *", placeholder="太郎")
            
            # フリガナも姓・名に分けて入力
            col_furigana1, col_furigana2 = st.columns(2)
            with col_furigana1:
                furigana_last_name = st.text_input("フリガナ（姓）", placeholder="ヤマダ")
            with col_furigana2:
                furigana_first_name = st.text_input("フリガナ（名）", placeholder="タロウ")
            
            estimated_age = st.text_input("推定年齢", placeholder="30代")
            
        with col2:
            # 役職入力
            position_name = st.text_input("役職", placeholder="部長、課長、マネージャーなど")
            
            # 優先度選択
            if not masters['priorities'].empty:
                priority_options = [""] + masters['priorities']['priority_name'].tolist()
                selected_priority = st.selectbox("優先度", priority_options)
            else:
                selected_priority = st.text_input("優先度", placeholder="高・中・低")
            
            # 検索担当者選択
            if not masters['search_assignees'].empty:
                assignee_options = [""] + masters['search_assignees']['assignee_name'].tolist()
                selected_assignee = st.selectbox("検索担当者", assignee_options)
            else:
                selected_assignee = st.text_input("検索担当者", placeholder="担当者名")
            
            search_date = st.date_input("検索日", value=None)
        
        st.markdown("#### 詳細情報")
        
        col3, col4 = st.columns(2)
        
        with col3:
            profile = st.text_area("プロフィール", placeholder="経歴や専門分野など")
            url = st.text_input("URL", placeholder="LinkedIn、会社HP等のURL")
            name_search_key = st.text_input("検索キー", placeholder="検索に使用したキーワード")
        
        with col4:
            screening_status = st.text_input("精査状況", placeholder="精査済み、要精査など")
            primary_screening_comment = st.text_area("精査コメント", placeholder="精査時のコメント")
            work_comment = st.text_area("作業コメント", placeholder="作業時のメモ")
        
        st.markdown("#### 履歴情報")
        email_trial_history = st.text_area("メール履歴", placeholder="メール送信履歴やトライアル状況")
        
        submitted = st.form_submit_button("登録", type="primary")
        
        if submitted:
            # 必須項目チェック
            if not last_name or not first_name:
                st.error("姓と名は必須項目です")
                return
            
            # 氏名を結合
            full_name = f"{last_name} {first_name}"
            furigana = None
            if furigana_last_name and furigana_first_name:
                furigana = f"{furigana_last_name} {furigana_first_name}"
            elif furigana_last_name:
                furigana = furigana_last_name
            elif furigana_first_name:
                furigana = furigana_first_name
            
            # 企業IDを取得
            target_company_id = None
            if selected_company and not masters['target_companies'].empty:
                company_match = masters['target_companies'][masters['target_companies']['company_name'] == selected_company]
                if not company_match.empty:
                    target_company_id = int(company_match.iloc[0]['target_company_id'])
            
            # 部署名はテキストとして保存
            
            # 優先度IDを取得
            priority_id = None
            if selected_priority and not masters['priorities'].empty:
                priority_match = masters['priorities'][masters['priorities']['priority_name'] == selected_priority]
                if not priority_match.empty:
                    priority_id = int(priority_match.iloc[0]['priority_id'])
            
            # 検索担当者IDを取得
            search_assignee_id = None
            if selected_assignee and not masters['search_assignees'].empty:
                assignee_match = masters['search_assignees'][masters['search_assignees']['assignee_name'] == selected_assignee]
                if not assignee_match.empty:
                    search_assignee_id = int(assignee_match.iloc[0]['assignee_id'])
            
            try:
                # contactsテーブルに挿入
                contact_data = {
                    'target_company_id': target_company_id,
                    'full_name': full_name,
                    'last_name': last_name,
                    'first_name': first_name,
                    'furigana': furigana,
                    'furigana_last_name': furigana_last_name if furigana_last_name else None,
                    'furigana_first_name': furigana_first_name if furigana_first_name else None,
                    'estimated_age': estimated_age if estimated_age else None,
                    'profile': profile if profile else None,
                    'url': url if url else None,
                    'screening_status': screening_status if screening_status else None,
                    'primary_screening_comment': primary_screening_comment if primary_screening_comment else None,
                    'priority_id': priority_id,
                    'name_search_key': name_search_key if name_search_key else None,
                    'work_comment': work_comment if work_comment else None,
                    'search_assignee_id': search_assignee_id,
                    'search_date': search_date.isoformat() if search_date else None,
                    'email_trial_history': email_trial_history if email_trial_history else None,
                    'department_name': selected_department if selected_department else None,
                    'position_name': position_name if position_name else None
                }
                
                # None値を除去
                contact_data = {k: v for k, v in contact_data.items() if v is not None}
                
                response = supabase.table('contacts').insert(contact_data).execute()
                st.success(f"コンタクト「{full_name}」が正常に登録されました")
                st.rerun()
                
            except Exception as e:
                st.error(f"登録に失敗しました: {str(e)}")


def show_contacts_edit():
    """コンタクト詳細編集機能"""
    st.markdown("### ✏️ コンタクト詳細編集")
    
    # 実際のデータベースデータのみを取得
    if supabase is None:
        st.warning("データベースに接続されていません。編集機能を使用するにはSupabase接続が必要です。")
        return
    
    try:
        response = supabase.table('contacts_detail').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
        else:
            df = pd.DataFrame()
    except:
        df = pd.DataFrame()
    
    if df.empty:
        st.info("データベースに登録されたコンタクトがありません。まず「新規登録」タブからコンタクトを追加してください。")
        return
    
    # 編集対象選択
    contact_options = df.apply(lambda row: f"{row.get('full_name', 'N/A')} ({row.get('company_name', 'N/A')})", axis=1).tolist()
    
    # selected_contact_idが設定されている場合、自動選択
    default_index = 0
    selected_contact_id = None
    
    # 編集ボタンから来た場合の選択ID
    if 'selected_contact_id' in st.session_state and st.session_state.selected_contact_id:
        selected_contact_id = st.session_state.selected_contact_id
    # 一覧から選択した場合のID
    elif 'selected_contact_id_from_list' in st.session_state and st.session_state.selected_contact_id_from_list:
        selected_contact_id = st.session_state.selected_contact_id_from_list
    
    if selected_contact_id:
        try:
            # 該当するコンタクトのインデックスを探す
            matching_indices = df[df['contact_id'] == selected_contact_id].index
            if len(matching_indices) > 0:
                default_index = df.index.get_loc(matching_indices[0])
        except:
            pass
    
    selected_index = st.selectbox("編集するコンタクトを選択してください", range(len(contact_options)),
                                  format_func=lambda x: contact_options[x],
                                  index=default_index)
    
    if selected_index is not None:
        selected_contact = df.iloc[selected_index]
        contact_id = selected_contact.get('contact_id')
        
        masters = fetch_master_data()
        
        # アプローチ履歴と案件アサイン状況を表示
        st.markdown("---")
        
        # タブで分割
        approach_tab, assignment_tab = st.tabs(["📞 アプローチ履歴管理", "🎯 案件アサイン状況"])
        
        with approach_tab:
            st.markdown("#### 📞 アプローチ履歴管理")
            
            # 既存のアプローチ履歴を取得・表示
            approaches_df = fetch_contact_approaches(contact_id)
            
            if not approaches_df.empty:
                st.markdown("**既存のアプローチ履歴:**")
                for _, approach in approaches_df.iterrows():
                    col_date, col_method, col_action = st.columns([2, 2, 1])
                    with col_date:
                        st.text(f"📅 {approach['approach_date']}")
                    with col_method:
                        st.text(f"📞 {approach['method_name']}")
                    with col_action:
                        if st.button(f"🗑️", key=f"delete_approach_{approach['approach_id']}", help="削除"):
                            try:
                                supabase.table('contact_approaches').delete().eq('approach_id', approach['approach_id']).execute()
                                st.success("アプローチ履歴を削除しました")
                                st.rerun()
                            except Exception as e:
                                st.error(f"削除に失敗しました: {str(e)}")
            else:
                st.info("アプローチ履歴がありません")
            
            # 新しいアプローチ履歴を追加
            st.markdown("**新しいアプローチを追加:**")
            
            with st.form("add_approach_form"):
                col_date, col_method = st.columns(2)
                
                with col_date:
                    approach_date = st.date_input("アプローチ日", value=date.today())
                
                with col_method:
                    if not masters['approach_methods'].empty:
                        method_options = [""] + masters['approach_methods']['method_name'].tolist()
                        selected_method = st.selectbox("アプローチ手法", method_options)
                    else:
                        selected_method = st.text_input("アプローチ手法", placeholder="電話、メール、LinkedIn等")
                
                # 案件との関連付け（オプション）
                project_note = st.text_area("備考（案件名や詳細等）", placeholder="どの案件に対するアプローチか、結果はどうだったか等")
                
                if st.form_submit_button("📞 アプローチ履歴を追加"):
                    if selected_method:
                        try:
                            # 次のapproach_orderを取得
                            existing_approaches = supabase.table('contact_approaches').select('approach_order').eq('contact_id', contact_id).execute()
                            max_order = 0
                            if existing_approaches.data:
                                max_order = max([a['approach_order'] for a in existing_approaches.data])
                            next_order = max_order + 1
                            
                            # アプローチ手法IDを取得
                            method_id = None
                            if not masters['approach_methods'].empty:
                                method_data = masters['approach_methods'][masters['approach_methods']['method_name'] == selected_method]
                                if not method_data.empty:
                                    method_id = method_data.iloc[0]['method_id']
                            
                            if method_id:
                                approach_data = {
                                    'contact_id': contact_id,
                                    'approach_date': approach_date.isoformat(),
                                    'approach_method_id': method_id,
                                    'approach_order': next_order
                                }
                                
                                supabase.table('contact_approaches').insert(approach_data).execute()
                                st.success("✅ アプローチ履歴を追加しました！")
                                st.rerun()
                            else:
                                st.error("アプローチ手法が見つかりません")
                        except Exception as e:
                            st.error(f"追加に失敗しました: {str(e)}")
                    else:
                        st.warning("アプローチ手法を選択してください")
        
        with assignment_tab:
            st.markdown("#### 🎯 案件アサイン状況")
            
            # 案件アサイン履歴を取得・表示
            assignments_df = fetch_project_assignments_for_contact(contact_id)
            
            if not assignments_df.empty:
                st.markdown("**案件アサイン履歴:**")
                for _, assignment in assignments_df.iterrows():
                    col_project, col_company, col_status, col_date = st.columns([3, 2, 2, 2])
                    with col_project:
                        st.text(f"🎯 {assignment['project_name']}")
                    with col_company:
                        st.text(f"🏢 {assignment['company_name']}")
                    with col_status:
                        status_color = {"ASSIGNED": "🟢", "CANDIDATE": "🟡", "INTERVIEW": "🔵", "COMPLETED": "✅", "REJECTED": "🔴"}
                        status_icon = status_color.get(assignment['assignment_status'], "⚪")
                        st.text(f"{status_icon} {assignment['assignment_status']}")
                    with col_date:
                        st.text(f"📅 {assignment.get('created_at', 'N/A')[:10] if assignment.get('created_at') else 'N/A'}")
            else:
                st.info("案件アサイン履歴がありません")
        
        st.markdown("---")
        
        with st.form("edit_contact_form"):
            st.markdown(f"#### 編集中: {selected_contact.get('full_name', 'N/A')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 企業選択
                current_company = selected_contact.get('company_name', '')
                if not masters['target_companies'].empty:
                    company_options = [""] + masters['target_companies']['company_name'].tolist()
                    try:
                        company_index = company_options.index(current_company) if current_company in company_options else 0
                    except ValueError:
                        company_index = 0
                    selected_company = st.selectbox("企業名", company_options, index=company_index)
                else:
                    selected_company = st.text_input("企業名", value=current_company)
                
                # 姓・名
                last_name = st.text_input("姓", value=selected_contact.get('last_name', ''))
                first_name = st.text_input("名", value=selected_contact.get('first_name', ''))
                
                # フリガナ
                furigana_last_name = st.text_input("フリガナ（姓）", value=selected_contact.get('furigana_last_name', ''))
                furigana_first_name = st.text_input("フリガナ（名）", value=selected_contact.get('furigana_first_name', ''))
                
                estimated_age = st.text_input("推定年齢", value=selected_contact.get('estimated_age', ''))
                
                # 生年月日
                from datetime import datetime
                min_date = datetime(1900, 1, 1).date()  # 1900年から選択可能
                max_date = date.today()  # 今日まで選択可能
                current_birth_date = selected_contact.get('birth_date')
                if current_birth_date:
                    try:
                        birth_date = st.date_input("生年月日", value=pd.to_datetime(current_birth_date).date(), format="YYYY-MM-DD", min_value=min_date, max_value=max_date, key=f"edit_birth_date_{selected_contact.get('id', 'default')}")
                    except:
                        birth_date = st.date_input("生年月日", value=None, format="YYYY-MM-DD", min_value=min_date, max_value=max_date, key=f"edit_birth_date_{selected_contact.get('id', 'default')}_fallback")
                else:
                    birth_date = st.date_input("生年月日", value=None, format="YYYY-MM-DD", min_value=min_date, max_value=max_date, key=f"edit_birth_date_{selected_contact.get('id', 'default')}_new")
                
                # 生年月日から実年齢を自動計算
                if birth_date:
                    today = date.today()
                    actual_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    st.text_input("実年齢", value=f"{actual_age}歳", disabled=True)
                else:
                    actual_age = None
                    st.text_input("実年齢", value="生年月日を選択してください", disabled=True)
                
            with col2:
                # 部署
                selected_department = st.text_input("部署名", value=selected_contact.get('department_name', ''))
                position_name = st.text_input("役職", value=selected_contact.get('position_name', ''))
                
                # 優先度
                current_priority = selected_contact.get('priority_name', '')
                if not masters['priorities'].empty:
                    priority_options = [""] + masters['priorities']['priority_name'].tolist()
                    try:
                        priority_index = priority_options.index(current_priority) if current_priority in priority_options else 0
                    except ValueError:
                        priority_index = 0
                    selected_priority = st.selectbox("優先度", priority_options, index=priority_index)
                else:
                    selected_priority = st.text_input("優先度", value=current_priority)
                
                # 検索担当者
                current_assignee = selected_contact.get('search_assignee', '')
                if not masters['search_assignees'].empty:
                    assignee_options = [""] + masters['search_assignees']['assignee_name'].tolist()
                    try:
                        assignee_index = assignee_options.index(current_assignee) if current_assignee in assignee_options else 0
                    except ValueError:
                        assignee_index = 0
                    selected_assignee = st.selectbox("検索担当者", assignee_options, index=assignee_index)
                else:
                    selected_assignee = st.text_input("検索担当者", value=current_assignee)
                
                # 検索日
                current_search_date = selected_contact.get('search_date')
                if current_search_date:
                    try:
                        search_date = st.date_input("検索日", value=pd.to_datetime(current_search_date).date())
                    except:
                        search_date = st.date_input("検索日", value=None)
                else:
                    search_date = st.date_input("検索日", value=None)
            
            # 詳細情報
            st.markdown("#### 詳細情報")
            col3, col4 = st.columns(2)
            
            with col3:
                profile = st.text_area("プロフィール", value=selected_contact.get('profile', ''))
                url = st.text_input("URL", value=selected_contact.get('url', ''))
                name_search_key = st.text_input("検索キー", value=selected_contact.get('name_search_key', ''))
            
            with col4:
                screening_status = st.text_input("精査状況", value=selected_contact.get('screening_status', ''))
                primary_screening_comment = st.text_area("精査コメント", value=selected_contact.get('primary_screening_comment', ''))
                work_comment = st.text_area("作業コメント", value=selected_contact.get('work_comment', ''))
            
            email_trial_history = st.text_area("メール履歴", value=selected_contact.get('email_trial_history', ''))
            
            submitted = st.form_submit_button("更新", type="primary")
            
            if submitted:
                # 氏名を結合
                full_name = f"{last_name} {first_name}" if last_name and first_name else selected_contact.get('full_name', '')
                furigana = None
                if furigana_last_name and furigana_first_name:
                    furigana = f"{furigana_last_name} {furigana_first_name}"
                elif furigana_last_name:
                    furigana = furigana_last_name
                elif furigana_first_name:
                    furigana = furigana_first_name
                
                # 企業IDを取得
                target_company_id = None
                if selected_company and not masters['target_companies'].empty:
                    company_match = masters['target_companies'][masters['target_companies']['company_name'] == selected_company]
                    if not company_match.empty:
                        target_company_id = int(company_match.iloc[0]['target_company_id'])
                
                # 優先度IDを取得
                priority_id = None
                if selected_priority and not masters['priorities'].empty:
                    priority_match = masters['priorities'][masters['priorities']['priority_name'] == selected_priority]
                    if not priority_match.empty:
                        priority_id = int(priority_match.iloc[0]['priority_id'])
                
                # 検索担当者IDを取得
                search_assignee_id = None
                if selected_assignee and not masters['search_assignees'].empty:
                    assignee_match = masters['search_assignees'][masters['search_assignees']['assignee_name'] == selected_assignee]
                    if not assignee_match.empty:
                        search_assignee_id = int(assignee_match.iloc[0]['assignee_id'])
                
                try:
                    # 更新データ準備
                    update_data = {
                        'target_company_id': target_company_id,
                        'full_name': full_name,
                        'last_name': last_name,
                        'first_name': first_name,
                        'furigana': furigana,
                        'furigana_last_name': furigana_last_name if furigana_last_name else None,
                        'furigana_first_name': furigana_first_name if furigana_first_name else None,
                        'estimated_age': estimated_age if estimated_age else None,
                        'birth_date': birth_date.isoformat() if birth_date else None,
                        'actual_age': actual_age if actual_age else None,
                        'profile': profile if profile else None,
                        'url': url if url else None,
                        'screening_status': screening_status if screening_status else None,
                        'primary_screening_comment': primary_screening_comment if primary_screening_comment else None,
                        'priority_id': priority_id,
                        'name_search_key': name_search_key if name_search_key else None,
                        'work_comment': work_comment if work_comment else None,
                        'search_assignee_id': search_assignee_id,
                        'search_date': search_date.isoformat() if search_date else None,
                        'email_trial_history': email_trial_history if email_trial_history else None,
                        'department_name': selected_department if selected_department else None,
                        'position_name': position_name if position_name else None
                    }
                    
                    # None値を除去
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    response = supabase.table('contacts').update(update_data).eq('contact_id', contact_id).execute()
                    st.success(f"コンタクト「{full_name}」が正常に更新されました")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"更新に失敗しました: {str(e)}")


def show_contacts_delete():
    """コンタクト削除機能"""
    st.markdown("### 🗑️ コンタクト削除")
    
    # 実際のデータベースデータのみを取得
    if supabase is None:
        st.warning("データベースに接続されていません。削除機能を使用するにはSupabase接続が必要です。")
        return
    
    try:
        response = supabase.table('contacts_detail').select('*').execute()
        if response.data:
            df = pd.DataFrame(response.data)
        else:
            df = pd.DataFrame()
    except:
        df = pd.DataFrame()
    
    if df.empty:
        st.info("データベースに登録されたコンタクトがありません。削除可能なデータがありません。")
        return
    
    st.warning("⚠️ 削除されたデータは復元できません。十分ご注意ください。")
    
    # 削除対象選択
    contact_options = df.apply(lambda row: f"{row.get('full_name', 'N/A')} ({row.get('company_name', 'N/A')})", axis=1).tolist()
    
    # selected_contact_idが設定されている場合、自動選択
    default_index = 0
    selected_contact_id = None
    
    # 編集ボタンから来た場合の選択ID
    if 'selected_contact_id' in st.session_state and st.session_state.selected_contact_id:
        selected_contact_id = st.session_state.selected_contact_id
    # 一覧から選択した場合のID
    elif 'selected_contact_id_from_list' in st.session_state and st.session_state.selected_contact_id_from_list:
        selected_contact_id = st.session_state.selected_contact_id_from_list
    
    if selected_contact_id:
        try:
            # 該当するコンタクトのインデックスを探す
            matching_indices = df[df['contact_id'] == selected_contact_id].index
            if len(matching_indices) > 0:
                default_index = df.index.get_loc(matching_indices[0])
        except:
            pass
    
    selected_index = st.selectbox("削除するコンタクトを選択してください", range(len(contact_options)),
                                  format_func=lambda x: contact_options[x],
                                  index=default_index)
    
    if selected_index is not None:
        selected_contact = df.iloc[selected_index]
        contact_id = selected_contact.get('contact_id')
        
        # 削除対象の詳細表示
        st.markdown("#### 削除対象の詳細")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text(f"氏名: {selected_contact.get('full_name', 'N/A')}")
            st.text(f"企業名: {selected_contact.get('company_name', 'N/A')}")
            st.text(f"部署名: {selected_contact.get('department_name', 'N/A')}")
            st.text(f"役職: {selected_contact.get('position_name', 'N/A')}")
        
        with col2:
            st.text(f"優先度: {selected_contact.get('priority_name', 'N/A')}")
            st.text(f"検索担当者: {selected_contact.get('search_assignee', 'N/A')}")
            st.text(f"検索日: {selected_contact.get('search_date', 'N/A')}")
            st.text(f"精査状況: {selected_contact.get('screening_status', 'N/A')}")
        
        # 確認チェックボックス
        confirm_delete = st.checkbox("上記のコンタクトを削除することを確認しました")
        
        if confirm_delete:
            if st.button("🗑️ 削除実行", type="primary"):
                try:
                    # 関連データも削除する必要がある場合は先に削除
                    # (外部キー制約により)
                    
                    # まず関連するproject_assignmentsを削除
                    supabase.table('project_assignments').delete().eq('contact_id', contact_id).execute()
                    
                    # 関連するcontact_approachesを削除
                    supabase.table('contact_approaches').delete().eq('contact_id', contact_id).execute()
                    
                    # 関連するwork_locationsを削除
                    supabase.table('work_locations').delete().eq('contact_id', contact_id).execute()
                    
                    # 最後にcontactsテーブルから削除
                    response = supabase.table('contacts').delete().eq('contact_id', contact_id).execute()
                    
                    st.success(f"コンタクト「{selected_contact.get('full_name', 'N/A')}」が正常に削除されました")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"削除に失敗しました: {str(e)}")


# CSV インポート関数
def show_data_import():
    """📥 データインポート機能"""
    st.title("📥 データインポート")
    st.markdown("---")
    
    # サンプルファイルダウンロードセクション
    st.subheader("📋 サンプルCSVダウンロード")
    st.markdown("適切な形式でデータをインポートするため、まずサンプルCSVファイルをダウンロードしてフォーマットを確認してください。")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🏢 企業データサンプル**")
        company_sample = generate_company_sample_csv()
        st.download_button(
            label="📥 企業データサンプル.csv",
            data=company_sample,
            file_name="企業データサンプル.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.markdown("**🎯 案件データサンプル**")
        project_sample = generate_project_sample_csv()
        st.download_button(
            label="📥 案件データサンプル.csv",
            data=project_sample,
            file_name="案件データサンプル.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        st.markdown("**👥 コンタクトデータサンプル**")
        contact_sample = generate_contact_sample_csv()
        st.download_button(
            label="📥 コンタクトデータサンプル.csv",
            data=contact_sample,
            file_name="コンタクトデータサンプル.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # 重複処理オプション
    st.subheader("⚙️ インポート設定")
    col1, col2 = st.columns(2)
    
    with col1:
        duplicate_handling = st.radio(
            "重複データ処理方法",
            options=["重複を許可（すべて登録）", "重複をスキップ（新規のみ登録）", "重複を更新（既存データを更新）"],
            index=0,
            help="既存データと同じ情報がある場合の処理方法を選択してください"
        )
    
    with col2:
        st.markdown("**重複判定基準:**")
        st.markdown("- 🏢 **企業**: 企業名")  
        st.markdown("- 🎯 **案件**: 企業名 + 案件名")
        st.markdown("- 👥 **コンタクト**: 企業名 + 氏名")
    
    st.markdown("---")
    
    # タブ分け
    tab1, tab2, tab3 = st.tabs(["🏢 企業データ", "🎯 案件データ", "👥 コンタクトデータ"])
    
    with tab1:
        st.subheader("🏢 企業データインポート")
        
        # ファイルアップローダー
        uploaded_file = st.file_uploader(
            "企業データCSVファイルを選択してください",
            type=['csv'],
            key="company_upload"
        )
        
        if uploaded_file:
            try:
                # CSVを読み込み
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                
                # データプレビュー
                st.write("**データプレビュー:**")
                st.dataframe(df.head())
                
                # カラムマッピング設定
                st.write("**カラムマッピング設定:**")
                col1, col2 = st.columns(2)
                
                with col1:
                    company_name_col = st.selectbox(
                        "企業名カラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('企業名') if '企業名' in df.columns else 0
                    )
                    
                    industry_col = st.selectbox(
                        "業種カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('業種') + 1 if '業種' in df.columns else 0
                    )
                
                with col2:
                    target_dept_col = st.selectbox(
                        "ターゲット部署カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('TG部署') + 1 if 'TG部署' in df.columns else 0
                    )
                
                # インポートボタン
                if st.button("📥 企業データをインポート", type="primary"):
                    if supabase is None:
                        st.warning("⚠️ データベース接続がありません。サンプルデータモードでは実際のインポートはできません。")
                        return
                        
                    success_count = import_company_data(df, company_name_col, industry_col, target_dept_col, duplicate_handling)
                    if success_count > 0:
                        st.success(f"✅ {success_count}件の企業データをインポートしました")
                        st.cache_data.clear()
                        st.rerun()
                    
            except Exception as e:
                st.error(f"❌ ファイル読み込みエラー: {str(e)}")
    
    with tab2:
        st.subheader("🎯 案件データインポート")
        
        # ファイルアップローダー
        uploaded_file = st.file_uploader(
            "案件データCSVファイルを選択してください",
            type=['csv'],
            key="project_upload"
        )
        
        if uploaded_file:
            try:
                # CSVを読み込み
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                
                # データプレビュー
                st.write("**データプレビュー:**")
                st.dataframe(df.head())
                
                # カラムマッピング設定
                st.write("**カラムマッピング設定:**")
                col1, col2, col3 = st.columns(3)
                
                mapping_config = {}
                
                with col1:
                    mapping_config['company_name'] = st.selectbox(
                        "企業名カラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('企業名') if '企業名' in df.columns else 0
                    )
                    mapping_config['project_name'] = st.selectbox(
                        "案件名カラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('案件名') if '案件名' in df.columns else 0
                    )
                    mapping_config['status'] = st.selectbox(
                        "ステータスカラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('ステータス') if 'ステータス' in df.columns else 0
                    )
                
                with col2:
                    mapping_config['contract_start'] = st.selectbox(
                        "契約開始日カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('契約開始日') + 1 if '契約開始日' in df.columns else 0
                    )
                    mapping_config['contract_end'] = st.selectbox(
                        "契約終了日カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('契約終了日') + 1 if '契約終了日' in df.columns else 0
                    )
                    mapping_config['headcount'] = st.selectbox(
                        "契約人数カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('契約人数') + 1 if '契約人数' in df.columns else 0
                    )
                
                with col3:
                    mapping_config['co_manager'] = st.selectbox(
                        "担当COカラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('担当CO') + 1 if '担当CO' in df.columns else 0
                    )
                    mapping_config['re_manager'] = st.selectbox(
                        "担当REカラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('担当RE') + 1 if '担当RE' in df.columns else 0
                    )
                
                # インポートボタン
                if st.button("📥 案件データをインポート", type="primary"):
                    if supabase is None:
                        st.warning("⚠️ データベース接続がありません。サンプルデータモードでは実際のインポートはできません。")
                        return
                        
                    success_count = import_project_data(df, mapping_config, duplicate_handling)
                    if success_count > 0:
                        st.success(f"✅ {success_count}件の案件データをインポートしました")
                        st.cache_data.clear()
                        st.rerun()
                    
            except Exception as e:
                st.error(f"❌ ファイル読み込みエラー: {str(e)}")
    
    with tab3:
        st.subheader("👥 コンタクトデータインポート")
        
        # ファイルアップローダー
        uploaded_file = st.file_uploader(
            "コンタクトデータCSVファイルを選択してください",
            type=['csv'],
            key="contact_upload"
        )
        
        if uploaded_file:
            try:
                # CSVを読み込み
                df = pd.read_csv(uploaded_file, encoding='utf-8')
                
                # データプレビュー
                st.write("**データプレビュー:**")
                st.dataframe(df.head())
                
                # カラムマッピング設定
                st.write("**カラムマッピング設定:**")
                col1, col2, col3 = st.columns(3)
                
                mapping_config = {}
                
                with col1:
                    mapping_config['company_name'] = st.selectbox(
                        "企業名カラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('企業名') if '企業名' in df.columns else 0,
                        key="contact_company"
                    )
                    mapping_config['full_name'] = st.selectbox(
                        "氏名カラム",
                        options=df.columns.tolist(),
                        index=df.columns.tolist().index('氏名') if '氏名' in df.columns else 0,
                        key="contact_name"
                    )
                    mapping_config['department'] = st.selectbox(
                        "部署カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('部署') + 1 if '部署' in df.columns else 0,
                        key="contact_dept"
                    )
                    mapping_config['position'] = st.selectbox(
                        "役職カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('役職') + 1 if '役職' in df.columns else 0,
                        key="contact_position"
                    )
                
                with col2:
                    mapping_config['email'] = st.selectbox(
                        "メールアドレスカラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('メール') + 1 if 'メール' in df.columns else 0,
                        key="contact_email"
                    )
                    mapping_config['phone'] = st.selectbox(
                        "電話番号カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('電話番号') + 1 if '電話番号' in df.columns else 0,
                        key="contact_phone"
                    )
                    mapping_config['age'] = st.selectbox(
                        "年齢カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('年齢') + 1 if '年齢' in df.columns else 0,
                        key="contact_age"
                    )
                
                with col3:
                    mapping_config['priority'] = st.selectbox(
                        "優先度カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('優先度') + 1 if '優先度' in df.columns else 0,
                        key="contact_priority"
                    )
                    mapping_config['assignee'] = st.selectbox(
                        "担当者カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('担当者') + 1 if '担当者' in df.columns else 0,
                        key="contact_assignee"
                    )
                    mapping_config['status'] = st.selectbox(
                        "スクリーニング状況カラム",
                        options=['選択しない'] + df.columns.tolist(),
                        index=df.columns.tolist().index('スクリーニング状況') + 1 if 'スクリーニング状況' in df.columns else 0,
                        key="contact_status"
                    )
                
                # インポートボタン
                if st.button("📥 コンタクトデータをインポート", type="primary"):
                    if supabase is None:
                        st.warning("⚠️ データベース接続がありません。サンプルデータモードでは実際のインポートはできません。")
                        return
                        
                    success_count = import_contact_data(df, mapping_config, duplicate_handling)
                    if success_count > 0:
                        st.success(f"✅ {success_count}件のコンタクトデータをインポートしました")
                        st.cache_data.clear()
                        st.rerun()
                    
            except Exception as e:
                st.error(f"❌ ファイル読み込みエラー: {str(e)}")


# CSV サンプル生成関数
def generate_company_sample_csv():
    """企業データサンプルCSVを生成"""
    sample_data = {
        '企業名': ['株式会社サンプルIT', 'サンプル商事株式会社', '株式会社サンプル製造'],
        '業種': ['IT・情報通信業', '卸売業・小売業', '製造業'],
        'TG部署': ['システム開発部', '営業部', '生産管理部'],
        'HPサーチ': ['済', '未', '済'],
        'KWサーチ': ['済', '済', '未'],
        'Eightサーチ': ['未', '済', '未'],
        'LinkedIn': ['未', '未', '済'],
        'メアドサーチ': ['済', '未', '未']
    }
    
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False, encoding='utf-8-sig')


def generate_project_sample_csv():
    """案件データサンプルCSVを生成"""
    sample_data = {
        '企業名': ['株式会社サンプルIT', 'サンプル商事株式会社', '株式会社サンプル製造'],
        '案件名': ['Webシステム開発エンジニア', '営業マネージャー', '生産管理スペシャリスト'],
        'ステータス': ['OPEN', 'OPEN', 'CLOSED'],
        '契約開始日': ['2024/04/01', '2024/05/01', '2024/03/01'],
        '契約終了日': ['2024/12/31', '2025/03/31', '2024/12/31'],
        '契約人数': [3, 1, 2],
        '担当CO': ['田中', '佐藤', '山田'],
        '担当RE': ['鈴木', '高橋', '渡辺'],
        '業務内容': ['Webアプリケーション開発', '新規顧客開拓', '生産計画策定・管理'],
        '人材要件': ['Java, Spring Boot経験3年以上', '営業経験5年以上', '製造業経験必須'],
        '雇用形態': ['正社員', '正社員', '契約社員'],
        'レイヤー': ['シニア', 'マネージャー', 'スペシャリスト'],
        '勤務地': ['東京都港区', '東京都千代田区', '神奈川県横浜市'],
        '年齢下限': [25, 30, 28],
        '年齢上限': [40, 45, 50],
        '学歴': ['大卒以上', '大卒以上', '専門卒以上'],
        '必要資格': ['基本情報技術者', 'なし', '品質管理検定'],
        '紹介用職業分類': ['013 情報処理・通信技術者', '033 営業関係者', '061 生産技術者']
    }
    
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False, encoding='utf-8-sig')


def generate_contact_sample_csv():
    """コンタクトデータサンプルCSVを生成"""
    sample_data = {
        '企業名': ['株式会社サンプルIT', 'サンプル商事株式会社', '株式会社サンプル製造', '株式会社サンプルIT', 'サンプル商事株式会社'],
        '氏名': ['山田太郎', '佐藤花子', '田中次郎', '鈴木一郎', '高橋美咲'],
        '部署': ['システム開発部', '営業部', '生産管理部', 'インフラ部', 'マーケティング部'],
        '役職': ['部長', 'マネージャー', 'スペシャリスト', '課長', '主任'],
        'メール': ['yamada@sample-it.co.jp', 'sato@sample-trade.com', 'tanaka@sample-mfg.co.jp', 'suzuki@sample-it.co.jp', 'takahashi@sample-trade.com'],
        '電話番号': ['03-1234-5678', '03-2345-6789', '045-3456-7890', '03-1234-5679', '03-2345-6780'],
        '年齢': [45, 38, 42, 35, 29],
        '優先度': ['高', '中', '高', '中', '低'],
        '担当者': ['田中', '佐藤', '山田', '田中', '佐藤'],
        'スクリーニング状況': ['未実施', '実施済み', '実施中', '未実施', '実施済み']
    }
    
    df = pd.DataFrame(sample_data)
    return df.to_csv(index=False, encoding='utf-8-sig')


def import_company_data(df, company_name_col, industry_col, target_dept_col, duplicate_handling):
    """企業データをデータベースにインポート"""
    success_count = 0
    skip_count = 0
    update_count = 0
    
    try:
        for _, row in df.iterrows():
            company_name = str(row[company_name_col]).strip()
            
            # 空の行はスキップ
            if not company_name or company_name.lower() in ['nan', 'null', '']:
                continue
            
            # 重複チェック
            existing_company = supabase.table('target_companies').select('target_company_id').eq('company_name', company_name).execute()
            
            if existing_company.data:
                # 重複データが存在する場合
                if duplicate_handling == "重複をスキップ（新規のみ登録）":
                    skip_count += 1
                    continue
                elif duplicate_handling == "重複を更新（既存データを更新）":
                    # 既存データを更新
                    target_company_id = existing_company.data[0]['target_company_id']
                    update_data = {'updated_at': datetime.now().isoformat()}
                    
                    # 業種情報があれば追加
                    if industry_col != '選択しない' and industry_col in df.columns:
                        industry = str(row[industry_col]).strip()
                        if industry and industry.lower() not in ['nan', 'null', '']:
                            industry_mapping = {
                                'SIer': 'IT・情報通信業',
                                'IT': 'IT・情報通信業',
                                '製造': '製造業',
                                '金融': '金融業',
                                '商社': '卸売業・小売業',
                                'コンサル': 'サービス業'
                            }
                            mapped_industry = industry_mapping.get(industry, industry)
                            update_data['industry'] = mapped_industry
                    
                    supabase.table('target_companies').update(update_data).eq('target_company_id', target_company_id).execute()
                    update_count += 1
                    continue
                # else: 重複を許可（すべて登録）の場合は通常通り処理
            
            # 企業データ作成
            company_data = {
                'company_name': company_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 業種情報があれば追加
            if industry_col != '選択しない' and industry_col in df.columns:
                industry = str(row[industry_col]).strip()
                if industry and industry.lower() not in ['nan', 'null', '']:
                    # 業種マッピング（必要に応じて調整）
                    industry_mapping = {
                        'SIer': 'IT・情報通信業',
                        'IT': 'IT・情報通信業',
                        '製造': '製造業',
                        '金融': '金融業',
                        '商社': '卸売業・小売業',
                        'コンサル': 'サービス業'
                    }
                    mapped_industry = industry_mapping.get(industry, industry)
                    company_data['industry'] = mapped_industry
            
            # 企業をデータベースに挿入
            company_response = supabase.table('target_companies').insert(company_data).execute()
            
            if company_response.data:
                target_company_id = company_response.data[0]['target_company_id']
                success_count += 1
                
                # ターゲット部署情報があれば部署テーブルに追加
                if target_dept_col != '選択しない' and target_dept_col in df.columns:
                    target_dept = str(row[target_dept_col]).strip()
                    if target_dept and target_dept.lower() not in ['nan', 'null', '']:
                        dept_data = {
                            'company_id': target_company_id,
                            'department_name': target_dept,
                            'is_target_department': True,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        # 部署マスタは廃止：各コンタクトに直接部署名を保存
                        pass
        
        # 結果表示
        if success_count > 0 or skip_count > 0 or update_count > 0:
            result_message = f"📊 企業データ処理結果: 新規登録 {success_count}件"
            if skip_count > 0:
                result_message += f", スキップ {skip_count}件"
            if update_count > 0:
                result_message += f", 更新 {update_count}件"
            st.info(result_message)
        
        return success_count + update_count  # 処理された件数として返す
        
    except Exception as e:
        st.error(f"❌ インポート中にエラーが発生しました: {str(e)}")
        return success_count


def import_project_data(df, mapping_config, duplicate_handling):
    """案件データをデータベースにインポート"""
    success_count = 0
    skip_count = 0
    update_count = 0
    
    try:
        for _, row in df.iterrows():
            company_name = str(row[mapping_config['company_name']]).strip()
            project_name = str(row[mapping_config['project_name']]).strip()
            
            # 空の行はスキップ
            if not company_name or not project_name or \
               company_name.lower() in ['nan', 'null', ''] or \
               project_name.lower() in ['nan', 'null', '']:
                continue
            
            # 企業IDを取得
            company_response = supabase.table('target_companies').select('target_company_id').eq('company_name', company_name).execute()
            
            if not company_response.data:
                st.warning(f"⚠️ 企業「{company_name}」が見つかりません。先に企業データをインポートしてください。")
                continue
                
            target_company_id = company_response.data[0]['target_company_id']
            
            # 重複チェック（企業名 + 案件名で判定）
            existing_project = supabase.table('projects').select('project_id').eq('target_company_id', target_company_id).eq('project_name', project_name).execute()
            
            if existing_project.data:
                # 重複データが存在する場合
                if duplicate_handling == "重複をスキップ（新規のみ登録）":
                    skip_count += 1
                    continue
                elif duplicate_handling == "重複を更新（既存データを更新）":
                    # 既存データを更新
                    project_id = existing_project.data[0]['project_id']
                    update_data = {
                        'status': str(row[mapping_config['status']]).strip(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # オプションフィールドを追加
                    optional_fields = {
                        'contract_start': 'contract_start_date',
                        'contract_end': 'contract_end_date',
                        'headcount': 'required_headcount',
                        'co_manager': 'co_manager',
                        're_manager': 're_manager'
                    }
                    
                    for config_key, db_field in optional_fields.items():
                        col_name = mapping_config.get(config_key)
                        if col_name and col_name != '選択しない' and col_name in df.columns:
                            value = str(row[col_name]).strip()
                            if value and value.lower() not in ['nan', 'null', '']:
                                if 'date' in db_field:
                                    try:
                                        if '/' in value:
                                            date_obj = datetime.strptime(value, '%Y/%m/%d').date()
                                        elif '-' in value:
                                            date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                                        else:
                                            continue
                                        update_data[db_field] = date_obj.isoformat()
                                    except:
                                        continue
                                elif 'headcount' in db_field:
                                    try:
                                        update_data[db_field] = int(float(value))
                                    except:
                                        continue
                                else:
                                    update_data[db_field] = value
                    
                    supabase.table('projects').update(update_data).eq('project_id', project_id).execute()
                    update_count += 1
                    continue
                # else: 重複を許可（すべて登録）の場合は通常通り処理
            
            # 案件データ作成
            project_data = {
                'target_company_id': target_company_id,
                'project_name': project_name,
                'status': str(row[mapping_config['status']]).strip(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # オプションフィールドを追加
            optional_fields = {
                'contract_start': 'contract_start_date',
                'contract_end': 'contract_end_date',
                'headcount': 'required_headcount',
                'co_manager': 'co_manager',
                're_manager': 're_manager'
            }
            
            for config_key, db_field in optional_fields.items():
                col_name = mapping_config.get(config_key)
                if col_name and col_name != '選択しない' and col_name in df.columns:
                    value = str(row[col_name]).strip()
                    if value and value.lower() not in ['nan', 'null', '']:
                        if 'date' in db_field:
                            # 日付フォーマット変換
                            try:
                                if '/' in value:
                                    date_obj = datetime.strptime(value, '%Y/%m/%d').date()
                                elif '-' in value:
                                    date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                                else:
                                    continue
                                project_data[db_field] = date_obj.isoformat()
                            except:
                                continue
                        elif 'headcount' in db_field:
                            try:
                                project_data[db_field] = int(float(value))
                            except:
                                continue
                        else:
                            project_data[db_field] = value
            
            # 案件をデータベースに挿入
            project_response = supabase.table('projects').insert(project_data).execute()
            
            if project_response.data:
                success_count += 1
        
        # 結果表示
        if success_count > 0 or skip_count > 0 or update_count > 0:
            result_message = f"📊 案件データ処理結果: 新規登録 {success_count}件"
            if skip_count > 0:
                result_message += f", スキップ {skip_count}件"
            if update_count > 0:
                result_message += f", 更新 {update_count}件"
            st.info(result_message)
        
        return success_count + update_count
        
    except Exception as e:
        st.error(f"❌ インポート中にエラーが発生しました: {str(e)}")
        return success_count


def import_contact_data(df, mapping_config, duplicate_handling):
    """コンタクトデータをデータベースにインポート"""
    success_count = 0
    skip_count = 0
    update_count = 0
    
    try:
        for _, row in df.iterrows():
            company_name = str(row[mapping_config['company_name']]).strip()
            full_name = str(row[mapping_config['full_name']]).strip()
            
            # 空の行をスキップ
            if not company_name or not full_name or \
               company_name.lower() in ['nan', 'null', ''] or \
               full_name.lower() in ['nan', 'null', '']:
                continue
            
            # 企業IDを取得
            company_response = supabase.table('target_companies').select('target_company_id').eq('company_name', company_name).execute()
            
            if not company_response.data:
                st.warning(f"⚠️ 企業「{company_name}」が見つかりません。先に企業データをインポートしてください。")
                continue
            
            target_company_id = company_response.data[0]['target_company_id']
            
            # 重複チェック（企業名 + 氏名で判定）
            existing_contact = supabase.table('contacts').select('contact_id').eq('target_company_id', target_company_id).eq('full_name', full_name).execute()
            
            if existing_contact.data:
                # 重複データが存在する場合
                if duplicate_handling == "重複をスキップ（新規のみ登録）":
                    skip_count += 1
                    continue
                elif duplicate_handling == "重複を更新（既存データを更新）":
                    # 既存データを更新
                    contact_id = existing_contact.data[0]['contact_id']
                    update_data = {'updated_at': datetime.now().isoformat()}
                    
                    # オプションフィールドを追加
                    optional_fields = {
                        'department': 'department_name',
                        'position': 'position_name',
                        'age': 'estimated_age',
                        'status': 'screening_status'
                    }
                    
                    for config_key, db_field in optional_fields.items():
                        col_name = mapping_config.get(config_key)
                        if col_name and col_name != '選択しない' and col_name in df.columns:
                            value = str(row[col_name]).strip()
                            if value and value.lower() not in ['nan', 'null', '']:
                                update_data[db_field] = value
                    
                    # 優先度の処理
                    if mapping_config.get('priority') and mapping_config['priority'] != '選択しない':
                        priority_value = str(row[mapping_config['priority']]).strip()
                        if priority_value and priority_value.lower() not in ['nan', 'null', '']:
                            priority_response = supabase.table('priority_levels').select('priority_id').eq('priority_name', priority_value).execute()
                            if priority_response.data:
                                update_data['priority_id'] = priority_response.data[0]['priority_id']
                    
                    # 担当者の処理
                    if mapping_config.get('assignee') and mapping_config['assignee'] != '選択しない':
                        assignee_value = str(row[mapping_config['assignee']]).strip()
                        if assignee_value and assignee_value.lower() not in ['nan', 'null', '']:
                            assignee_response = supabase.table('search_assignees').select('assignee_id').eq('assignee_name', assignee_value).execute()
                            if assignee_response.data:
                                update_data['search_assignee_id'] = assignee_response.data[0]['assignee_id']
                    
                    supabase.table('contacts').update(update_data).eq('contact_id', contact_id).execute()
                    update_count += 1
                    continue
                # else: 重複を許可（すべて登録）の場合は通常通り処理
            
            # コンタクトデータ作成
            contact_data = {
                'target_company_id': target_company_id,
                'full_name': full_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # オプションフィールドを追加
            optional_fields = {
                'department': 'department_name',
                'position': 'position_name',
                'age': 'estimated_age',
                'status': 'screening_status'
            }
            
            for config_key, db_field in optional_fields.items():
                col_name = mapping_config.get(config_key)
                if col_name and col_name != '選択しない' and col_name in df.columns:
                    value = str(row[col_name]).strip()
                    if value and value.lower() not in ['nan', 'null', '']:
                        contact_data[db_field] = value
            
            # 優先度の処理
            if mapping_config.get('priority') and mapping_config['priority'] != '選択しない':
                priority_value = str(row[mapping_config['priority']]).strip()
                if priority_value and priority_value.lower() not in ['nan', 'null', '']:
                    priority_response = supabase.table('priority_levels').select('priority_id').eq('priority_name', priority_value).execute()
                    if priority_response.data:
                        contact_data['priority_id'] = priority_response.data[0]['priority_id']
            
            # 担当者の処理
            if mapping_config.get('assignee') and mapping_config['assignee'] != '選択しない':
                assignee_value = str(row[mapping_config['assignee']]).strip()
                if assignee_value and assignee_value.lower() not in ['nan', 'null', '']:
                    assignee_response = supabase.table('search_assignees').select('assignee_id').eq('assignee_name', assignee_value).execute()
                    if assignee_response.data:
                        contact_data['search_assignee_id'] = assignee_response.data[0]['assignee_id']
            
            # データベースに挿入
            response = supabase.table('contacts').insert(contact_data).execute()
            
            if response.data:
                success_count += 1
        
        # 結果表示
        if success_count > 0 or skip_count > 0 or update_count > 0:
            result_message = f"📊 コンタクトデータ処理結果: 新規登録 {success_count}件"
            if skip_count > 0:
                result_message += f", スキップ {skip_count}件"
            if update_count > 0:
                result_message += f", 更新 {update_count}件"
            st.info(result_message)
        
        return success_count + update_count
        
    except Exception as e:
        st.error(f"❌ インポート中にエラーが発生しました: {str(e)}")
        return success_count

# =============================================================================
# 新しいDB機能（検索管理系）
# =============================================================================


def show_search_progress():
    """検索進捗ダッシュボード"""
    st.header("🔍 検索進捗ダッシュボード")
    
    if supabase is None:
        st.error("データベース接続エラー")
        return
    
    try:
        # target_companiesデータを取得
        companies_result = supabase.table('target_companies').select('*').execute()
        if not companies_result.data:
            st.info("企業データがありません")
            return
        
        companies_df = pd.DataFrame(companies_result.data)
        total_companies = len(companies_df)
        
        # 検索進捗の計算
        search_types = {
            'メール検索': 'email_searched',
            'LinkedIn検索': 'linkedin_searched',
            'ホームページ検索': 'homepage_searched',
            'Eight検索': 'eight_search'
        }
        
        # メトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        for i, (search_name, column_name) in enumerate(search_types.items()):
            completed = companies_df[column_name].notna().sum()
            progress = completed / total_companies if total_companies > 0 else 0
            
            with [col1, col2, col3, col4][i]:
                st.metric(
                    label=search_name,
                    value=f"{completed}/{total_companies}",
                    delta=f"{progress:.1%}"
                )
                st.progress(progress)
        
        # 企業別詳細進捗
        st.subheader("📊 企業別検索状況")
        
        progress_data = []
        for _, company in companies_df.iterrows():
            company_progress = {
                '企業名': company['company_name'],
                'メール検索': '✅' if pd.notna(company['email_searched']) else '⏳',
                'LinkedIn検索': '✅' if pd.notna(company['linkedin_searched']) else '⏳',
                'ホームページ検索': '✅' if pd.notna(company['homepage_searched']) else '⏳',
                'Eight検索': '✅' if pd.notna(company['eight_search']) else '⏳',
                '完了率': f"{sum([pd.notna(company[col]) for col in search_types.values()]) / len(search_types) * 100:.0f}%"
            }
            progress_data.append(company_progress)
        
        progress_df = pd.DataFrame(progress_data)
        st.dataframe(progress_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"データ取得エラー: {str(e)}")


def show_keyword_search():
    """キーワード検索管理"""
    st.header("🎯 キーワード検索管理")
    
    if supabase is None:
        st.error("データベース接続エラー")
        return
    
    # 企業選択
    companies_result = supabase.table('target_companies').select('target_company_id, company_name').execute()
    if not companies_result.data:
        st.info("企業データがありません")
        return
    
    company_options = {f"{c['company_name']}": c['target_company_id'] for c in companies_result.data}
    selected_company = st.selectbox("企業を選択", list(company_options.keys()))
    
    if selected_company:
        company_id = company_options[selected_company]
        
        # 既存のキーワード検索履歴を取得
        result = supabase.table('target_companies').select('keyword_searches').eq('target_company_id', company_id).execute()
        existing_searches = []
        if result.data and result.data[0]['keyword_searches']:
            existing_searches = result.data[0]['keyword_searches']
        
        st.subheader(f"📋 {selected_company} のキーワード検索履歴")
        
        # 既存履歴の表示
        if existing_searches:
            for search in existing_searches:
                col1, col2, col3 = st.columns([1, 2, 3])
                with col1:
                    st.write(f"検索{search.get('search_number', 'N/A')}")
                with col2:
                    st.write(search.get('date', 'N/A'))
                with col3:
                    st.write(search.get('keyword', 'N/A'))
        else:
            st.info("まだキーワード検索履歴がありません")
        
        # 新規検索履歴の追加
        st.subheader("➕ 新しい検索を追加")
        
        col1, col2 = st.columns(2)
        with col1:
            search_date = st.date_input("検索日", value=date.today())
        with col2:
            keyword = st.text_input("検索キーワード", placeholder="例: Python エンジニア 東京")
        
        if st.button("検索履歴を追加"):
            if keyword:
                new_search = {
                    "date": search_date.isoformat(),
                    "keyword": keyword,
                    "search_number": len(existing_searches) + 1
                }
                updated_searches = existing_searches + [new_search]
                
                try:
                    supabase.table('target_companies').update({
                        'keyword_searches': updated_searches
                    }).eq('target_company_id', company_id).execute()
                    
                    st.success("✅ 検索履歴を追加しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 追加に失敗しました: {str(e)}")
            else:
                st.error("キーワードを入力してください")


def show_email_management():
    """メール管理機能"""
    st.header("📧 メール管理システム")
    
    # URLパラメータから選択状態を取得
    query_params = st.query_params
    default_project_id = query_params.get("email_project", "")
    default_company_id = query_params.get("email_company", "")
    
    if supabase is None:
        st.error("データベース接続エラー")
        return
    
    # 案件とターゲット企業の選択UI
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 案件を選択")
        # 案件データを取得
        project_options = {"選択してください": None}
        
        try:
            projects_result = supabase.table('projects').select('project_id, project_name').order('project_name').execute()
            if projects_result.data:
                for p in projects_result.data:
                    project_options[p['project_name']] = p['project_id']
        except Exception as e:
            st.warning(f"案件データ取得エラー: {str(e)}")
        
        # URLパラメータからデフォルト選択を設定
        default_project_name = "選択してください"
        if default_project_id:
            for name, pid in project_options.items():
                if str(pid) == default_project_id:
                    default_project_name = name
                    break
        
        selected_project_name = st.selectbox(
            "案件",
            options=list(project_options.keys()),
            index=list(project_options.keys()).index(default_project_name),
            key="email_project_select"
        )
        selected_project_id = project_options[selected_project_name]
        
        # URLパラメータを更新
        if selected_project_id:
            st.query_params["email_project"] = str(selected_project_id)
        else:
            if "email_project" in st.query_params:
                del st.query_params["email_project"]
            if "email_company" in st.query_params:
                del st.query_params["email_company"]
    
    with col2:
        st.subheader("🏢 ターゲット企業を選択")
        company_id = None
        selected_company = None
        
        # 案件が選択されている場合、その案件に関連する企業のみ表示
        if selected_project_id:
            company_options = {"選択してください": None}
            
            try:
                # project_target_companiesから該当案件のターゲット企業を取得
                target_result = supabase.table('project_target_companies').select(
                    'target_company_id, target_companies(company_name)'
                ).eq('project_id', selected_project_id).execute()
                
                if target_result.data:
                    for t in target_result.data:
                        if t.get('target_companies'):
                            company_name = t['target_companies']['company_name']
                            company_options[company_name] = t['target_company_id']
            except Exception as e:
                st.warning(f"企業データ取得エラー: {str(e)}")
            
            # URLパラメータからデフォルト選択を設定
            default_company_name = "選択してください"
            if default_company_id:
                for name, cid in company_options.items():
                    if str(cid) == default_company_id:
                        default_company_name = name
                        break
            
            selected_company_name = st.selectbox(
                "ターゲット企業",
                options=list(company_options.keys()),
                index=list(company_options.keys()).index(default_company_name),
                key="email_company_select",
                disabled=False
            )
            company_id = company_options[selected_company_name]
            selected_company = selected_company_name if company_id else None
            
            # URLパラメータを更新
            if company_id:
                st.query_params["email_company"] = str(company_id)
            elif "email_company" in st.query_params:
                del st.query_params["email_company"]
        else:
            st.selectbox(
                "ターゲット企業",
                options=["先に案件を選択してください"],
                key="email_company_select",
                disabled=True
            )
    
    # メール管理機能の表示
    if company_id and selected_company:
        st.markdown("---")
        st.subheader(f"📧 {selected_company} のメール管理")
        
        # タブで機能を分割
        tabs = st.tabs(["🔍 検索パターン", "✅ 確認済みメール", "❌ 誤送信履歴"])
        
        with tabs[0]:
            show_email_patterns_tab(company_id, selected_company)
            # 検索パターンの下にメモセクションを追加
            st.divider()
            show_email_memo_section(company_id, selected_company)
        
        with tabs[1]:
            show_confirmed_emails_tab(company_id, selected_company)
        
        with tabs[2]:
            show_misdelivery_emails_tab(company_id, selected_company)
    else:
        st.info("📌 案件とターゲット企業を選択してください")


def show_email_patterns_tab(company_id, company_name):
    """メール検索パターンタブ"""
    st.subheader(f"🔍 {company_name} のメール検索パターン")
    
    # 既存パターンの取得（Session Stateを使わずに直接DBから取得）
    result = supabase.table('target_companies').select('email_search_patterns').eq('target_company_id', company_id).execute()
    existing_patterns = []
    if result.data and result.data[0]['email_search_patterns']:
        existing_patterns = result.data[0]['email_search_patterns']
    
    # 既存パターンの表示と削除
    if existing_patterns:
        st.write("### 登録済みパターン")
        patterns_to_keep = existing_patterns.copy()
        for i, pattern in enumerate(existing_patterns):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.text(f"• {pattern}")
            with col2:
                if st.button("🗑️ 削除", key=f"delete_existing_pattern_{company_id}_{i}"):
                    patterns_to_keep.remove(pattern)
                    try:
                        supabase.table('target_companies').update({
                            'email_search_patterns': patterns_to_keep if patterns_to_keep else None
                        }).eq('target_company_id', company_id).execute()
                        st.success("✅ パターンを削除しました")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 削除に失敗しました: {str(e)}")
        st.divider()
    
    # 新しいパターンの追加
    st.write("### 新しいパターンを追加")
    new_pattern = st.text_input(
        "メールパターン",
        placeholder="例: firstname.lastname@company.com (*をワイルドカードとして使用可能)",
        key=f"new_pattern_{company_id}"
    )
    
    if st.button("➕ パターンを追加", key=f"add_pattern_{company_id}", type="primary"):
        if new_pattern:
            updated_patterns = existing_patterns + [new_pattern]
            try:
                supabase.table('target_companies').update({
                    'email_search_patterns': updated_patterns
                }).eq('target_company_id', company_id).execute()
                st.success("✅ パターンを追加しました")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 追加に失敗しました: {str(e)}")
        else:
            st.error("パターンを入力してください")


def show_confirmed_emails_tab(company_id, company_name):
    """確認済みメールタブ"""
    st.subheader(f"✅ {company_name} の確認済みメール")
    
    # 既存メールの取得
    result = supabase.table('target_companies').select('confirmed_emails').eq('target_company_id', company_id).execute()
    existing_emails = []
    if result.data and result.data[0]['confirmed_emails']:
        existing_emails = result.data[0]['confirmed_emails']
    
    # 既存メールの表示と削除機能
    if existing_emails:
        st.write("### 登録済みメールアドレス")
        
        # メールアドレスの昇順でソート
        sorted_emails = sorted(existing_emails, key=lambda x: x.get('email', '').lower())
        
        # ヘッダー行
        col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 1.5, 1.5, 1.5, 1.5, 0.5])
        with col1:
            st.markdown("**メールアドレス**")
        with col2:
            st.markdown("**氏名**")
        with col3:
            st.markdown("**部署**")
        with col4:
            st.markdown("**役職**")
        with col5:
            st.markdown("**確認方法**")
        with col6:
            st.markdown("**確認日**")
        with col7:
            st.markdown("**削除**")
        
        st.divider()
        
        # 各メールを個別に表示（削除ボタン付き）
        for email_data in sorted_emails:
            # 元のリストでのインデックスを取得（削除用）
            original_index = existing_emails.index(email_data)
            col1, col2, col3, col4, col5, col6, col7 = st.columns([3, 2, 1.5, 1.5, 1.5, 1.5, 0.5])
            
            with col1:
                st.write(email_data.get('email', ''))
            with col2:
                st.write(email_data.get('name', ''))
            with col3:
                st.write(email_data.get('department', ''))
            with col4:
                st.write(email_data.get('position', ''))
            with col5:
                st.write(email_data.get('confirmation_method', ''))
            with col6:
                # 日付のフォーマット
                confirmed_date = email_data.get('confirmed_date', '')
                if confirmed_date:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(confirmed_date.replace('Z', '+00:00'))
                        st.write(dt.strftime('%Y/%m/%d'))
                    except:
                        st.write(confirmed_date[:10] if len(confirmed_date) >= 10 else confirmed_date)
                else:
                    st.write('')
            with col7:
                if st.button("🗑️", key=f"delete_email_{company_id}_{original_index}", help=f"{email_data.get('email', '')}を削除"):
                    updated_emails = [e for j, e in enumerate(existing_emails) if j != original_index]
                    try:
                        supabase.table('target_companies').update({
                            'confirmed_emails': updated_emails if updated_emails else None
                        }).eq('target_company_id', company_id).execute()
                        
                        st.success(f"✅ {email_data.get('email', '')} を削除しました")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 削除に失敗しました: {str(e)}")
    else:
        st.info("まだ確認済みメールがありません")
    
    # 新規メール追加フォーム
    st.subheader("➕ 新しいメールを追加")
    st.caption("※ * は必須項目です")
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("メールアドレス *", key="new_email")
        name = st.text_input("氏名 *", key="new_name")
        department = st.text_input("部署", key="new_dept")
    
    with col2:
        position = st.text_input("役職", key="new_position")
        method = st.selectbox("確認方法", ["LinkedIn", "企業HP", "名刺交換", "電話確認"], key="new_method")
        confirmed_date = st.date_input("確認日", value=date.today(), key="new_confirmed_date")
    
    if st.button("メールを追加", key="add_email"):
        if email and name:
            new_email = {
                "email": email,
                "name": name,
                "department": department,
                "position": position,
                "confirmed_date": confirmed_date.isoformat(),
                "confirmation_method": method
            }
            updated_emails = existing_emails + [new_email]
            
            try:
                supabase.table('target_companies').update({
                    'confirmed_emails': updated_emails
                }).eq('target_company_id', company_id).execute()
                
                st.success("✅ メールを追加しました")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 追加に失敗しました: {str(e)}")
        else:
            st.error("メールアドレスと氏名は必須です")


def show_misdelivery_emails_tab(company_id, company_name):
    """誤送信履歴タブ"""
    st.subheader(f"❌ {company_name} の誤送信履歴")
    
    # 既存履歴の取得
    result = supabase.table('target_companies').select('misdelivery_emails').eq('target_company_id', company_id).execute()
    existing_misdelivery = []
    if result.data and result.data[0]['misdelivery_emails']:
        existing_misdelivery = result.data[0]['misdelivery_emails']
    
    # 既存履歴の表示と削除機能
    if existing_misdelivery:
        st.write("### 登録済み誤送信履歴")
        
        # メールアドレスの昇順でソート
        sorted_misdelivery = sorted(existing_misdelivery, key=lambda x: x.get('email', '').lower())
        
        # ヘッダー行
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 3, 0.5])
        with col1:
            st.markdown("**誤送信先メール**")
        with col2:
            st.markdown("**送信日**")
        with col3:
            st.markdown("**理由**")
        with col4:
            st.markdown("**詳細メモ**")
        with col5:
            st.markdown("**削除**")
        
        st.divider()
        
        # 各履歴を個別に表示（削除ボタン付き）
        for sorted_idx, misdelivery_data in enumerate(sorted_misdelivery):
            # 元のリストでのインデックスを取得（削除用）
            original_index = existing_misdelivery.index(misdelivery_data)
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 3, 0.5])
            
            with col1:
                st.write(misdelivery_data.get('email', ''))
            with col2:
                # 日付のフォーマット
                sent_date = misdelivery_data.get('sent_date', '')
                if sent_date:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(sent_date.replace('Z', '+00:00'))
                        st.write(dt.strftime('%Y/%m/%d'))
                    except:
                        st.write(sent_date[:10] if len(sent_date) >= 10 else sent_date)
                else:
                    st.write('')
            with col3:
                st.write(misdelivery_data.get('reason', ''))
            with col4:
                st.write(misdelivery_data.get('memo', ''))
            with col5:
                if st.button("🗑️", key=f"delete_misdelivery_{company_id}_{sorted_idx}_{original_index}", help=f"{misdelivery_data.get('email', '')}を削除"):
                    updated_misdelivery = [e for j, e in enumerate(existing_misdelivery) if j != original_index]
                    try:
                        supabase.table('target_companies').update({
                            'misdelivery_emails': updated_misdelivery if updated_misdelivery else None
                        }).eq('target_company_id', company_id).execute()
                        
                        st.success(f"✅ {misdelivery_data.get('email', '')} の記録を削除しました")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 削除に失敗しました: {str(e)}")
    else:
        st.info("誤送信履歴はありません")
    
    # 新規履歴追加フォーム
    st.subheader("➕ 誤送信記録を追加")
    st.caption("※ * は必須項目です")
    
    col1, col2 = st.columns(2)
    with col1:
        wrong_email = st.text_input("誤送信先メール *", key="wrong_email")
        sent_date = st.date_input("送信日", value=date.today(), key="sent_date")
    
    with col2:
        reason = st.selectbox("理由", ["同姓同名の別人", "退職済み", "部署間違い", "会社間違い", "その他"], key="reason")
        memo = st.text_area("詳細メモ", key="memo")
    
    if st.button("記録を追加", key="add_misdelivery"):
        if wrong_email:
            new_record = {
                "email": wrong_email,
                "sent_date": sent_date.isoformat(),
                "reason": reason,
                "memo": memo
            }
            updated_records = existing_misdelivery + [new_record]
            
            try:
                supabase.table('target_companies').update({
                    'misdelivery_emails': updated_records
                }).eq('target_company_id', company_id).execute()
                
                st.success("✅ 記録を追加しました")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 追加に失敗しました: {str(e)}")
        else:
            st.error("メールアドレスは必須です")


def show_email_memo_section(company_id, company_name):
    """メール検索メモセクション"""
    st.subheader(f"📝 メール検索メモ")
    
    # 既存メモの取得
    result = supabase.table('target_companies').select('email_search_memo').eq('target_company_id', company_id).execute()
    existing_memo = ""
    if result.data and result.data[0]['email_search_memo']:
        existing_memo = result.data[0]['email_search_memo']
    
    memo = st.text_area(
        "パターンに関する備考",
        value=existing_memo,
        height=150,
        placeholder="メール検索パターンに関する備考やメモを記録...\n例：\n- 旧姓の場合は maiden.name@company.com を使用\n- 外国人スタッフは英語名を使用\n- HR部門は別ドメイン hr@company-hr.com を使用",
        key="email_memo"
    )
    
    if st.button("💾 メモを保存", key="save_memo", type="secondary"):
        try:
            supabase.table('target_companies').update({
                'email_search_memo': memo if memo else None
            }).eq('target_company_id', company_id).execute()
            
            st.success("✅ メモを保存しました")
        except Exception as e:
            st.error(f"❌ 保存に失敗しました: {str(e)}")


def show_company_management():
    """企業管理機能"""
    st.header("🏢 企業管理")
    
    if supabase is None:
        st.error("データベース接続エラー")
        return
    
    tab1, tab2 = st.tabs(["📋 企業一覧", "➕ 新規企業追加"])
    
    with tab1:
        # 企業一覧の表示
        companies_result = supabase.table('target_companies').select('*').execute()
        if companies_result.data:
            df = pd.DataFrame(companies_result.data)
            
            # 表示用にカラムを選択・整理
            display_columns = ['company_name', 'company_url', 'created_at']
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                st.dataframe(df[available_columns], use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.info("企業データがありません")
    
    with tab2:
        # 新規企業追加フォーム
        st.subheader("新しい企業を追加")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("企業名")
        with col2:
            company_url = st.text_input("企業URL", placeholder="https://example.com")
        
        if st.button("企業を追加"):
            if company_name:
                try:
                    new_company = {
                        'company_name': company_name,
                        'company_url': company_url if company_url else None
                    }
                    
                    supabase.table('target_companies').insert(new_company).execute()
                    st.success("✅ 企業を追加しました")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 追加に失敗しました: {str(e)}")
            else:
                st.error("企業名は必須です")


def show_matching():
    """人材マッチング機能"""
    st.header("🤝 人材マッチング")
    st.markdown("案件と人材の効率的なマッチングを行います")
    
    if supabase is None:
        st.error("データベース接続エラー")
        return
    
    # レイアウト設定
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 案件選択")
        
        # 案件データを取得
        try:
            projects_result = supabase.table('projects').select(
                'project_id, project_name, required_headcount, requirements, min_age, max_age'
            ).order('project_name').execute()
            
            project_options = {"選択してください": None}
            project_details = {}
            
            if projects_result.data:
                for p in projects_result.data:
                    project_options[p['project_name']] = p['project_id']
                    project_details[p['project_id']] = p
        except Exception as e:
            st.error(f"案件データ取得エラー: {str(e)}")
            return
        
        selected_project_name = st.selectbox(
            "案件を選択",
            options=list(project_options.keys()),
            key="matching_project_select"
        )
        selected_project_id = project_options[selected_project_name]
        
        # 選択された案件の詳細表示
        if selected_project_id:
            project = project_details[selected_project_id]
            st.info(f"""
            **📊 案件詳細**
            - 必要人数: {project.get('required_headcount', 'N/A')}名
            - 年齢要件: {project.get('min_age', 'N/A')}〜{project.get('max_age', 'N/A')}歳
            - 要件: {project.get('requirements', '未設定')[:100]}...
            """)
    
    with col2:
        st.subheader("👤 候補者検索・一覧")
        
        if selected_project_id:
            # 詳細フィルタオプション
            with st.expander("🔍 詳細フィルタ設定", expanded=True):
                # 基本条件
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    name_search = st.text_input("氏名検索", key="candidate_name_search", placeholder="氏名で検索...")
                    age_filter = st.slider("年齢範囲", 20, 65, (25, 50), key="age_filter")
                with col_f2:
                    company_filter = st.text_input("企業名", key="company_filter", placeholder="企業名で絞込...")
                    department_filter = st.text_input("部署名", key="department_filter", placeholder="部署名で絞込...")
                
                # 追加条件
                col_f3, col_f4 = st.columns(2)
                with col_f3:
                    position_filter = st.text_input("役職", key="position_filter", placeholder="役職で絞込...")
                with col_f4:
                    # 既に登録済みの候補者を除外するオプション
                    exclude_assigned = st.checkbox("この案件の登録済み候補者を除外", value=True, key="exclude_assigned")
            
            # ページネーション設定
            items_per_page = st.selectbox("表示件数", [10, 20, 50, 100], index=1, key="items_per_page")
            
            # 候補者データを取得
            try:
                contacts_query = supabase.table('contacts').select(
                    'contact_id, full_name, actual_age, estimated_age, department_name, position_name, target_companies!contacts_target_company_id_fkey(company_name)'
                )
                
                contacts_result = contacts_query.execute()
                
                if contacts_result.data:
                    # 既に登録済みの候補者IDを取得
                    assigned_contact_ids = set()
                    if exclude_assigned:
                        try:
                            assigned_result = supabase.table('project_assignments').select('contact_id').eq('project_id', selected_project_id).execute()
                            if assigned_result.data:
                                assigned_contact_ids = {item['contact_id'] for item in assigned_result.data}
                        except:
                            pass
                    
                    candidates = []
                    for c in contacts_result.data:
                        # 既に登録済みの候補者をスキップ
                        if exclude_assigned and c['contact_id'] in assigned_contact_ids:
                            continue
                        
                        # 年齢フィルタ
                        age = c.get('actual_age')
                        if not age:
                            estimated = c.get('estimated_age', '')
                            if estimated:
                                try:
                                    if '歳' in estimated:
                                        age = int(estimated.split('歳')[0])
                                    elif '代' in estimated:
                                        decade = int(estimated.split('代')[0])
                                        age = decade + 5
                                    else:
                                        age = int(estimated)
                                except (ValueError, IndexError):
                                    age = 30
                            else:
                                age = 30
                        
                        if not (age_filter[0] <= age <= age_filter[1]):
                            continue
                        
                        # 各フィルタ条件をチェック
                        company_name = c.get('target_companies', {}).get('company_name', '') if c.get('target_companies') else ''
                        department_name = c.get('department_name', '') or ''
                        position_name = c.get('position_name', '') or ''
                        full_name = c.get('full_name', '') or ''
                        
                        # フィルタ条件に合致しない場合はスキップ
                        if name_search and name_search.lower() not in full_name.lower():
                            continue
                        if company_filter and company_filter.lower() not in company_name.lower():
                            continue
                        if department_filter and department_filter.lower() not in department_name.lower():
                            continue
                        if position_filter and position_filter.lower() not in position_name.lower():
                            continue
                        
                        candidates.append({
                            'contact_id': c['contact_id'],
                            'name': full_name,
                            'age': age,
                            'company': company_name,
                            'department': department_name,
                            'position': position_name
                        })
                    
                    # ページネーション
                    total_candidates = len(candidates)
                    total_pages = (total_candidates + items_per_page - 1) // items_per_page
                    
                    st.write(f"**検索結果: {total_candidates}名**")
                    
                    if total_candidates > 0:
                        # ページ選択
                        if total_pages > 1:
                            col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
                            with col_page2:
                                current_page = st.number_input(
                                    f"ページ (1-{total_pages})",
                                    min_value=1,
                                    max_value=total_pages,
                                    value=1,
                                    key="current_page"
                                )
                        else:
                            current_page = 1
                        
                        # 現在のページの候補者を表示
                        start_idx = (current_page - 1) * items_per_page
                        end_idx = min(start_idx + items_per_page, total_candidates)
                        page_candidates = candidates[start_idx:end_idx]
                        
                        st.write(f"**{start_idx + 1} - {end_idx} 名を表示中 (全{total_candidates}名)**")
                        
                        # 候補者リスト表示
                        for i, candidate in enumerate(page_candidates):
                            with st.container():
                                ccol1, ccol2 = st.columns([3, 1])
                                with ccol1:
                                    st.write(f"**{candidate['name']}** ({candidate['company']})")
                                    details = []
                                    if candidate['age']:
                                        details.append(f"年齢: {candidate['age']}歳")
                                    if candidate['department']:
                                        details.append(f"部署: {candidate['department']}")
                                    if candidate['position']:
                                        details.append(f"役職: {candidate['position']}")
                                    if details:
                                        st.caption(" | ".join(details))
                                with ccol2:
                                    if st.button("➕ 追加", key=f"add_{candidate['contact_id']}_{current_page}", type="secondary"):
                                        add_candidate_to_project(selected_project_id, candidate['contact_id'], candidate['name'])
                                
                                if i < len(page_candidates) - 1:  # 最後の要素以外に区切り線を追加
                                    st.divider()
                        
                        # ページネーション情報
                        if total_pages > 1:
                            st.caption(f"ページ {current_page} / {total_pages} ({total_candidates} 件中 {start_idx + 1} - {end_idx} 件目)")
                    else:
                        st.info("フィルタ条件に合致する候補者が見つかりませんでした。条件を変更してください。")
                
            except Exception as e:
                st.error(f"候補者データ取得エラー: {str(e)}")
        else:
            st.info("先に案件を選択してください")
    
    # 紐付け済み候補者の表示
    if selected_project_id:
        st.markdown("---")
        show_project_assignments(selected_project_id, selected_project_name)


def add_candidate_to_project(project_id, contact_id, contact_name):
    """候補者を案件に追加"""
    try:
        # 既に紐付け済みかチェック
        existing = supabase.table('project_assignments').select('assignment_id').eq(
            'project_id', project_id
        ).eq('contact_id', contact_id).execute()
        
        if existing.data:
            st.warning(f"{contact_name}さんは既にこの案件に登録されています")
            return
        
        # 新規追加
        assignment_data = {
            'project_id': project_id,
            'contact_id': contact_id,
            'assignment_status': '候補者'
        }
        
        supabase.table('project_assignments').insert(assignment_data).execute()
        st.success(f"✅ {contact_name}さんを候補者として追加しました")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 追加に失敗しました: {str(e)}")


def show_project_assignments(project_id, project_name):
    """案件の候補者一覧表示"""
    st.subheader(f"📌 {project_name} の候補者")
    
    try:
        # 紐付け済み候補者を取得
        assignments_result = supabase.table('project_assignments').select(
            'assignment_id, assignment_status, created_at, contacts(contact_id, full_name, target_companies!contacts_target_company_id_fkey(company_name))'
        ).eq('project_id', project_id).execute()
        
        if assignments_result.data:
            # ステータス別にグループ化
            status_groups = {}
            for assignment in assignments_result.data:
                status = assignment.get('assignment_status', '候補者')
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(assignment)
            
            # ステータス別表示
            status_colors = {
                '候補者': '🟢',
                'スクリーニング中': '🟡',
                '面談中': '🟠',
                '内定': '🔵',
                '採用決定': '🟣',
                '見送り': '🔴',
                '辞退': '⚫'
            }
            
            for status, assignments in status_groups.items():
                color = status_colors.get(status, '🔘')
                st.write(f"**{color} {status} ({len(assignments)}名)**")
                
                for assignment in assignments:
                    contact = assignment.get('contacts', {})
                    company_name = contact.get('target_companies', {}).get('company_name', '不明') if contact.get('target_companies') else '不明'
                    
                    acol1, acol2, acol3 = st.columns([2, 1, 1])
                    with acol1:
                        st.write(f"• {contact.get('full_name', '不明')} ({company_name})")
                    with acol2:
                        new_status = st.selectbox(
                            "ステータス",
                            ['候補者', 'スクリーニング中', '面談中', '内定', '採用決定', '見送り', '辞退'],
                            index=['候補者', 'スクリーニング中', '面談中', '内定', '採用決定', '見送り', '辞退'].index(status),
                            key=f"status_{assignment['assignment_id']}"
                        )
                        if new_status != status:
                            update_assignment_status(assignment['assignment_id'], new_status)
                    with acol3:
                        if st.button("🗑️ 削除", key=f"delete_{assignment['assignment_id']}"):
                            delete_assignment(assignment['assignment_id'], contact.get('full_name', '不明'))
                
                st.divider()
        else:
            st.info("まだ候補者が登録されていません")
            
    except Exception as e:
        st.error(f"候補者データ取得エラー: {str(e)}")


def update_assignment_status(assignment_id, new_status):
    """アサインメントのステータスを更新"""
    try:
        supabase.table('project_assignments').update({
            'assignment_status': new_status
        }).eq('assignment_id', assignment_id).execute()
        st.success(f"✅ ステータスを「{new_status}」に更新しました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 更新に失敗しました: {str(e)}")


def delete_assignment(assignment_id, contact_name):
    """アサインメントを削除"""
    try:
        supabase.table('project_assignments').delete().eq('assignment_id', assignment_id).execute()
        st.success(f"✅ {contact_name}さんを削除しました")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 削除に失敗しました: {str(e)}")


def show_contact_project_assignments(contact_id):
    """コンタクトの紐付け案件を表示"""
    try:
        # 紐付け案件を取得
        assignments_result = supabase.table('project_assignments').select(
            'assignment_id, assignment_status, created_at, projects(project_id, project_name)'
        ).eq('contact_id', contact_id).execute()
        
        if assignments_result.data:
            st.markdown("---")
            st.markdown("#### 🎯 紐付け案件")
            
            # ステータス別にカウント
            status_count = {}
            for assignment in assignments_result.data:
                status = assignment.get('assignment_status', '候補者')
                status_count[status] = status_count.get(status, 0) + 1
            
            # サマリー表示
            status_colors = {
                '候補者': '🟢',
                'スクリーニング中': '🟡',
                '面談中': '🟠',
                '内定': '🔵',
                '採用決定': '🟣',
                '見送り': '🔴',
                '辞退': '⚫'
            }
            
            col_summary = st.columns(len(status_count))
            for i, (status, count) in enumerate(status_count.items()):
                if i < len(col_summary):
                    color = status_colors.get(status, '🔘')
                    col_summary[i].metric(f"{color} {status}", f"{count}件")
            
            # 案件一覧
            st.write("**案件一覧:**")
            for assignment in assignments_result.data:
                project = assignment.get('projects', {})
                status = assignment.get('assignment_status', '候補者')
                created_at = assignment.get('created_at', '')[:10]  # 日付部分のみ
                color = status_colors.get(status, '🔘')
                
                acol1, acol2, acol3 = st.columns([2, 1, 1])
                with acol1:
                    st.write(f"{color} **{project.get('project_name', '不明')}**")
                with acol2:
                    st.write(f"ステータス: {status}")
                with acol3:
                    st.write(f"登録日: {created_at}")
            
            # 新しい案件を追加するボタン
            if st.button("➕ 新しい案件に追加", key=f"add_project_to_contact_{contact_id}"):
                st.info("人材マッチング画面から案件を選択して追加してください")
                st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
        else:
            st.markdown("---")
            st.markdown("#### 🎯 紐付け案件")
            st.info("まだ案件に紐付けられていません")
            if st.button("➕ 案件に追加", key=f"add_project_to_contact_{contact_id}"):
                st.info("人材マッチング画面から案件を選択して追加してください")
                st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
                
    except Exception as e:
        st.error(f"紐付け案件データ取得エラー: {str(e)}")


def show_project_candidates_summary(project_id, use_sample_data=False):
    """案件の候補者サマリーを表示"""
    try:
        # サンプルデータモードかデータベース接続がない場合
        if use_sample_data or supabase is None:
            # サンプルデータから候補者を取得
            assignments_df = generate_sample_project_assignments()
            
            # 特定のproject_idに対する候補者をフィルタ
            project_assignments = assignments_df[assignments_df['project_id'] == project_id]
            
            if not project_assignments.empty:
                st.markdown("---")
                st.markdown("#### 👤 候補者サマリー")
                st.info("🎯 サンプルデータの候補者を表示中")
                
                # ステータス別にカウント
                status_mapping = {
                    'ASSIGNED': '割当済',
                    'CANDIDATE': '候補者',
                    'INTERVIEW': '面談中',
                    'COMPLETED': '完了',
                    'REJECTED': '見送り'
                }
                
                status_count = {}
                for _, assignment in project_assignments.iterrows():
                    original_status = assignment.get('assignment_status', 'CANDIDATE')
                    status = status_mapping.get(original_status, original_status)
                    status_count[status] = status_count.get(status, 0) + 1
                
                # サマリー表示
                status_colors = {
                    '候補者': '🟢',
                    '割当済': '🔵',
                    '面談中': '🟠',
                    '完了': '🟣',
                    '見送り': '🔴'
                }
                
                total_candidates = len(project_assignments)
                st.metric("総候補者数", f"{total_candidates}名")
                
                if len(status_count) > 1:
                    col_summary = st.columns(min(len(status_count), 4))
                    for i, (status, count) in enumerate(status_count.items()):
                        if i < len(col_summary):
                            color = status_colors.get(status, '🔘')
                            col_summary[i].metric(f"{color} {status}", f"{count}名")
                
                # 最新の候補者を表示（最大5名）
                st.write("**最新候補者 (最大5名):**")
                recent_assignments = project_assignments.sort_values('created_at', ascending=False).head(5)
                
                for idx, assignment in recent_assignments.iterrows():
                    contact_id = assignment.get('contact_id')
                    original_status = assignment.get('assignment_status', 'CANDIDATE')
                    status = status_mapping.get(original_status, original_status)
                    created_at = str(assignment.get('created_at', ''))[:10]
                    color = status_colors.get(status, '🔘')
                    company_name = assignment.get('contact_company', '不明')
                    contact_name = assignment.get('contact_name', '不明')
                    
                    ccol1, ccol2, ccol3, ccol4 = st.columns([2, 1, 1, 1])
                    with ccol1:
                        st.write(f"{color} **{contact_name}** ({company_name})")
                    with ccol2:
                        st.write(f"{status}")
                    with ccol3:
                        st.write(f"{created_at}")
                    with ccol4:
                        if st.button("👤 詳細", key=f"view_candidate_detail_{contact_id}_{project_id}", help="コンタクト管理で詳細確認・編集"):
                            
                            # セッション状態でナビゲーション履歴と選択状態を管理
                            st.session_state.navigation_history = {
                                'from_page': 'projects',
                                'from_url': '?page=projects',
                                'current_contact_id': contact_id,
                                'selected_project_id': project_id,  # 選択されていた案件ID
                                'expanded_project': project_id  # 展開されていた案件
                            }
                            
                            # 現在のselectboxの選択状態を保存
                            if hasattr(st.session_state, 'project_selector') and st.session_state.project_selector is not None:
                                st.session_state.navigation_history['selectbox_selection'] = st.session_state.project_selector
                            
                            # 現在のフィルタ条件も保存
                            if 'project_filter_status' in st.session_state:
                                st.session_state.navigation_history['filter_status'] = st.session_state.project_filter_status
                            if 'project_filter_company' in st.session_state:
                                st.session_state.navigation_history['filter_company'] = st.session_state.project_filter_company
                            
                            # コンタクト管理画面に遷移
                            st.query_params.update({
                                'page': 'contacts',
                                'contact_id': str(contact_id),
                                'from_projects': 'true'
                            })
                            st.rerun()
                
                # 詳細リンク
                if st.button("📊 候補者詳細を見る", key=f"view_candidates_{project_id}"):
                    st.info("人材マッチング画面で詳細な候補者管理ができます")
                    st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
            else:
                st.markdown("---")
                st.markdown("#### 👤 候補者サマリー")
                st.info("この案件にはまだ候補者が登録されていません")
                if st.button("➕ 候補者を追加", key=f"add_candidates_{project_id}"):
                    st.info("人材マッチング画面から候補者を追加してください")
                    st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
        else:
            # 通常のデータベースモード
            assignments_result = supabase.table('project_assignments').select(
                'assignment_id, assignment_status, created_at, contacts(contact_id, full_name, target_companies!contacts_target_company_id_fkey(company_name))'
            ).eq('project_id', project_id).execute()
            
            if assignments_result.data:
                st.markdown("---")
                st.markdown("#### 👤 候補者サマリー")
                
                # ステータス別にカウント
                status_count = {}
                for assignment in assignments_result.data:
                    status = assignment.get('assignment_status', '候補者')
                    status_count[status] = status_count.get(status, 0) + 1
                
                # サマリー表示
                status_colors = {
                    '候補者': '🟢',
                    'スクリーニング中': '🟡',
                    '面談中': '🟠',
                    '内定': '🔵',
                    '採用決定': '🟣',
                    '見送り': '🔴',
                    '辞退': '⚫'
                }
                
                total_candidates = len(assignments_result.data)
                st.metric("総候補者数", f"{total_candidates}名")
                
                if len(status_count) > 1:
                    col_summary = st.columns(min(len(status_count), 4))
                    for i, (status, count) in enumerate(status_count.items()):
                        if i < len(col_summary):
                            color = status_colors.get(status, '🔘')
                            col_summary[i].metric(f"{color} {status}", f"{count}名")
                
                # 最新の候補者を表示
                st.write("**最新候補者 (最大5名):**")
                recent_assignments = sorted(assignments_result.data, 
                                         key=lambda x: x.get('created_at', ''), reverse=True)[:5]
                
                for assignment in recent_assignments:
                    contact = assignment.get('contacts', {})
                    contact_id = contact.get('contact_id')
                    status = assignment.get('assignment_status', '候補者')
                    created_at = assignment.get('created_at', '')[:10]
                    color = status_colors.get(status, '🔘')
                    company_name = contact.get('target_companies', {}).get('company_name', '不明') if contact.get('target_companies') else '不明'
                    contact_name = contact.get('full_name', '不明')
                    
                    ccol1, ccol2, ccol3, ccol4 = st.columns([2, 1, 1, 1])
                    with ccol1:
                        st.write(f"{color} **{contact_name}** ({company_name})")
                    with ccol2:
                        st.write(f"{status}")
                    with ccol3:
                        st.write(f"{created_at}")
                    with ccol4:
                        if contact_id and st.button("👤 詳細", key=f"view_candidate_detail_{contact_id}_{project_id}", help="コンタクト管理で詳細確認・編集"):
                            # セッション状態でナビゲーション履歴と選択状態を管理
                            st.session_state.navigation_history = {
                                'from_page': 'projects',
                                'from_url': '?page=projects',
                                'current_contact_id': contact_id,
                                'selected_project_id': project_id,  # 選択されていた案件ID
                                'expanded_project': project_id  # 展開されていた案件
                            }
                            # 現在のselectboxの選択状態を保存
                            if hasattr(st.session_state, 'project_selector') and st.session_state.project_selector is not None:
                                st.session_state.navigation_history['selectbox_selection'] = st.session_state.project_selector
                            
                            # 現在のフィルタ条件も保存
                            if 'project_filter_status' in st.session_state:
                                st.session_state.navigation_history['filter_status'] = st.session_state.project_filter_status
                            if 'project_filter_company' in st.session_state:
                                st.session_state.navigation_history['filter_company'] = st.session_state.project_filter_company
                            
                            # コンタクト管理画面に遷移
                            st.query_params.update({
                                'page': 'contacts',
                                'contact_id': str(contact_id),
                                'from_projects': 'true'
                            })
                            st.rerun()
                
                # 詳細リンク
                if st.button("📊 候補者詳細を見る", key=f"view_candidates_{project_id}"):
                    st.info("人材マッチング画面で詳細な候補者管理ができます")
                    st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
            else:
                st.markdown("---")
                st.markdown("#### 👤 候補者サマリー")
                st.info("まだ候補者が登録されていません")
                if st.button("➕ 候補者を追加", key=f"add_candidates_{project_id}"):
                    st.info("人材マッチング画面から候補者を追加してください")
                    st.markdown("[🤝 人材マッチング画面を開く](?page=matching)")
                
    except Exception as e:
        st.error(f"候補者データ取得エラー: {str(e)}")




def show_contact_project_assignments_summary(contact_id):
    """候補者の紐付け案件サマリー（簡略版）"""
    try:
        assignments_result = supabase.table('project_assignments').select(
            'assignment_status, created_at, projects(project_name)'
        ).eq('contact_id', contact_id).execute()
        
        if assignments_result.data:
            st.markdown("#### 🎯 紐付け案件（一覧）")
            
            for assignment in assignments_result.data:
                project = assignment.get('projects', {})
                status = assignment.get('assignment_status', '候補者')
                created_at = assignment.get('created_at', '')[:10]
                
                status_colors = {
                    '候補者': '🟢', 'スクリーニング中': '🟡', '面談中': '🟠',
                    '内定': '🔵', '採用決定': '🟣', '見送り': '🔴', '辞退': '⚫'
                }
                color = status_colors.get(status, '🔘')
                
                st.write(f"{color} **{project.get('project_name', '不明')}** ({status}) - {created_at}")
        
    except Exception as e:
        st.warning(f"紐付け案件取得エラー: {str(e)}")


if __name__ == "__main__":
    main()
