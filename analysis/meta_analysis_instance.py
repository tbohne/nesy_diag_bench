import numpy as np
import pandas as pd

df = pd.read_csv("res.csv")

correlation_matrix = np.corrcoef(df["#fault_paths"], df["avg_fp_len"])
print("corrcoef num fault paths --- fault path len:", round(correlation_matrix[0, 1], 2))
