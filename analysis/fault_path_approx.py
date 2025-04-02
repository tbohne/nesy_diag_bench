#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import math

CONF = "c5"
PROB_EPSILON = 0.03
MAX_EXP = 20
CONFIGS = {  # gt comprises the avg / median number of fault paths across the entire instance set
    "c0": {"C": 129, "alpha": 0.2, "beta": 0.1, "gt_avg": 64.55, "gt_median": 35},
    "c1": {"C": 129, "alpha": 0.2, "beta": 0.01, "gt_avg": 23.56, "gt_median": 24},
    "c2": {"C": 129, "alpha": 0.1, "beta": 0.05, "gt_avg": 10.54, "gt_median": 11},
    "c3": {"C": 129, "alpha": 0.1, "beta": 0.2, "gt_avg": 17.99, "gt_median": 13.5},
    "c4": {"C": 129, "alpha": 0.05, "beta": 0.2, "gt_avg": 4.53, "gt_median": 5},
    "c5": {"C": 129, "alpha": 0.3, "beta": 0.1, "gt_avg": 2352.1, "gt_median": 804.5},
    "c6": {"C": 129, "alpha": 0.2, "beta": 0.05, "gt_avg": 19.3, "gt_median": 19},
    "c7": {"C": 129, "alpha": 0.05, "beta": 0.05, "gt_avg": 5.35, "gt_median": 5.5},
    "c8": {"C": 129, "alpha": 0.05, "beta": 0.1, "gt_avg": 4.92, "gt_median": 5},
    "c9": {"C": 129, "alpha": 0.2, "beta": 0.02, "gt_avg": 21.87, "gt_median": 22},
    "c10": {"C": 129, "alpha": 0.1, "beta": 0.1, "gt_avg": 9.56, "gt_median": 10},
    "c11": {"C": 129, "alpha": 0.2, "beta": 0.07, "gt_avg": 24.25, "gt_median": 22},
    "c12": {"C": 129, "alpha": 0.4, "beta": 0.05, "gt_avg": 345.8, "gt_median": 118}
}

print(CONFIGS[CONF])
alpha = CONFIGS[CONF]["alpha"]
beta = CONFIGS[CONF]["beta"]
C = CONFIGS[CONF]["C"]

num_of_anomalous_conn = (math.ceil(alpha * C) - 1) * (beta / 2)
p_cont = num_of_anomalous_conn / (1 + num_of_anomalous_conn)


def approx_exponent() -> int:
    """
    Approximates the exponent, i.e., the number of levels of the fault path approximation procedure.
    With each iteration, the probability of continuation gets smaller.

    :return: approximated exponent
    """
    for i in range(MAX_EXP):
        if p_cont ** i <= PROB_EPSILON:
            return i
    return MAX_EXP


len_exp_0 = math.log(C) / math.log(1 / (beta / 2))
print("expected LENGTH of fault paths (m0):", len_exp_0)

# floor() empirically works better compared to ceil()
len_exp_1 = math.log((math.floor(alpha * C) - 1) * (beta / 2)) / math.log(1 / (1 - (beta / 2)))
print("expected LENGTH of fault paths (m1):", len_exp_1)

print("---------------------------------------------------------")
print("method 1")
print("---------------------------------------------------------")


def method_one(exponent: float) -> float:
    """
    Fault path approximation method one.

    :param exponent: number of levels of the fault path approximation procedure
    :return: approximated num of fault paths
    """
    exp_fault_paths = 0
    for i in range(int(exponent)):
        exp_fault_paths += (alpha ** i) * (((beta / 2) * C) ** i)
    return exp_fault_paths


print("expected num of fault paths (approx_exponent):", method_one(approx_exponent()))
print("expected num of fault paths (len_exp_0):", method_one(len_exp_0))
print("expected num of fault paths (len_exp_1):", method_one(len_exp_1))

print("---------------------------------------------------------")
print("method 2")
print("---------------------------------------------------------")

# floor() empirically works better compared to ceil()
num_anomalies = math.floor(alpha * C)
exp_fault_paths = num_anomalies * (1 - (beta / 2) / num_anomalies) ** num_anomalies
print("expected num of fault paths:", exp_fault_paths)

print("---------------------------------------------------------")
print("method 3")
print("---------------------------------------------------------")


def method_three(exponent: float) -> float:
    """
    Fault path approximation method three.

    :param exponent: number of levels of the fault path approximation procedure
    :return: approximated num of fault paths
    """
    avg_branching_factor = beta / 2
    total_fault_paths = num_anomalies
    for i in range(int(exponent)):
        total_fault_paths += avg_branching_factor * (num_anomalies - i) ** 2
    return total_fault_paths


print("expected num of fault paths (approx_exponent):", method_three(approx_exponent()))
print("expected num of fault paths (len_exp_0):", method_three(len_exp_0))
print("**************************************************************")
print("expected num of fault paths (len_exp_1): (!!!)", method_three(len_exp_1), "(!!!)")
print("**************************************************************")

print("---------------------------------------------------------")
print("method 4")
print("---------------------------------------------------------")


def method_four(exponent: float) -> float:
    """
    Fault path approximation method four.

    :param exponent: number of levels of the fault path approximation procedure
    :return: approximated num of fault paths
    """
    return (alpha * C) * (1 + (beta / 2)) ** exponent


print("expected num of fault paths (approx_exponent):", method_four(approx_exponent()))
print("expected num of fault paths (len_exp_0):", method_four(len_exp_0))
print("expected num of fault paths (len_exp_1):", method_four(len_exp_1))

print("---------------------------------------------------------")
print("method 5")
print("---------------------------------------------------------")

print("expected num of fault paths:", math.factorial(int(alpha * C)) ** (beta / 2))

print("---------------------------------------------------------")
print("method 6")
print("---------------------------------------------------------")

print("expected num of fault paths:", (alpha * C) * ((beta / 2) * (C - 1)) ** (C / ((beta / 2) * alpha * C)))

print("---------------------------------------------------------")
print("method 7")
print("---------------------------------------------------------")

L = math.log(num_anomalies) / math.log((beta / 2) * C)
prod = ((beta / 2) * (alpha * (beta / 2) * C)) ** L
print("expected num of fault paths:", num_anomalies * prod)
