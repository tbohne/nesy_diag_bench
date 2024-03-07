#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import csv
import glob
import os

import pandas as pd


def write_instance_set_res_to_csv(
        instance_set_sol, num_of_instances, avg_tp, avg_tn, avg_fp, avg_fn, fp_dev_mean, fp_dev_max, avg_accuracy,
        avg_prec, avg_rec, avg_spec, avg_f1, avg_ano_link_percentage, avg_model_acc, gt_match_percentage,
        avg_num_fault_paths, max_num_fault_paths, avg_fault_path_len, max_fault_path_len, filename, avg_runtime,
        avg_classification_ratio, avg_ratio_of_found_gtfp
):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(
                ["instance_set", "num_instances", "avg_tp", "avg_tn", "avg_fp", "avg_fn", "fp_dev_mean", "fp_dev_max",
                 "avg_acc", "avg_prec", "avg_rec", "avg_spec", "avg_f1", "avg_ano_link_perc", "avg_model_acc",
                 "gt_match_perc", "avg_ratio_of_found_gtfp", "avg_num_fault_paths", "max_num_fault_paths",
                 "avg_fault_path_len", "max_fault_path_len", "avg_runtime (s)", "avg_classification_ratio"]
            )
        instance_set_sol = instance_set_sol.split("/")[1].replace(".csv", "")
        writer.writerow([instance_set_sol, num_of_instances, avg_tp, avg_tn, avg_fp, avg_fn, fp_dev_mean, fp_dev_max,
                         avg_accuracy, avg_prec, avg_rec, avg_spec, avg_f1, avg_ano_link_percentage, avg_model_acc,
                         gt_match_percentage, avg_ratio_of_found_gtfp, avg_num_fault_paths, max_num_fault_paths,
                         avg_fault_path_len, max_fault_path_len, avg_runtime, avg_classification_ratio])


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
        avg_accuracy = round(df["acc"].describe()["mean"], 2)
        avg_prec = round(df["prec"].describe()["mean"], 2)
        avg_rec = round(df["rec"].describe()["mean"], 2)
        avg_spec = round(df["spec"].describe()["mean"], 2)
        avg_f1 = round(df["F1"].describe()["mean"], 2)
        avg_ano_link_percentage = round(df["ano_link_perc"].describe()["mean"], 2)
        avg_model_acc = round(df["avg_model_acc"].describe()["mean"], 2)

        top_class = df["gt_match"].describe()["top"]
        top_freq = df["gt_match"].describe()["freq"]
        gt_match_percentage = top_freq if top_class else 100 - top_freq

        avg_num_fault_paths = round(df["#fault_paths"].describe()["mean"], 2)
        max_num_fault_paths = df["#fault_paths"].describe()["max"]
        avg_fault_path_len = round(df["avg_fp_len"].describe()["mean"], 2)
        max_fault_path_len = df["avg_fp_len"].describe()["max"]

        avg_runtime = round(df["runtime (s)"].describe()["mean"], 2)
        avg_classification_ratio = round(df["classification_ratio"].describe()["mean"], 2)
        avg_ratio_of_found_gtfp = round(df["ratio_of_found_gtfp"].describe()["mean"], 2)

        write_instance_set_res_to_csv(
            instance_set_sol, num_of_instances, avg_tp, avg_tn, avg_fp, avg_fn, fp_dev_mean, fp_dev_max, avg_accuracy,
            avg_prec, avg_rec, avg_spec, avg_f1, avg_ano_link_percentage, avg_model_acc, gt_match_percentage,
            avg_num_fault_paths, max_num_fault_paths, avg_fault_path_len, max_fault_path_len, filename, avg_runtime,
            avg_classification_ratio, avg_ratio_of_found_gtfp
        )
