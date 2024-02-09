#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

def log_info(msg) -> None:
    """
    Custom logging to override defaults.

    :param msg: msg to be logged
    """
    pass


def log_warn(msg) -> None:
    """
    Custom logging to override defaults.

    :param msg: msg to be logged
    """
    pass


def log_debug(msg) -> None:
    """
    Custom logging to override defaults.

    :param msg: msg to be logged
    """
    pass


def log_err(msg) -> None:
    """
    Custom logging to override defaults.

    :param msg: msg to be logged
    """
    print("[ ERROR ] : " + str(msg))
