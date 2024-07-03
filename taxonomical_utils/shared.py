import json
from typing import Any, Dict, List, Tuple

import pandas as pd

from taxonomical_utils.exceptions import UnsupportedFileTypeError


def save_json(data: Any, filepath: str) -> None:
    with open(filepath, "w") as out:
        json.dump(data, out, indent=2, sort_keys=True)


def load_json(filepath: str) -> Any:
    with open(filepath) as tmpfile:
        return json.load(tmpfile)


def normalize_json_upper(json_data: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    matches = pd.json_normalize(json_data, record_path=["results", "matches"])
    unmatched = pd.DataFrame(json_data[0]["unmatched_names"], columns=["unmatched_names"])
    return matches, unmatched


def normalize_json_resolver(json_data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    matches = pd.json_normalize(json_data, record_path=["results", "matches"])
    unmatched = pd.DataFrame(json_data["unmatched_names"], columns=["unmatched_names"])
    return matches, unmatched


def read_table(input_file: str) -> pd.DataFrame:
    # Detect file type by extension
    if input_file.endswith(".csv"):
        delimiter = ","
    elif input_file.endswith(".tsv"):
        delimiter = "\t"
    else:
        raise UnsupportedFileTypeError(input_file)

    return pd.read_csv(input_file, delimiter=delimiter)
