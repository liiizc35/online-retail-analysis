# Online Retail 真实电商订单数据分析

> 这个项目你**两天能独立完成**，产出物直接写进简历。

## 数据集
- **UCI Online Retail** 公开数据集
- 英国某在线零售商 2010.12 - 2011.12 全年交易
- **392,692 条**清洗后订单
- 4,338 客户 × 3,665 商品 × 37 国家
- 总销售额 £888,721

## 项目结构

```
online_retail_project/
├── README.md                    ← 你正在读的这份
├── data/
│   ├── online_retail.csv        ← Step 1 下载的原始数据
│   ├── online_retail_clean.csv  ← Step 2 清洗后数据
│   └── online_retail.db         ← Step 3 SQLite 数据库
├── scripts/
│   ├── step1_download.py        ← 下载数据
│   ├── step2_clean.py           ← 数据清洗
│   ├── step3_load_sql.py        ← SQL 入库 + 建索引
│   ├── step4_sql_analysis.py    ← SQL 业务指标分析
│   ├── step5_rfm.py             ← RFM 用户分层模型
│   └── step6_visualize.py       ← 可视化图表
└── output/
    ├── metrics.md               ← Step 4 指标汇总（复制进简历）
    ├── rfm_segments.csv         ← Step 5 用户分层结果
    └── charts/                  ← Step 6 六张图
        ├── 01_daily_trend.png
        ├── 02_top10_products.png
        ├── 03_countries.png
        ├── 04_price_dist.png
        ├── 05_rfm_segments.png
        └── 06_rfm_scatter.png
```

## 两天计划

### Day 1（约 3 小时）：数据下载 → 清洗 → SQL 入库 → 基础指标

| 时间 | 任务 | 运行命令 | 产出物 |
|------|------|---------|--------|
| 15 min | 下载数据 | `py scripts/step1_download.py` | `data/online_retail.csv` |
| 30 min | 读 README，理解每步做什么 | 阅读本文件 | 心里有数 |
| 45 min | 数据清洗 | `py scripts/step2_clean.py` | `data/online_retail_clean.csv` |
| 30 min | 读清洗脚本 + 思考为什么要这样清洗 | 打开 `scripts/step2_clean.py` 每一行注释 | 面试能解释 |
| 30 min | SQL 入库 + 建索引 | `py scripts/step3_load_sql.py` | `data/online_retail.db` |
| 45 min | SQL 业务指标分析 | `py scripts/step4_sql_analysis.py` | `output/metrics.md` |

### Day 2（约 3 小时）：RFM 建模 → 可视化 → 整理产出

| 时间 | 任务 | 运行命令 | 产出物 |
|------|------|---------|--------|
| 45 min | RFM 用户分层 | `py scripts/step5_rfm.py` | `output/rfm_segments.csv` |
| 30 min | 读 RFM 脚本 + 理解 R/F/M 打分逻辑 | 打开 `scripts/step5_rfm.py` | 面试能解释 |
| 30 min | 可视化图表 | `py scripts/step6_visualize.py` | `output/charts/*.png` |
| 60 min | 整理产出物 + 写简历项目描述（参考下文） | — | — |
| 15 min | （可选）推 GitHub + 写 README | git init → commit → push | GitHub repo |

## 简历项目描述模板

> 下面这段可以直接放进简历（根据你实际跑出来的数字微调）

```
电商订单数据分析与 RFM 用户分层模型 | Python · SQL · Pandas · SQLite
自下载 UCI Online Retail 真实电商数据集（39 万条订单，4338 客户，英国 2010-2011 全年交易），
完整走通"数据清洗 → SQL 入库 → 业务指标计算 → RFM 建模 → 可视化"全流程：
- 数据清洗：用 Python Pandas 处理缺失值、取消订单、无效记录，数据量从 54 万条降至 39 万条（去掉 28% 脏数据）
- SQL 分析：用 SQLite 建 5 个索引加速查询，编写多表 GROUP BY + 聚合 SQL，计算 TOP10 畅销商品、
  各国家销售额、月度趋势、客单价分布、复购率等 15+ 业务指标（总销售额 £88.9 万，英国占 82%）
- RFM 建模：对 4338 客户用分位数打 R/F/M 各 1-5 分，将用户分为 6 档——重要价值用户 21.4%、
  流失风险用户 39.0%（平均间隔 170 天），并为每档制定差异化运营策略
- 可视化：用 Matplotlib 生成 6 张图表（月度趋势、TOP10 商品、国家分布、客单价、RFM 饼图/散点）
```

## 面试可能被问到的题 + 你怎么答

| 面试官问 | 你可以答 |
|---------|---------|
| 你做了什么？ | 下载了 UCI Online Retail 真实电商数据，用 Python + SQL 分析了 39 万条订单 |
| 为什么要清洗？ | 原始数据有 13.5 万条 CustomerID 为空、9000 条 Quantity<=0、5000 条重复，不洗会歪 |
| RFM 是什么？ | R=最近购买间隔、F=购买频次、M=总消费，用分位数打 1-5 分再分层 |
| 你的分层结果？ | 21% 重要价值用户（高消费高频），39% 流失风险用户（间隔 170 天），应该重点召回 |
| SQL 怎么优化的？ | 建了 CustomerID、StockCode、InvoiceDate 等 5 个索引，GROUP BY 前加 WHERE 缩小范围 |
| Pandas 用了什么？ | 去 NA、去重、datetime 转换、计算 TotalAmount、qcut 分位数打分 |
| 发现了什么洞察？ | 英国占 82% 销售额，11 月是旺季（黑五/圣诞），67% 订单客单价超 £200 |

## 快速开始（只需 Python）

```bash
# 安装依赖
py -m pip install pandas matplotlib openpyxl

# 进入项目目录
cd online_retail_project

# 按顺序跑 6 步
py scripts/step1_download.py      # 下载数据
py scripts/step2_clean.py         # 清洗
py scripts/step3_load_sql.py      # SQL 入库
py scripts/step4_sql_analysis.py  # 业务指标
py scripts/step5_rfm.py           # RFM 分层
py scripts/step6_visualize.py     # 可视化
```

每步跑完都会打印进度，产出物自动保存到 `output/` 目录。
