"""
DGIWG GeoPackage Compliance Validator v1.54.1
Double-click this file (or run: python DGIWG_Validator_v1_54.py) to launch.
v1.54.1 fix: import _load_epsg_json_cache into checks.py (Req 13 NameError).
"""
import sys
import os

# Ensure the dgiwg_validator package folder next to this script is on the path
sys.path.insert(0, os.path.dir