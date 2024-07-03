class FileDownloadError(Exception):
    def __init__(self, path_to_file: str):
        message = f"The file {path_to_file} does not exist."
        super().__init__(message)


class ColumnNotFoundError(Exception):
    def __init__(self, column_name: str):
        message = f"The specified column '{column_name}' does not exist in the input file."
        super().__init__(message)
