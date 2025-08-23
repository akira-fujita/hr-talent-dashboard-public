#!/usr/bin/env python3
"""
CSV データインポートスクリプト
企業テーブルと案件テーブルのCSVファイルをデータベースにインポートする
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from supabase import create_client, Client
import sys
import os

def init_supabase():
    """Supabaseクライアントを初期化"""
    try:
        # Streamlitの秘密情報ファイルから読み取り
        secrets_file = ".streamlit/secrets.toml"
        if os.path.exists(secrets_file):
            import toml
            secrets = toml.load(secrets_file)
            url = secrets["SUPABASE_URL"]
            key = secrets["SUPABASE_ANON_KEY"]
        else:
            # 環境変数から取得
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_ANON_KEY")
            
        if not url or not key:
            raise ValueError("Supabase credentials not found")
            
        return create_client(url, key)
    except Exception as e:
        print(f"Supabase接続エラー: {str(e)}")
        return None


def import_companies(supabase, csv_file):
    """企業CSVファイルをインポート"""
    print(f"企業データをインポート中: {csv_file}")
    
    try:
        # CSVファイル読み込み（UTF-8 BOMに対応）
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"読み込み完了: {len(df)}行")
        print("カラム:", list(df.columns))
        
        success_count = 0
        
        for index, row in df.iterrows():
            company_name = str(row['企業名']).strip()
            
            # 空の行をスキップ
            if not company_name or company_name.lower() in ['nan', '', 'null']:
                continue
                
            print(f"インポート中: {company_name}")
            
            # 企業データ作成
            company_data = {
                'company_name': company_name,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 業種情報があれば追加
            if '業種' in df.columns:
                industry = str(row['業種']).strip()
                if industry and industry.lower() not in ['nan', '', 'null']:
                    # 業種マッピング
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
            
            # データベースに挿入
            response = supabase.table('target_companies').insert(company_data).execute()
            
            if response.data:
                target_company_id = response.data[0]['target_company_id']
                success_count += 1
                
                # ターゲット部署があれば部署テーブルに追加
                if 'TG部署' in df.columns:
                    target_dept = str(row['TG部署']).strip()
                    if target_dept and target_dept.lower() not in ['nan', '', 'null']:
                        dept_data = {
                            'target_company_id': target_company_id,
                            'department_name': target_dept,
                            'is_target_department': True,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        supabase.table('departments').insert(dept_data).execute()
                        print(f"  部署も追加: {target_dept}")
        
        print(f"✅ 企業データインポート完了: {success_count}件")
        return success_count
        
    except Exception as e:
        print(f"❌ 企業データインポートエラー: {str(e)}")
        return 0


def import_projects(supabase, csv_file):
    """案件CSVファイルをインポート"""
    print(f"案件データをインポート中: {csv_file}")
    
    try:
        # CSVファイル読み込み（UTF-8 BOMに対応）
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        print(f"読み込み完了: {len(df)}行")
        print("カラム:", list(df.columns))
        
        success_count = 0
        
        for index, row in df.iterrows():
            company_name = str(row['企業名']).strip()
            project_name = str(row['案件名']).strip()
            
            # 空の行をスキップ
            if not company_name or not project_name or \
               company_name.lower() in ['nan', '', 'null'] or \
               project_name.lower() in ['nan', '', 'null']:
                continue
            
            print(f"インポート中: {company_name} - {project_name}")
            
            # 企業IDを取得
            company_response = supabase.table('target_companies').select('target_company_id').eq('company_name', company_name).execute()
            
            if not company_response.data:
                print(f"⚠️ 企業「{company_name}」が見つかりません")
                continue
            
            target_company_id = company_response.data[0]['target_company_id']
            
            # 案件データ作成
            project_data = {
                'target_company_id': target_company_id,
                'project_name': project_name,
                'status': str(row['ステータス']).strip() if 'ステータス' in df.columns else 'OPEN',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # オプションフィールドを追加
            if '契約開始日' in df.columns:
                start_date = str(row['契約開始日']).strip()
                if start_date and start_date.lower() not in ['nan', '', 'null']:
                    try:
                        if '/' in start_date:
                            date_obj = datetime.strptime(start_date, '%Y/%m/%d').date()
                        else:
                            date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                        project_data['contract_start_date'] = date_obj.isoformat()
                    except:
                        pass
            
            if '契約終了日' in df.columns:
                end_date = str(row['契約終了日']).strip()
                if end_date and end_date.lower() not in ['nan', '', 'null']:
                    try:
                        if '/' in end_date:
                            date_obj = datetime.strptime(end_date, '%Y/%m/%d').date()
                        else:
                            date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                        project_data['contract_end_date'] = date_obj.isoformat()
                    except:
                        pass
            
            if '契約人数' in df.columns:
                headcount = str(row['契約人数']).strip()
                if headcount and headcount.lower() not in ['nan', '', 'null']:
                    try:
                        project_data['required_headcount'] = int(float(headcount))
                    except:
                        pass
            
            if '担当CO' in df.columns:
                co_manager = str(row['担当CO']).strip()
                if co_manager and co_manager.lower() not in ['nan', '', 'null']:
                    project_data['co_manager'] = co_manager
            
            if '担当RE' in df.columns:
                re_manager = str(row['担当RE']).strip()
                if re_manager and re_manager.lower() not in ['nan', '', 'null']:
                    project_data['re_manager'] = re_manager
            
            # データベースに挿入
            response = supabase.table('projects').insert(project_data).execute()
            
            if response.data:
                success_count += 1
        
        print(f"✅ 案件データインポート完了: {success_count}件")
        return success_count
        
    except Exception as e:
        print(f"❌ 案件データインポートエラー: {str(e)}")
        return 0


def main():
    """メイン実行関数"""
    print("🚀 CSV データインポートを開始します")
    
    # Supabase接続
    supabase = init_supabase()
    if not supabase:
        print("❌ データベース接続に失敗しました")
        sys.exit(1)
    
    # CSVファイルのパス
    company_csv = "企業テーブル.csv"
    project_csv = "案件テーブル.csv"
    
    # ファイル存在確認
    if not os.path.exists(company_csv):
        print(f"❌ 企業CSVファイルが見つかりません: {company_csv}")
        sys.exit(1)
    
    if not os.path.exists(project_csv):
        print(f"❌ 案件CSVファイルが見つかりません: {project_csv}")
        sys.exit(1)
    
    # インポート実行
    company_count = import_companies(supabase, company_csv)
    project_count = import_projects(supabase, project_csv)
    
    print(f"🎉 インポート完了!")
    print(f"  - 企業: {company_count}件")
    print(f"  - 案件: {project_count}件")


if __name__ == "__main__":
    main()