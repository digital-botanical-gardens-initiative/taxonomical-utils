import pandas as pd
import requests
from pandas import json_normalize


def wd_taxo_fetcher_from_ott(url: str, ott_id: int) -> pd.DataFrame:
    query = f"""
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    SELECT ?ott ?wd ?img
    WHERE{{
        ?wd wdt:P9157 ?ott
        OPTIONAL{{ ?wd wdt:P18 ?img }}
        VALUES ?ott {{'{ott_id}'}}
    }}
    """

    r = requests.get(url, params={"format": "json", "query": query}, timeout=10)
    data = r.json()
    results = pd.DataFrame.from_dict(data).results.bindings
    df = json_normalize(results)

    # Handle duplicates by keeping only the first occurrence for each 'ott.value'
    df = df.drop_duplicates(subset=["ott.value"], keep="first")

    return df
