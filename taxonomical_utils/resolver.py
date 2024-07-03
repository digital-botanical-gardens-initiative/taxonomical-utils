import pandas as pd

from taxonomical_utils.processor import process_species_list, resolve_organisms
from taxonomical_utils.shared import load_json, normalize_json_resolver, save_json


def resolve_taxa(
    input_file: str,
    output_file: str,
    org_column_header: str,
) -> pd.DataFrame:
    # Process the species list in the input file
    species_list_df = process_species_list(input_file, org_column_header)

    # Resolve organisms
    organisms = species_list_df["taxon_search_string"].unique().tolist()
    # Here also we make sure to remove NaN values
    organisms = [x for x in organisms if str(x) != "nan"]
    print(f"Resolving {len(organisms)} organisms")
    print(organisms)
    organisms_tnrs_matched = resolve_organisms(organisms)

    # Save taxon info to JSON
    # We keep the original input file name, strip the extension and add "_taxon_info.json" to it

    input_file_no_ext = input_file.split(".")[0]

    taxon_info_filename = f"{input_file_no_ext}_taxon_info.json"
    save_json(organisms_tnrs_matched, taxon_info_filename)

    # Load and normalize json
    json_data = load_json(taxon_info_filename)
    df_organism_tnrs_matched, df_organism_tnrs_unmatched = normalize_json_resolver(json_data)

    if not df_organism_tnrs_matched.empty:
        # Process the results and update the dataframe
        df_organism_tnrs_matched.sort_values(["search_string", "is_synonym"], axis=0, inplace=True)

        # Ensure we keep all unique matches for each search_string
        df_organism_tnrs_matched.drop_duplicates(subset=["search_string"], keep="first", inplace=True)

        # Drop duplicates based on the provided org_column_header
        df_organism_tnrs_matched.drop_duplicates(
            subset=["search_string", "matched_name", "taxon.ott_id"], keep="first", inplace=True
        )

        # Save the final dataframe
        df_organism_tnrs_matched.to_csv(output_file, sep=",", index=False, encoding="utf-8")

    else:
        print(f"No organisms were resolved for {organisms}")

    return df_organism_tnrs_matched
