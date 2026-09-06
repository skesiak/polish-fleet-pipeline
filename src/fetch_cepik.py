import ssl
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context


class LegacyTLSAdapter(HTTPAdapter):
    """CEPiK API uses weak DH parameters rejected by OpenSSL 3 defaults."""

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


session = requests.Session()
session.mount("https://", LegacyTLSAdapter())




def fetch_page(url):

    for attempt in range(5):
        answer = session.get(url)
        status = answer.status_code
        if status == 200:
            return answer.json()
        elif status == 429:
            sleep_time = 2 ** attempt
            time.sleep(sleep_time)
        else:
            raise RuntimeError(f"Error {status}. URL: {url}")

    raise RuntimeError(f"Error {status} after 5 attempts. URL: {url}")



url = "https://api.cepik.gov.pl/pojazdy?wojewodztwo=02&data-od=20240701&data-do=20240731&limit=1&page=1"
answer = fetch_page(url)

print(answer["meta"]["count"])

