import ssl
import json
import requests
import time
import calendar
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from pathlib import Path

MAX_ATTEMPTS = 8
REQUEST_DELAY = 2.0
RAW_DIR = Path("data/raw")
BASE_URL = "https://api.cepik.gov.pl/pojazdy"
LIMIT = 200
FIELDS = (
    "marka,model,rodzaj-pojazdu,podrodzaj-pojazdu,pochodzenie-pojazdu,"
    "rok-produkcji,data-pierwszej-rejestracji-w-kraju,rodzaj-paliwa,"
    "rodzaj-pierwszego-paliwa-alternatywnego,pojemnosc-skokowa-silnika,"
    "moc-netto-silnika,masa-wlasna,rejestracja-powiat,"
    "wojewodztwo-kod"
)
VOIVODESHIPS = [
    "02", "04", "06", "08", "10", "12", "14", "16",
    "18", "20", "22", "24", "26", "28", "30", "32",
]

class LegacyTLSAdapter(HTTPAdapter):
    """CEPiK API uses weak DH parameters rejected by OpenSSL 3 defaults."""

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)



def fetch_page(url):

    for attempt in range(MAX_ATTEMPTS):
        try:
            answer = session.get(url, timeout=30)
        except requests.RequestException:
            time.sleep(2 ** attempt)
            continue

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

def month_periods(start_year, start_month, count):
    periods = []
    year = start_year
    month = start_month


    for _ in range(count):
        days_in_month = calendar.monthrange(year, month)[1]
        period = f"{year}{month:02d}"
        date_from = f"{year}{month:02d}01"
        date_to = f"{year}{month:02d}{days_in_month:02d}"
        periods.append((period, date_from, date_to))
        month += 1
        if month > 12:
            month = 1
            year += 1

    return periods

session = requests.Session()
session.mount("https://", LegacyTLSAdapter())
session.headers.update({"User-Agent": "polish-fleet-pipeline/0.1"})


RAW_DIR.mkdir(parents=True, exist_ok=True)
for voivodeship in VOIVODESHIPS:
    print(f"=== {voivodeship} ===")
    for period, date_from, date_to in month_periods(2024, 7, 1):
        print(f"=== {period} ===")
        url = (
            f"{BASE_URL}?wojewodztwo={voivodeship}"
            f"&data-od={date_from}&data-do={date_to}"
            f"&limit={LIMIT}&page=1"
            f"&fields={FIELDS}"
        )
        page_num = 1

        while url:
            path = RAW_DIR / f"pojazdy_{voivodeship}_{period}_p{page_num:04d}.json"

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

