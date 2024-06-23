from typing import Optional

import click
import pandas as pd

from taxonomical_utils.merger import merge_files
from taxonomical_utils.resolver import resolve_taxa
from taxonomical_utils.upper_taxa_lineage_appender import append_upper_taxa_lineage
from taxonomical_utils.wikidata_fetcher import wd_taxo_fetcher_from_ott


@click.group()
def cli() -> None:
    pass


@click.command()
@click.option("--input-file", required=True, type=click.Path(exists=True), help="Path to the input file.")
@click.option("--output-file", required=True, type=click.Path(), help="Path to the output file.")
@click.option("--org-column-header", required=True, type=str, help="Column header for the organism.")
def resolve(input_file: str, output_file: str, org_column_header: str) -> None:
    resolve_taxa(input_file, output_file, org_column_header)


@click.command()
@click.option("--input-file", required=True, type=click.Path(exists=True), help="Path to the input file.")
@click.option("--output-file", required=True, type=click.Path(), help="Path to the output file.")
def append_taxonomy(input_file: str, output_file: str) -> None:
    append_upper_taxa_lineage(input_file, output_file)


@click.command()
@click.option("--input-file", required=True, type=click.Path(exists=True), help="Path to the input file.")
@click.option("--output-file", required=True, type=click.Path(), help="Path to the output file.")
def append_wd_id(input_file: str, output_file: str) -> None:
    url = "https://query.wikidata.org/sparql"
    input_df = pd.read_csv(input_file)
    results = []
    for ott_id in input_df["ott_id"]:
        result_df = wd_taxo_fetcher_from_ott(url, ott_id)
        results.append(result_df)
    final_df = pd.concat(results, ignore_index=True)
    final_df.to_csv(output_file, index=False)


@click.command()
@click.option("--input-file", required=True, type=click.Path(exists=True), help="Path to the input file.")
@click.option("--output-file", required=True, type=click.Path(), help="Path to the output file.")
@click.option("--org-column-header", required=True, type=str, help="Column header for the organism.")
@click.option("--delimiter", default=",", type=str, help="Delimiter of the input file.")
@click.option("--resolved-taxa-file", type=click.Path(exists=True), help="Path to the resolved taxa file.")
@click.option("--upper-taxa-lineage-file", type=click.Path(exists=True), help="Path to the upper taxa lineage file.")
@click.option("--wd-file", type=click.Path(exists=True), help="Path to the Wikidata ID file.")
def merge(
    input_file: str,
    output_file: str,
    org_column_header: str,
    delimiter: str,
    resolved_taqa_file: Optional[str] = None,
    upper_taxa_lineage_file: Optional[str] = None,
    wd_file: Optional[str] = None,
) -> None:
    merge_files(
        input_file, output_file, org_column_header, delimiter, resolved_taqa_file, upper_taxa_lineage_file, wd_file
    )


cli.add_command(resolve)
cli.add_command(append_taxonomy)
cli.add_command(append_wd_id)
cli.add_command(merge)

if __name__ == "__main__":
    cli()
