#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import json
import random
from collections import defaultdict
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
        num_of_comp: int, percentage_of_anomalies: float, affected_by_ub_percentage: float
) -> Dict[str, Tuple[bool, List[str]]]:
    suspect_components = {}
    for i in range(num_of_comp):
        # each component has a tuple of (anomaly: bool, affected_by: list)
        # --> init all without anomaly and affected_by relations
        suspect_components["C" + str(i)] = (False, [])

    # gen anomalies
    num_elements = round(num_of_comp * percentage_of_anomalies)
    selected_elements = random.sample(suspect_components.keys(), num_elements)

    # gen affected_by - each comp should have a number [0, min(n-1, config_param)] random affected_by relations
    for i in range(num_of_comp):
        rand_num = random.randint(0, min(num_of_comp - 1, int(affected_by_ub_percentage * num_of_comp)))
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
        fault_cond = error_codes[k][0]
        associated_comps = error_codes[k][1]
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


def find_paths_dfs(anomaly_graph, node, path=[]):
    path = path + [node]  # not using append() because it wouldn't create a new list
    if node not in anomaly_graph:
        return [path]
    paths = []
    for node in anomaly_graph[node]:
        paths.extend(find_paths_dfs(anomaly_graph, node, path))
    return paths


def find_all_longest_paths(anomaly_graph):
    all_paths = []
    nodes_with_incoming_edges = [inc for targets in anomaly_graph.values() for inc in targets]
    for path_src in anomaly_graph:
        if path_src in nodes_with_incoming_edges:
            continue
        all_paths.extend(find_paths_dfs(anomaly_graph, path_src))
    return all_paths


def generate_ground_truth_fault_paths(component_net):
    anomalous_components = [k for k in component_net.keys() if component_net[k][0]]

    # finding all anomalous affecting components for all anomalous components,
    # those are the edges in the final fault paths
    edges = []
    for anomaly in anomalous_components:
        for aff_by in component_net[anomaly][1]:
            if aff_by in anomalous_components:
                edges.append(aff_by + " -> " + anomaly)

    edges = edges[::-1]  # has to be reversed, affected-by direction
    # create adjacency lists
    anomaly_graph = defaultdict(list)
    for edge in edges:
        start, end = edge.split(' -> ')
        anomaly_graph[start].append(end)

    fault_paths = find_all_longest_paths(anomaly_graph)

    # handle one-component-paths
    for anomaly in anomalous_components:
        if anomaly not in " ".join(edges):
            fault_paths.append([anomaly])

    return fault_paths


def test_branching_fault_path_instance_one():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (True, []),
        "C0006": (True, []),
        "C0008": (True, ['C0009']),
        "C0009": (True, ['C0010']),
        "C0010": (False, []),
        "C0011": (True, ['C0012']),
        "C0012": (True, ['C0007']),
        "C0013": (False, ['C0014']),
        "C0014": (True, ['C0015']),
        "C0015": (True, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 5
    assert ground_truth_fault_paths[0] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[1] == ['C0007', 'C0012', 'C0011']
    assert ground_truth_fault_paths[3] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[4] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[2] == ['C0007', 'C0004', 'C0002', 'C0001']


def test_branching_fault_path_instance_two():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (True, ['C0012']),
        "C0006": (True, []),
        "C0008": (True, ['C0009']),
        "C0009": (True, ['C0010']),
        "C0010": (False, []),
        "C0011": (True, []),
        "C0012": (True, ['C0011']),
        "C0013": (False, ['C0014']),
        "C0014": (True, ['C0015']),
        "C0015": (True, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 4
    assert ground_truth_fault_paths[2] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[0] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[3] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[1] == ['C0011', 'C0012', 'C0007', 'C0004', 'C0002', 'C0001']


def test_simple_fault_path():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (False, []),
        "C0006": (True, ['C0008']),
        "C0008": (True, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 1
    assert ground_truth_fault_paths[0] == ['C0008', 'C0006', 'C0004', 'C0002', 'C0001']


def test_simple_two_fault_paths():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (False, []),
        "C0006": (True, []),
        "C0008": (True, ['C0009']),
        "C0009": (True, ['C0010']),
        "C00010": (False, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 2
    assert ground_truth_fault_paths[0] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[1] == ['C0006', 'C0004', 'C0002', 'C0001']


def test_several_fault_paths():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (False, []),
        "C0006": (True, []),
        "C0008": (True, ['C0009']),
        "C0009": (True, ['C0010']),
        "C0010": (False, []),
        "C0011": (True, ['C0012']),
        "C0012": (True, ['C0007']),
        "C0013": (False, ['C0014']),
        "C0014": (True, ['C0015']),
        "C0015": (False, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 4
    assert ground_truth_fault_paths[0] == ['C0012', 'C0011']
    assert ground_truth_fault_paths[1] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[2] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[3] == ['C0014']


def test_complex_case():
    component_net = {
        "C0001": (True, ['C0002']),
        "C0002": (True, ['C0004']),
        "C0004": (True, ['C0007', 'C0006']),
        "C0003": (False, ['C0005']),
        "C0005": (False, ['C0008']),
        "C0007": (True, ['C0012', 'C0019']),
        "C0006": (True, ['C0019']),
        "C0008": (True, ['C0009']),
        "C0009": (True, ['C0010']),
        "C0010": (False, []),
        "C0011": (True, []),
        "C0012": (True, ['C0011']),
        "C0013": (False, ['C0014']),
        "C0014": (True, ['C0015', 'C0016']),
        "C0015": (True, []),
        "C0016": (True, ['C0018', 'C0017']),
        "C0017": (True, []),
        "C0018": (False, []),
        "C0019": (True, [])
    }
    ground_truth_fault_paths = generate_ground_truth_fault_paths(component_net)
    assert len(ground_truth_fault_paths) == 6
    assert ground_truth_fault_paths[3] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[0] == ['C0017', 'C0016', 'C0014']
    assert ground_truth_fault_paths[1] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[4] == ['C0019', 'C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[5] == ['C0019', 'C0007', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[2] == ['C0011', 'C0012', 'C0007', 'C0004', 'C0002', 'C0001']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Randomly generate parametrized NeSy diag problem instances.')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--components', type=int, default=129)  # 129 is the number of UCR datasets
    parser.add_argument('--error-codes', type=int, default=50)
    parser.add_argument('--input-error-codes', type=int, default=1)
    parser.add_argument('--anomaly-percentage', type=float, default=0.2)
    parser.add_argument('--extend-kg', action='store_true', default=False)
    parser.add_argument('--affected-by-ub-percentage', type=float, default=0.4)
    args = parser.parse_args()

    random.seed(args.seed)

    # test basic functionality of instance / fault path generation
    test_branching_fault_path_instance_one()
    test_branching_fault_path_instance_two()
    test_simple_fault_path()
    test_simple_two_fault_paths()
    test_several_fault_paths()
    test_complex_case()

    print("COMPONENTS:")
    sus_comp = randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(
        args.components, args.anomaly_percentage, args.affected_by_ub_percentage
    )
    for k in sus_comp.keys():
        print(k, ":", sus_comp[k])

    print("GROUND TRUTH FAULT PATHS:")
    ground_truth_fault_paths = generate_ground_truth_fault_paths(sus_comp)
    print(ground_truth_fault_paths)

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

    if args.extend_kg:
        add_generated_instance_to_kg(sus_comp, errors)
