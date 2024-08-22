#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import pearsonr


def determine_correlation(arr_a: List[float], arr_b: List[float]) -> Tuple[float, float, bool]:
    """
    Determines the Pearson correlation coefficient between `arr_a` and `arr_b`.

    "The p-value roughly indicates the probability of an uncorrelated system producing datasets that have a Pearson
    correlation at least as extreme as the one computed from these datasets. The p-values are not entirely
    reliable but are probably reasonable for datasets larger than 500 or so." -- pydoc.help

    IMPORTANT: we only have a dataset size of 100 on the instance level (!)

    --> p-value associated with the chosen alternative
        p-value low (generally < 0.05), corr. statistically significant
        p-value high (generally > 0.05), corr. not statistically significant

    :param arr_a: first array of comparison
    :param arr_b: second array of comparison
    :return: (correlation coefficient, p-value, whether corr. statistically significant)
    """
    assert len(arr_a) == len(arr_b)

    if len(np.unique(arr_a)) <= 1 or len(np.unique(arr_b)) <= 1:
        return 0, 0, False

    # numpy is not estimating the significance
    np_corr_coeff = round(np.corrcoef(arr_a, arr_b)[0, 1], 2)
    corr_coeff, p_val = pearsonr(arr_a, arr_b)
    assert np_corr_coeff == round(corr_coeff, 2)
    return corr_coeff, p_val, p_val < 0.05


df = pd.read_csv("res.csv")

corr_coeff, p_val, significant = determine_correlation(df["#fault_paths"], df["avg_fp_len"])
print("fault_paths --- avg_fp_len:")
print("\tcorr. coeff.:", round(corr_coeff, 2), "p-val:", p_val, "significant:", significant)
