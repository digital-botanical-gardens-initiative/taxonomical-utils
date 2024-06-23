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
