#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

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


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
    random.seed(42)

    print("COMPONENTS:")
    sus_comp = randomly_gen_suspect_components_with_affected_by_relations_and_anomalies(6, 30)
    for k in sus_comp.keys():
        print(k, ":", sus_comp[k])

    print("ERRORS:")
    errors = randomly_gen_error_codes_with_fault_cond_and_suspect_components(4, list(sus_comp.keys()))
    for k in errors.keys():
        print(k, ":", errors[k])
