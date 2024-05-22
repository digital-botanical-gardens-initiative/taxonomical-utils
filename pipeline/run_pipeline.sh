#!/bin/bash

# Resolve Taxa
poetry run taxonomical-utils resolve --input-file data/in/metadata_final_sub.csv --output-file data/out/metadata_final_sub_treated.csv --org-column-header idTaxon

# Append Upper Taxa Lineage
poetry run taxonomical-utils append-taxonomy --input-file data/out/metadata_final_sub_treated.csv --output-file data/out/metadata_final_sub_upper_taxo.csv

# Merge Resolved Taxa with Upper Taxa Lineage
poetry run taxonomical-utils merge --input-file data/in/metadata_final_sub.csv --resolved-taxa-file data/out/metadata_final_sub_treated.csv --upper-taxa-lineage-file data/out/metadata_final_sub_upper_taxo.csv --output-file data/out/metadata_final_sub_final_output.csv --org-column-header idTaxon
