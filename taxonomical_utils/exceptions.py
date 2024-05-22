class FileDownloadError(Exception):
    def __init__(self, path_to_file: str):
        message = f"The file {path_to_file} does not exist."
        super().__init__(message)
