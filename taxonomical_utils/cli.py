import click

from taxonomical_utils.merger import merge_files
from taxonomical_utils.resolver import resolve_taxa
from taxonomical_utils.upper_taxa_lineage_appender import append_upper_taxa_lineage


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
@click.option(
    "--resolved-taxa-file", required=True, type=click.Path(exists=True), help="Path to the resolved taxa file."
)
@click.option(
    "--upper-taxa-lineage-file",
    required=True,
    type=click.Path(exists=True),
    help="Path to the upper taxa lineage file.",
)
@click.option("--output-file", required=True, type=click.Path(), help="Path to the output file.")
@click.option("--org-column-header", required=True, type=str, help="Column header for the organism.")
@click.option("--delimiter", default=",", type=str, help="Delimiter of the input file.")
def merge(
    input_file: str,
    resolved_taxa_file: str,
    upper_taxa_lineage_file: str,
    output_file: str,
    org_column_header: str,
    delimiter: str,
) -> None:
    merge_files(input_file, resolved_taxa_file, upper_taxa_lineage_file, output_file, org_column_header, delimiter)


cli.add_command(resolve)
cli.add_command(append_taxonomy)
cli.add_command(merge)

if __name__ == "__main__":
    cli()
