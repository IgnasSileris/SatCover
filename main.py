from datetime import datetime, timedelta, timezone
from tqdm import tqdm
from skyfield.api import load

import ingest
import save
import transform


def main():
    for input_df in tqdm(ingest.load_and_filter_data()):
        ts = load.timescale()
        start = datetime.now(timezone.utc) - timedelta(days=7)
        datetimes = [
            start + timedelta(minutes=5 * i) for i in range(14 * 24 * 12)
        ]  # one week back, one week forward
        times = ts.from_datetimes(datetimes)

        processed_df = transform.transform_data(input_df, ts, datetimes, times)

        save.save_processed_data(processed_df)


if __name__ == "__main__":
    main()
