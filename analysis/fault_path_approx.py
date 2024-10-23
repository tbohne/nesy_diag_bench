#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import math

########################################################################
########################################################################
CONF = "c5"

configs = {
    "c0": {"C": 129, "alpha": 0.2, "beta": 0.1, "gt": 64.55},
    "c1": {"C": 129, "alpha": 0.2, "beta": 0.01, "gt": 23.56},
    "c2": {"C": 129, "alpha": 0.1, "beta": 0.05, "gt": 10.54},
    "c3": {"C": 129, "alpha": 0.1, "beta": 0.2, "gt": 17.99},
    "c4": {"C": 129, "alpha": 0.05, "beta": 0.2, "gt": 4.53},
    "c5": {"C": 129, "alpha": 0.3, "beta": 0.1, "gt": 810}
}

print(configs[CONF])
alpha = configs[CONF]["alpha"]
beta = configs[CONF]["beta"]
C = configs[CONF]["C"]

num_of_anomalous_conn = alpha * (beta / 2) * C
p_cont = num_of_anomalous_conn / (1 + num_of_anomalous_conn)


########################################################################
########################################################################

def approx_exponent():
    for i in range(20):
        if p_cont ** i <= 0.03:
            return i


len_exp_0 = math.log(C) / math.log(1 / (beta / 2))
print("expected LENGTH of fault paths (m0):", len_exp_0)

len_exp_1 = math.log(C * (beta / 2)) / math.log(1 / (1 - (beta / 2)))
print("expected LENGTH of fault paths (m1):", len_exp_1)

print("---------------------------------------------------------")
print("method 1")
print("---------------------------------------------------------")


def method_one(exponent):
    end_sum = 0
    for i in range(int(exponent)):
        end_sum += (alpha ** i) * (((beta / 2) * C) ** i)
    return end_sum


print("expected num of fault paths:", method_one(approx_exponent()))
print("expected num of fault paths:", method_one(len_exp_0))
print("expected num of fault paths:", method_one(len_exp_1))

print("---------------------------------------------------------")
print("method 2")
print("---------------------------------------------------------")

num_anomalies = alpha * C
expected_fault_paths = num_anomalies * (1 - (beta / 2) / num_anomalies) ** num_anomalies
print("expected num of fault paths:", expected_fault_paths)

print("---------------------------------------------------------")
print("method 3")
print("---------------------------------------------------------")


def method_three(exponent):
    average_branching_factor = beta / 2
    total_fault_paths = num_anomalies
    current_anomalies = num_anomalies
    for _ in range(int(exponent)):
        new_branches = current_anomalies * average_branching_factor * num_anomalies
        total_fault_paths += new_branches
        current_anomalies = new_branches
    return total_fault_paths


print("expected num of fault paths:", method_three(approx_exponent()))
print("expected num of fault paths:", method_three(len_exp_0))
print("expected num of fault paths:", method_three(len_exp_1))

print("---------------------------------------------------------")
print("method 4")
print("---------------------------------------------------------")


def method_four(exponent):
    return (alpha * C) * (1 + (beta / 2)) ** exponent


print("expected num of fault paths:", method_four(approx_exponent()))
print("expected num of fault paths:", method_four(len_exp_0))
print("expected num of fault paths:", method_four(len_exp_1))

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
