# -*- coding: utf-8 -*-
"""
Step 4: SQL 业务指标分析
========================
用 SQL 写各种业务查询，输出 metrics.md（复制进简历用）

运行: py scripts/step4_sql_analysis.py
"""

import os
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
OUT_DIR = os.path.join(BASE, "output")
DB = os.path.join(DATA_DIR, "online_retail.db")
METRICS = os.path.join(OUT_DIR, "metrics.md")

conn = sqlite3.connect(DB)
print("=" * 60)
print("  Step 4: SQL 业务指标分析")
print("=" * 60)

lines = ["# Online Retail 数据分析指标汇总", ""]

# ========= 1. 整体概况 =========
print("\n[1/6] 整体概况...")
q = """
SELECT
  COUNT(DISTINCT InvoiceNo) AS 订单数,
  COUNT(DISTINCT CustomerID) AS 客户数,
  COUNT(DISTINCT StockCode) AS 商品数,
  COUNT(DISTINCT Country) AS 国家数,
  ROUND(SUM(TotalAmount), 2) AS 总销售额,
  ROUND(SUM(TotalAmount) / COUNT(DISTINCT InvoiceNo), 2) AS 平均客单价,
  ROUND(SUM(TotalAmount) / COUNT(DISTINCT CustomerID), 2) AS 人均消费
FROM orders
"""
df = pd.read_sql(q, conn)
print(df.to_string(index=False))
for col in df.columns:
    lines.append(f"- **{col}**: {df[col].values[0]}")
lines.append("")

# ========= 2. TOP10 畅销商品 =========
print("\n[2/6] TOP10 畅销商品...")
q = """
SELECT StockCode, Description,
  COUNT(DISTINCT InvoiceNo) AS 订单数,
  SUM(Quantity) AS 销售数量,
  ROUND(SUM(TotalAmount), 2) AS 销售额
FROM orders
WHERE StockCode NOT IN ('POST','D','M','DOT','C2','BANK CHARGES','AMAZONFEE','S','PAD','SP1002')
GROUP BY StockCode
ORDER BY 销售额 DESC
LIMIT 10
"""
df = pd.read_sql(q, conn)
print(df.to_string(index=False))
lines.append("## TOP10 畅销商品（按销售额）")
lines.append("| StockCode | Description | 订单数 | 销售数量 | 销售额 |")
lines.append("|-----------|-------------|--------|----------|--------|")
for _, r in df.iterrows():
    lines.append(f"| {r.StockCode} | {str(r.Description)[:30]} | {r.订单数:,} | {r.销售数量:,} | £{r.销售额:,.2f} |")
lines.append("")

# ========= 3. 各国家销售额 =========
print("\n[3/6] 各国家销售额 TOP10...")
q = """
SELECT Country,
  COUNT(DISTINCT InvoiceNo) AS 订单数,
  COUNT(DISTINCT CustomerID) AS 客户数,
  ROUND(SUM(TotalAmount), 2) AS 销售额,
  ROUND(SUM(TotalAmount) / COUNT(DISTINCT CustomerID), 2) AS 人均消费
FROM orders
GROUP BY Country
ORDER BY 销售额 DESC
LIMIT 10
"""
df = pd.read_sql(q, conn)
print(df.to_string(index=False))
lines.append("## 各国家销售额 TOP10")
for _, r in df.iterrows():
    lines.append(f"- **{r.Country}**: {r.客户数:,} 客户 / {r.订单数:,} 订单 / £{r.销售额:,.2f} 销售额")
lines.append("")

# ========= 4. 月度趋势 =========
print("\n[4/6] 月度趋势...")
q = """
SELECT strftime('%Y-%m', InvoiceDate) AS month,
  COUNT(DISTINCT InvoiceNo) AS 订单数,
  ROUND(SUM(TotalAmount), 2) AS 销售额
FROM orders
GROUP BY month
ORDER BY month
"""
df_month = pd.read_sql(q, conn)
print(df_month.to_string(index=False))
lines.append("## 月度销售趋势")
for _, r in df_month.iterrows():
    lines.append(f"- {r.month}: {r.订单数:,} 订单, £{r.销售额:,.2f} 销售额")
lines.append("")

# ========= 5. 复购率 =========
print("\n[5/6] 复购率分析...")
q = """
SELECT
  (SELECT COUNT(DISTINCT CustomerID) FROM orders) AS 付费客户总数,
  COUNT(*) AS 有多次购买的客户数,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT CustomerID) FROM orders), 2) AS 复购率_pct
FROM (
  SELECT CustomerID
  FROM orders
  GROUP BY CustomerID
  HAVING COUNT(DISTINCT InvoiceNo) >= 2
)
"""
df = pd.read_sql(q, conn)
print(df.to_string(index=False))
for col in df.columns:
    lines.append(f"- **{col}**: {df[col].values[0]}")
lines.append("")

# ========= 6. 客单价分布 =========
print("\n[6/6] 客单价分布...")
q = """
SELECT
  CASE
    WHEN total < 10  THEN '< £10'
    WHEN total < 30  THEN '£10-30'
    WHEN total < 50  THEN '£30-50'
    WHEN total < 100 THEN '£50-100'
    WHEN total < 200 THEN '£100-200'
    ELSE '> £200'
  END AS price_range,
  COUNT(*) AS 订单数,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS 占比_pct
FROM (
  SELECT InvoiceNo, SUM(TotalAmount) AS total
  FROM orders GROUP BY InvoiceNo
)
GROUP BY price_range
ORDER BY MIN(total)
"""
df = pd.read_sql(q, conn)
print(df.to_string(index=False))
lines.append("## 客单价分布")
for _, r in df.iterrows():
    lines.append(f"- {r.price_range}: {r.订单数:,} 订单 ({r.占比_pct}%)")
lines.append("")

# ========= 保存 =========
with open(METRICS, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"\n✓ 指标汇总已保存: {METRICS}")
conn.close()
