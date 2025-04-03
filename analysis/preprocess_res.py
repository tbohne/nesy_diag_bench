#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import pandas as pd


def create_compact_instance_notation_cumulative(data_frame: pd.DataFrame) -> None:
    """
    Creates a compact instance notation for the cumulative results.

    :param data_frame: data frame to be adjusted
    """
    for i in range(len(data_frame["instance_set"])):
        e = data_frame["instance_set"][i].split("_")
        data_frame.at[i, "instance_set"] = "_".join([e[1], e[2], e[5], e[6]])

        # transform p0 from [0, 100] to [0, 1]
        e = round(float(data_frame["avg_ano_link_perc"][i]) / 100.0, 2)
        data_frame.at[i, "avg_ano_link_perc"] = e


def create_compact_instance_notation_instance_level(data_frame: pd.DataFrame) -> None:
    """
    Creates a compact instance notation for the instance-level results.

    :param data_frame: data frame to be adjusted
    """
    for i in range(len(data_frame["instance"])):
        e = data_frame["instance"][i].split("_")
        # e.g., 129_10_20_50_10_95_99_42_64
        data_frame.at[i, "instance"] = "_".join([e[1], e[2], e[5], e[6], e[8]])


# cumulative res
df = pd.read_csv("results/cumulative_res.csv")
create_compact_instance_notation_cumulative(df)
df.to_csv("results/compact_cumulative_res.csv", sep=',', encoding='utf-8', index=False)

# instance set res
df = pd.read_csv("results/res.csv")
create_compact_instance_notation_instance_level(df)
df.to_csv("results/compact_res.csv", sep=',', encoding='utf-8', index=False)
