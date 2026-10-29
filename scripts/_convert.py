import pandas as pd
import os
import time

base = r"C:\Users\Liiizc\Documents\Trae-CN\temp_20261029_01\online_retail_project"
xlsx = os.path.join(base, "data", "online_retail.xlsx")
csv = os.path.join(base, "data", "online_retail.csv")

print("读取 XLSX...")
t0 = time.time()
df = pd.read_excel(xlsx)
print(f"读取完成: {len(df):,} 行, 耗时 {time.time()-t0:.1f}s")

print(df.head(3))
print(f"\n列名: {list(df.columns)}")
print(f"\n数据类型:\n{df.dtypes}")

print("\n写入 CSV...")
t1 = time.time()
df.to_csv(csv, index=False, encoding="utf-8-sig")
print(f"写入完成, 耗时 {time.time()-t1:.1f}s")
print(f"CSV 大小: {os.path.getsize(csv)/1024/1024:.1f} MB")

os.remove(xlsx)
print("\n✓ 完成!")
