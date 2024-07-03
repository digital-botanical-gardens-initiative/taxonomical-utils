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
    print(r)

    if r.status_code == 200:
        data = r.json()
        print(data)
        results = pd.DataFrame.from_dict(data).results.bindings
        df = json_normalize(results)

        # Handle duplicates by keeping only the first occurrence for each 'ott.value'
        df = df.drop_duplicates(subset=["ott.value"], keep="first")

    if r.status_code != 200:
        # raise WikidataFetchError(ott_id)
        # Handle empty results
        # Return empty df with the following columns if no results are found (ott.type,ott.value,wd.type,wd.value,img.type,img.value)
        df = pd.DataFrame(columns=["ott.type", "ott.value", "wd.type", "wd.value", "img.type", "img.value"])

    return df
