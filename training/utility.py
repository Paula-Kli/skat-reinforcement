import os
import re
from typing import Optional


def find_latest_model(training_dir: str):
    latest_model: Optional[str] = None
    latest_model_iterations = 0
    for filename in os.listdir(training_dir):
        match = re.fullmatch(r"((\d+_?)+)\.zip", filename)
        if match and (int(match.group(1)) > latest_model_iterations):
            latest_model = f"{training_dir}/{filename}"
            latest_model_iterations = int(match.group(1))
    return latest_model, latest_model_iterations
