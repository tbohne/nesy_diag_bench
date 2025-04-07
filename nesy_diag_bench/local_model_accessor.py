#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import json
from typing import Union, Tuple, List, Dict

from nesy_diag_smach.config import TRAINED_MODEL_POOL
from nesy_diag_smach.interfaces.model_accessor import ModelAccessor
from tensorflow import keras


class LocalModelAccessor(ModelAccessor):
    """
    Implementation of the model accessor interface for evaluation purposes.
    """

    def __init__(self, instance: str, verbose: bool = False) -> None:
        """
        Initializes the local model accessor.

        :param verbose: sets verbosity of model accessor
        :param instance: problem instance to be solved
        """
        self.verbose = verbose
        self.instance = instance

    def get_keras_univariate_ts_classification_model_by_component(
            self, component: str
    ) -> Union[Tuple[keras.models.Model, Dict], None]:
        """
        Retrieves a trained model to classify signals of the specified component.

        The provided model is expected to be a Keras model satisfying the following assumptions:
            - input_shape: (None, len_of_ts, 1)
            - output_shape: (None, 1)
        Thus, in both cases we have a variable batch size due to `None`. For the input we expect a list of scalars and
        for the output exactly one scalar.

        :param component: component to retrieve trained model for
        :return: trained model and model meta info dictionary or `None` if unavailable
        """
        try:
            # generally, there should be a model for each component (irrelevant for the eval)
            trained_model_file = TRAINED_MODEL_POOL + "C0" + ".h5"
            if self.verbose:
                print("loading trained model:", trained_model_file)
            model_meta_info = {
                "normalization_method": "z_norm",
                "model_id": "keras_univariate_ts_classification_model_001"
            }
            return keras.models.load_model(trained_model_file), model_meta_info
        except OSError as e:
            print("no trained model available for the signal (component) to be classified:", component)
            print("ERROR:", e)

    def get_sim_univariate_ts_classification_model_by_component(self, component: str) -> Tuple[List[str], int]:
        """
        Retrieves simulated model accuracies for the specified component.

        :param component: component to retrieve simulated models for
        :return: (simulated model accuracies, total number of simulated accuracies)
        """
        with open(self.instance, "r") as f:
            problem_instance = json.load(f)
        return problem_instance["sim_accuracies"][component], len(problem_instance["sim_accuracies"])
