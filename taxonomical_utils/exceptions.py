class ColumnNotFoundError(Exception):
    def __init__(self, column_name: str):
        message = f"The specified column '{column_name}' does not exist in the input file."
        super().__init__(message)


class UnsupportedFileTypeError(Exception):
    def __init__(self, path_to_file: str):
        message = f"Unsupported file type for {path_to_file}. Only .csv and .tsv files are supported. Please check your input file format."
        super().__init__(message)


class WikidataFetchError(Exception):
    def __init__(self, ott_id: int):
        message = f"Error fetching data from Wikidata for OTT ID: {ott_id}"
        super().__init__(message)
