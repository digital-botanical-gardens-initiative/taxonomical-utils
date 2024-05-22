import json
from typing import Any, Dict, List, Tuple

import pandas as pd


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
