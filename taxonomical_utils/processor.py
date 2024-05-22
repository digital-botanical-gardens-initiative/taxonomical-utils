import json
from typing import Any, Dict, List, Tuple

import pandas as pd
from opentree import OT
from pandas import json_normalize


def process_species_list(
    path_to_input_file: str, org_column_header: str = "source_taxon", delimiter: str = "\t"
) -> pd.DataFrame:
    species_list_df = pd.read_csv(path_to_input_file, sep=delimiter, encoding="unicode_escape")
    species_list_df[org_column_header].dropna(inplace=True)
    species_list_df[org_column_header] = species_list_df[org_column_header].str.lower()
    species_list_df[org_column_header] = species_list_df[org_column_header].str.replace(r" sp", "", regex=True)
    species_list_df[org_column_header] = species_list_df[org_column_header].str.replace(r" x ", " ", regex=True)
    species_list_df[org_column_header] = species_list_df[org_column_header].str.replace(r" x$", "", regex=True)

    return species_list_df


def resolve_organisms(organisms: List[str]) -> Dict[str, Any]:
    results: Dict[str, Any] = {"results": [], "unmatched_names": []}
    for organism in organisms:
        match = OT.tnrs_match([organism], context_name=None, do_approximate_matching=True, include_suppressed=False)
        results["results"].extend(match.response_dict["results"])
        results["unmatched_names"].extend(match.response_dict["unmatched_names"])
    return results


def save_json(data: Dict[str, Any], filepath: str) -> None:
    with open(filepath, "w") as out:
        json.dump(data, out, indent=2, sort_keys=True)


def load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath) as tmpfile:
        data: Dict[str, Any] = json.load(tmpfile)
        return data


def normalize_json(json_data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    matches = json_normalize(json_data, record_path=["results", "matches"])
    unmatched = json_normalize(json_data, record_path=["unmatched_names"])
    return matches, unmatched
