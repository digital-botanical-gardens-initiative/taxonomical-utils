import os
from typing import Optional

import pandas as pd

from .downloader import switch_downloader
from .exceptions import FileDownloadError
from .processor import load_json, normalize_json, process_species_list, resolve_organisms, save_json


def main(
    data_in_path: str,
    data_out_path: str,
    input_filename: str,
    org_column_header: str,
    delimiter: Optional[str] = None,
    switch_id: Optional[str] = None,
) -> pd.DataFrame:
    # Define paths
    path_to_input_file = os.path.join(data_in_path, input_filename)
    organisms_tnrs_matched_filename = os.path.join(
        data_out_path, f"{os.path.splitext(input_filename)[0]}_organisms.json"
    )

    # Download file from Switch if switch_id is provided, else use local file
    if switch_id:
        switch_downloader(switch_id, path_to_input_file)
    elif not os.path.isfile(path_to_input_file):
        raise FileDownloadError(path_to_file=path_to_input_file)

    # Detect file type by extension if delimiter is not specified
    delimiter = "," if input_filename.endswith(".csv") else "\t" if delimiter is None else delimiter

    # Process species list
    species_list_df = process_species_list(path_to_input_file, org_column_header, delimiter)

    # Resolve organisms
    organisms = species_list_df["taxon_search_string"].unique().tolist()
    organisms_tnrs_matched = resolve_organisms(organisms)

    # Save matched organisms to json
    save_json(organisms_tnrs_matched, organisms_tnrs_matched_filename)

    # Load and normalize json
    json_data = load_json(organisms_tnrs_matched_filename)
    df_organism_tnrs_matched, df_organism_tnrs_unmatched = normalize_json(json_data)

    # Process the results and update the dataframe
    df_organism_tnrs_matched.sort_values(["search_string", "is_synonym"], axis=0, inplace=True)
    df_organism_tnrs_matched_unique = df_organism_tnrs_matched.drop_duplicates("search_string", keep="first")

    # Merge with the original dataframe
    merged_df = species_list_df.merge(
        df_organism_tnrs_matched_unique, how="left", left_on="taxon_search_string", right_on="search_string"
    )
    merged_df.drop_duplicates(subset=[org_column_header, "matched_name", "taxon.ott_id"], keep="first", inplace=True)

    # Save the final dataframe
    treated_filename = f"{os.path.splitext(input_filename)[0]}_treated.csv"
    merged_df.to_csv(os.path.join(data_out_path, treated_filename), sep=",", index=False)

    return merged_df
