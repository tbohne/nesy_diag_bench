#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse
import json
import os
import random
import shutil
from collections import defaultdict
from typing import Dict, Tuple, List

import requests
from nesy_diag_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer

from config import BACKUP_URL, UPDATE_ENDPOINT


def randomly_gen_error_codes_with_fault_cond_and_suspect_components(
        ground_truth_fault_paths: List[List[str]], components: List[str], fault_path_comp_ub_percentage: float,
        distractor_ub_percentage: float
) -> Dict[str, Tuple[str, List[str]]]:
    """
    Randomly generates error codes with fault conditions and suspect components.

    :param ground_truth_fault_paths: ground truth fault paths to generate errors for
    :param components: list of suspect components
    :param fault_path_comp_ub_percentage: UB for fault path component percentage
    :param distractor_ub_percentage: UB percentage for distractors
    :return: {error_code: (fault_cond, suspect_components)}
    """
    error_codes = {}
    # we need as many random error codes as we have ground truth fault paths (assuming no duplicates)
    for i in range(len(ground_truth_fault_paths)):
        # gen diag associations - each code should have a number [1, n] random associated components from the
        # corresponding ground truth fault path
        ub = int(fault_path_comp_ub_percentage * len(ground_truth_fault_paths[i]))
        if len(ground_truth_fault_paths[i]) == 1 or ub in [0, 1]:
            num_of_fault_path_comp = 1
        else:
            num_of_fault_path_comp = random.randint(1, ub)
        sus_components = []
        for j in range(num_of_fault_path_comp):
            # the first one always has to be the "anti-root-cause" so that all components are reachable via affected-by
            if j == 0:
                # the "anti-root-cause", the beginning of the "affected-by chain"
                r = len(ground_truth_fault_paths[i]) - 1
            else:
                r = random.randint(0, len(ground_truth_fault_paths[i]) - 1)
                while ground_truth_fault_paths[i][r] in sus_components:
                    r = random.randint(0, len(ground_truth_fault_paths[i]) - 1)
            sus_components.append(ground_truth_fault_paths[i][r])

        # also add some "distractors", i.e., include some suspect components that are not part of the fault path
        num_of_distractors = random.randint(
            1, int(distractor_ub_percentage * (len(components) - len(sus_components) - 1))
        )
        for j in range(num_of_distractors):
            r = random.randint(0, len(components) - 1)
            while components[r] in sus_components:
                r = random.randint(0, len(components) - 1)
            sus_components.append(components[r])
        error_codes["E" + str(i)] = ("FC" + str(i), sus_components)
    return error_codes


def randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(
        num_of_comp: int, percentage_of_anomalies: float, affected_by_ub_percentage: float
) -> Dict[str, Tuple[bool, List[str]]]:
    """
    Randomly generates suspect components with affected-by relations and anomalies.

    :param num_of_comp: number of components
    :param percentage_of_anomalies: fraction of components with anomalies
    :param affected_by_ub_percentage: UB percentage for affected-by relations per component
    :return: {component: (anomaly, affected-by list)}
    """
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
    """
    Adds the generated problem instance to the KG.

    :param suspect_components: suspect components
    :param error_codes: error codes
    """
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer(verbose=False)

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


def write_instance_to_file(
        suspect_components: Dict[str, Tuple[bool, List[str]]], ground_truth_fault_paths: List[List[str]],
        error_codes: Dict[str, Tuple[str, List[str]]], seed: int, anomaly_percentage: float, affected_by_ub: float,
        fault_path_comp_ub: float, distractor_ub: float, idx: int, sim_accuracies: Dict[str, Tuple[str, str]],
        model_acc_lb: float, model_acc_ub: float
) -> str:
    """
    Writes the problem instance to file.

    :param suspect_components: suspect components
    :param ground_truth_fault_paths: ground truth fault paths
    :param error_codes: error codes
    :param seed: seed for random processes
    :param anomaly_percentage: fraction of components with anomalies
    :param affected_by_ub: UB for the affected-by relations of each component
    :param fault_path_comp_ub: UB for the fault path components
    :param distractor_ub: UB for distractors
    :param idx: instance index
    :param sim_accuracies: simulated accuracies for components
    :param model_acc_lb: LB for model accuracy
    :param model_acc_ub: UB for model accuracy
    :return: filename
    """
    data = {
        "suspect_components": suspect_components,
        "ground_truth_fault_paths": ground_truth_fault_paths,
        "error_codes": error_codes,
        "sim_accuracies": sim_accuracies
    }
    # naming scheme:
    # <comp>_<ano_perc>_<affected_by_ub>_<fp_comp_ub>_<distractor_ub>_<model_acc_lb>_<model_acc_ub>_<seed>_<idx>.json
    filename = (str(len(suspect_components.keys())) + "_"
                + str(int(anomaly_percentage * 100)) + "_" + str(int(affected_by_ub * 100)) + "_"
                + str(int(fault_path_comp_ub * 100)) + "_" + str(int(distractor_ub * 100)) + "_"
                + str(int(model_acc_lb * 100)) + "_" + str(int(model_acc_ub * 100)) + "_"
                + str(seed) + "_" + str(idx))

    os.makedirs("instances", exist_ok=True)
    with open("instances/" + filename + ".json", "w") as f:
        json.dump(data, f, indent=4, default=str)
    return filename


def find_paths_dfs(anomaly_graph: Dict[str, List[str]], node: str, path: List[str] = []) -> List[List[str]]:
    """
    Finds paths in the anomaly graph in a depth-first fashion.

    :param anomaly_graph: anomaly graph to find paths in
    :param node: currently considered node (e.g., path source)
    :param path: currently considered path
    :return: list of found paths
    """
    if node in path:  # deal with cyclic relations
        return [path]
    path = path + [node]  # not using append() because it wouldn't create a new list
    if node not in anomaly_graph:
        return [path]
    paths = []
    for node in anomaly_graph[node]:
        paths.extend(find_paths_dfs(anomaly_graph, node, path))
    return paths


def find_all_longest_paths(anomaly_graph: Dict[str, List[str]]) -> List[List[str]]:
    """
    Finds all longest paths in the anomaly graph.

    :param anomaly_graph: anomaly graph to find longest paths in
    :return: unique longest paths
    """
    all_paths = []
    for path_src in anomaly_graph:
        all_paths.extend(find_paths_dfs(anomaly_graph, path_src))
    return find_unique_longest_paths(all_paths)


def find_unique_longest_paths(paths: List[List[str]]) -> List[List[str]]:
    """
    Extracts the unique longest paths from the list of identified paths.

    :param paths: identified paths to find unique longest paths in
    :return: unique longest paths
    """
    unique_paths = []
    paths_sorted = sorted(paths, key=len, reverse=True)
    for path in paths_sorted:
        if not any("-" + "-".join(list(path)) + "-" in "-" + "-".join(up) + "-" for up in unique_paths):
            unique_paths.append(list(path))
    return unique_paths


def generate_ground_truth_fault_paths(component_net: Dict[str, Tuple[bool, List[str]]]) -> List[List[str]]:
    """
    Generates the ground truth fault paths based on the component network.

    :param component_net: component network, i.e., mapping of components to states and affected-by relations
    :return: ground truth fault paths
    """
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
        edge_comp = "-" + "-".join(["-".join(edge.split(" -> ")) for edge in edges]) + "-"
        if "-" + anomaly + "-" not in edge_comp:
            fault_paths.append([anomaly])
    return fault_paths


def test_branching_fault_path_instance_one() -> None:
    """
    Tests for the expected behavior with branching fault paths -- instance one.
    """
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
    assert ground_truth_fault_paths[3] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[2] == ['C0007', 'C0012', 'C0011']
    assert ground_truth_fault_paths[4] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[1] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[0] == ['C0007', 'C0004', 'C0002', 'C0001']


def test_branching_fault_path_instance_two() -> None:
    """
    Tests for the expected behavior with branching fault paths -- instance two.
    """
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
    assert ground_truth_fault_paths[3] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[2] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[1] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[0] == ['C0011', 'C0012', 'C0007', 'C0004', 'C0002', 'C0001']


def test_simple_fault_path() -> None:
    """
    Tests for the expected behavior with one simple fault path.
    """
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


def test_simple_two_fault_paths() -> None:
    """
    Tests for the expected behavior with two simple fault paths.
    """
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
    assert ground_truth_fault_paths[1] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[0] == ['C0006', 'C0004', 'C0002', 'C0001']


def test_several_fault_paths() -> None:
    """
    Tests for the expected behavior with several fault paths.
    """
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
    assert ground_truth_fault_paths[1] == ['C0012', 'C0011']
    assert ground_truth_fault_paths[2] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[0] == ['C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[3] == ['C0014']


def test_complex_case() -> None:
    """
    Tests for the expected behavior with a more complex case.
    """
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
    assert ground_truth_fault_paths[5] == ['C0009', 'C0008']
    assert ground_truth_fault_paths[3] == ['C0017', 'C0016', 'C0014']
    assert ground_truth_fault_paths[4] == ['C0015', 'C0014']
    assert ground_truth_fault_paths[1] == ['C0019', 'C0006', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[2] == ['C0019', 'C0007', 'C0004', 'C0002', 'C0001']
    assert ground_truth_fault_paths[0] == ['C0011', 'C0012', 'C0007', 'C0004', 'C0002', 'C0001']


def create_kg_file_for_generated_instance(filename: str) -> None:
    """
    Creates the KG file for a generated instance (.nt).

    :param filename: instance name
    """
    # create KG file (.nt) - perform backup and compress result using gzip
    response = requests.get(BACKUP_URL, headers={"Accept": "application/n-triples"})
    if response.status_code == 200:
        with open("instances/" + filename + ".nt", "wb") as f:
            f.write(response.content)
    else:
        print(f"HTTP status: {response.status_code}")


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
        # get home dir in platform-independent way
        home_dir = os.path.expanduser("~")
        target_dir = os.path.join(home_dir, "run", "databases", "nesy_diag")

        # remove backups to not clutter SSD
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        return True
    else:
        print("failed to clear dataset..")
        return False


def test_basic_functionality() -> None:
    """
    Tests the basic functionality of instance / fault path generation.
    """
    test_branching_fault_path_instance_one()
    test_branching_fault_path_instance_two()
    test_simple_fault_path()
    test_simple_two_fault_paths()
    test_several_fault_paths()
    test_complex_case()


def generate_instance(args: argparse.Namespace, idx: int) -> None:
    """
    Generates a problem instance based on the specified config.

    :param args: arguments of the instance generation, i.e., parameters
    :param idx: instance index
    """
    sus_comp = randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(
        args.components, args.anomaly_percentage, args.affected_by_ub_percentage
    )
    ground_truth_fault_paths = generate_ground_truth_fault_paths(sus_comp)
    errors = randomly_gen_error_codes_with_fault_cond_and_suspect_components(
        ground_truth_fault_paths, list(sus_comp.keys()), args.fault_path_comp_ub_percentage,
        args.distractor_ub_percentage
    )
    sim_accuracies = []
    if args.sim_classification_models:
        # we need a model, i.e., an acc, for each component
        sim_accuracies = {comp: (
            str(random.uniform(args.model_acc_lb, args.model_acc_ub)), str(sus_comp[comp][0])
        ) for comp in sus_comp.keys()}

    filename = write_instance_to_file(
        sus_comp, ground_truth_fault_paths, errors, args.seed, args.anomaly_percentage, args.affected_by_ub_percentage,
        args.fault_path_comp_ub_percentage, args.distractor_ub_percentage, idx, sim_accuracies, args.model_acc_lb,
        args.model_acc_ub
    )
    if args.extend_kg:
        assert clear_hosted_kg()
        add_generated_instance_to_kg(sus_comp, errors)
        create_kg_file_for_generated_instance(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Randomly generate parametrized NeSy diag problem instances.')
    # cf. paper for reasoning about default parameter settings
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--components', type=int, default=129)  # 129 is the number of UCR datasets
    parser.add_argument('--anomaly-percentage', type=float, default=0.2)
    parser.add_argument('--extend-kg', action='store_true', default=False)
    parser.add_argument('--affected-by-ub-percentage', type=float, default=0.4)
    parser.add_argument('--fault-path-comp-ub-percentage', type=float, default=1)
    parser.add_argument('--distractor-ub-percentage', type=float, default=0.5)
    parser.add_argument('--instances-per-conf', type=int, default=1)
    parser.add_argument('--sim-classification-models', action='store_true', default=False)
    parser.add_argument('--model-acc-lb', type=float, default=0.6)
    parser.add_argument('--model-acc-ub', type=float, default=0.95)
    args = parser.parse_args()

    random.seed(args.seed)
    test_basic_functionality()

    for i in range(args.instances_per_conf):
        print("gen instance", i)
        generate_instance(args, i)
