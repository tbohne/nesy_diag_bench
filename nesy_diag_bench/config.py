#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

FUSEKI_URL = "http://localhost:3030"
DATASET_NAME = "nesy_diag"
UPDATE_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/update"
DATA_ENDPOINT = f"{FUSEKI_URL}/{DATASET_NAME}/data"
BACKUP_URL = f"{FUSEKI_URL}/{DATASET_NAME}/data?graph=default"
