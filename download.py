from datetime import datetime, timezone
from dotenv import load_dotenv
import os
from pathlib import Path
import requests
import time

load_dotenv()

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=ACTIVE&FORMAT=CSV"


def download_data(current_time: datetime) -> Path:
    csv_path = os.getenv("CSV_DATA_PATH")
    if not csv_path:
        raise Exception("No CSV_DATA_PATH environment variable set")

    timestamp = current_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    input_path = Path(csv_path) / f"satellites_{timestamp}"
    input_path.mkdir(parents=True, exist_ok=True)

    response = requests.get(CELESTRAK_URL, timeout=60)
    response.raise_for_status()

    file_path = input_path / f"{timestamp}.csv"
    file_path.write_bytes(response.content)

    return input_path


def try_download(current_time: datetime) -> Path | None:
    MAX_TRIES = 5

    num_tries = 1
    while num_tries <= MAX_TRIES:
        try:
            input_path = download_data(current_time)
            return input_path
        except Exception as e:
            print(f"Problem with download: {e}")
            print(f"Try {num_tries} / {MAX_TRIES}")
            num_tries += 1
            time.sleep(30)
    return None
