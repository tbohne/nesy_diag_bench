#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import csv
import glob
import os

import pandas as pd


def write_instance_set_res_to_csv(
        instance_set_sol: str, num_of_instances: int, avg_tp: float, avg_tn: float, avg_fp: float, avg_fn: float,
        fp_dev_mean: float, fp_dev_max: float, avg_accuracy: float, avg_prec: float, avg_rec: float, avg_spec: float,
        avg_f1: float, avg_ano_link_percentage: float, avg_model_acc: float, gt_match_percentage: float,
        avg_num_fault_paths: float, max_num_fault_paths: float, avg_fault_path_len: float, max_fault_path_len: float,
        filename: str, avg_runtime: float, avg_classification_ratio: float, avg_ratio_of_found_gtfp: float,
        diag_success_percentage: float, median_runtime: float, median_num_fault_paths: float,
        median_fault_path_len: float, max_runtime: float, avg_compensation_by_aff_by_savior: float,
        avg_missed_chances: float, avg_no_second_chance: float, fp_dev_min: float, avg_ratio_found_anomalies: float
) -> None:
    """
    Writes the results for the specified instance set to csv file.

    :param instance_set_sol: solution file for instance set
    :param num_of_instances: number of instances part of the set
    :param avg_tp: average number of true positives
    :param avg_tn: average number of true negatives
    :param avg_fp: average number of false positives
    :param avg_fn: average number of false negatives
    :param fp_dev_mean: mean of fault path deviations
    :param fp_dev_max: max of fault path deviations
    :param avg_accuracy: average prediction accuracy
    :param avg_prec: average prediction precision
    :param avg_rec: average prediction recall
    :param avg_spec: average prediction specificity
    :param avg_f1: average F1 score
    :param avg_ano_link_percentage: average anomaly link percentage
    :param avg_model_acc: average model accuracy
    :param gt_match_percentage: ground truth match percentage
    :param avg_num_fault_paths: average number of fault paths
    :param max_num_fault_paths: maximum number of fault paths
    :param avg_fault_path_len: average fault path length
    :param max_fault_path_len: maximum fault path length
    :param filename: name of the csv file
    :param avg_runtime: average runtime
    :param avg_classification_ratio: average classification ratio
    :param avg_ratio_of_found_gtfp: average ratio of found ground truth fault paths
    :param diag_success_percentage: diagnosis success percentage
    :param median_runtime: median runtime
    :param median_num_fault_paths: median number of fault paths
    :param median_fault_path_len: median fault path length
    :param max_runtime: maximum runtime
    :param avg_compensation_by_aff_by_savior: average compensation by affected-by savior
    :param avg_missed_chances: average missed chances
    :param avg_no_second_chance: average 'no second chance' cases
    :param fp_dev_min: minimum fault path deviations
    :param avg_ratio_found_anomalies: average ratio of found anomalies
    """
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(
                ["instance_set", "num_instances", "avg_tp", "avg_tn", "avg_fp", "avg_fn", "fp_dev_mean", "fp_dev_max",
                 "avg_acc", "avg_prec", "avg_rec", "avg_spec", "avg_f1", "avg_ano_link_perc", "avg_model_acc",
                 "gt_match_perc", "avg_ratio_of_found_gtfp", "avg_num_fault_paths", "max_num_fault_paths",
                 "avg_fault_path_len", "max_fault_path_len", "avg_runtime (s)", "avg_classification_ratio",
                 "diag_success_percentage", "median_runtime (s)", "median_num_fault_paths", "median_fault_path_len",
                 "max_runtime (s)", "avg_compensation_by_aff_by_savior", "avg_missed_chances", "avg_no_second_chance",
                 "fp_dev_min", "avg_ratio_found_anomalies"]
            )
        instance_set_sol = instance_set_sol.split("/")[1].replace(".csv", "")
        writer.writerow(
            [instance_set_sol, num_of_instances, avg_tp, avg_tn, avg_fp, avg_fn, fp_dev_mean, fp_dev_max, avg_accuracy,
             avg_prec, avg_rec, avg_spec, avg_f1, avg_ano_link_percentage, avg_model_acc, gt_match_percentage,
             avg_ratio_of_found_gtfp, avg_num_fault_paths, max_num_fault_paths, avg_fault_path_len, max_fault_path_len,
             avg_runtime, avg_classification_ratio, diag_success_percentage, median_runtime, median_num_fault_paths,
             median_fault_path_len, max_runtime, avg_compensation_by_aff_by_savior, avg_missed_chances,
             avg_no_second_chance, fp_dev_min, avg_ratio_found_anomalies]
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze results and generate cumulated results file.')
    parser.add_argument('--instance-set-sol', type=str, required=True)
    filename = "cumulative_res.csv"
    args = parser.parse_args()

    for instance_set_sol in glob.glob(args.instance_set_sol + "/*.csv"):
        print("working on instance set:", instance_set_sol)
        df = pd.read_csv(instance_set_sol)
        num_of_instances = df.count()["instance"]
        avg_tp = round(df["TP"].describe()["mean"], 2)
        avg_tn = round(df["TN"].describe()["mean"], 2)
        avg_fp = round(df["FP"].describe()["mean"], 2)
        avg_fn = round(df["FN"].describe()["mean"], 2)
        fp_dev_mean = round(df["#fp_dev"].describe()["mean"], 2)
        fp_dev_max = df["#fp_dev"].describe()["max"]
        fp_dev_min = df["#fp_dev"].describe()["min"]
        avg_accuracy = round(df["acc"].describe()["mean"], 2)
        avg_prec = round(df["prec"].describe()["mean"], 2)
        avg_rec = round(df["rec"].describe()["mean"], 2)
        avg_spec = round(df["spec"].describe()["mean"], 2)
        avg_f1 = round(df["F1"].describe()["mean"], 2)
        avg_ano_link_percentage = round(df["ano_link_perc"].describe()["mean"], 2)
        avg_model_acc = round(df["avg_model_acc"].describe()["mean"], 2)

        top_class_gt_match = df["gt_match"].describe()["top"]
        top_freq_gt_match = df["gt_match"].describe()["freq"]
        gt_match_percentage = top_freq_gt_match if top_class_gt_match else 100 - top_freq_gt_match

        top_class_diag_success = df["diag_success"].describe()["top"]
        top_freq_diag_success = df["diag_success"].describe()["freq"]
        diag_success_percentage = top_freq_diag_success if top_class_diag_success else 100 - top_freq_diag_success

        avg_num_fault_paths = round(df["#fault_paths"].describe()["mean"], 2)
        median_num_fault_paths = round(df["#fault_paths"].median(), 2)
        max_num_fault_paths = df["#fault_paths"].describe()["max"]
        avg_fault_path_len = round(df["avg_fp_len"].describe()["mean"], 2)
        median_fault_path_len = round(df["avg_fp_len"].median(), 2)
        max_fault_path_len = df["avg_fp_len"].describe()["max"]

        avg_runtime = round(df["runtime (s)"].describe()["mean"], 2)
        median_runtime = round(df["runtime (s)"].median(), 2)
        max_runtime = round(df["runtime (s)"].describe()["max"], 2)

        avg_classification_ratio = round(df["classification_ratio"].describe()["mean"], 2)
        avg_ratio_of_found_gtfp = round(df["ratio_of_found_gtfp"].describe()["mean"], 2)

        avg_compensation_by_aff_by_savior = round(df["compensation_by_aff_by_savior"].describe()["mean"], 2)
        avg_missed_chances = round(df["missed_chances"].describe()["mean"], 2)
        avg_no_second_chance = round(df["no_second_chance"].describe()["mean"], 2)

        components = int(instance_set_sol.split("/")[1].split("_")[0])
        alpha = int(instance_set_sol.split("/")[1].split("_")[1])
        num_anomalies = round(components * (alpha / 100.0))  # same rounding is applied in instance gen
        avg_missed_anomalies = num_anomalies - avg_tp
        avg_ratio_found_anomalies = round(float(num_anomalies - avg_missed_anomalies) / num_anomalies, 2)

        write_instance_set_res_to_csv(
            instance_set_sol, num_of_instances, avg_tp, avg_tn, avg_fp, avg_fn, fp_dev_mean, fp_dev_max, avg_accuracy,
            avg_prec, avg_rec, avg_spec, avg_f1, avg_ano_link_percentage, avg_model_acc, gt_match_percentage,
            avg_num_fault_paths, max_num_fault_paths, avg_fault_path_len, max_fault_path_len, filename, avg_runtime,
            avg_classification_ratio, avg_ratio_of_found_gtfp, diag_success_percentage, median_runtime,
            median_num_fault_paths, median_fault_path_len, max_runtime, avg_compensation_by_aff_by_savior,
            avg_missed_chances, avg_no_second_chance, fp_dev_min, avg_ratio_found_anomalies
        )
