#!/bin/bash

# Resolve Taxa
poetry run taxonomical-utils resolve --input-file data/in/example.csv --output-file data/out/example_resolved.csv --org-column-header idTaxon

# Append Upper Taxa Lineage
poetry run taxonomical-utils append-taxonomy --input-file data/out/example_resolved.csv --output-file data/out/example_upper_taxo.csv

# Merge Resolved Taxa with Upper Taxa Lineage
poetry run taxonomical-utils merge --input-file data/in/example.csv --resolved-taxa-file data/out/example_resolved.csv --upper-taxa-lineage-file data/out/example_upper_taxo.csv --output-file data/out/example_final_output.csv --org-column-header idTaxon
