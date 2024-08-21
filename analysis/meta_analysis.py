#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import csv
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

df = pd.read_csv("cumulative_res.csv")

anomaly_percentages = [float(i.split("_")[1]) for i in df["instance_set"]]
affected_by_percentages = [float(i.split("_")[2]) for i in df["instance_set"]]

avg_misclassifications = [
    df["avg_fp"][i] + df["avg_fn"][i] for i in range(len(df["avg_fp"]))
]

# approximation: #FP * beta / 2 * C * gamma
potential_for_misclassification = [
    # round(df["avg_fp"][i] * (affected_by_percentages[i] / 100.0 / 2) * 129 * df["avg_model_acc"][i], 2)
    round(df["avg_fp"][i] * (affected_by_percentages[i] / 100.0 / 2) * 129 * (1 - df["avg_classification_ratio"][i]), 2)
    for i in range(len(df["avg_fp"]))
]

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

anomaly_percentages_filtered = [anomaly_percentages[i] for i in range(len(anomaly_percentages)) if
                                df["avg_model_acc"][i] != 1.0]
affected_by_percentages_filtered = [affected_by_percentages[i] for i in range(len(affected_by_percentages)) if
                                    df["avg_model_acc"][i] != 1.0]
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
    abs(round(anomaly_link_perc_scores[i] - df["avg_f1"][i], 2))
    for i in range(len(df["avg_f1"]))
]

# same thing: I don't think this makes much sense
compensation_gtfp = [
    abs(round(df["avg_ratio_of_found_gtfp"][i] - df["avg_f1"][i], 2))
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

print("beta:\n", affected_by_percentages)
tp_fp_sum = [
    round(df["avg_tp"][i] + df["avg_fp"][i], 2) for i in range(len(affected_by_percentages))
]
print("TP+FP:\n", tp_fp_sum)

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

fn_tn_sum = [
    round(df["avg_fn"][i] + df["avg_tn"][i], 2) for i in range(len(avg_num_found_anomalies))
]

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

sum_missed_and_correct = [round(missed_anomalies_unclassified[i] + miss_due_to_class_iss[i] + correctly_found[i], 1) for
                          i in range(len(true_num_anomalies))]
assert all(sum_missed_and_correct[i] == true_num_anomalies[i] for i in range(len(true_num_anomalies)))

# permutations -- and approximations (expected fault paths)
permutations = [np.math.factorial(i) for i in true_num_anomalies]
permutation_perc = [round(df["avg_num_fault_paths"][i] / permutations[i] * 100.0, 2) for i in range(len(permutations))]
# there's at least one fault path per anomalous component and then potentially more based on beta, thus "+"
permutation_approx = [
    true_num_anomalies[i]
    + np.math.factorial(1 + round((true_num_anomalies[i] - 1) * affected_by_percentages[i] / 2 / 100.0))
    for i in range(len(true_num_anomalies))
]
approx_perc = [round(df["avg_num_fault_paths"][i] / permutation_approx[i] * 100.0, 2) for i in range(len(permutations))]
permutations = [np.format_float_scientific(i, precision=2) for i in permutations]
print("\n-----------------------------------------------------------------------")
print("avg approx perc:", round(np.average(approx_perc), 2))
print("median approx perc:", round(np.median(approx_perc), 2))
print("max approx perc:", round(np.max(approx_perc), 2))
print("min approx perc:", round(np.min(approx_perc), 2))
print("-----------------------------------------------------------------------")

#################################

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
         "all_missed_anomalies", "diag_success_percentage", "fp_dev_max", "fp_dev_mean", "permutations",
         "permutation_perc", "permutation_approx", "approx_perc", "avg_compensation_by_aff_by_savior",
         "avg_missed_chances", "avg_no_second_chance", "avg_misclassifications", "potential_for_misclassification"]
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
            df["fp_dev_mean"][i],
            permutations[i],
            permutation_perc[i],
            permutation_approx[i],
            approx_perc[i],
            df["avg_compensation_by_aff_by_savior"][i],
            df["avg_missed_chances"][i],
            df["avg_no_second_chance"][i],
            avg_misclassifications[i],
            potential_for_misclassification[i]
        ])


################## correlation coefficients

def determine_correlation(arr_a: List[float], arr_b: List[float]) -> Tuple[float, float, bool]:
    """
    Determines the Pearson correlation coefficient between `arr_a` and `arr_b`.

    "The p-value roughly indicates the probability of an uncorrelated system producing datasets that have a Pearson
    correlation at least as extreme as the one computed from these datasets. The p-values are not entirely
    reliable but are probably reasonable for datasets larger than 500 or so." -- pydoc.help

    IMPORTANT: we only have a dataset size of 39 (!)

    --> p-value associated with the chosen alternative
        p-value low (generally < 0.05), corr. statistically significant
        p-value high (generally > 0.05), corr. not statistically significant

    :param arr_a: first array of comparison
    :param arr_b: second array of comparison
    :return: (correlation coefficient, p-value, whether corr. statistically significant)
    """
    assert len(arr_a) == len(arr_b)

    if len(np.unique(arr_a)) <= 1 or len(np.unique(arr_b)) <= 1:
        return 0, 0, False

    # numpy is not estimating the significance
    np_corr_coeff = round(np.corrcoef(arr_a, arr_b)[0, 1], 2)
    corr_coeff, p_val = pearsonr(arr_a, arr_b)
    assert np_corr_coeff == round(corr_coeff, 2)
    return corr_coeff, p_val, p_val < 0.05


print("\n----- correlation coefficients -----\n")

# FOR FPs
corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_model_acc_aggregation, df["avg_fp"])
print("anomaly_perc_aff_by_model_acc_aggregation --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["avg_fp"])
print("anomaly percentage --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_fp"])
print("affected by percentage --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["avg_fp"])
print("avg model acc --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, df["avg_fp"])
print("anomaly perc aff by prod --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, df["avg_fp"])
print("num classifications model acc ratio --- FP:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(
    anomaly_perc_aff_by_model_acc_aggregation_filtered, avg_fp_filtered
)
print("anomaly_perc_aff_by_model_acc_aggregation_filtered --- FP filtered")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

# FOR FNs

print("-------------------------------------------------------------------------------------------")

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_aggregation, df["avg_fn"])
print("anomaly_perc_model_acc_aggregation --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["avg_fn"])
print("anomaly percentage --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_fn"])
print("affected by percentage --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["avg_fn"])
print("avg model acc --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, df["avg_fn"])
print("anomaly perc aff by prod --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, df["avg_fn"])
print("num classifications model acc ratio --- FN:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_aggregation_filtered, avg_fn_filtered)
print("anomaly_perc_model_acc_aggregation_filtered --- FN filtered")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

# for runtime analysis

print("-------------------------------------------------------------------------------------------")

corr_coeff, p_val, significant = determine_correlation(sum_of_max_fault_paths_and_dev, df["max_runtime (s)"])
print("sum_of_max_fault_paths_and_dev --- max_runtime:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(sum_of_avg_fault_paths_and_dev, df["max_runtime (s)"])
print("sum_of_avg_fault_paths_and_dev --- max_runtime:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_num_fault_paths"], df["avg_fault_path_len"])
print("avg_num_fault_paths --- avg_fault_path_len:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

# more

print("-------------------------------------------------------------------------------------------")

corr_coeff, p_val, significant = determine_correlation(df["avg_f1"], num_classifications)
print("F1 --- num_classifications:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_f1"], df["avg_ratio_of_found_gtfp"])
print("F1 --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_f1"], anomaly_link_perc_scores)
print("F1 --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_f1"], df["avg_ratio_found_anomalies"])
print("F1 --- anomaly scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_f1"], df["gt_match_perc"])
print("F1 --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(all_missed_anomalies, anomaly_link_perc_scores)
print("all_missed_anomalies --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(missed_anomalies_unclassified, anomaly_link_perc_scores)
print("missed_anomalies_unclassified --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(miss_due_to_class_iss, anomaly_link_perc_scores)
print("miss_due_to_class_iss --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(all_missed_anomalies, df["avg_ratio_found_anomalies"])
print("all_missed_anomalies --- avg_ratio_found_anomalies:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(missed_anomalies_unclassified, df["avg_ratio_found_anomalies"])
print("missed_anomalies_unclassified --- avg_ratio_found_anomalies:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(miss_due_to_class_iss, df["avg_ratio_found_anomalies"])
print("miss_due_to_class_iss --- avg_ratio_found_anomalies:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(all_missed_anomalies, df["avg_ratio_of_found_gtfp"])
print("all_missed_anomalies --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(missed_anomalies_unclassified, df["avg_ratio_of_found_gtfp"])
print("missed_anomalies_unclassified --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(miss_due_to_class_iss, df["avg_ratio_of_found_gtfp"])
print("miss_due_to_class_iss --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_ratio, compensation_ano_link)
print("anomaly_perc_aff_by_ratio --- compensation_ano_link:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# model acc

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], anomaly_link_perc_scores)
print("avg_model_acc --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["avg_ratio_of_found_gtfp"])
print("avg_model_acc --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["gt_match_perc"])
print("avg_model_acc --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["diag_success_percentage"])
print("avg_model_acc --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["fp_dev_mean"])
print("avg_model_acc --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_model_acc"], df["fp_dev_max"])
print("avg_model_acc --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# affected by

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, anomaly_link_perc_scores)
print("affected_by_percentages --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_ratio_found_anomalies"])
print("affected_by_percentages --- avg_ratio_found_anomalies:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_ratio_of_found_gtfp"])
print("affected_by_percentages --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["gt_match_perc"])
print("affected_by_percentages --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["diag_success_percentage"])
print("affected_by_percentages --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["fp_dev_mean"])
print("affected_by_percentages --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["fp_dev_max"])
print("affected_by_percentages --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# alpha / gamma

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, anomaly_link_perc_scores)
print("anomaly_perc_model_acc_ratio --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["avg_ratio_found_anomalies"])
print("anomaly_perc_model_acc_ratio --- avg_ratio_found_anomalies:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["avg_ratio_of_found_gtfp"])
print("anomaly_perc_model_acc_ratio --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["gt_match_perc"])
print("anomaly_perc_model_acc_ratio --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["diag_success_percentage"])
print("anomaly_perc_model_acc_ratio --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["fp_dev_mean"])
print("anomaly_perc_model_acc_ratio --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_model_acc_ratio, df["fp_dev_max"])
print("anomaly_perc_model_acc_ratio --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# alpha

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, anomaly_link_perc_scores)
print("anomaly_percentages --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["avg_ratio_of_found_gtfp"])
print("anomaly_percentages --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["gt_match_perc"])
print("anomaly_percentages --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["diag_success_percentage"])
print("anomaly_percentages --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["fp_dev_mean"])
print("anomaly_percentages --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["fp_dev_max"])
print("anomaly_percentages --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# gamma / beta

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, anomaly_link_perc_scores)
print("model_acc_connectivity_ratio --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, df["avg_ratio_of_found_gtfp"])
print("model_acc_connectivity_ratio --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, df["gt_match_perc"])
print("model_acc_connectivity_ratio --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, df["diag_success_percentage"])
print("model_acc_connectivity_ratio --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, df["fp_dev_mean"])
print("model_acc_connectivity_ratio --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(model_acc_connectivity_ratio, df["fp_dev_max"])
print("model_acc_connectivity_ratio --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# n_c / gamma

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, anomaly_link_perc_scores)
print("num_classifications_model_acc_ratio --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio,
                                                       df["avg_ratio_of_found_gtfp"])
print("num_classifications_model_acc_ratio --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, df["gt_match_perc"])
print("num_classifications_model_acc_ratio --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio,
                                                       df["diag_success_percentage"])
print("num_classifications_model_acc_ratio --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, df["fp_dev_mean"])
print("num_classifications_model_acc_ratio --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications_model_acc_ratio, df["fp_dev_max"])
print("num_classifications_model_acc_ratio --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# n_c

corr_coeff, p_val, significant = determine_correlation(num_classifications, anomaly_link_perc_scores)
print("num_classifications --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications, df["avg_ratio_of_found_gtfp"])
print("num_classifications --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications, df["gt_match_perc"])
print("num_classifications --- gt_match_perc:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications, df["diag_success_percentage"])
print("num_classifications --- diag_success_percentage:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications, df["fp_dev_mean"])
print("num_classifications --- fp_dev_mean:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(num_classifications, df["fp_dev_max"])
print("num_classifications --- fp_dev_max:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# complicated plot

corr_coeff, p_val, significant = determine_correlation(df["avg_ratio_of_found_gtfp"], anomaly_link_perc_scores)
print("avg_ratio_of_found_gtfp --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, compensation_ano_link)
print("anomaly_perc_aff_by_prod --- compensation_ano_link:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, anomaly_link_perc_scores)
print("anomaly_perc_aff_by_prod --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, df["avg_ratio_of_found_gtfp"])
print("anomaly_perc_aff_by_prod --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(compensation_gtfp, compensation_ano_link)
print("compensation_gtfp --- compensation_ano_link:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, compensation_gtfp)
print("anomaly_perc_aff_by_prod --- compensation_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# complicated plot -- ratio

corr_coeff, p_val, significant = determine_correlation(df["avg_ratio_of_found_gtfp"], anomaly_link_perc_scores)
print("avg_ratio_of_found_gtfp --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_ratio, compensation_ano_link)
print("anomaly_perc_aff_by_ratio --- compensation_ano_link:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_ratio, anomaly_link_perc_scores)
print("anomaly_perc_aff_by_ratio --- anomaly_link_perc_scores:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_ratio, df["avg_ratio_of_found_gtfp"])
print("anomaly_perc_aff_by_ratio --- avg_ratio_of_found_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(compensation_gtfp, compensation_ano_link)
print("compensation_gtfp --- compensation_ano_link:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_ratio, compensation_gtfp)
print("anomaly_perc_aff_by_ratio --- compensation_gtfp:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# num of fault paths / fault path length

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_num_fault_paths"])
print("affected_by_percentages --- avg_num_fault_paths:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_num_fault_paths"], df["avg_fault_path_len"])
print("avg_num_fault_paths --- avg_fault_path_len:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["avg_num_fault_paths"])
print("anomaly_percentages --- avg_num_fault_paths:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_percentages, df["avg_fault_path_len"])
print("anomaly_percentages --- avg_fault_path_len:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, df["avg_num_fault_paths"])
print("anomaly_perc_aff_by_prod --- avg_num_fault_paths:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(anomaly_perc_aff_by_prod, df["avg_fault_path_len"])
print("anomaly_perc_aff_by_prod --- avg_fault_path_len:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# compensation

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_compensation_by_aff_by_savior"])
print("affected_by_percentages --- avg_compensation_by_aff_by_savior:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_fn"], df["avg_compensation_by_aff_by_savior"])
print("FN --- avg_compensation_by_aff_by_savior:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_missed_chances"])
print("affected_by_percentages --- avg_missed_chances:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(affected_by_percentages, df["avg_no_second_chance"])
print("affected_by_percentages --- avg_no_second_chance:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(df["avg_ratio_of_found_gtfp"], df["avg_missed_chances"])
print("avg_ratio_of_found_gtfp --- avg_missed_chances:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# misc

potentially_missed = [
    all_missed_anomalies[i] + df["avg_compensation_by_aff_by_savior"][i] for i in range(len(all_missed_anomalies))
]

corr_coeff, p_val, significant = determine_correlation(df["avg_compensation_by_aff_by_savior"], potentially_missed)
print("avg_compensation_by_aff_by_savior --- potentially_missed:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

# all filtered based on alpha=0.2
beta_filtered = [affected_by_percentages[i] for i in range(len(affected_by_percentages)) if
                 anomaly_percentages[i] == 20]
compensation_filtered = [df["avg_compensation_by_aff_by_savior"][i] for i in
                         range(len(df["avg_compensation_by_aff_by_savior"])) if anomaly_percentages[i] == 20]
# would be interesting to consider beta vs. potential for misclassifications (for alpha = 0.2)
pot_misclassifications_filtered = [potential_for_misclassification[i] for i in
                                   range(len(potential_for_misclassification)) if anomaly_percentages[i] == 20]
misclassifications_filtered = [avg_misclassifications[i] for i in range(len(avg_misclassifications)) if
                               anomaly_percentages[i] == 20 and df["avg_model_acc"][i] <= 0.95]
beta_filtered_more = [affected_by_percentages[i] for i in range(len(affected_by_percentages)) if
                      anomaly_percentages[i] == 20 and df["avg_model_acc"][i] <= 0.95]

corr_coeff, p_val, significant = determine_correlation(beta_filtered, compensation_filtered)
print("beta_filtered --- compensation_filtered:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(beta_filtered, pot_misclassifications_filtered)
print("beta_filtered --- pot_misclassifications_filtered:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

corr_coeff, p_val, significant = determine_correlation(beta_filtered_more, misclassifications_filtered)
print("beta_filtered_more --- misclassifications_filtered:")
print("\tcorr. coeff.:", corr_coeff, "p-val:", p_val, "significant:", significant)

print("-------------------------------------------------------------------------------------------")

# averages of performance metrics

avg_F1 = round(df["avg_f1"].describe()["mean"], 2)
avg_p0 = round(df["avg_ano_link_perc"].describe()["mean"], 2)
avg_p1 = round(df["avg_ratio_of_found_gtfp"].describe()["mean"], 2)
avg_p2 = round(df["gt_match_perc"].describe()["mean"], 2)
print(avg_F1)
print(avg_p0)
print(avg_p1)
print(avg_p2)
