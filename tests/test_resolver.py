import json
import os

import pandas as pd
import pytest

from taxonomical_utils.exceptions import FileDownloadError
from taxonomical_utils.resolver import resolve_taxa


def test_main_local_file(tmpdir):
    data_in_path = "tests/data/sample_data.csv"
    data_out_path = tmpdir.join("sample_data_treated.csv")
    org_column_header = "idTaxon"

    # Run the resolver
    result_df = resolve_taxa(
        input_file=data_in_path, output_file=str(data_out_path), org_column_header=org_column_header
    )

    # Verify that the resulting DataFrame is not empty and contains expected columns
    assert not result_df.empty
    assert "idTaxon" not in result_df.columns
    assert "matched_name" in result_df.columns

    # Check intermediate JSON output
    json_filepath = f"{os.path.splitext(data_in_path)[0]}_organisms.json"
    assert os.path.isfile(json_filepath)

    with open(json_filepath) as f:
        json_data = json.load(f)

    assert "results" in json_data
    assert "unmatched_names" in json_data

    # Example check for specific resolved data in JSON
    matched_names = [match["matched_name"] for result in json_data["results"] for match in result["matches"]]
    assert "Abelia mosanensis" in matched_names
    assert "Abies nordmanniana" in matched_names
    assert "Nana" not in matched_names

    # Check final CSV output
    treated_df = pd.read_csv(str(data_out_path))
    assert not treated_df.empty
    assert "idTaxon" not in treated_df.columns
    assert "matched_name" in treated_df.columns

    # Print search_string values for debugging
    print("search_string values:", treated_df["search_string"].tolist())

    # Verify the correctness of other taxonomical fields with partial matching
    search_string_normalized = treated_df["search_string"].str.strip().str.lower()
    assert any("abies nordmanniana" in taxon for taxon in search_string_normalized)

    abies_nordmanniana_row = treated_df[search_string_normalized.str.contains("abies nordmanniana")]
    assert not abies_nordmanniana_row.empty
    assert not abies_nordmanniana_row["is_synonym"].values[0]  # Use `assert not` for False value


def test_main_missing_file():
    data_in_path = "tests/data/missing_file.csv"
    data_out_path = "tests/data/missing_file_treated.csv"
    org_column_header = "idTaxon"

    with pytest.raises(FileDownloadError) as excinfo:
        resolve_taxa(input_file=data_in_path, output_file=data_out_path, org_column_header=org_column_header)
    assert str(excinfo.value) == f"The file {data_in_path} does not exist."


# Run the test
if __name__ == "__main__":
    pytest.main([__file__])
