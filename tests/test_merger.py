import os

import pandas as pd
import pytest

from taxonomical_utils.merger import merge_files


@pytest.mark.order("last")
def test_merge_files():
    input_file = "tests/data/sample_data.csv"
    output_file = "tests/data/merged_output.csv"
    org_column_header = "idTaxon"
    resolved_taxa_file = "tests/data/sample_data_treated.csv"
    upper_taxa_lineage_file = "tests/data/sample_data_upper_taxo.csv"
    wd_file = "tests/data/sample_data_wd.csv"
    delimiter = ","

    merge_files(
        input_file=input_file,
        output_file=output_file,
        org_column_header=org_column_header,
        delimiter=delimiter,
        resolved_taxa_file=resolved_taxa_file,
        upper_taxa_lineage_file=upper_taxa_lineage_file,
        wd_file=wd_file,
    )

    merged_df = pd.read_csv(output_file)

    # Check that the file is not empty
    assert not merged_df.empty

    # Check for the presence of prefixed columns
    assert any(col.startswith("otl_") for col in merged_df.columns)
    assert any(col.startswith("wd_") for col in merged_df.columns)

    # Check that original columns are still present
    assert org_column_header in merged_df.columns


@pytest.mark.order("last")
def test_merge_files_remove_intermediates(tmpdir):
    # Create temporary input files
    input_file = tmpdir.join("input_file.csv")
    resolved_taxa_file = tmpdir.join("resolved_taxa_file.csv")
    upper_taxa_lineage_file = tmpdir.join("upper_taxa_lineage_file.csv")
    wd_file = tmpdir.join("wd_file.csv")
    output_file = tmpdir.join("output_file.csv")

    # Sample data
    input_data = {"org_column": ["A", "B", "C"], "other_column": [1, 2, 3]}
    resolved_taxa_data = {"search_string": ["A", "B", "C"], "taxon.ott_id": [10, 20, 30]}
    upper_taxa_lineage_data = {"ott_id": [10, 20, 30], "lineage_column": ["L1", "L2", "L3"]}
    wd_data = {"ott.value": [10, 20, 30], "wd_column": ["W1", "W2", "W3"]}

    # Write data to temporary files
    pd.DataFrame(input_data).to_csv(input_file, index=False)
    pd.DataFrame(resolved_taxa_data).to_csv(resolved_taxa_file, index=False)
    pd.DataFrame(upper_taxa_lineage_data).to_csv(upper_taxa_lineage_file, index=False)
    pd.DataFrame(wd_data).to_csv(wd_file, index=False)

    # Call merge_files with remove_intermediate=True
    merge_files(
        input_file=str(input_file),
        output_file=str(output_file),
        org_column_header="org_column",
        resolved_taxa_file=str(resolved_taxa_file),
        upper_taxa_lineage_file=str(upper_taxa_lineage_file),
        wd_file=str(wd_file),
        remove_intermediate=True,
    )

    # Check that the output file exists
    assert os.path.exists(output_file)

    # Check that intermediate files are removed
    assert not os.path.exists(resolved_taxa_file)
    assert not os.path.exists(upper_taxa_lineage_file)
    assert not os.path.exists(wd_file)
    assert os.path.exists(input_file)

    # Check the contents of the output file
    output_df = pd.read_csv(output_file)
    print(output_df)
    assert "org_column" in output_df.columns
    assert "otl_search_string" in output_df.columns
    assert "otl_ott_id" in output_df.columns
    assert "wd_wd_column" in output_df.columns
