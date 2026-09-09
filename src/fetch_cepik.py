import ssl
import json
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from pathlib import Path

MAX_ATTEMPTS = 8
REQUEST_DELAY = 2.0
VOIVODESHIP = "02"
PERIOD = "202407"
RAW_DIR = Path("data/raw")

class LegacyTLSAdapter(HTTPAdapter):
    """CEPiK API uses weak DH parameters rejected by OpenSSL 3 defaults."""

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)



def fetch_page(url):

    for attempt in range(MAX_ATTEMPTS):
        answer = session.get(url)
        status = answer.status_code
        if status == 200:
            try:
                return answer.json()
            except ValueError:
                time.sleep(2 ** attempt)
                continue
        elif status in (429, 404):
            time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"Error {status}. URL: {url}")

    raise RuntimeError(f"Error {status} after {MAX_ATTEMPTS} attempts. URL: {url}")

session = requests.Session()
session.mount("https://", LegacyTLSAdapter())
session.headers.update({"User-Agent": "polish-fleet-pipeline/0.1"})

url = "https://api.cepik.gov.pl/pojazdy?wojewodztwo=02&data-od=20240701&data-do=20240731&limit=200&page=1"
page_num = 1

RAW_DIR.mkdir(parents=True, exist_ok=True)


while url:
    path = RAW_DIR / f"pojazdy_{VOIVODESHIP}_{PERIOD}_p{page_num:04d}.json"

    if path.exists():
        page = json.loads(path.read_text(encoding="utf-8"))
        print(f"Page {page_num} - cached")
    else:
        page = fetch_page(url)
        path.write_text(json.dumps(page, ensure_ascii=False), encoding="utf-8")
        print(f"Page {page_num}, {len(page['data'])} records")
        time.sleep(REQUEST_DELAY)

    url = page["links"].get("next")
    page_num += 1

