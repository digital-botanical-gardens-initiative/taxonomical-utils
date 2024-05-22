import requests


def switch_downloader(switch_id: str, path_to_file: str, timeout: int = 30) -> None:
    """Downloads a switch file if given a switch id
    Args:
        switch_id (string): a SWITCH Drive id
        path_to_file (string): local path to save the downloaded file
        timeout (int): timeout in seconds for the request
    Returns:
        nothing
    """
    switch_url = f"https://drive.switch.ch/index.php/s/{switch_id}/download"
    response = requests.get(switch_url, timeout=timeout)
    response.raise_for_status()  # Check if the request was successful

    with open(path_to_file, "wb") as file:
        file.write(response.content)
