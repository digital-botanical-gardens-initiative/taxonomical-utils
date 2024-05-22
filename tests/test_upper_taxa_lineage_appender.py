from taxonomical_utils.upper_taxa_lineage_appender import append_upper_taxa_lineage


def test_append_upper_taxa_lineage():
    input_filename = "tests/data/sample_data_treated.csv"
    output_filename = "tests/data/sample_data_upper_taxo.csv"

    result_df = append_upper_taxa_lineage(input_file=input_filename, output_file=output_filename)

    assert not result_df.empty
    assert "organism_otol_kingdom" in result_df.columns
    assert "organism_otol_phylum" in result_df.columns
    assert "organism_otol_class" in result_df.columns
    assert "organism_otol_order" in result_df.columns
    assert "organism_otol_family" in result_df.columns
    assert "organism_otol_genus" in result_df.columns
    assert "organism_otol_species" in result_df.columns


# Run the test
if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
