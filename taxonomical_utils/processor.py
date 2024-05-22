import json
from typing import Any, Dict, List, Tuple

import pandas as pd
from opentree import OT
from pandas import json_normalize


def process_species_list(
    path_to_input_file: str, org_column_header: str = "source_taxon", delimiter: str = ","
) -> pd.DataFrame:
    species_list_df = pd.read_csv(path_to_input_file, sep=delimiter, encoding="unicode_escape")
    print("Columns in DataFrame:", species_list_df.columns.tolist())  # Debug print
    species_list_df.columns = species_list_df.columns.str.strip()  # Strip any leading/trailing whitespace
    # First, we copy the original column to a new column with a standardized name
    species_list_df["taxon_search_string"] = species_list_df[org_column_header]
    species_list_df["taxon_search_string"].dropna(inplace=True)
    species_list_df["taxon_search_string"] = species_list_df["taxon_search_string"].str.lower()
    species_list_df["taxon_search_string"] = species_list_df["taxon_search_string"].str.replace(r" sp ", "", regex=True)
    species_list_df["taxon_search_string"] = species_list_df["taxon_search_string"].str.replace(r" x ", " ", regex=True)
    species_list_df["taxon_search_string"] = species_list_df["taxon_search_string"].str.replace(r" x$", "", regex=True)
    # Here the first two words are taken as the genus and species
    species_list_df["taxon_search_string"] = species_list_df["taxon_search_string"].str.split().str[:2].str.join(" ")

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
    unmatched = pd.DataFrame(json_data["unmatched_names"], columns=["unmatched_names"])
    return matches, unmatched
