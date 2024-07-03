import os

import pandas as pd

from taxonomical_utils.wikidata_fetcher import wd_taxo_fetcher_from_ott


def test_wd_taxo_fetcher_from_ott():
    url = "https://query.wikidata.org/sparql"
    input_file = "tests/data/sample_data_treated.csv"
    output_file = "tests/data/sample_data_wd.csv"

    # Load the input file
    input_df = pd.read_csv(input_file)

    # Ensure the input DataFrame contains the 'taxon.ott_id' column
    assert "taxon.ott_id" in input_df.columns

    # Fetch data for all OTT IDs
    results = []
    for ott_id in input_df["taxon.ott_id"]:
        print(f"Fetching data for OTT ID: {ott_id}")
        result_df = wd_taxo_fetcher_from_ott(url, ott_id)
        print(result_df)
        results.append(result_df)

    # Concatenate all results into a single DataFrame
    final_df = pd.concat(results, ignore_index=True)

    # Verify the DataFrame is not empty
    assert not final_df.empty

    # Write the output to a file
    final_df.to_csv(output_file, index=False)

    # Verify the output file exists
    assert os.path.isfile(output_file)

    # Read the output file and check its contents
    output_df = pd.read_csv(output_file)
    assert not output_df.empty
    assert "ott.value" in output_df.columns
    assert "wd.value" in output_df.columns

    # Print the contents for debugging
    print(output_df)


if __name__ == "__main__":
    test_wd_taxo_fetcher_from_ott()
