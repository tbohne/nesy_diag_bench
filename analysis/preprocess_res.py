import pandas as pd

df = pd.read_csv("cumulative_res.csv")

for i in range(len(df["instance_set"])):
    e = df["instance_set"][i].split("_")
    df.at[i, "instance_set"] = "_".join([e[1], e[2], e[5], e[6]])

df.to_csv("compact_cumulative_res.csv", sep=',', encoding='utf-8', index=False)
