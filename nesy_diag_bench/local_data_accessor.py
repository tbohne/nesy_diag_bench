#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import json
from typing import List

import pandas as pd
from nesy_diag_smach.config import SIGNAL_SESSION_FILES
from nesy_diag_smach.data_types.fault_context import FaultContext
from nesy_diag_smach.data_types.sensor_data import SensorData
from nesy_diag_smach.interfaces.data_accessor import DataAccessor


class LocalDataAccessor(DataAccessor):
    """
    Implementation of the data accessor interface used for evaluation purposes.
    """

    def __init__(self, instance):
        self.instance = instance

    def get_fault_context(self) -> FaultContext:
        """
        Retrieves the fault context data required in the diagnostic process.

        :return: fault context data
        """
        with open(self.instance, "r") as f:
            problem_instance = json.load(f)
        # only take list of error codes as input, not more
        input_error_codes = list(problem_instance["error_codes"].keys())
        fault_context = FaultContext(input_error_codes, "1234567890ABCDEFGHJKLMNPRSTUVWXYZ")
        return fault_context

    def get_signals_by_components(self, components: List[str]) -> List[SensorData]:
        """
        Retrieves the sensor data for the specified components.

        :param components: components to retrieve sensor data for
        :return: sensor data for each component
        """
        signals = []
        # for each component we need to check the ground truth of the instance - if it should have an anomaly
        with open(self.instance, "r") as f:
            problem_instance = json.load(f)
        for comp in components:
            # we consider class 0 as anomaly
            ground_truth_label = "0" if problem_instance["suspect_components"][comp][0] else "1"
            # TODO: each comp should have its own associated data, not all C0
            # path = "res/" + SIGNAL_SESSION_FILES + "/" + comp + ".tsv"
            path = "res/" + SIGNAL_SESSION_FILES + "/" + "C0" + ".tsv"
            # parse one signal from tsv file
            _, values = self.read_ucr_recording(path, ground_truth_label)
            signals.append(SensorData(values, comp))
        return signals

    @staticmethod
    def read_ucr_recording(path, ground_truth_label):
        # TODO: should be random from those with ground_truth_label
        sample_idx = 4 if ground_truth_label == "0" else 25
        # dataframe containing all signals from the dataset + label in col 0
        df = pd.read_csv(path, delimiter='\t', header=None, na_values=['-∞', '∞'])
        selected_sample_label = int(df.iloc[sample_idx].to_list()[0])
        selected_sample_values = df.iloc[sample_idx].to_list()[1:]
        #print("label:", selected_sample_label)
        #print("signal:", selected_sample_values[:10])
        return selected_sample_label, selected_sample_values

    def get_manual_judgement_for_component(self, component: str) -> bool:
        """
        Retrieves a manual judgement by the human for the specified component.

        :param component: component to get manual judgement for
        :return: true -> anomaly, false -> regular
        """
        pass

    def get_manual_judgement_for_sensor(self) -> bool:
        """
        Retrieves a manual judgement by the human for the currently considered sensor.

        :return: true -> anomaly, false -> regular
        """
        pass
