from typing import Optional

import click

from .resolver import main


@click.command()
@click.option("--data-in-path", default="./data/in/", help="Input data directory path.")
@click.option("--data-out-path", default="./data/out/fibl/", help="Output data directory path.")
@click.option("--input-filename", default="metadata_final.csv", help="Input filename with extension.")
@click.option("--org-column-header", default="source_taxon", help="Column header for the original taxon names.")
@click.option("--delimiter", default=None, help="Delimiter used in the input file.")
@click.option("--switch-id", default=None, help="Switch Drive ID for downloading the file.")
def cli(
    data_in_path: str,
    data_out_path: str,
    input_filename: str,
    org_column_header: str,
    delimiter: Optional[str],
    switch_id: Optional[str],
) -> None:
    main(data_in_path, data_out_path, input_filename, org_column_header, delimiter, switch_id)


if __name__ == "__main__":
    cli()
