from __future__ import annotations

import logging
from typing import List, Dict, Optional, Any

import requests

SHEETS_QUERY_URL = "https://ecotaxoguide.imev-mer.fr/api/sheets/published-for-taxa"


def getGuideSheets(
    instrument_id: str, taxon_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
    """Published guide sheet id by taxon id, keys are str as callers look up str(taxon.id)"""
    params: Dict[str, Any] = {"ins_id": instrument_id, "cat_ids": taxon_ids}
    try:
        rsp = requests.get(SHEETS_QUERY_URL, params=params, timeout=15)
        guides: List[Dict[str, Any]] = rsp.json()
        return {str(assoc["taxon_id"]): assoc["sheet_id"] for assoc in guides}
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return {}
