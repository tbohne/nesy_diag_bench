#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import json
import random
from typing import Dict, Tuple, List

from nesy_diag_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer


def randomly_gen_error_codes_with_fault_cond_and_suspect_components(
        num_of_codes: int, components: List[str]
) -> Dict[str, Tuple[str, List[str]]]:
    error_codes = {}
    for i in range(num_of_codes):
        # gen diag associations - each code should have a number [0, n] random associated components
        rand_num = random.randint(0, len(components))
        sus_components = []
        for j in range(rand_num):
            r = random.randint(0, len(components) - 1)
            while components[r] in sus_components:
                r = random.randint(0, len(components) - 1)
            sus_components.append(components[r])

        error_codes["E" + str(i)] = ("FC" + str(i), sus_components)
    return error_codes


def randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(
        num_of_comp: int, percentage_of_anomalies: float
) -> Dict[str, Tuple[bool, List[str]]]:
    suspect_components = {}
    for i in range(num_of_comp):
        # each component has a tuple of (anomaly: bool, affected_by: list)
        # --> init all without anomaly and affected_by relations
        suspect_components["C" + str(i)] = (False, [])

    # gen anomalies
    num_elements = round(num_of_comp * (percentage_of_anomalies / 100))
    selected_elements = random.sample(suspect_components.keys(), num_elements)

    # gen affected_by - each comp should have a number [0, n-1] random affected_by relations
    for i in range(num_of_comp):
        rand_num = random.randint(0, num_of_comp - 1)
        affected_by_relations = []
        for j in range(rand_num):
            r = random.randint(0, num_of_comp - 1)
            while r == i or "C" + str(r) in affected_by_relations:
                r = random.randint(0, num_of_comp - 1)
            affected_by_relations.append("C" + str(r))
        suspect_components["C" + str(i)] = ("C" + str(i) in selected_elements, affected_by_relations)
    return suspect_components


def add_generated_instance_to_kg(
        suspect_components: Dict[str, Tuple[bool, List[str]]], error_codes: Dict[str, Tuple[str, List[str]]]
) -> None:
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()

    for k in suspect_components.keys():
        # init each component without any affected_by relations
        expert_knowledge_enhancer.add_component_to_knowledge_graph(k, [])

    for k in suspect_components.keys():
        # affected_by relations
        if len(suspect_components[k][1]) > 0:
            expert_knowledge_enhancer.add_component_to_knowledge_graph(k, suspect_components[k][1])

    for k in error_codes.keys():
        code = k
        fault_cond = errors[k][0]
        associated_comps = errors[k][1]
        expert_knowledge_enhancer.add_error_code_to_knowledge_graph(code, fault_cond, associated_comps)


def write_instance_to_file(suspect_components, error_codes, input_error_codes, seed):
    data = {
        "suspect_components": suspect_components,
        "error_codes": error_codes,
        "input_error_codes": input_error_codes
    }
    # naming scheme: <num_of_comp>_<num_of_error_codes>_<num_of_input_errors>_<seed>.json
    with open("instances/"
              + str(len(suspect_components.keys())) + "_"
              + str(len(error_codes.keys())) + "_"
              + str(len(input_error_codes)) + "_"
              + str(seed) + ".json", "w") as f:
        json.dump(data, f, indent=4, default=str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Randomly generate parametrized NeSy diag problem instances.')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--components', type=int, default=129)  # 129 is the number of UCR datasets
    parser.add_argument('--error-codes', type=int, default=50)
    parser.add_argument('--input-error-codes', type=int, default=1)
    parser.add_argument('--anomaly-percentage', type=float, default=0.2)
    args = parser.parse_args()

    random.seed(args.seed)

    print("COMPONENTS:")
    sus_comp = randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(
        args.components, args.anomaly_percentage
    )
    for k in sus_comp.keys():
        print(k, ":", sus_comp[k])

    print("ERRORS:")
    errors = randomly_gen_error_codes_with_fault_cond_and_suspect_components(
        args.error_codes, list(sus_comp.keys())
    )
    for k in errors.keys():
        print(k, ":", errors[k])

    # generate random input error code(s) - max 2 - for the moment only 1
    input_err = list(errors.keys())[random.randint(0, len(errors.keys()) - 1)]
    print("input error:", input_err)

    write_instance_to_file(sus_comp, errors, input_err, args.seed)

    add_generated_instance_to_kg(sus_comp, errors)
