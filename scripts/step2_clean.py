# -*- coding: utf-8 -*-
"""
Step 2: 数据清洗
===============
对 Online Retail 原始数据进行清洗：
  1. 去掉空格/NA
  2. 去掉 Quantity <= 0 和 UnitPrice <= 0 的记录（退货/免费订单）
  3. 去掉 CustomerID 为空的记录（匿名交易）
  4. 去掉 InvoiceNo 以 'C' 开头的记录（英国零售 C 开头表示取消）
  5. 计算 Total = Quantity * UnitPrice
  6. 转换日期格式

运行: py scripts/step2_clean.py
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
RAW = os.path.join(DATA_DIR, "online_retail.csv")
CLEAN = os.path.join(DATA_DIR, "online_retail_clean.csv")

print("=" * 60)
print("  Step 2: 数据清洗")
print("=" * 60)

# ========= 1. 读原始数据 =========
print("\n[1/6] 读取原始 CSV...")
df = pd.read_csv(RAW, low_memory=False, encoding="utf-8-sig")
print(f"  原始行数: {len(df):,}")
print(f"  列名: {list(df.columns)}")

# 统一列名（原始数据列名可能有空格）
df.columns = [c.strip() for c in df.columns]
print(f"  清洗后列名: {list(df.columns)}")

# ========= 2. 基本去空 =========
print("\n[2/6] 去掉缺失值...")
before = len(df)
df = df.dropna(subset=["InvoiceNo", "StockCode", "Quantity", "UnitPrice", "CustomerID"])
# Description 可以为空
print(f"  去掉缺失值: {before - len(df):,} 行, 剩余 {len(df):,}")

# CustomerID 转 int
df["CustomerID"] = df["CustomerID"].astype(int)

# ========= 3. 去掉 Quantity / UnitPrice 无效值 =========
print("\n[3/6] 去掉无效订单（Quantity<=0 或 UnitPrice<=0）...")
before = len(df)
df = df[(df.Quantity > 0) & (df.UnitPrice > 0)]
print(f"  去掉无效订单: {before - len(df):,} 行, 剩余 {len(df):,}")

# ========= 4. 去掉取消订单（InvoiceNo 以 C 开头）=========
print("\n[4/6] 去掉取消订单（InvoiceNo 以 C 开头）...")
before = len(df)
df = df[~df.InvoiceNo.astype(str).str.upper().str.startswith("C")]
print(f"  去掉取消订单: {before - len(df):,} 行, 剩余 {len(df):,}")

# ========= 5. 日期转换 + 计算 Total =========
print("\n[5/6] 日期转换 + 计算订单金额...")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["InvoiceDate"].dt.to_period("M")
df["Date"] = df["InvoiceDate"].dt.date
print(f"  日期范围: {df.InvoiceDate.min()} → {df.InvoiceDate.max()}")
print(f"  总销售额: £{df.TotalAmount.sum():,.2f}")

# ========= 6. 去重复 =========
print("\n[6/6] 去重复...")
before = len(df)
df = df.drop_duplicates()
print(f"  去掉重复: {before - len(df):,} 行, 剩余 {len(df):,}")

# ========= 保存 =========
df.to_csv(CLEAN, index=False, encoding="utf-8-sig")
print(f"\n✓ 清洗完成！保存到: {CLEAN}")
print(f"  最终行数: {len(df):,}")

# ========= 快速统计 =========
print("\n" + "=" * 60)
print("  清洗后数据概览")
print("=" * 60)
print(f"  订单总数 (InvoiceNo):   {df.InvoiceNo.nunique():,}")
print(f"  商品数 (StockCode):     {df.StockCode.nunique():,}")
print(f"  客户数 (CustomerID):    {df.CustomerID.nunique():,}")
print(f"  国家数 (Country):       {df.Country.nunique()}")
print(f"  总销售额:               £{df.TotalAmount.sum():,.2f}")
print(f"  平均客单价:             £{df.groupby('InvoiceNo')['TotalAmount'].sum().mean():.2f}")
print(f"  平均订单量:             {df.Quantity.sum() / df.InvoiceNo.nunique():.1f} 件")
