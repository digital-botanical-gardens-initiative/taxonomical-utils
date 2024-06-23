import os

import pandas as pd
import pytest

from taxonomical_utils.merger import merge_files


@pytest.mark.order("last")
def test_merge_files():
    # Define paths to test data files
    input_file = "tests/data/sample_data.csv"
    resolved_taxa_file = "tests/data/sample_data_treated.csv"
    upper_taxa_lineage_file = "tests/data/sample_data_upper_taxo.csv"
    output_file = "tests/data/sample_data_final_output.csv"
    org_column_header = "idTaxon"

    # Run the merger
    result_df = merge_files(input_file, resolved_taxa_file, upper_taxa_lineage_file, output_file, org_column_header)

    # Verify the resulting DataFrame is not empty and contains expected columns
    assert not result_df.empty
    assert "idTaxon" in result_df.columns
    assert "matched_name" in result_df.columns
    assert "organism_otol_kingdom" in result_df.columns

    # Check the output file exists
    assert os.path.isfile(output_file)

    # Load the output file to verify its content
    final_df = pd.read_csv(output_file, encoding="utf-8-sig")

    # Verify the content of the output file
    assert not final_df.empty
    assert "idTaxon" in final_df.columns
    assert "matched_name" in final_df.columns
    assert "organism_otol_kingdom" in final_df.columns
    assert (
        final_df[final_df["idTaxon"] == "Abelia mosanensis"]["organism_otol_species"].values[0] == "Zabelia mosanensis"
    )
    assert (
        final_df[final_df["idTaxon"] == "Abelia x grandiflora (André) Rehder"]["organism_otol_species"].values[0]
        == "Abelia x grandiflora"
    )
