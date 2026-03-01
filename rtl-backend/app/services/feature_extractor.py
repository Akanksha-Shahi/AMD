import re

def extract_features(code: str):
    features = {}

    features["num_modules"] = len(re.findall(r"\bmodule\b", code))
    features["num_always_blocks"] = len(re.findall(r"\balways\b", code))
    features["num_if"] = len(re.findall(r"\bif\b", code))
    features["num_case"] = len(re.findall(r"\bcase\b", code))
    features["num_loops"] = len(re.findall(r"\bfor\b", code))
    features["num_assignments"] = len(re.findall(r"<=|=", code))
    features["code_length"] = len(code.splitlines())

    return features
