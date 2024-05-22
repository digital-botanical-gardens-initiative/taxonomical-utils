import pandas as pd

from taxonomical_utils.processor import process_species_list


def merge_files(
    input_file: str,
    resolved_taxa_file: str,
    upper_taxa_lineage_file: str,
    output_file: str,
    org_column_header: str,
    delimiter: str = ",",
) -> pd.DataFrame:
    # Process the species list in the input file
    processed_species_list_df = process_species_list(input_file, org_column_header, delimiter)

    # Load the resolved taxa file and upper taxa lineage file
    resolved_taxa_df = pd.read_csv(resolved_taxa_file)
    upper_taxa_lineage_df = pd.read_csv(upper_taxa_lineage_file)

    # Merge the resolved taxa file and upper taxa lineage file on 'taxon.ott_id' and 'ott_id'
    merged_taxa_df = pd.merge(
        resolved_taxa_df, upper_taxa_lineage_df, left_on="taxon.ott_id", right_on="ott_id", how="left"
    )

    # Merge the input dataframe with the merged taxa dataframe
    final_df = pd.merge(
        processed_species_list_df,
        merged_taxa_df,
        left_on="taxon_search_string",
        right_on="search_string",
        how="left",
        suffixes=("_input", "_merged"),
    )

    # Save the final dataframe to the output file
    final_df.to_csv(output_file, sep=",", index=False, encoding="utf-8")

    return final_df
