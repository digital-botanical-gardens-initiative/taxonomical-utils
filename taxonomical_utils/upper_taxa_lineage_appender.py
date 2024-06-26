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
    # Process the JSON data
    lineage_data = []

    for entry in json_data:
        if "lineage" in entry and entry["lineage"]:
            lineage_data.append(entry)
        else:
            # Create a fake lineage for entries with an empty lineage
            fake_lineage = [
                {
                    "name": entry["unique_name"],
                    "ott_id": entry["ott_id"],
                    "flags": entry["flags"],
                    "rank": entry["rank"],
                }
            ]
            lineage_data.append({**entry, "lineage": fake_lineage})

    # Normalize the JSON data
    df = json_normalize(
        lineage_data,
        record_path=["lineage"],
        meta=["ott_id", "unique_name", "flags", "rank"],
        record_prefix="sub_",
        errors="ignore",
    )

    return df


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
    # We keep the original input file name, strip the extension and add "_upper_taxa_lineage.json" to it

    input_file_no_ext = input_file.split(".")[0]

    taxon_info_filename = f"{input_file_no_ext}_upper_taxa_lineage.json"
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
    # renaming_dict = {
    #     "kingdom": "organism_otol_kingdom",
    #     "phylum": "organism_otol_phylum",
    #     "class": "organism_otol_class",
    #     "order": "organism_otol_order",
    #     "family": "organism_otol_family",
    #     "genus": "organism_otol_genus",
    #     "species": "organism_otol_species",
    #     "unique_name": "organism_otol_unique_name",
    #     "kingdom_ott_id": "organism_otol_kingdom_ott_id",
    #     "phylum_ott_id": "organism_otol_phylum_ott_id",
    #     "class_ott_id": "organism_otol_class_ott_id",
    #     "order_ott_id": "organism_otol_order_ott_id",
    #     "family_ott_id": "organism_otol_family_ott_id",
    #     "genus_ott_id": "organism_otol_genus_ott_id",
    #     "species_ott_id": "organism_otol_species_ott_id",
    # }

    # class
    # domain
    # family
    # forma
    # genus
    # infrakingdom
    # infraorder
    # infraphylum
    # infraspecificname
    # kingdom
    # no rank
    # no rank - terminal
    # order
    # phylum
    # section
    # species
    # species group
    # species subgroup
    # subclass
    # subdivision
    # subfamily
    # subgenus
    # subkingdom
    # suborder
    # subphylum
    # subsection
    # subspecies
    # subtribe
    # superclass
    # superfamily
    # superorder
    # tribe
    # varietas
    # variety
    renaming_dict = {
        "class": "organism_otol_class",
        "domain": "organism_otol_domain",
        "family": "organism_otol_family",
        "forma": "organism_otol_forma",
        "genus": "organism_otol_genus",
        "infrakingdom": "organism_otol_infrakingdom",
        "infraorder": "organism_otol_infraorder",
        "infraphylum": "organism_otol_infraphylum",
        "infraspecificname": "organism_otol_infraspecificname",
        "kingdom": "organism_otol_kingdom",
        "no rank": "organism_otol_no_rank",
        "no rank - terminal": "organism_otol_no_rank_terminal",
        "order": "organism_otol_order",
        "phylum": "organism_otol_phylum",
        "section": "organism_otol_section",
        "species": "organism_otol_species",
        "species group": "organism_otol_species_group",
        "species subgroup": "organism_otol_species_subgroup",
        "subclass": "organism_otol_subclass",
        "subdivision": "organism_otol_subdivision",
        "subfamily": "organism_otol_subfamily",
        "subgenus": "organism_otol_subgenus",
        "subkingdom": "organism_otol_subkingdom",
        "suborder": "organism_otol_suborder",
        "subphylum": "organism_otol_subphylum",
        "subsection": "organism_otol_subsection",
        "subspecies": "organism_otol_subspecies",
        "subtribe": "organism_otol_subtribe",
        "superclass": "organism_otol_superclass",
        "superfamily": "organism_otol_superfamily",
        "superorder": "organism_otol_superorder",
        "tribe": "organism_otol_tribe",
        "varietas": "organism_otol_varietas",
        "variety": "organism_otol_variety",
        "class_ott_id": "organism_otol_class_ott_id",
        "domain_ott_id": "organism_otol_domain_ott_id",
        "family_ott_id": "organism_otol_family_ott_id",
        "forma_ott_id": "organism_otol_forma_ott_id",
        "genus_ott_id": "organism_otol_genus_ott_id",
        "infrakingdom_ott_id": "organism_otol_infrakingdom_ott_id",
        "infraorder_ott_id": "organism_otol_infraorder_ott_id",
        "infraphylum_ott_id": "organism_otol_infraphylum_ott_id",
        "infraspecificname_ott_id": "organism_otol_infraspecificname_ott_id",
        "kingdom_ott_id": "organism_otol_kingdom_ott_id",
        "no rank_ott_id": "organism_otol_no_rank_ott_id",
        "no rank - terminal_ott_id": "organism_otol_no_rank_terminal_ott_id",
        "order_ott_id": "organism_otol_order_ott_id",
        "phylum_ott_id": "organism_otol_phylum_ott_id",
        "section_ott_id": "organism_otol_section_ott_id",
        "species_ott_id": "organism_otol_species_ott_id",
        "species group_ott_id": "organism_otol_species_group_ott_id",
        "species subgroup_ott_id": "organism_otol_species_subgroup_ott_id",
        "subclass_ott_id": "organism_otol_subclass_ott_id",
        "subdivision_ott_id": "organism_otol_subdivision_ott_id",
        "subfamily_ott_id": "organism_otol_subfamily_ott_id",
        "subgenus_ott_id": "organism_otol_subgenus_ott_id",
        "subkingdom_ott_id": "organism_otol_subkingdom_ott_id",
        "suborder_ott_id": "organism_otol_suborder_ott_id",
        "subphylum_ott_id": "organism_otol_subphylum_ott_id",
        "subsection_ott_id": "organism_otol_subsection_ott_id",
        "subspecies_ott_id": "organism_otol_subspecies_ott_id",
        "subtribe_ott_id": "organism_otol_subtribe_ott_id",
        "superclass_ott_id": "organism_otol_superclass_ott_id",
        "superfamily_ott_id": "organism_otol_superfamily_ott_id",
        "superorder_ott_id": "organism_otol_superorder_ott_id",
        "tribe_ott_id": "organism_otol_tribe_ott_id",
        "varietas_ott_id": "organism_otol_varietas_ott_id",
        "variety_ott_id": "organism_otol_variety_ott_id",
    }

    merged = rename_columns(merged, renaming_dict)

    # # Ensure all necessary columns are present
    # required_columns = [
    #     "organism_otol_kingdom",
    #     "organism_otol_phylum",
    #     "organism_otol_class",
    #     "organism_otol_order",
    #     "organism_otol_family",
    #     "organism_otol_genus",
    #     "organism_otol_species",
    #     "organism_otol_unique_name",
    #     "organism_otol_kingdom_ott_id",
    #     "organism_otol_phylum_ott_id",
    #     "organism_otol_class_ott_id",
    #     "organism_otol_order_ott_id",
    #     "organism_otol_family_ott_id",
    #     "organism_otol_genus_ott_id",
    #     "organism_otol_species_ott_id",
    # ]

    # Ensure all necessary columns are present
    required_columns = [
        "organism_otol_class",
        "organism_otol_domain",
        "organism_otol_family",
        "organism_otol_forma",
        "organism_otol_genus",
        "organism_otol_infrakingdom",
        "organism_otol_infraorder",
        "organism_otol_infraphylum",
        "organism_otol_infraspecificname",
        "organism_otol_kingdom",
        "organism_otol_no_rank",
        "organism_otol_no_rank_terminal",
        "organism_otol_order",
        "organism_otol_phylum",
        "organism_otol_section",
        "organism_otol_species",
        "organism_otol_species_group",
        "organism_otol_species_subgroup",
        "organism_otol_subclass",
        "organism_otol_subdivision",
        "organism_otol_subfamily",
        "organism_otol_subgenus",
        "organism_otol_subkingdom",
        "organism_otol_suborder",
        "organism_otol_subphylum",
        "organism_otol_subsection",
        "organism_otol_subspecies",
        "organism_otol_subtribe",
        "organism_otol_superclass",
        "organism_otol_superfamily",
        "organism_otol_superorder",
        "organism_otol_tribe",
        "organism_otol_varietas",
        "organism_otol_variety",
        "organism_otol_unique_name",
        "organism_otol_class_ott_id",
        "organism_otol_domain_ott_id",
        "organism_otol_family_ott_id",
        "organism_otol_forma_ott_id",
        "organism_otol_genus_ott_id",
        "organism_otol_infrakingdom_ott_id",
        "organism_otol_infraorder_ott_id",
        "organism_otol_infraphylum_ott_id",
        "organism_otol_infraspecificname_ott_id",
        "organism_otol_kingdom_ott_id",
        "organism_otol_no_rank_ott_id",
        "organism_otol_no_rank_terminal_ott_id",
        "organism_otol_order_ott_id",
        "organism_otol_phylum_ott_id",
        "organism_otol_section_ott_id",
        "organism_otol_species_ott_id",
        "organism_otol_species_group_ott_id",
        "organism_otol_species_subgroup_ott_id",
        "organism_otol_subclass_ott_id",
        "organism_otol_subdivision_ott_id",
        "organism_otol_subfamily_ott_id",
        "organism_otol_subgenus_ott_id",
        "organism_otol_subkingdom_ott_id",
        "organism_otol_suborder_ott_id",
        "organism_otol_subphylum_ott_id",
        "organism_otol_subsection_ott_id",
        "organism_otol_subspecies_ott_id",
        "organism_otol_subtribe_ott_id",
        "organism_otol_superclass_ott_id",
        "organism_otol_superfamily_ott_id",
        "organism_otol_superorder_ott_id",
        "organism_otol_tribe_ott_id",
        "organism_otol_varietas_ott_id",
        "organism_otol_variety_ott_id",
    ]

    for column in required_columns:
        if (column not in merged.columns) or (merged[column].isnull().all()):
            merged[column] = pd.NA

    # Reorder columns as listed above and keep any additional columns
    merged = merged[required_columns + [col for col in merged.columns if col not in required_columns]]

    # Save to CSV
    merged.to_csv(output_file, sep=",", index=False, encoding="utf-8")

    return merged
