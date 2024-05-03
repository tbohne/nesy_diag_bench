import pandas as pd
import csv
import numpy as np

df = pd.read_csv("cumulative_res.csv")

anomaly_percentages = [float(i.split("_")[1]) for i in df["instance_set"]]
affected_by_percentages = [float(i.split("_")[2]) for i in df["instance_set"]]

# `affected_by` has a positive and a negative effect
#   - pos: can compensate false negatives by reaching the component again
#   - neg: leads to more classifications and thus also to more potential misclassifications
# -> do these effects cancel each other out?
anomaly_perc_aff_by_ratio = [
    float(anomaly_percentages[i]) / float(affected_by_percentages[i])
    for i in range(len(anomaly_percentages))
]

anomaly_perc_aff_by_prod = [
    float(anomaly_percentages[i]) * float(affected_by_percentages[i])
    for i in range(len(anomaly_percentages))
]

anomaly_perc_aff_by_model_acc_aggregation = [
    (float(anomaly_percentages[i]) + float(affected_by_percentages[i])) / df["avg_model_acc"][i]
    # float(anomaly_percentages[i]) * float(affected_by_percentages[i]) * df["avg_model_acc"][i]
    # np.average(
    #     [float(anomaly_percentages[i]), float(affected_by_percentages[i]), df["avg_model_acc"][i]],
    #     weights=[0.5, 0.3, 1]
    # )
    for i in range(len(anomaly_percentages))
]

anomaly_perc_model_acc_aggregation = [
    float(anomaly_percentages[i]) / df["avg_model_acc"][i]
    # np.average(
    #     [float(anomaly_percentages[i]), df["avg_model_acc"][i]],
    #     weights=[0.8, 0.5]
    # )
    for i in range(len(anomaly_percentages))
]

anomaly_percentages_filtered = [anomaly_percentages[i] for i in range(len(anomaly_percentages)) if df["avg_model_acc"][i] != 1.0]
affected_by_percentages_filtered = [affected_by_percentages[i] for i in range(len(affected_by_percentages)) if df["avg_model_acc"][i] != 1.0]
model_acc_filtered = [df["avg_model_acc"][i] for i in range(len(anomaly_percentages)) if df["avg_model_acc"][i] != 1.0]
avg_fp_filtered = [df["avg_fp"][i] for i in range(len(df["avg_fp"])) if df["avg_model_acc"][i] != 1.0]
avg_fn_filtered = [df["avg_fn"][i] for i in range(len(df["avg_fn"])) if df["avg_model_acc"][i] != 1.0]

anomaly_perc_aff_by_model_acc_aggregation_filtered = [
    (float(anomaly_percentages_filtered[i]) + float(affected_by_percentages_filtered[i])) / model_acc_filtered[i]
    for i in range(len(anomaly_percentages_filtered))
]

anomaly_perc_model_acc_aggregation_filtered = [
    float(anomaly_percentages_filtered[i]) / model_acc_filtered[i]
    for i in range(len(anomaly_percentages_filtered))
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

num_classifications = [df["avg_classification_ratio"][i] * 129 for i in range(len(df["avg_classification_ratio"]))]

anomaly_perc_model_acc_ratio = [
    round(float(anomaly_percentages[i]) / (df["avg_model_acc"][i] * 100), 2)
    for i in range(len(df["avg_model_acc"]))
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

sum_of_avg_fault_paths_and_dev = [
    round(df["fp_dev_mean"][i] + df["avg_num_fault_paths"][i], 2)
    for i in range(len(df["fp_dev_mean"]))
]

sum_of_max_fault_paths_and_dev = [
    round(df["fp_dev_max"][i] + df["max_num_fault_paths"][i], 2)
    for i in range(len(df["fp_dev_max"]))
]

################################## missed anomalies

true_num_anomalies = [
    round(129 * anomaly_percentages[i] / 100.0) for i in range(len(df["avg_tp"]))
]
print("true num anomalies:\n", true_num_anomalies)

avg_num_found_anomalies = [round(df["avg_fp"][i] + df["avg_tp"][i], 1) for i in range(len(df["avg_tp"]))]
print("\nfound anomalies:\n", avg_num_found_anomalies)

# negative -> found more than expected due to FPs
diff_ano = [
    round(true_num_anomalies[i] - avg_num_found_anomalies[i], 1) for i in range(len(df["avg_tp"]))
]
print("\ndiff:\n", diff_ano)

# missed not as some consequence of the misclassification, but only the misclassifications themselves
miss_due_to_class_iss = [
    round(df["avg_fn"][i], 2) for i in range(len(avg_num_found_anomalies))
]
print("\nmissed due to wrong classification:\n", miss_due_to_class_iss)

correctly_found = [df["avg_tp"][i] for i in range(len(df["avg_tp"]))]

# entirely missed, not even considered due to abortion criterion
missed_anomalies_unclassified = [
    round(true_num_anomalies[i] - miss_due_to_class_iss[i] - correctly_found[i], 2) for i in range(len(df["avg_tp"]))
]
print("\nentirely missed anomalies:\n", missed_anomalies_unclassified)

all_missed_anomalies = [
    round(true_num_anomalies[i] - df["avg_tp"][i], 2) for i in range(len(true_num_anomalies))
]
print("\nall missed anomalies:\n", all_missed_anomalies)

assert all(round(miss_due_to_class_iss[i] + missed_anomalies_unclassified[i], 2) == all_missed_anomalies[i]
    for i in range(len(all_missed_anomalies)))

sum_missed_and_correct = [round(missed_anomalies_unclassified[i] + miss_due_to_class_iss[i] + correctly_found[i], 1) for i in range(len(true_num_anomalies))]
assert all(sum_missed_and_correct[i] == true_num_anomalies[i] for i in range(len(true_num_anomalies)))

##################################

with open("meta_analysis.csv", mode='a', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(
        ["anomaly_perc", "affected_by_perc", "anomaly_perc_aff_by_ratio", "f1_scores", "anomaly_link_perc_scores",
        "compensation_ano_link", "gt_match_perc", "avg_ratio_gtfp", "compensation_gtfp",
        "model_acc_connectivity_ratio", "num_classifications_model_acc_ratio", "avg_model_acc",
        "anomaly_perc_model_acc_ratio", "num_classifications", "avg_num_fault_paths", "avg_fault_path_len",
        "anomaly_perc_aff_by_prod", "avg_runtime (s)", "median_runtime (s)", "median_num_fault_paths",
        "median_fault_path_len", "sum_of_avg_fault_paths_and_dev", "sum_of_max_fault_paths_and_dev",
        "max_runtime (s)", "anomaly_perc_aff_by_model_acc_aggregation", "avg_fp", "avg_fn",
        "anomaly_perc_model_acc_aggregation", "miss_due_to_class_iss", "missed_anomalies_unclassified",
        "all_missed_anomalies", "diag_success_percentage", "fp_dev_max", "fp_dev_mean"]
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
            num_classifications_model_acc_ratio[i],
            df["avg_model_acc"][i],
            anomaly_perc_model_acc_ratio[i],
            num_classifications[i],
            df["avg_num_fault_paths"][i],
            df["avg_fault_path_len"][i],
            anomaly_perc_aff_by_prod[i],
            df["avg_runtime (s)"][i],
            df["median_runtime (s)"][i],
            df["median_num_fault_paths"][i],
            df["median_fault_path_len"][i],
            sum_of_avg_fault_paths_and_dev[i],
            sum_of_max_fault_paths_and_dev[i],
            df["max_runtime (s)"][i],
            anomaly_perc_aff_by_model_acc_aggregation[i],
            df["avg_fp"][i],
            df["avg_fn"][i],
            anomaly_perc_model_acc_aggregation[i],
            miss_due_to_class_iss[i],
            missed_anomalies_unclassified[i],
            all_missed_anomalies[i],
            df["diag_success_percentage"][i],
            df["fp_dev_max"][i],
            df["fp_dev_mean"][i]
        ])

################## correlation coefficients

print("\n----- correlation coefficients -----\n")

# FOR FPs

correlation_matrix = np.corrcoef(anomaly_perc_aff_by_model_acc_aggregation, df["avg_fp"])
print("corrcoef anomaly_perc_aff_by_model_acc_aggregation --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["avg_fp"])
print("corrcoef anomaly percentage --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["avg_fp"])
print("corrcoef affected by percentage --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["avg_fp"])
print("corrcoef avg model acc --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_aff_by_prod, df["avg_fp"])
print("corrcoef anomaly perc aff by prod --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(num_classifications_model_acc_ratio, df["avg_fp"])
print("corrcoef num classifications model acc ratio --- FP:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_aff_by_model_acc_aggregation_filtered, avg_fp_filtered)
print("corrcoef anomaly_perc_aff_by_model_acc_aggregation_filtered --- FP filtered", round(correlation_matrix[0, 1], 2))

# FOR FNs

print("-------------------------------------------------------------------------------------------")

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_aggregation, df["avg_fn"])
print("corrcoef anomaly_perc_model_acc_aggregation --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["avg_fn"])
print("corrcoef anomaly percentage --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["avg_fn"])
print("corrcoef affected by percentage --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["avg_fn"])
print("corrcoef avg model acc --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_aff_by_prod, df["avg_fn"])
print("corrcoef anomaly perc aff by prod --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(num_classifications_model_acc_ratio, df["avg_fn"])
print("corrcoef num classifications model acc ratio --- FN:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_aggregation_filtered, avg_fn_filtered)
print("corrcoef anomaly_perc_model_acc_aggregation_filtered --- FN filtered", round(correlation_matrix[0, 1], 2))

# for runtime analysis

print("-------------------------------------------------------------------------------------------")

correlation_matrix = np.corrcoef(sum_of_max_fault_paths_and_dev, df["max_runtime (s)"])
print("corrcoef sum_of_max_fault_paths_and_dev --- max_runtime:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(sum_of_avg_fault_paths_and_dev, df["max_runtime (s)"])
print("corrcoef sum_of_avg_fault_paths_and_dev --- max_runtime:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_num_fault_paths"], df["avg_fault_path_len"])
print("corrcoef avg_num_fault_paths --- avg_fault_path_len:", round(correlation_matrix[0, 1], 2))

# more

print("-------------------------------------------------------------------------------------------")

correlation_matrix = np.corrcoef(df["avg_f1"], num_classifications)
print("corrcoef F1 --- num_classifications:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_f1"], df["avg_ratio_of_found_gtfp"])
print("corrcoef F1 --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_f1"], anomaly_link_perc_scores)
print("corrcoef F1 --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_f1"], df["gt_match_perc"])
print("corrcoef F1 --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(all_missed_anomalies, anomaly_link_perc_scores)
print("corrcoef all_missed_anomalies --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(missed_anomalies_unclassified, anomaly_link_perc_scores)
print("corrcoef missed_anomalies_unclassified --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(miss_due_to_class_iss, anomaly_link_perc_scores)
print("corrcoef miss_due_to_class_iss --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(all_missed_anomalies, df["avg_ratio_of_found_gtfp"])
print("corrcoef all_missed_anomalies --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(missed_anomalies_unclassified, df["avg_ratio_of_found_gtfp"])
print("corrcoef missed_anomalies_unclassified --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(miss_due_to_class_iss, df["avg_ratio_of_found_gtfp"])
print("corrcoef miss_due_to_class_iss --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_aff_by_ratio, compensation_ano_link)
print("corrcoef anomaly_perc_aff_by_ratio --- compensation_ano_link:", round(correlation_matrix[0, 1], 2))

print("-------------------------------------------------------------------------------------------")

# model acc

correlation_matrix = np.corrcoef(df["avg_model_acc"], anomaly_link_perc_scores)
print("corrcoef avg_model_acc --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["avg_ratio_of_found_gtfp"])
print("corrcoef avg_model_acc --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["gt_match_perc"])
print("corrcoef avg_model_acc --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["diag_success_percentage"])
print("corrcoef avg_model_acc --- diag_success_percentage:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["fp_dev_mean"])
print("corrcoef avg_model_acc --- fp_dev_mean:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(df["avg_model_acc"], df["fp_dev_max"])
print("corrcoef avg_model_acc --- fp_dev_max:", round(correlation_matrix[0, 1], 2))

print("-------------------------------------------------------------------------------------------")

# affected by

correlation_matrix = np.corrcoef(affected_by_percentages, anomaly_link_perc_scores)
print("corrcoef affected_by_percentages --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["avg_ratio_of_found_gtfp"])
print("corrcoef affected_by_percentages --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["gt_match_perc"])
print("corrcoef affected_by_percentages --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["diag_success_percentage"])
print("corrcoef affected_by_percentages --- diag_success_percentage:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["fp_dev_mean"])
print("corrcoef affected_by_percentages --- fp_dev_mean:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(affected_by_percentages, df["fp_dev_max"])
print("corrcoef affected_by_percentages --- fp_dev_max:", round(correlation_matrix[0, 1], 2))

print("-------------------------------------------------------------------------------------------")

# alpha / gamma

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, anomaly_link_perc_scores)
print("corrcoef anomaly_perc_model_acc_ratio --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, df["avg_ratio_of_found_gtfp"])
print("corrcoef anomaly_perc_model_acc_ratio --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, df["gt_match_perc"])
print("corrcoef anomaly_perc_model_acc_ratio --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, df["diag_success_percentage"])
print("corrcoef anomaly_perc_model_acc_ratio --- diag_success_percentage:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, df["fp_dev_mean"])
print("corrcoef anomaly_perc_model_acc_ratio --- fp_dev_mean:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_perc_model_acc_ratio, df["fp_dev_max"])
print("corrcoef anomaly_perc_model_acc_ratio --- fp_dev_max:", round(correlation_matrix[0, 1], 2))

print("-------------------------------------------------------------------------------------------")

# alpha

correlation_matrix = np.corrcoef(anomaly_percentages, anomaly_link_perc_scores)
print("corrcoef anomaly_percentages --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["avg_ratio_of_found_gtfp"])
print("corrcoef anomaly_percentages --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["gt_match_perc"])
print("corrcoef anomaly_percentages --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["diag_success_percentage"])
print("corrcoef anomaly_percentages --- diag_success_percentage:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["fp_dev_mean"])
print("corrcoef anomaly_percentages --- fp_dev_mean:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(anomaly_percentages, df["fp_dev_max"])
print("corrcoef anomaly_percentages --- fp_dev_max:", round(correlation_matrix[0, 1], 2))

print("-------------------------------------------------------------------------------------------")

# gamme / beta

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, anomaly_link_perc_scores)
print("corrcoef model_acc_connectivity_ratio --- anomaly_link_perc_scores:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, df["avg_ratio_of_found_gtfp"])
print("corrcoef model_acc_connectivity_ratio --- avg_ratio_of_found_gtfp:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, df["gt_match_perc"])
print("corrcoef model_acc_connectivity_ratio --- gt_match_perc:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, df["diag_success_percentage"])
print("corrcoef model_acc_connectivity_ratio --- diag_success_percentage:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, df["fp_dev_mean"])
print("corrcoef model_acc_connectivity_ratio --- fp_dev_mean:", round(correlation_matrix[0, 1], 2))

correlation_matrix = np.corrcoef(model_acc_connectivity_ratio, df["fp_dev_max"])
print("corrcoef model_acc_connectivity_ratio --- fp_dev_max:", round(correlation_matrix[0, 1], 2))
