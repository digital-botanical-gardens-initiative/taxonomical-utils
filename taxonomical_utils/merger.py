import os
from typing import Optional

import pandas as pd

from taxonomical_utils.processor import process_species_list


def merge_files(
    input_file: str,
    output_file: str,
    org_column_header: str,
    delimiter: str = ",",
    resolved_taxa_file: Optional[str] = None,
    upper_taxa_lineage_file: Optional[str] = None,
    wd_file: Optional[str] = None,
    remove_intermediate: bool = False,
) -> pd.DataFrame:
    input_df = pd.read_csv(input_file, delimiter=delimiter)

    # Process the species list in the input file
    input_df = process_species_list(input_file, org_column_header, delimiter)

    if resolved_taxa_file:
        resolved_taxa_df = pd.read_csv(resolved_taxa_file)
        resolved_taxa_df = resolved_taxa_df.add_prefix("otl_")
        input_df = pd.merge(
            input_df, resolved_taxa_df, left_on="taxon_search_string", right_on="otl_search_string", how="left"
        )

    if upper_taxa_lineage_file and "otl_taxon.ott_id" in input_df.columns:
        upper_taxa_lineage_df = pd.read_csv(upper_taxa_lineage_file)
        upper_taxa_lineage_df = upper_taxa_lineage_df.add_prefix("otl_")
        input_df = pd.merge(
            input_df, upper_taxa_lineage_df, left_on="otl_taxon.ott_id", right_on="otl_ott_id", how="left"
        )

    if wd_file and "otl_taxon.ott_id" in input_df.columns:
        wd_df = pd.read_csv(wd_file)
        wd_df = wd_df.add_prefix("wd_")
        input_df = pd.merge(input_df, wd_df, left_on="otl_taxon.ott_id", right_on="wd_ott.value", how="left")

    input_df.to_csv(output_file, index=False, sep=delimiter)

    if remove_intermediate:
        if resolved_taxa_file and os.path.exists(resolved_taxa_file):
            os.remove(resolved_taxa_file)
        if upper_taxa_lineage_file and os.path.exists(upper_taxa_lineage_file):
            os.remove(upper_taxa_lineage_file)
        if wd_file and os.path.exists(wd_file):
            os.remove(wd_file)

    return input_df
