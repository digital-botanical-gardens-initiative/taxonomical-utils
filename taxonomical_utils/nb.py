from typing import Optional

import pandas as pd

from taxonomical_utils.processor import process_species_list
from taxonomical_utils.wikidata_fetcher import wd_taxo_fetcher_from_ott

url = "https://query.wikidata.org/sparql"
ott_id = 514975  # Example ott_id
wd_taxo_fetcher_from_ott(url, ott_id)

input_file = "tests/data/sample_data.csv"
output_file = "tests/data/merged_output.csv"
org_column_header = "idTaxon"
resolved_taxa_file = "tests/data/sample_data_treated.csv"
upper_taxa_lineage_file = "tests/data/sample_data_upper_taxo.csv"
wd_file = "tests/data/sample_data_wd.csv"
delimiter = ","


def merge_files(
    input_file: str,
    output_file: str,
    org_column_header: str,
    resolved_taxa_file: Optional[str] = None,
    upper_taxa_lineage_file: Optional[str] = None,
    wd_file: Optional[str] = None,
) -> None:
    input_df = pd.read_csv(input_file, delimiter=delimiter)

    # Process the species list in the input file
    input_df = process_species_list(input_file, org_column_header)

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

    input_df.to_csv(output_file, sep=delimiter, index=False)


merge_files(
    input_file=input_file,
    output_file=output_file,
    org_column_header=org_column_header,
    resolved_taxa_file=resolved_taxa_file,
    upper_taxa_lineage_file=upper_taxa_lineage_file,
    wd_file=wd_file,
)
