import ssl
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

MAX_RANGE = 8

class LegacyTLSAdapter(HTTPAdapter):
    """CEPiK API uses weak DH parameters rejected by OpenSSL 3 defaults."""

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


session = requests.Session()
session.mount("https://", LegacyTLSAdapter())




def fetch_page(url):

    for attempt in range(MAX_RANGE):
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

    raise RuntimeError(f"Error {status} after {MAX_RANGE} attempts. URL: {url}")


session.headers.update({"User-Agent": "polish-fleet-pipeline/0.1"})
url = "https://api.cepik.gov.pl/pojazdy?wojewodztwo=02&data-od=20240701&data-do=20240731&limit=200&page=1"
page_num = 1

while url:
    page = fetch_page(url)
    print(f"Page {page_num} , {len(page['data'])} records")
    url = page["links"].get("next")
    time.sleep(2.0)
    page_num += 1



