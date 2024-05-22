from typing import Any, Dict, List

import pandas as pd
from opentree import OT


def process_species_list(
    path_to_input_file: str, org_column_header: str = "source_taxon", delimiter: str = ","
) -> pd.DataFrame:
    species_list_df = pd.read_csv(path_to_input_file, sep=delimiter, encoding="utf-8")
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
