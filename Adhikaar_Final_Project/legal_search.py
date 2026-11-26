"""Indian Kanoon legal-document search using a server-side API token."""

import html
import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


BASE_URL = "https://api.indiankanoon.org/search/"
LOGO_URL = "https://api.indiankanoon.org/static/pics/ikanoon6_powered_transparent.png"

SEARCH_TERMS = {
    "vehicle_documents": "Motor Vehicles Act driving licence registration certificate vehicle documents",
    "challan": "Motor Vehicles Act traffic challan",
    "vehicle_stop": "traffic police vehicle checking Motor Vehicles Act",
    "other_traffic": "Motor Vehicles Act traffic vehicle rules",
    "police_question": "police interaction citizen rights India",
    "police_complaint": "police complaint FIR procedure India",
    "other_police": "police powers citizen rights India",
    "detention": "arrest detention procedure safeguards BNSS",
    "arrest_rights": "arrest procedure rights BNSS India",
    "other_arrest": "arrest detention safeguards India",
    "images": "cybercrime online image threat blackmail reporting India",
    "account": "cybercrime hacked account reporting India",
    "money": "online financial cyber fraud reporting India",
}


def _token() -> str:
    try:
        return str(st.secrets.get("INDIANKANOON_API_TOKEN", os.getenv("INDIANKANOON_API_TOKEN", ""))).strip()
    except Exception:
        return os.getenv("INDIANKANOON_API_TOKEN", "").strip()


def available() -> bool:
    return bool(_token())


def query_for(scenario: str | None, cyber_type: str | None, topic: str) -> str:
    key = cyber_type if topic == "cyber" else scenario
    return SEARCH_TERMS.get(key or "", "Indian law legal rights " + topic)


def _clean_snippet(value: str) -> str:
    text = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def search(query: str) -> dict:
    token = _token()
    if not token:
        raise RuntimeError("Add INDIANKANOON_API_TOKEN to the private app settings first.")
    params = urlencode({"formInput": query, "pagenum": 0, "doctypes": "laws,madhyapradesh"})
    request = Request(
        f"{BASE_URL}?{params}",
        headers={
            "Authorization": f"Token {token}",
            "Accept": "application/json",
            "User-Agent": "ADHIKAAR classroom legal-awareness project",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 403:
            raise RuntimeError("Indian Kanoon rejected the API token. Check the private token setting.") from error
        raise RuntimeError(f"Indian Kanoon search failed (HTTP {error.code}). Check your API account and prepaid balance.") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError("Could not connect to the Indian Kanoon API. Check your internet connection and try again.") from error

    results = []
    for item in payload.get("docs", [])[:5]:
        doc_id = str(item.get("tid", ""))
        if not doc_id.isdigit():
            continue
        results.append({
            "title": _clean_snippet(str(item.get("title", "Legal document"))),
            "headline": _clean_snippet(str(item.get("headline", ""))),
            "source": _clean_snippet(str(item.get("docsource", ""))),
            "url": f"https://indiankanoon.org/doc/{doc_id}/",
        })
    return {"found": payload.get("found", 0), "results": results, "query": query}
