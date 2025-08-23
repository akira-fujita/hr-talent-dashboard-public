#!/usr/bin/env python3
"""
CSV データ分析スクリプト
企業テーブルと案件テーブルのCSVファイルを分析してインポート準備を行う
"""

import pandas as pd
import os
from datetime import datetime

def analyze_company_csv(csv_file):
    """企業CSVファイルを分析"""
    print(f"\n📊 企業データ分析: {csv_file}")
    print("=" * 50)
    
    try:
        # CSVファイル読み込み（UTF-8 BOMに対応）
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        print(f"📈 データ概要:")
        print(f"  - 総行数: {len(df)}行")
        print(f"  - 総列数: {len(df.columns)}列")
        
        print(f"\n📋 カラム一覧:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n🏢 企業データ詳細:")
        
        # 企業名カラムの分析
        if '企業名' in df.columns:
            company_data = df['企業名'].dropna()
            valid_companies = company_data[company_data.str.strip() != '']
            print(f"  - 有効な企業名: {len(valid_companies)}件")
            print(f"  - 空の企業名: {len(df) - len(valid_companies)}件")
            
            if len(valid_companies) > 0:
                print(f"  - サンプル企業名:")
                for i, company in enumerate(valid_companies.head(5), 1):
                    print(f"    {i}. {company}")
        
        # 業種データの分析
        if '業種' in df.columns:
            industry_data = df['業種'].dropna()
            valid_industries = industry_data[industry_data.str.strip() != '']
            print(f"\n🏭 業種データ:")
            print(f"  - 有効な業種: {len(valid_industries)}件")
            if len(valid_industries) > 0:
                industry_counts = valid_industries.value_counts()
                print(f"  - 業種分布:")
                for industry, count in industry_counts.head(10).items():
                    print(f"    {industry}: {count}件")
        
        # ターゲット部署データの分析
        if 'TG部署' in df.columns:
            dept_data = df['TG部署'].dropna()
            valid_depts = dept_data[dept_data.str.strip() != '']
            print(f"\n🎯 ターゲット部署データ:")
            print(f"  - 有効な部署: {len(valid_depts)}件")
            if len(valid_depts) > 0:
                dept_counts = valid_depts.value_counts()
                print(f"  - 部署分布:")
                for dept, count in dept_counts.head(10).items():
                    print(f"    {dept}: {count}件")
        
        return df
        
    except Exception as e:
        print(f"❌ 企業データ分析エラー: {str(e)}")
        return None


def analyze_project_csv(csv_file):
    """案件CSVファイルを分析"""
    print(f"\n📊 案件データ分析: {csv_file}")
    print("=" * 50)
    
    try:
        # CSVファイル読み込み（UTF-8 BOMに対応）
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        print(f"📈 データ概要:")
        print(f"  - 総行数: {len(df)}行")
        print(f"  - 総列数: {len(df.columns)}列")
        
        print(f"\n📋 カラム一覧:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n🎯 案件データ詳細:")
        
        # 企業名・案件名の分析
        if '企業名' in df.columns and '案件名' in df.columns:
            company_data = df['企業名'].dropna()
            project_data = df['案件名'].dropna()
            valid_companies = company_data[company_data.str.strip() != '']
            valid_projects = project_data[project_data.str.strip() != '']
            
            print(f"  - 有効な企業名: {len(valid_companies)}件")
            print(f"  - 有効な案件名: {len(valid_projects)}件")
            
            if len(valid_projects) > 0:
                print(f"  - サンプル案件:")
                for i, (company, project) in enumerate(zip(valid_companies.head(3), valid_projects.head(3)), 1):
                    print(f"    {i}. {company} - {project}")
        
        # ステータス分析
        if 'ステータス' in df.columns:
            status_data = df['ステータス'].dropna()
            valid_status = status_data[status_data.str.strip() != '']
            print(f"\n📊 ステータス分布:")
            if len(valid_status) > 0:
                status_counts = valid_status.value_counts()
                for status, count in status_counts.items():
                    print(f"    {status}: {count}件")
        
        # 契約日分析
        if '契約開始日' in df.columns:
            start_date_data = df['契約開始日'].dropna()
            valid_start_dates = start_date_data[start_date_data.str.strip() != '']
            print(f"\n📅 契約開始日:")
            print(f"  - 有効な開始日: {len(valid_start_dates)}件")
            if len(valid_start_dates) > 0:
                print(f"  - サンプル開始日: {valid_start_dates.iloc[0]}")
        
        if '契約終了日' in df.columns:
            end_date_data = df['契約終了日'].dropna()
            valid_end_dates = end_date_data[end_date_data.str.strip() != '']
            print(f"  - 有効な終了日: {len(valid_end_dates)}件")
            if len(valid_end_dates) > 0:
                print(f"  - サンプル終了日: {valid_end_dates.iloc[0]}")
        
        # 契約人数分析
        if '契約人数' in df.columns:
            headcount_data = df['契約人数'].dropna()
            valid_headcount = headcount_data[headcount_data.astype(str).str.strip() != '']
            print(f"\n👥 契約人数:")
            print(f"  - 有効な人数データ: {len(valid_headcount)}件")
            if len(valid_headcount) > 0:
                try:
                    headcount_numeric = pd.to_numeric(valid_headcount, errors='coerce').dropna()
                    print(f"  - 平均人数: {headcount_numeric.mean():.1f}人")
                    print(f"  - 最大人数: {headcount_numeric.max()}人")
                    print(f"  - 最小人数: {headcount_numeric.min()}人")
                except:
                    print(f"  - 人数データの変換に失敗")
        
        # 担当者分析
        if '担当CO' in df.columns:
            co_data = df['担当CO'].dropna()
            valid_co = co_data[co_data.str.strip() != '']
            print(f"\n👨‍💼 担当者情報:")
            print(f"  - 担当CO: {len(valid_co)}件")
            if len(valid_co) > 0:
                co_counts = valid_co.value_counts()
                print(f"    担当CO一覧:")
                for co, count in co_counts.head(5).items():
                    print(f"      {co}: {count}案件")
        
        if '担当RE' in df.columns:
            re_data = df['担当RE'].dropna()
            valid_re = re_data[re_data.str.strip() != '']
            print(f"  - 担当RE: {len(valid_re)}件")
            if len(valid_re) > 0:
                re_counts = valid_re.value_counts()
                print(f"    担当RE一覧:")
                for re, count in re_counts.head(5).items():
                    print(f"      {re}: {count}案件")
        
        return df
        
    except Exception as e:
        print(f"❌ 案件データ分析エラー: {str(e)}")
        return None


def generate_import_summary(company_df, project_df):
    """インポート概要を生成"""
    print(f"\n🚀 インポート準備完了")
    print("=" * 50)
    
    # 企業データ概要
    if company_df is not None:
        valid_companies = 0
        if '企業名' in company_df.columns:
            company_data = company_df['企業名'].dropna()
            valid_companies = len(company_data[company_data.str.strip() != ''])
        
        print(f"✅ 企業データ:")
        print(f"  - インポート可能企業数: {valid_companies}件")
        
        if 'TG部署' in company_df.columns:
            dept_data = company_df['TG部署'].dropna()
            valid_depts = len(dept_data[dept_data.str.strip() != ''])
            print(f"  - インポート可能部署数: {valid_depts}件")
    
    # 案件データ概要
    if project_df is not None:
        valid_projects = 0
        if '案件名' in project_df.columns:
            project_data = project_df['案件名'].dropna()
            valid_projects = len(project_data[project_data.str.strip() != ''])
        
        print(f"✅ 案件データ:")
        print(f"  - インポート可能案件数: {valid_projects}件")
    
    print(f"\n💡 次のステップ:")
    print(f"  1. データベース接続設定を確認")
    print(f"  2. import_sample_data.py を実行してインポート")
    print(f"  3. Streamlitアプリでデータ確認")


def main():
    """メイン実行関数"""
    print("🔍 CSV データ分析を開始します")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # CSVファイルのパス
    company_csv = "企業テーブル.csv"
    project_csv = "案件テーブル.csv"
    
    # ファイル存在確認
    if not os.path.exists(company_csv):
        print(f"❌ 企業CSVファイルが見つかりません: {company_csv}")
        return
    
    if not os.path.exists(project_csv):
        print(f"❌ 案件CSVファイルが見つかりません: {project_csv}")
        return
    
    # 分析実行
    company_df = analyze_company_csv(company_csv)
    project_df = analyze_project_csv(project_csv)
    
    # インポート概要生成
    generate_import_summary(company_df, project_df)


if __name__ == "__main__":
    main()