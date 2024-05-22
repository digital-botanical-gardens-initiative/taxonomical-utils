import os
from typing import Any, Dict

from taxonomical_utils.processor import process_species_list, resolve_organisms
from taxonomical_utils.shared import load_json, normalize_json_resolver, save_json


def test_process_species_list():
    input_file = "tests/data/sample_data.csv"
    df = process_species_list(input_file, org_column_header="idTaxon")
    print(df.head())  # Debug print to check the DataFrame
    assert not df.empty
    assert "idTaxon" in df.columns


def test_resolve_organisms():
    organisms = ["Abelia mosanensis Nakai", "Abelia x grandiflora (André) Rehder"]
    resolved = resolve_organisms(organisms)
    assert "results" in resolved
    assert "unmatched_names" in resolved


def test_save_load_json(tmpdir):
    data: Dict[str, Any] = {"key": "value"}
    json_file = os.path.join(tmpdir, "test.json")
    save_json(data, json_file)
    loaded_data = load_json(json_file)
    assert loaded_data == data


def test_normalize_json_resolver():
    data: Dict[str, Any] = {
        "results": [{"matches": [{"name": "Abelia mosanensis"}]}],
        "unmatched_names": ["Unknown species"],
    }
    matches, unmatched = normalize_json_resolver(data)
    assert not matches.empty
    assert not unmatched.empty
    assert "name" in matches.columns
    assert "unmatched_names" in unmatched.columns
