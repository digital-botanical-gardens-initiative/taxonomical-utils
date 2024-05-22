import json
import os

import pandas as pd

from taxonomical_utils.exceptions import FileDownloadError
from taxonomical_utils.resolver import main


def test_main_local_file(tmpdir):
    data_in_path = "tests/data"
    data_out_path = tmpdir
    input_filename = "sample_data.csv"
    org_column_header = "idTaxon"

    # Run the resolver
    result_df = main(data_in_path, data_out_path, input_filename, org_column_header)

    # Verify that the resulting DataFrame is not empty and contains expected columns
    assert not result_df.empty
    assert "idTaxon" in result_df.columns
    assert "matched_name" in result_df.columns

    # Check intermediate JSON output
    json_filepath = os.path.join(data_out_path, "sample_data_organisms.json")
    assert os.path.isfile(json_filepath)

    with open(json_filepath) as f:
        json_data = json.load(f)

    assert "results" in json_data
    assert "unmatched_names" in json_data

    # Example check for specific resolved data in JSON
    matched_names = [match["matched_name"] for result in json_data["results"] for match in result["matches"]]
    assert "Abelia mosanensis" in matched_names
    assert "Abies nordmanniana" in matched_names

    # Check final CSV output
    csv_filepath = os.path.join(data_out_path, "sample_data_treated.csv")
    assert os.path.isfile(csv_filepath)

    treated_df = pd.read_csv(csv_filepath)
    assert not treated_df.empty
    assert "idTaxon" in treated_df.columns
    assert "matched_name" in treated_df.columns

    # Print idTaxon values for debugging
    print("idTaxon values:", treated_df["idTaxon"].tolist())

    # Verify the correctness of other taxonomical fields with partial matching
    idTaxon_normalized = treated_df["idTaxon"].str.strip().str.lower()
    assert any("abies nordmanniana" in taxon for taxon in idTaxon_normalized)

    abies_nordmanniana_row = treated_df[idTaxon_normalized.str.contains("abies nordmanniana")]
    assert not abies_nordmanniana_row.empty
    assert not abies_nordmanniana_row["is_synonym"].values[0]  # Use `assert not` for False value


def test_main_missing_file():
    data_in_path = "tests/data"
    data_out_path = "tests/data"
    input_filename = "missing_file.csv"
    org_column_header = "idTaxon"

    try:
        main(data_in_path, data_out_path, input_filename, org_column_header)
    except FileDownloadError as e:
        assert str(e) == "The file tests/data/missing_file.csv does not exist."
