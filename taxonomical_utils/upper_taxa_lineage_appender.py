import json
from typing import Any, Dict, List

import pandas as pd
from opentree import OT
from pandas import json_normalize


# Define the utility functions
def save_json(data: Any, filename: str) -> None:
    with open(filename, "w") as f:
        json.dump(data, f)


def load_json(filename: str) -> Any:
    with open(filename) as f:
        return json.load(f)


def convert_ott_ids_to_int(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    df[column_name] = df[column_name].astype("Int64")
    return df


def get_unique_ott_ids(df: pd.DataFrame, column_name: str) -> List[int]:
    return list(df[column_name].dropna().astype("int"))


def fetch_taxon_info(ott_ids: List[int]) -> List[Dict[str, Any]]:
    taxon_info = []
    for ott_id in ott_ids:
        query = OT.taxon_info(ott_id, include_lineage=True)
        taxon_info.append(query.response_dict)
    return taxon_info


def extract_lineage(json_data: List[Dict[str, Any]]) -> pd.DataFrame:
    return json_normalize(
        json_data,
        record_path=["lineage"],
        meta=["ott_id", "unique_name", "flags", "rank"],
        record_prefix="sub_",
        errors="ignore",
    )


def pivot_taxonomy(df: pd.DataFrame, value_column: str, suffix: str = "") -> pd.DataFrame:
    pivot_df = df.pivot(index="ott_id", columns="sub_rank", values=value_column)
    if suffix:
        pivot_df = pivot_df.add_suffix(suffix)
    return pivot_df


def merge_taxonomy_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(df1, df2, how="left", on="ott_id")


def add_lowest_taxon_rank(df: pd.DataFrame) -> pd.DataFrame:
    for index, row in df.iterrows():
        rank = row["rank"]
        unique_name_col = f"{rank}"
        ott_id_col = f"{rank}_ott_id"
        df.at[index, unique_name_col] = row["unique_name"]
        df.at[index, ott_id_col] = row["ott_id"]
    return df


def rename_columns(df: pd.DataFrame, renaming_dict: Dict[str, str]) -> pd.DataFrame:
    return df.rename(columns=renaming_dict)


# Main function to append upper taxonomy lineage
def append_upper_taxa_lineage(input_file: str, output_file: str) -> pd.DataFrame:
    # Load the merged dataframe from the input file
    merged_df = pd.read_csv(input_file, sep=",", encoding="utf-8")

    # Convert ott_ids to int
    merged_df = convert_ott_ids_to_int(merged_df, "taxon.ott_id")
    ott_list = get_unique_ott_ids(merged_df, "taxon.ott_id")

    # Fetch taxon info
    taxon_info = fetch_taxon_info(ott_list)

    # Save taxon info to JSON
    # We keep the original input file name, strip the extension and add "_taxon_info.json" to it

    input_file_no_ext = input_file.split(".")[0]

    taxon_info_filename = f"{input_file_no_ext}_taxon_info.json"
    save_json(taxon_info, taxon_info_filename)

    # Load and normalize JSON
    json_data = load_json(taxon_info_filename)

    df_tax_lineage_filtered = extract_lineage(json_data)

    # Filter and pivot taxonomy data
    df_tax_lineage_filtered = df_tax_lineage_filtered.groupby(["ott_id", "sub_rank"], as_index=False).last()
    df_tax_lineage_filtered_flat = pivot_taxonomy(df_tax_lineage_filtered, "sub_name")
    df_tax_lineage_filtered_flat_ott_ids = pivot_taxonomy(df_tax_lineage_filtered, "sub_ott_id", "_ott_id")

    # Add species name and remove duplicates
    df_tax_lineage_filtered_flat = merge_taxonomy_dataframes(
        df_tax_lineage_filtered_flat, df_tax_lineage_filtered[["ott_id", "unique_name"]]
    )
    df_tax_lineage_filtered_flat.drop_duplicates(subset=["ott_id", "unique_name"], inplace=True)

    # Merge taxonomy IDs
    df_tax_lineage_filtered_flat_full = merge_taxonomy_dataframes(
        df_tax_lineage_filtered_flat, df_tax_lineage_filtered_flat_ott_ids
    )

    # Drop duplicates and handle flags and ranks
    df_tax_lineage_filtered["flags_tuple"] = df_tax_lineage_filtered["flags"].apply(lambda x: tuple(x))
    df_tax_lineage_filtered_sub = df_tax_lineage_filtered.drop_duplicates(
        subset=["ott_id", "flags_tuple", "rank"], keep="first", ignore_index=False
    )

    # Merge with ranks
    merged = merge_taxonomy_dataframes(
        df_tax_lineage_filtered_flat_full, df_tax_lineage_filtered_sub[["ott_id", "flags", "rank"]]
    )
    merged = add_lowest_taxon_rank(merged)

    # Rename columns
    renaming_dict = {
        "kingdom": "organism_otol_kingdom",
        "phylum": "organism_otol_phylum",
        "class": "organism_otol_class",
        "order": "organism_otol_order",
        "family": "organism_otol_family",
        "genus": "organism_otol_genus",
        "species": "organism_otol_species",
        "unique_name": "organism_otol_unique_name",
        "kingdom_ott_id": "organism_otol_kingdom_ott_id",
        "phylum_ott_id": "organism_otol_phylum_ott_id",
        "class_ott_id": "organism_otol_class_ott_id",
        "order_ott_id": "organism_otol_order_ott_id",
        "family_ott_id": "organism_otol_family_ott_id",
        "genus_ott_id": "organism_otol_genus_ott_id",
        "species_ott_id": "organism_otol_species_ott_id",
    }
    merged = rename_columns(merged, renaming_dict)

    # Ensure all necessary columns are present
    required_columns = [
        "ott_id",
        "organism_otol_kingdom",
        "organism_otol_phylum",
        "organism_otol_class",
        "organism_otol_order",
        "organism_otol_family",
        "organism_otol_genus",
        "organism_otol_species",
        "organism_otol_unique_name",
        "organism_otol_kingdom_ott_id",
        "organism_otol_phylum_ott_id",
        "organism_otol_class_ott_id",
        "organism_otol_order_ott_id",
        "organism_otol_family_ott_id",
        "organism_otol_genus_ott_id",
        "organism_otol_species_ott_id",
    ]
    for column in required_columns:
        if (column not in merged.columns) or (merged[column].isnull().all()):
            merged[column] = pd.NA

    # Reorder columns as listed above and keep any additional columns
    merged = merged[required_columns + [col for col in merged.columns if col not in required_columns]]

    # Save to CSV
    merged.to_csv(output_file, sep=",", index=False, encoding="utf-8")

    return merged
