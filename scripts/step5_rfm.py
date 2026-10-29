# -*- coding: utf-8 -*-
"""
Step 5: RFM 用户分层模型
========================
R = Recency: 最近一次购买距今天数 (越小越好)
F = Frequency: 订单数 (越多越好)
M = Monetary: 总消费额 (越多越好)

运行: py scripts/step5_rfm.py
"""

import os
import sqlite3
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data")
OUT_DIR = os.path.join(BASE, "output")
DB = os.path.join(DATA_DIR, "online_retail.db")
RFM_CSV = os.path.join(OUT_DIR, "rfm_segments.csv")

conn = sqlite3.connect(DB)
print("=" * 60)
print("  Step 5: RFM 用户分层")
print("=" * 60)

# 观察截止日 = 数据集中最大日期 + 1 天
max_date = pd.read_sql("SELECT MAX(InvoiceDate) AS d FROM orders", conn)["d"].values[0]
print(f"\n  数据截止日: {max_date}")

# 计算每个客户的 R / F / M
rfm_sql = f"""
SELECT
  CustomerID,
  CAST(julianday('{max_date}') - julianday(DATE(MAX(InvoiceDate))) AS INTEGER) AS R,
  COUNT(DISTINCT InvoiceNo) AS F,
  ROUND(SUM(TotalAmount), 2) AS M
FROM orders
GROUP BY CustomerID
"""

rfm = pd.read_sql(rfm_sql, conn)
print(f"  客户数: {len(rfm):,}")
print(f"  R 范围: {rfm.R.min()} ~ {rfm.R.max()} 天")
print(f"  F 范围: {rfm.F.min()} ~ {rfm.F.max()} 次")
print(f"  M 范围: £{rfm.M.min():.2f} ~ £{rfm.M.max():.2f}")

# 分位数打分 1~5
print("\n  分位数打分...")
rfm["R_score"] = pd.qcut(rfm.R.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm.F.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm.M.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["RFM总分"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

# 用户分层
def segment(row):
    r, f, m, t = row["R_score"], row["F_score"], row["M_score"], row["RFM总分"]
    if t >= 13: return "重要价值用户"
    elif t >= 11: return "重要发展用户" if r >= 4 else "重要保持用户"
    elif t >= 8: return "一般价值用户" if r >= 4 else "一般保持用户"
    else: return "流失风险用户"

rfm["用户分层"] = rfm.apply(segment, axis=1)

# 统计
seg_order = ["重要价值用户", "重要发展用户", "重要保持用户",
             "一般价值用户", "一般保持用户", "流失风险用户"]

print("\n" + "=" * 60)
print("  用户分层统计")
print("=" * 60)

seg_stats = rfm.groupby("用户分层").agg(
    用户数=("CustomerID", "count"),
    平均订单数=("F", "mean"),
    平均消费=("M", "mean"),
    平均间隔_天=("R", "mean"),
).reindex(seg_order)
seg_stats["占比"] = (seg_stats.用户数 / seg_stats.用户数.sum() * 100).round(2)
seg_stats["平均消费"] = seg_stats["平均消费"].round(2)
seg_stats["平均间隔_天"] = seg_stats["平均间隔_天"].round(1)
print(seg_stats.to_string())

# 保存
rfm.to_csv(RFM_CSV, index=False, encoding="utf-8-sig")
print(f"\n✓ RFM 分层已保存: {RFM_CSV}")

# 运营建议
print("\n" + "=" * 60)
print("  各层用户运营建议（简历可以写）")
print("=" * 60)
suggestions = {
    "重要价值用户": "VIP 专属权益 + 会员体系 + 优先客服 → 保持满意度",
    "重要发展用户": "推荐更多品类 + 新品体验 + 交叉销售 → 提升客单",
    "重要保持用户": "主动触达 + 优惠券唤醒 + 专属活动 → 防止流失",
    "一般价值用户": "推荐爆款 + 首单立减 → 刺激首次大额消费",
    "一般保持用户": "内容种草 + 社群运营 → 建立情感连接",
    "流失风险用户": "大力度召回券 + 推送高性价比商品",
}
for seg in seg_order:
    row = seg_stats.loc[seg]
    print(f"\n  【{seg}】({row['占比']:.1f}%, {int(row['用户数']):,}人)")
    print(f"    平均订单数: {row['平均订单数']:.1f}, 平均消费: £{row['平均消费']:.2f}, 平均间隔: {row['平均间隔_天']} 天")
    print(f"    → {suggestions[seg]}")

conn.close()
