# 电商订单数据分析与 RFM 用户分层模型

基于 UCI Online Retail 公开数据集，对一家英国在线零售商 2010.12 - 2011.12 全年交易数据做完整分析：数据清洗 → SQL 入库与指标计算 → RFM 用户分层 → 可视化。

## 数据集

| 项目 | 说明 |
| --- | --- |
| 来源 | UCI Machine Learning Repository — Online Retail |
| 原始规模 | 541,909 行 |
| 清洗后 | 392,692 行（过滤 149,217 行，占 27.5%） |
| 业务规模 | 18,532 笔订单 · 4,338 客户 · 3,665 商品 · 37 国家 |

## 分析流程

| 步骤 | 脚本 | 内容 |
| --- | --- | --- |
| 1 | `step1_download.py` | 从 UCI 官方直链下载原始数据，XLSX 转 CSV |
| 2 | `step2_clean.py` | 去缺失值、无效订单、取消订单、重复行 |
| 3 | `step3_load_sql.py` | 写入 SQLite，建 5 个索引并用 `EXPLAIN QUERY PLAN` 验证 |
| 4 | `step4_sql_analysis.py` | 15+ 项业务指标：TOP10 商品、国家分布、月度趋势、复购率、客单价 |
| 5 | `step5_rfm.py` | R/F/M 各 1-5 分位数打分，六档用户分层 |
| 6 | `step6_visualize.py` | Matplotlib 输出 6 张图表 |

## 关键发现

**整体指标**

| 指标 | 数值 |
| --- | --- |
| 总销售额 | £8,887,208.89 |
| 平均客单价 | £479.56 |
| 人均消费 | £2,048.69 |
| 复购率（≥2 单） | 65.58%（2,845 / 4,338） |
| 月度峰值 | 2011-11，£1,156,205.61 |

**地域结构**：英国占销售额 82%（£7,285,024.64 / £8,887,208.89）。海外客户数量少但客单极高——荷兰 9 个客户贡献 £285,446，EIRE 3 个客户贡献 £265,262，属典型 B2B 批发客户。

**用户分层（RFM）**

| 分层 | 占比 | 人数 | 平均订单数 | 平均消费 | 平均购买间隔 |
| --- | --- | --- | --- | --- | --- |
| 重要价值 | 21.4% | 929 | 11.8 | £6,706.37 | 14.0 天 |
| 重要发展 | 9.2% | 401 | 3.5 | £1,090.16 | 15.7 天 |
| 重要保持 | 6.0% | 260 | 5.5 | £2,331.93 | 69.2 天 |
| 一般价值 | 8.1% | 349 | 1.9 | £458.69 | 17.0 天 |
| 一般保持 | 16.3% | 706 | 2.8 | £1,159.40 | 96.9 天 |
| 流失风险 | 39.0% | 1,693 | 1.2 | £375.02 | 169.9 天 |

21.4% 的「重要价值用户」贡献约 70% 销售额（929 × £6,706 ≈ £623 万），呈典型二八分布；而 39% 的「流失风险用户」平均 170 天未回购、人均仅 £375，是召回优先级最高但价值最低的一批。

## 图表

| 月度销售趋势 | TOP10 畅销商品 |
| --- | --- |
| ![月度趋势](output/01_daily_trend.png) | ![TOP10](output/02_top10_products.png) |

| 各国家销售额 | 客单价分布 |
| --- | --- |
| ![国家](output/03_countries.png) | ![客单价](output/04_price_dist.png) |

| RFM 分层占比 | RFM 三维分布 |
| --- | --- |
| ![RFM 分层](output/05_rfm_segments.png) | ![RFM 散点](output/06_rfm_scatter.png) |

## 数据处理说明

- **为什么删除 27.5% 的数据**：主要来自 `CustomerID` 为空的匿名交易（135,080 行，占过滤总量 90%）。RFM 以客户为单位建模，匿名交易无法归属到具体用户，只能剔除；代价是总销售额低于全量成交额。
- **取消订单为什么单独处理**：取消订单的 `Quantity` 为负，已在「无效订单」一步被 `Quantity > 0` 过滤，单独一步为防御性写法。
- **索引验证**：`EXPLAIN QUERY PLAN` 输出 `SEARCH orders USING COVERING INDEX idx_orders_customer (CustomerID=?)`，确认查询命中覆盖索引。
- **RFM 打分**：用 `pd.qcut(rank(method="first"), 5)` 做等频分箱，避免等距分箱在长尾消费分布下严重倾斜。

## 目录结构

```
online_retail_project/
├── scripts/            # 6 个分析脚本，按流程顺序命名
├── data/               # 原始与清洗后数据（未入库，可从 UCI 重新下载）
├── output/
│   ├── metrics.md      # 指标汇总
│   ├── rfm_segments.csv
│   └── *.png           # 6 张图表
└── .gitignore
```

## 复现

```bash
py -m pip install pandas matplotlib openpyxl
py scripts/step1_download.py
py scripts/step2_clean.py
py scripts/step3_load_sql.py
py scripts/step4_sql_analysis.py
py scripts/step5_rfm.py
py scripts/step6_visualize.py
```

数据文件体积较大（CSV 46MB / SQLite 78MB），不纳入版本控制，运行 `step1_download.py` 可自动从 UCI 官方地址重新下载。
