#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne
import json
import logging

import smach
import tensorflow as tf
from nesy_diag_smach.config import FAULT_CONTEXT_INPUT_FILE
from nesy_diag_smach.nesy_diag_smach import NeuroSymbolicDiagnosisStateMachine
from termcolor import colored

from local_data_accessor import LocalDataAccessor
from local_data_provider import LocalDataProvider
from local_model_accessor import LocalModelAccessor
from util import log_info, log_debug, log_warn, log_err


def run_smach():
    smach.set_loggers(log_info, log_debug, log_warn, log_err)  # set custom logging functions

    # init local implementations of I/O interfaces
    data_acc = LocalDataAccessor()
    model_acc = LocalModelAccessor()
    data_prov = LocalDataProvider()

    sm = NeuroSymbolicDiagnosisStateMachine(data_acc, model_acc, data_prov)
    tf.get_logger().setLevel(logging.ERROR)
    sm.execute()
    final_out = sm.userdata.final_output
    print("final output of smach execution (fault path(s)):", final_out)
    return final_out


if __name__ == '__main__':

    fault_paths = run_smach()

    # compare to ground truth
    with open(FAULT_CONTEXT_INPUT_FILE, "r") as f:
        problem_instance = json.load(f)

    ground_truth_fault_paths = problem_instance["ground_truth_fault_paths"]
    determined_fault_paths = [path.split(" -> ") for path in fault_paths]
    print("#####################################################################")
    print("GROUND TRUTH FAULT PATHS:", ground_truth_fault_paths)
    print("DETERMINED FAULT PATHS:", determined_fault_paths)
    print("#####################################################################")

    assert len(ground_truth_fault_paths) == len(fault_paths)
    assert all(gtfp in determined_fault_paths for gtfp in ground_truth_fault_paths)
    print("result, i.e., set of generated fault paths, of state machine execution with instance X matches ground truth")

    for fault_path in fault_paths:
        print(colored(fault_path, "red", "on_white", ["bold"]))
