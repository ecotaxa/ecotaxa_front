from __future__ import annotations

import logging
from typing import List, Dict

import requests

SHEETS_QUERY_URL = "https://ecotaxoguide.imev-mer.fr/api/sheets/published-for-taxa"


def getGuideSheets(instrument_id: str, taxon_ids: List[int] = None) -> Dict[str, int]:
    try:
        rsp = requests.get(SHEETS_QUERY_URL, params={"ins_id": instrument_id, "cat_ids": taxon_ids}, timeout=5)
        guides: List[Dict[str, int|str]] = rsp.json()
        return dict([(assoc["taxon_id"], assoc["sheet_id"]) for assoc in guides])
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return {}
