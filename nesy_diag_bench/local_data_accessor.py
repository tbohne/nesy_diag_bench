#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import json
from typing import List

from nesy_diag_smach.config import SIGNAL_SESSION_FILES
from nesy_diag_smach.data_types.fault_context import FaultContext
from nesy_diag_smach.data_types.sensor_data import SensorData
from nesy_diag_smach.interfaces.data_accessor import DataAccessor
from oscillogram_classification import preprocess


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
            anomaly_suffix = "NEG" if problem_instance["suspect_components"][comp][0] else "POS"
            path = "res/" + SIGNAL_SESSION_FILES + "/" + comp + "/dummy_signal_" + anomaly_suffix + ".csv"
            _, values = preprocess.read_oscilloscope_recording(path, verbose=False)
            signals.append(SensorData(values, comp))
        return signals

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
