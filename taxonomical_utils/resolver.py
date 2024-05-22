import os

import pandas as pd

from taxonomical_utils.exceptions import FileDownloadError
from taxonomical_utils.processor import process_species_list, resolve_organisms
from taxonomical_utils.shared import load_json, normalize_json_resolver, save_json


def resolve_taxa(
    input_file: str,
    output_file: str,
    org_column_header: str,
) -> pd.DataFrame:
    # Define paths
    path_to_input_file = input_file
    organisms_tnrs_matched_filename = f"{os.path.splitext(input_file)[0]}_organisms.json"

    # Check if the input file exists
    if not os.path.isfile(path_to_input_file):
        raise FileDownloadError(path_to_file=path_to_input_file)

    # Detect file type by extension if delimiter is not specified
    delimiter = "," if input_file.endswith(".csv") else "\t"

    # Process species list
    species_list_df = process_species_list(path_to_input_file, org_column_header, delimiter)

    # Resolve organisms
    organisms = species_list_df["taxon_search_string"].unique().tolist()
    organisms_tnrs_matched = resolve_organisms(organisms)

    # Save matched organisms to json
    save_json(organisms_tnrs_matched, organisms_tnrs_matched_filename)

    # Load and normalize json
    json_data = load_json(organisms_tnrs_matched_filename)
    df_organism_tnrs_matched, df_organism_tnrs_unmatched = normalize_json_resolver(json_data)

    # Process the results and update the dataframe
    df_organism_tnrs_matched.sort_values(["search_string", "is_synonym"], axis=0, inplace=True)

    # Ensure we keep all unique matches for each search_string
    df_organism_tnrs_matched_unique = df_organism_tnrs_matched.drop_duplicates(
        subset=["search_string"], keep="first"
    ).copy()

    # Drop duplicates based on the provided org_column_header
    df_organism_tnrs_matched_unique.drop_duplicates(
        subset=["search_string", "matched_name", "taxon.ott_id"], keep="first", inplace=True
    )

    # Save the final dataframe
    df_organism_tnrs_matched_unique.to_csv(output_file, sep=",", index=False, encoding="utf-8")

    return df_organism_tnrs_matched_unique
