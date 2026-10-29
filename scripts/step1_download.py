# -*- coding: utf-8 -*-
"""
Step 1: 下载 UCI Online Retail 真实电商数据
==========================================
数据集描述: 英国某在线零售商 2010.12 - 2011.12 全年交易数据
- 541,909 行订单记录
- 8 列: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
- CSV 大小约 46MB

运行: py scripts/step1_download.py
"""

import os
import sys
import time
import urllib.request
import urllib.error
import zipfile
import io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
CSV_PATH = os.path.join(DATA_DIR, "online_retail.csv")

# 多个下载源，失败时依次尝试
SOURCES = [
    # 源 1: UCI 官方
    ("UCI 官方", "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"),
    # 源 2: UCI 镜像 (CSV)
    ("Kaggle 镜像", "https://raw.githubusercontent.com/gulertan/Consumer-Analytics-with-R/main/online_retail_sample.csv"),
    # 源 3: 小样本 CSV 直接放
    ("备用源", "https://raw.githubusercontent.com/LBoodram26/Data607-Week1/main/Online%20Retail.xlsx"),
]

def download(url, dest):
    """带进度条下载"""
    def reporthook(blocknum, blocksize, totalsize):
        if totalsize > 0:
            pct = blocknum * blocksize * 100 // totalsize
            mb = blocknum * blocksize / 1024 / 1024
            total_mb = totalsize / 1024 / 1024
            sys.stdout.write(f"\r  进度: {pct}% ({mb:.1f}/{total_mb:.1f} MB)")
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\r  进度: {blocknum * blocksize / 1024 / 1024:.1f} MB")
            sys.stdout.flush()

    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)

print("=" * 60)
print("  Step 1: 下载 Online Retail 真实电商数据")
print("=" * 60)

# 如果已经有 CSV 就跳过
if os.path.exists(CSV_PATH):
    size_mb = os.path.getsize(CSV_PATH) / 1024 / 1024
    print(f"\n✓ 数据已存在: {CSV_PATH} ({size_mb:.1f} MB)")
else:
    # 先尝试下载 xlsx 再转 csv
    xlsx_path = os.path.join(DATA_DIR, "online_retail.xlsx")
    csv_ready = False

    for name, url in SOURCES:
        print(f"\n尝试下载 [{name}]...")
        try:
            print(f"  URL: {url[:60]}...")
            size = download(url, xlsx_path if ".xlsx" in url.lower() else CSV_PATH)
            print(f"\n  ✓ 下载成功! {size/1024/1024:.1f} MB")
            csv_ready = True
            break
        except Exception as e:
            print(f"\n  ✗ 失败: {e}")
            if os.path.exists(xlsx_path):
                os.remove(xlsx_path)
            if os.path.exists(CSV_PATH):
                os.remove(CSV_PATH)
            continue

    # 如果下载到了 xlsx，转成 csv
    if os.path.exists(xlsx_path) and not os.path.exists(CSV_PATH):
        print("\n转换 XLSX → CSV...")
        try:
            import pandas as pd
            df = pd.read_excel(xlsx_path)
            df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
            os.remove(xlsx_path)
            print(f"✓ 转换完成: {CSV_PATH} ({os.path.getsize(CSV_PATH)/1024/1024:.1f} MB)")
            csv_ready = True
        except ImportError:
            print("需要安装 openpyxl: py -m pip install openpyxl")
            sys.exit(1)

    if not csv_ready:
        print("\n" + "=" * 60)
        print("  自动下载失败！请手动下载：")
        print("=" * 60)
        print("""
方法 1 (推荐，54万行完整数据):
  1. 打开: https://archive.ics.uci.edu/ml/datasets/online+retail
  2. 点击 "Data Folder" → 下载 Online Retail.xlsx
  3. 把文件放到: C:\\Users\\Liiizc\\Documents\\Trae-CN\\temp_20261029_01\\online_retail_project\\data\\
  4. 然后运行: py scripts/step1b_manual_convert.py

方法 2 (Kaggle):
  1. 打开: https://www.kaggle.com/datasets/matthuan/online-retail
  2. 点击 Download
  3. 解压，把 online_retail.csv 放到 data/ 目录

方法 3 (极小样本，只有几千行，用于先跑通流程):
  直接在 data/ 目录手动创建一个 online_retail.csv，用 Excel 随便造 20 行数据，
  列名: InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country
""")
        sys.exit(0)

# ========= 快速验证 =========
print("\n" + "=" * 60)
print("  数据概览")
print("=" * 60)
try:
    import pandas as pd
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"\n  行数: {len(df):,}")
    print(f"  列数: {len(df.columns)}")
    print(f"  列名: {', '.join(df.columns)}")
    print(f"\n  前 5 行:")
    print(df.head().to_string())
    print(f"\n  数据类型:")
    print(df.dtypes)
except Exception as e:
    print(f"  读取失败: {e}")
    print("  如果是 CSV 编码问题，试试: df = pd.read_csv(CSV_PATH, encoding='gbk')")

print("\n✓ Step 1 完成！")
