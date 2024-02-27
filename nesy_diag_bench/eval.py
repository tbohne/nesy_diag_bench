#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import glob
import json
import logging

import requests
import smach
import tensorflow as tf
from nesy_diag_smach.nesy_diag_state_machine import NeuroSymbolicDiagnosisStateMachine
from termcolor import colored

from config import UPDATE_ENDPOINT, DATA_ENDPOINT
from local_data_accessor import LocalDataAccessor
from local_data_provider import LocalDataProvider
from local_model_accessor import LocalModelAccessor
from util import log_info, log_debug, log_warn, log_err


def run_smach(instance, verbose):
    smach.set_loggers(log_info, log_debug, log_warn, log_err)  # set custom logging functions

    # init local implementations of I/O interfaces
    data_acc = LocalDataAccessor(instance)
    model_acc = LocalModelAccessor(instance)
    data_prov = LocalDataProvider()

    sm = NeuroSymbolicDiagnosisStateMachine(data_acc, model_acc, data_prov, verbose=verbose)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Systematically evaluate NeSy diag system with generated instances.')
    parser.add_argument('--instances', type=str, required=True)
    parser.add_argument('--v', action='store_true')
    args = parser.parse_args()

    for instance in glob.glob(args.instances + "/*.json"):
        print("working on instance:", instance)
        assert clear_hosted_kg()
        assert upload_kg_for_instance(instance)

        fault_paths = run_smach(instance, args.v)

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

        try:
            assert len(ground_truth_fault_paths) == len(fault_paths)
            assert all(gtfp in determined_fault_paths for gtfp in ground_truth_fault_paths)
            print("..gen fault paths for", instance, "match ground truth..")
        except AssertionError as e:
            print("GROUND TRUTH FAULT PATHS:", ground_truth_fault_paths)
            print("DETERMINED FAULT PATHS:", determined_fault_paths)
            print("assertion error:", e)
            print("for instance:", instance)
            exit(0)

        if args.v:
            for fault_path in fault_paths:
                print(colored(fault_path, "red", "on_white", ["bold"]))
