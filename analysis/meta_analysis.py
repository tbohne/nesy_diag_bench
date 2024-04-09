import pandas as pd
import csv

df = pd.read_csv("cumulative_res.csv")

anomaly_percentages = [i.split("_")[1] for i in df["instance_set"]]
affected_by_percentages = [i.split("_")[2] for i in df["instance_set"]]

# `affected_by` has a positive and a negative effect
#   - pos: can compensate false negatives by reaching the component again
#   - neg: leads to more classifications and thus also to more potential misclassifications
# -> do these effects cancel each other out?
anomaly_perc_aff_by_ratio = [
    float(anomaly_percentages[i]) / float(affected_by_percentages[i]) 
    for i in range(len(anomaly_percentages))
]

# basic idea: the worse the model, the better the graph should be connected in
# order to compensate wrong classifications, however, this also has the neg
# side-effect again of leading to more classifications and thus also to more
# potential for wrong classifications
model_acc_connectivity_ratio = [
    df["avg_model_acc"][i] / (float(affected_by_percentages[i]) / 100.0)
    for i in range(len(df["avg_model_acc"]))
]

# idea: the performance should get worse when having too many classifications
# with a too poor model acc
num_classifications_model_acc_ratio = [
    round(df["avg_classification_ratio"][i] * 129 / (df["avg_model_acc"][i] * 100), 2)
    for i in range(len(df["avg_classification_ratio"]))
]

anomaly_link_perc_scores = [round(i / 100.0, 2) for i in df["avg_ano_link_perc"]]

# I don't think this metric makes much sense, it's not really a compensation;
# there should be a clear correlation between the two, but both F1 and the
# ano link perc depend on the number of anomalies, the model acc and the
# affected-by percentage -- but still, could look at this later...
compensation_ano_link = [
    round(anomaly_link_perc_scores[i] - df["avg_f1"][i], 2)
    for i in range(len(df["avg_f1"]))
]

# same thing: I don't think this makes much sense
compensation_gtfp = [
    round(df["avg_ratio_of_found_gtfp"][i] - df["avg_f1"][i], 2)
    for i in range(len(df["avg_f1"]))
]

with open("meta_analysis.csv", mode='a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(
        ["anomaly_perc", "affected_by_perc", "anomaly_perc_aff_by_ratio", "f1_scores", "anomaly_link_perc_scores",
        "compensation_ano_link", "gt_match_perc", "avg_ratio_gtfp", "compensation_gtfp",
        "model_acc_connectivity_ratio", "num_classifications_model_acc_ratio"]
    )

    for i in range(len(compensation_ano_link)):
        writer.writerow([
            anomaly_percentages[i],
            affected_by_percentages[i],
            anomaly_perc_aff_by_ratio[i],
            df["avg_f1"][i],
            anomaly_link_perc_scores[i],
            compensation_ano_link[i],
            df["gt_match_perc"][i],
            df["avg_ratio_of_found_gtfp"][i],
            compensation_gtfp[i],
            model_acc_connectivity_ratio[i],
            num_classifications_model_acc_ratio[i]
        ])
