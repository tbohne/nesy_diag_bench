import pandas as pd
import csv

df = pd.read_csv("cumulative_res.csv")

anomaly_percentages = [i.split("_")[1] for i in df["instance_set"]]
affected_by_percentages = [i.split("_")[2] for i in df["instance_set"]]

anomaly_perc_aff_by_ratio = [
    float(anomaly_percentages[i]) / float(affected_by_percentages[i]) 
    for i in range(len(anomaly_percentages))
]

anomaly_link_perc_scores = [round(i / 100.0, 2) for i in df["avg_ano_link_perc"]]

compensation_ano_link = [
    round(anomaly_link_perc_scores[i] - df["avg_f1"][i], 2)
    for i in range(len(df["avg_f1"]))
]

compensation_gtfp = [
    round(df["avg_ratio_of_found_gtfp"][i] - df["avg_f1"][i], 2)
    for i in range(len(df["avg_f1"]))
]

with open("compensation.csv", mode='a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(
        ["anomaly_perc_aff_by_ratio", "f1_scores", "anomaly_link_perc_scores",
        "compensation_ano_link", "gt_match_perc", "avg_ratio_gtfp", "compensation_gtfp"]
    )

    for i in range(len(compensation_ano_link)):
        writer.writerow([
            anomaly_perc_aff_by_ratio[i],
            df["avg_f1"][i],
            anomaly_link_perc_scores[i],
            compensation_ano_link[i],
            df["gt_match_perc"][i],
            df["avg_ratio_of_found_gtfp"][i],
            compensation_gtfp[i]
        ])
