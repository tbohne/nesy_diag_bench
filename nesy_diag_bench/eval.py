#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import csv
import glob
import json
import logging
import os

import numpy as np
import requests
import smach
import tensorflow as tf
from nesy_diag_smach.nesy_diag_state_machine import NeuroSymbolicDiagnosisStateMachine
from termcolor import colored

from config import UPDATE_ENDPOINT, DATA_ENDPOINT, SESSION_DIR, SIM_CLASSIFICATION_LOG_FILE
from local_data_accessor import LocalDataAccessor
from local_data_provider import LocalDataProvider
from local_model_accessor import LocalModelAccessor
from util import log_info, log_debug, log_warn, log_err


def run_smach(instance, verbose, sim_models, seed):
    smach.set_loggers(log_info, log_debug, log_warn, log_err)  # set custom logging functions

    # init local implementations of I/O interfaces
    data_acc = LocalDataAccessor(instance)
    model_acc = LocalModelAccessor(instance)
    data_prov = LocalDataProvider()

    sm = NeuroSymbolicDiagnosisStateMachine(
        data_acc, model_acc, data_prov, verbose=verbose, sim_models=sim_models, seed=seed
    )
    tf.get_logger().setLevel(logging.ERROR)
    sm.execute()
    final_out = sm.userdata.final_output
    if verbose:
        print("final output of smach execution (fault path(s)):", final_out)
    return final_out


def clear_hosted_kg():
    clear_query = """
        PREFIX rdfs: <http://www.w3.org/2000/01-rdf-syntax-ns#>
        DELETE WHERE {
            ?s ?p ?o .
        }
    """
    resp = requests.post(UPDATE_ENDPOINT, data={"update": clear_query})
    if resp.status_code == 200:
        print("dataset successfully cleared..")
        return True
    else:
        print("failed to clear dataset..")
        return False


def upload_kg_for_instance(instance):
    # upload new KG file (.nt)
    kg_file = instance.replace(".json", ".nt")
    with open(kg_file, "r") as f:
        resp = requests.post(DATA_ENDPOINT, data=f, headers={"Content-Type": "application/n-triples"})
    if resp.status_code == 200:
        print("kg successfully uploaded")
        return True
    else:
        print("failed to upload kg", resp.text)
        return False


def get_causal_links_from_fault_paths(fault_paths):
    links = []
    for fp in fault_paths:
        for i in range(len(fp) - 1):
            links.append(fp[i] + "->" + fp[i + 1])
    return links


def write_instance_res_to_csv(
        instance, tp, tn, fp, fn, num_of_fp_deviation, accuracy, precision, recall, specificity, f1,
        found_anomaly_links_percentage, avg_model_acc, gt_match, num_fps, avg_fp_len
):
    instance = instance.split("/")[1].replace(".json", "")
    idx_suffix = "_" + instance.split("_")[-1]
    filename = instance[:len(instance) - len(idx_suffix)] + ".csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(
                ["instance", "TP", "TN", "FP", "FN", "#fp_dev", "acc", "prec", "rec", "spec", "F1", "ano_link_perc",
                 "avg_model_acc", "gt_match", "#fault_paths", "avg_fp_len"]
            )
        writer.writerow([instance, tp, tn, fp, fn, num_of_fp_deviation, accuracy, precision, recall, specificity, f1,
                         found_anomaly_links_percentage, avg_model_acc, gt_match, num_fps, avg_fp_len])


def evaluate_instance_res(instance, ground_truth_fault_paths, determined_fault_paths):
    true_positives = []
    false_positives = []
    true_negatives = []
    false_negatives = []
    num_of_fp_deviation = abs(len(ground_truth_fault_paths) - len(determined_fault_paths))

    causal_links_pred = get_causal_links_from_fault_paths(determined_fault_paths)
    causal_links_ground_truth = get_causal_links_from_fault_paths(ground_truth_fault_paths)

    model_accuracies = []

    identified_causal_links = 0
    for link in causal_links_ground_truth:
        if link in causal_links_pred:
            identified_causal_links += 1

    # read sim classification log
    with open(SESSION_DIR + "/" + SIM_CLASSIFICATION_LOG_FILE, "r") as f:
        log_file = json.load(f)
        for classification in log_file:
            comp = list(classification.keys())[0]
            pred_anomaly = classification[comp]
            model_acc = round(classification["Model Accuracy"], 2)
            model_accuracies.append(model_acc)
            pred_val = classification["Predicted Value"]
            ground_truth_anomaly = classification["Ground Truth Anomaly"]
            print("--", comp, "pred:", pred_anomaly, "model acc:", model_acc, "pred val:", round(pred_val, 2),
                  "gt:", ground_truth_anomaly)

            if pred_anomaly == ground_truth_anomaly:  # true
                if pred_anomaly:
                    true_positives.append(comp)
                else:
                    true_negatives.append(comp)
            else:  # false
                if pred_anomaly:
                    false_positives.append(comp)
                else:
                    false_negatives.append(comp)

    tp = len(true_positives)
    tn = len(true_negatives)
    fp = len(false_positives)
    fn = len(false_negatives)
    print("---- confusion matrix ----")
    print("TP:", tp)
    print("TN:", tn)
    print("FP:", fp)
    print("FN (unidentified anomalies):", fn)
    print("--------")
    print("num of fault path deviation:", num_of_fp_deviation)
    # ratio of correct prediction to all predictions
    accuracy = round((float(tp + tn)) / (tp + tn + fp + fn), 2)
    # ratio of true pos to all pos
    precision = round(float(tp) / (tp + fp), 2)
    print("accuracy:", accuracy)
    print("precision:", precision)
    # how well are we able to recall the problems
    recall = round((float(tp) / (tp + fn)), 2)
    print("recall aka sensitivity:", recall)
    # ratio of true neg to all neg
    specificity = round(float(tn) / (fp + tn), 2)
    print("specificity:", specificity)
    f1 = round((2 * precision * recall) / (precision + recall), 2)
    print("f1-score:", f1)
    if identified_causal_links == len(causal_links_ground_truth):
        found_anomaly_links_percentage = 100.0
    else:
        found_anomaly_links_percentage = float(identified_causal_links) / len(causal_links_ground_truth)
    print("percentage of correctly identified causal links between anomalies:", found_anomaly_links_percentage, "%")

    gt_match = len(ground_truth_fault_paths) == len(determined_fault_paths) and all(
        gtfp in determined_fault_paths for gtfp in ground_truth_fault_paths)
    if gt_match:
        print("..gen fault paths for", instance, "match ground truth..")

    num_fps = len(ground_truth_fault_paths)
    avg_fp_len = round(np.average([len(fp) for fp in ground_truth_fault_paths]), 2)

    write_instance_res_to_csv(
        instance, tp, tn, fp, fn, num_of_fp_deviation, accuracy, precision, recall, specificity, f1,
        found_anomaly_links_percentage, round(np.average(model_accuracies), 2), gt_match, num_fps, avg_fp_len
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Systematically evaluate NeSy diag system with generated instances.')
    parser.add_argument('--instances', type=str, required=True)
    parser.add_argument('--v', action='store_true', default=False)
    parser.add_argument('--sim', action='store_true', default=False)
    args = parser.parse_args()

    for instance in glob.glob(args.instances + "/*.json"):
        print("working on instance:", instance)
        assert clear_hosted_kg()
        assert upload_kg_for_instance(instance)
        seed = instance.split("_")[-2]
        fault_paths = run_smach(instance, args.v, args.sim, seed)

        # compare to ground truth
        with open(instance, "r") as f:
            problem_instance = json.load(f)

        ground_truth_fault_paths = problem_instance["ground_truth_fault_paths"]
        determined_fault_paths = [path.split(" -> ") for path in fault_paths]
        if args.v:
            print("#####################################################################")
            print("GROUND TRUTH FAULT PATHS:", ground_truth_fault_paths)
            print("DETERMINED FAULT PATHS:", determined_fault_paths)
            print("#####################################################################")

        evaluate_instance_res(instance, ground_truth_fault_paths, determined_fault_paths)

        if args.v:
            for fault_path in fault_paths:
                print(colored(fault_path, "red", "on_white", ["bold"]))
