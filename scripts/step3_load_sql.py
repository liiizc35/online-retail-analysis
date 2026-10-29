# -*- coding: utf-8 -*-
"""
Step 3: SQL 入库 + 建索引
========================
把清洗后的数据载入 SQLite，建索引加速查询。
（用 SQLite 是因为零配置，但你的简历写的是 MySQL，原理一样）

运行: py scripts/step3_load_sql.py
"""

import os
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
CLEAN = os.path.join(DATA_DIR, "online_retail_clean.csv")
DB = os.path.join(DATA_DIR, "online_retail.db")

print("=" * 60)
print("  Step 3: SQL 入库 + 建索引")
print("=" * 60)

# 删除旧库
if os.path.exists(DB):
    os.remove(DB)
    print("\n  已删除旧数据库")

# 读清洗后的 CSV
print("\n  读取清洗后数据...")
df = pd.read_csv(CLEAN, low_memory=False, encoding="utf-8-sig",
                 parse_dates=["InvoiceDate"])
print(f"  {len(df):,} 行")

# 连 SQLite
conn = sqlite3.connect(DB)

# 写入
print("\n  写入 SQLite...")
df.to_sql("orders", conn, if_exists="replace", index=False)
print(f"  ✓ 写入完成")

# 建索引
print("\n  建索引...")
indexes = [
    "CREATE INDEX idx_orders_invoiceno   ON orders(InvoiceNo)",
    "CREATE INDEX idx_orders_customer    ON orders(CustomerID)",
    "CREATE INDEX idx_orders_stockcode   ON orders(StockCode)",
    "CREATE INDEX idx_orders_date         ON orders(InvoiceDate)",
    "CREATE INDEX idx_orders_country      ON orders(Country)",
]
for sql in indexes:
    conn.execute(sql)
conn.commit()
print(f"  ✓ 建了 {len(indexes)} 个索引")

# 验证
print("\n  验证索引是否生效...")
for row in conn.execute("EXPLAIN QUERY PLAN SELECT COUNT(*) FROM orders WHERE CustomerID = 17850"):
    print(f"    {row}")

print(f"\n✓ 数据库就绪: {DB} ({os.path.getsize(DB)/1024/1024:.1f} MB)")

# 快速查询
print("\n" + "=" * 60)
print("  SQLite 快速查询示例（简历上可以写）")
print("=" * 60)

queries = [
    ("总订单数",
     "SELECT COUNT(DISTINCT InvoiceNo) FROM orders"),
    ("TOP10 销售额商品",
     "SELECT StockCode, Description, ROUND(SUM(TotalAmount), 2) AS sales "
     "FROM orders GROUP BY StockCode ORDER BY sales DESC LIMIT 10"),
    ("各国家销售额",
     "SELECT Country, COUNT(DISTINCT CustomerID) AS users, "
     "ROUND(SUM(TotalAmount), 2) AS sales FROM orders "
     "GROUP BY Country ORDER BY sales DESC LIMIT 10"),
    ("各月销售额趋势",
     "SELECT strftime('%Y-%m', InvoiceDate) AS month, "
     "ROUND(SUM(TotalAmount), 2) AS sales, COUNT(DISTINCT InvoiceNo) AS orders "
     "FROM orders GROUP BY month ORDER BY month"),
    ("每个客户的订单数 + 总消费 (用于 RFM)",
     "SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS freq, "
     "ROUND(SUM(TotalAmount), 2) AS total_spent, "
     "MAX(InvoiceDate) AS last_purchase "
     "FROM orders GROUP BY CustomerID LIMIT 10"),
]

for title, sql in queries:
    print(f"\n  【{title}】")
    print(f"  SQL: {sql[:80]}...")
    try:
        result = pd.read_sql(sql, conn)
        print(result.head().to_string(index=False))
    except Exception as e:
        print(f"  ✗ 错误: {e}")

conn.close()
print("\n✓ Step 3 完成！")
