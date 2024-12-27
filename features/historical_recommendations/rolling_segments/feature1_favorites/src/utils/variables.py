# src/utils/variables.py

"""
Module containing global variables loaded from config.json.

Attributes
----------
VARIABLES : dict
    Dictionary containing all the configuration variables from config.json.
"""

import os
from .config_loader import load_config

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../config.json")
VARIABLES = load_config(CONFIG_PATH)

# Use .get() for an extra layer of safety
INPUT_CSV = VARIABLES.get("data", {}).get("input_csv", "default_input.csv")
INTERMEDIATE_CSV = VARIABLES.get("data", {}).get("intermediate_csv", "default_intermediate.csv")
OUTPUT_CSV = VARIABLES.get("data", {}).get("output_csv", "default_output.csv")
PARAMS = VARIABLES.get("parameters", {})
LOGGING_CONFIG = VARIABLES.get("logging", {})
