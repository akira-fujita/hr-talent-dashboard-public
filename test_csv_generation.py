#!/usr/bin/env python3
"""
CSVサンプル生成機能テスト
実装したサンプルCSV生成機能をテストする
"""

import sys
import os

# アプリケーションのディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# アプリケーションからサンプル生成関数をインポート
try:
    from app import generate_company_sample_csv, generate_project_sample_csv, generate_contact_sample_csv
    print("✅ サンプル生成関数のインポートに成功しました")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def test_csv_generation():
    """CSV生成機能をテスト"""
    print("\n🧪 CSVサンプル生成機能テスト")
    print("=" * 50)
    
    # 企業データサンプル生成
    print("\n🏢 企業データサンプル生成...")
    try:
        company_csv = generate_company_sample_csv()
        print(f"✅ 企業データCSV生成成功 ({len(company_csv)}文字)")
        
        # ファイルに保存
        with open("test_company_sample.csv", "w", encoding="utf-8") as f:
            f.write(company_csv)
        print("   💾 test_company_sample.csv に保存しました")
        
        # プレビュー表示
        lines = company_csv.split('\n')[:4]  # 最初の4行を表示
        print("   📋 プレビュー:")
        for i, line in enumerate(lines, 1):
            print(f"     {i}: {line}")
            
    except Exception as e:
        print(f"❌ 企業データサンプル生成エラー: {e}")
    
    # 案件データサンプル生成
    print("\n🎯 案件データサンプル生成...")
    try:
        project_csv = generate_project_sample_csv()
        print(f"✅ 案件データCSV生成成功 ({len(project_csv)}文字)")
        
        # ファイルに保存
        with open("test_project_sample.csv", "w", encoding="utf-8") as f:
            f.write(project_csv)
        print("   💾 test_project_sample.csv に保存しました")
        
        # プレビュー表示
        lines = project_csv.split('\n')[:4]  # 最初の4行を表示
        print("   📋 プレビュー:")
        for i, line in enumerate(lines, 1):
            print(f"     {i}: {line}")
            
    except Exception as e:
        print(f"❌ 案件データサンプル生成エラー: {e}")
    
    # コンタクトデータサンプル生成
    print("\n👥 コンタクトデータサンプル生成...")
    try:
        contact_csv = generate_contact_sample_csv()
        print(f"✅ コンタクトデータCSV生成成功 ({len(contact_csv)}文字)")
        
        # ファイルに保存
        with open("test_contact_sample.csv", "w", encoding="utf-8") as f:
            f.write(contact_csv)
        print("   💾 test_contact_sample.csv に保存しました")
        
        # プレビュー表示
        lines = contact_csv.split('\n')[:4]  # 最初の4行を表示
        print("   📋 プレビュー:")
        for i, line in enumerate(lines, 1):
            print(f"     {i}: {line}")
            
    except Exception as e:
        print(f"❌ コンタクトデータサンプル生成エラー: {e}")
    
    print(f"\n🎉 テスト完了!")
    print(f"生成されたファイル:")
    print(f"  - test_company_sample.csv")
    print(f"  - test_project_sample.csv")  
    print(f"  - test_contact_sample.csv")

if __name__ == "__main__":
    test_csv_generation()