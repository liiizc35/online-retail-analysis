# -*- coding: utf-8 -*-
"""
Step 6: 可视化图表
==================
生成 6 张图放到 output/charts/，简历里可以引用。

运行: py scripts/step6_visualize.py
"""

import os
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
OUT_DIR = os.path.join(BASE, "output")
CHART_DIR = os.path.join(OUT_DIR, "charts")
DB = os.path.join(DATA_DIR, "online_retail.db")
os.makedirs(CHART_DIR, exist_ok=True)

conn = sqlite3.connect(DB)
rfm = pd.read_csv(os.path.join(OUT_DIR, "rfm_segments.csv"), encoding="utf-8-sig")
print("=" * 60)
print("  Step 6: 可视化图表")
print("=" * 60)

# ========= 图 1: 月度销售趋势 =========
print("\n  [1/6] 月度销售趋势...")
df = pd.read_sql("""
    SELECT DATE(InvoiceDate) AS date,
           ROUND(SUM(TotalAmount), 2) AS sales,
           COUNT(DISTINCT InvoiceNo) AS orders
    FROM orders GROUP BY DATE(InvoiceDate) ORDER BY date
""", conn)
df["date"] = pd.to_datetime(df.date)

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(df.date, df.sales, color="#2c5f8a", linewidth=1.5)
ax1.set_ylabel("日销售额 (£)", color="#2c5f8a")
ax1.tick_params(axis="y", labelcolor="#2c5f8a")
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax2 = ax1.twinx()
ax2.bar(df.date, df.orders, alpha=0.3, color="#5bbf7a", width=1)
ax2.set_ylabel("日订单数", color="#5bbf7a")
ax2.tick_params(axis="y", labelcolor="#5bbf7a")
plt.title("Online Retail 日销售额 + 订单数趋势 (2010.12 - 2011.12)")
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "01_daily_trend.png"), dpi=120)
plt.close()
print("    ✓ 01_daily_trend.png")

# ========= 图 2: TOP10 畅销商品 =========
print("\n  [2/6] TOP10 畅销商品...")
df = pd.read_sql("""
    SELECT Description, ROUND(SUM(TotalAmount), 2) AS sales
    FROM orders GROUP BY Description
    ORDER BY sales DESC LIMIT 10
""", conn)
df["Description"] = df.Description.str[:40]

fig, ax = plt.subplots(figsize=(10, 6))
df = df.sort_values("sales")
ax.barh(range(len(df)), df.sales, color="#2c5f8a", alpha=0.8)
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df.Description)
ax.set_xlabel("销售额 (£)")
ax.set_title("TOP10 畅销商品（按销售额）")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "02_top10_products.png"), dpi=120)
plt.close()
print("    ✓ 02_top10_products.png")

# ========= 图 3: 各国家销售额 =========
print("\n  [3/6] 各国家销售额...")
df = pd.read_sql("""
    SELECT Country, ROUND(SUM(TotalAmount), 2) AS sales
    FROM orders GROUP BY Country
    ORDER BY sales DESC LIMIT 10
""", conn)
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(range(len(df)), df.sales, color="steelblue", alpha=0.8)
ax.set_xticks(range(len(df)))
ax.set_xticklabels(df.Country, rotation=45, ha="right")
ax.set_ylabel("销售额 (£)")
ax.set_title("各国家销售额 TOP10")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "03_countries.png"), dpi=120)
plt.close()
print("    ✓ 03_countries.png")

# ========= 图 4: 客单价分布 =========
print("\n  [4/6] 客单价分布...")
df = pd.read_sql("""
    SELECT CASE
      WHEN total < 10  THEN 'Under £10'
      WHEN total < 30  THEN '£10-30'
      WHEN total < 50  THEN '£30-50'
      WHEN total < 100 THEN '£50-100'
      WHEN total < 200 THEN '£100-200'
      ELSE 'Over £200'
    END AS range, COUNT(*) AS cnt
    FROM (
      SELECT InvoiceNo, SUM(TotalAmount) AS total
      FROM orders GROUP BY InvoiceNo
    ) GROUP BY range
    ORDER BY MIN(total)
""", conn)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(df["range"], df.cnt, color="#f39c12", alpha=0.8)
ax.set_xlabel("客单价区间")
ax.set_ylabel("订单数")
ax.set_title("客单价分布")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for i, v in enumerate(df.cnt):
    ax.text(i, v + 500, f"{v:,}", ha="center", fontsize=9)
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "04_price_dist.png"), dpi=120)
plt.close()
print("    ✓ 04_price_dist.png")

# ========= 图 5: RFM 分层饼图 =========
print("\n  [5/6] RFM 用户分层...")
seg_colors = {
    "重要价值用户": "#e74c3c", "重要发展用户": "#f39c12", "重要保持用户": "#3498db",
    "一般价值用户": "#27ae60", "一般保持用户": "#9b59b6", "流失风险用户": "#7f8c8d",
}
seg_order = list(seg_colors.keys())

seg_stats = rfm.groupby("用户分层").size().reindex(seg_order)

fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(seg_stats.values,
       labels=[f"{s}\n({v:,})" for s, v in zip(seg_order, seg_stats.values)],
       colors=[seg_colors[s] for s in seg_order],
       autopct="%1.1f%%", startangle=90, textprops={"fontsize": 10})
ax.set_title("RFM 用户分层分布")
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "05_rfm_segments.png"), dpi=120)
plt.close()
print("    ✓ 05_rfm_segments.png")

# ========= 图 6: RFM 三维散点 =========
print("\n  [6/6] RFM 三维散点...")
sample = rfm.sample(min(3000, len(rfm)), random_state=42)

fig, ax = plt.subplots(figsize=(10, 6))
for seg in seg_order:
    sub = sample[sample.用户分层 == seg]
    ax.scatter(sub.R, sub.F, s=sub.M / 5,
               color=seg_colors[seg], alpha=0.5, label=f"{seg}")
ax.set_xlabel("R: 最近购买间隔（天，越小越好）")
ax.set_ylabel("F: 订单数（越多越好）")
ax.set_title("RFM 三维散点图（气泡大小 = 消费额 M）")
ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
fig.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "06_rfm_scatter.png"), dpi=120)
plt.close()
print("    ✓ 06_rfm_scatter.png")

conn.close()
print(f"\n✓ 全部图表已保存到: {CHART_DIR}")
