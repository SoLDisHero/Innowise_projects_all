import pandas as pd

# READING DATA
data = pd.read_csv("include/datasets/original/database.csv", encoding="utf-8-sig", sep=",", low_memory=False)

# SEPARATING DATA BY MONTHS
data["departure"] = pd.to_datetime(data["departure"], dayfirst=True, errors="coerce")
data["month"] = data["departure"].dt.to_period("M")

for month, group in data.groupby("month"):
    file = f"include/datasets/by_months/{month}_date.csv"
    group.to_csv(file, index=False, chunksize=100_000)
    
