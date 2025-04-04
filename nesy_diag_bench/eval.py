#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import csv
import glob
import json
import logging
import os
import time
from typing import List, Tuple

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


def run_smach(instance: str, verbose: bool, sim_models: bool, seed: int) -> str:
    """
    Runs the diagnosis state machine.

    :param instance: problem instance file
    :param verbose: whether logging should be activated
    :param sim_models: whether model simulation should be activated
    :param seed: seed for random processes
    :return: final output of the state machine, i.e., diagnosis
    """
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


def clear_hosted_kg() -> bool:
    """
    Clears the hosted knowledge graph.

    :return: whether KG was successfully cleared
    """
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


def upload_kg_for_instance(instance: str) -> bool:
    """
    Uploads KG (.nt) for the specified instance.

    :param instance: problem instance
    :return: whether KG was successfully uploaded
    """
    kg_file = instance.replace(".json", ".nt")
    with open(kg_file, "r") as f:
        resp = requests.post(DATA_ENDPOINT, data=f, headers={"Content-Type": "application/n-triples"})
    if resp.status_code == 200:
        print("kg successfully uploaded")
        return True
    else:
        print("failed to upload kg", resp.text)
        return False


def get_causal_links_from_fault_paths(fault_paths: List[List[str]]) -> List[str]:
    """
    Retrieves causal links from fault paths.

    :param fault_paths: fault paths to retrieve causal links for
    :return: causal links
    """
    links = []
    for fp in fault_paths:
        for i in range(len(fp) - 1):
            links.append(fp[i] + "->" + fp[i + 1])
    return links


def write_instance_res_to_csv(
        instance: str, tp: int, tn: int, fp: int, fn: int, num_of_fp_deviation: int, accuracy: float, precision: float,
        recall: float, specificity: float, f1: float, found_anomaly_links_percentage: float, avg_model_acc: float,
        gt_match: bool, num_fps: int, avg_fp_len: float, runtime: float, classification_ratio: float,
        ratio_of_found_gtfp: float, diag_success: bool, compensation_by_aff_by_savior: int, missed_chances: int,
        no_second_chance: int
) -> None:
    """
    Writes the results for the instance to csv file.

    :param instance: problem instance file
    :param tp: number of true positives
    :param tn: number of true negatives
    :param fp: number of false positives
    :param fn: number of false negatives
    :param num_of_fp_deviation: number of fault path deviations
    :param accuracy: classification accuracy
    :param precision: classification precision
    :param recall: classification recall
    :param specificity: classification specificity
    :param f1: F1 score
    :param found_anomaly_links_percentage: found anomaly links percentage
    :param avg_model_acc: average model accuracy
    :param gt_match: whether the result matches the ground truth
    :param num_fps: number of fault paths
    :param avg_fp_len: average fault path length
    :param runtime: runtime
    :param classification_ratio: classification ratio
    :param ratio_of_found_gtfp: ratio of found ground truth fault paths
    :param diag_success: diagnosis success
    :param compensation_by_aff_by_savior: compensation by affected-by savior
    :param missed_chances: number of missed chances
    :param no_second_chance: 'no second chance' cases
    """
    instance = instance.split("/")[1].replace(".json", "")
    idx_suffix = "_" + instance.split("_")[-1]
    filename = instance[:len(instance) - len(idx_suffix)] + ".csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(
                ["instance", "TP", "TN", "FP", "FN", "#fp_dev", "acc", "prec", "rec", "spec", "F1", "ano_link_perc",
                 "avg_model_acc", "gt_match", "#fault_paths", "ratio_of_found_gtfp", "avg_fp_len", "runtime (s)",
                 "classification_ratio", "diag_success", "compensation_by_aff_by_savior", "missed_chances",
                 "no_second_chance"]
            )
        writer.writerow(
            [instance, tp, tn, fp, fn, num_of_fp_deviation, accuracy, precision, recall, specificity, f1,
             found_anomaly_links_percentage, avg_model_acc, gt_match, num_fps, ratio_of_found_gtfp, avg_fp_len, runtime,
             classification_ratio, diag_success, compensation_by_aff_by_savior, missed_chances, no_second_chance]
        )


def evaluate_instance_res(
        instance: str, ground_truth_fault_paths: List[List[str]], determined_fault_paths: List[List[str]],
        runtime: float, diag_success: bool
) -> None:
    """
    Evaluates the instance-level results.

    :param instance: problem instance file
    :param ground_truth_fault_paths: ground truth fault paths
    :param determined_fault_paths: determined fault paths
    :param runtime: runtime
    :param diag_success: whether diagnosis successful
    """
    true_positives = []
    false_positives = []
    true_negatives = []
    false_negatives = []
    num_of_fp_deviation = abs(len(ground_truth_fault_paths) - len(determined_fault_paths))

    matched_gtfp = 0
    for fp in determined_fault_paths:
        if fp in ground_truth_fault_paths:
            matched_gtfp += 1
    ratio_of_found_gtfp = round(float(matched_gtfp) / len(ground_truth_fault_paths), 2)

    causal_links_pred = get_causal_links_from_fault_paths(determined_fault_paths)
    causal_links_ground_truth = get_causal_links_from_fault_paths(ground_truth_fault_paths)

    model_accuracies = []

    identified_causal_links = 0
    for link in causal_links_ground_truth:
        if link in causal_links_pred:
            identified_causal_links += 1

    with open(SESSION_DIR + "/" + SIM_CLASSIFICATION_LOG_FILE, "r") as f:  # read sim classification log
        log_file = json.load(f)
        for classification in log_file:
            comp = list(classification.keys())[0]
            pred_anomaly = classification[comp]
            model_acc = round(classification["Model Accuracy"], 2)
            model_accuracies.append(model_acc)
            pred_val = classification["Predicted Value"]
            ground_truth_anomaly = classification["Ground Truth Anomaly"]
            print(
                "--", comp, "pred:", pred_anomaly, "model acc:", model_acc, "pred val:",
                round(pred_val, 2), "gt:", ground_truth_anomaly
            )
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
    accuracy = round((float(tp + tn)) / (tp + tn + fp + fn), 2)  # ratio of correct prediction to all predictions
    precision = round(float(tp) / (tp + fp), 2) if tp + fp > 0 else "NaN"  # ratio of true pos to all pos
    print("accuracy:", accuracy)
    print("precision:", precision)
    recall = round((float(tp) / (tp + fn)), 2)  # how well are we able to recall the problems
    print("recall aka sensitivity:", recall)
    specificity = round(float(tn) / (fp + tn), 2)  # ratio of true neg to all neg
    print("specificity:", specificity)
    prec_rec_sum = precision + recall
    f1 = round((2 * precision * recall) / prec_rec_sum, 2) if precision != "NaN" and prec_rec_sum > 0 else "NaN"
    print("f1-score:", f1)
    if identified_causal_links == len(causal_links_ground_truth):
        found_anomaly_links_percentage = 100.0
    else:
        found_anomaly_links_percentage = round(
            (float(identified_causal_links) / len(causal_links_ground_truth)) * 100.0, 2
        )
    print("percentage of correctly identified causal links between anomalies:", found_anomaly_links_percentage, "%")

    gt_match = len(ground_truth_fault_paths) == len(determined_fault_paths) and all(
        gtfp in determined_fault_paths for gtfp in ground_truth_fault_paths
    )
    if gt_match:
        print("..gen fault paths for", instance, "match ground truth..")

    num_fps = len(ground_truth_fault_paths)
    avg_fp_len = round(np.average([len(fp) for fp in ground_truth_fault_paths]), 2)

    # ratio of classified components to all components
    classification_ratio = round(float(tp + fp + tn + fn) / float(instance.split("/")[1].split("_")[0]), 2)

    compensation_by_aff_by_savior, missed_chances, no_second_chance = measure_compensation(tp, tn, fp, fn)

    write_instance_res_to_csv(
        instance, tp, tn, fp, fn, num_of_fp_deviation, accuracy, precision, recall, specificity, f1,
        found_anomaly_links_percentage, round(np.average(model_accuracies), 2), gt_match, num_fps, avg_fp_len, runtime,
        classification_ratio, ratio_of_found_gtfp, diag_success, compensation_by_aff_by_savior, missed_chances,
        no_second_chance
    )


def measure_compensation(tp: int, tn: int, fp: int, fn: int) -> Tuple[int, int, int]:
    """
    Measures the three types of compensation (cf. paper for definitions):
        - compensation_by_aff_by_savior
        - missed_chances
        - no_second_chance

    :param tp: number of true positives
    :param tn: number of true negatives
    :param fp: number of false positives
    :param fn: number of false negatives
    :return: (compensation_by_aff_by_savior, missed_chances, no_second_chance)
    """
    with open(SESSION_DIR + "/" + "classifications.json", 'r') as file:
        classifications = json.load(file)
    classified_comps = {  # mapping component to classification res
        list(classifications[i].keys())[0]: classifications[i][list(classifications[i].keys())[0]]
        for i in range(len(classifications))
    }
    compensation_aff_by_savior = 0
    missed_chance = 0
    no_second_chance = 0
    already_saved = []

    for c in classified_comps:  # find FNs (+ TNs)
        pred = classified_comps[c]
        gt = ground_truth_components[c][0]
        if pred == False and gt == True:
            print(c, "is FN")
        elif pred == False and gt == False:
            print(c, "is TN")  # this case can actually never lead to any missed anomalies in the synth. instances
        if not pred:  # FN or TN -- go through affected-by relations of the negatively classified component
            print("going through aff-by for", c)
            for aff_by in ground_truth_components[c][1]:
                # if anomaly + not considered
                if ground_truth_components[aff_by][0]:  # and aff_by not in classified_comps
                    print(aff_by, "ground truth anomaly, i.e., unconsidered (via this link) anomaly")
                    if aff_by in classified_comps:  # found via another link?
                        print(aff_by, "classified via another link -- as", classified_comps[aff_by])
                        if aff_by not in already_saved:  # counting each comp only once
                            already_saved.append(aff_by)
                            # this measure should highly correlate with beta (aff-by) -- would indicate compensation (!)
                            compensation_aff_by_savior += 1
                            # what about following anomalies based on this entry, should they be counted as well?
                            # --> could be arbitrary many
                        else:
                            print("not counted again...")
                    else:  # missed anomaly
                        tmp_missed_chances = missed_chance
                        # not found, but would it have been possible?
                        # - another classification that was wrong
                        # - there would've been another component, an unused savior
                        for comp in ground_truth_components:
                            if comp not in classified_comps and aff_by in ground_truth_components[comp][1]:
                                print("there would've been a chance:", comp)
                                missed_chance += 1
                                break
                        if tmp_missed_chances == missed_chance:
                            no_second_chance += 1
    # some sanity checks
    assert compensation_aff_by_savior <= tn + fn
    return compensation_aff_by_savior, missed_chance, no_second_chance


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Systematically evaluate NeSy diag system with synth. instances.')
    parser.add_argument('--instances', type=str, required=True)
    parser.add_argument('--v', action='store_true', default=False)
    parser.add_argument('--sim', action='store_true', default=False)
    args = parser.parse_args()

    for instance in glob.glob(args.instances + "/*.json"):
        print("working on instance:", instance)
        start_time = time.time()
        assert clear_hosted_kg()
        assert upload_kg_for_instance(instance)
        seed = instance.split("_")[-2]
        fault_paths = run_smach(instance, args.v, args.sim, seed)

        # compare to ground truth
        with open(instance, "r") as f:
            problem_instance = json.load(f)
        ground_truth_fault_paths = problem_instance["ground_truth_fault_paths"]
        ground_truth_components = problem_instance["suspect_components"]
        diag_success = fault_paths != "no_diag"
        determined_fault_paths = [path.split(" -> ") for path in fault_paths] if diag_success else []

        if args.v:
            print("#####################################################################")
            print("GROUND TRUTH FAULT PATHS:", ground_truth_fault_paths)
            print("DETERMINED FAULT PATHS:", determined_fault_paths)
            print("#####################################################################")
        end_time = time.time()
        runtime = round(end_time - start_time, 2)
        evaluate_instance_res(instance, ground_truth_fault_paths, determined_fault_paths, runtime, diag_success)
        if args.v:
            for fault_path in fault_paths:
                print(colored(fault_path, "red", "on_white", ["bold"]))
