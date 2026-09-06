from datetime import datetime, timedelta, timezone
from tqdm import tqdm
from skyfield.api import load
import uuid

import ingest
import save
import transform


def main():
    run_id = str(uuid.uuid4())

    # Round to nearest 5 minute interval
    now = datetime.now(timezone.utc)
    current = now + timedelta(
        minutes=round(now.minute / 5) * 5 - now.minute,
        seconds=-now.second,
        microseconds=-now.microsecond,
    )
    start = current - timedelta(days=7)
    datetimes = [
        start + timedelta(minutes=5 * i) for i in range(14 * 24 * 12)
    ]  # one week back, one week forward
    ts = load.timescale()
    times = ts.from_datetimes(datetimes)

    try:
        for batch_num, input_df in enumerate(tqdm(ingest.load_and_filter_data())):
            processed_df = transform.transform_data(input_df, ts, datetimes, times)

            if processed_df.is_empty():
                print(f"Batch {batch_num + 1} produced no output. Skipping save.")
                continue

            result = save.save_processed_data(processed_df, run_id)

            if result["failed"] > 0:
                raise RuntimeError("Parquet writes failed")

            break
        save.promote_staging(run_id)
    except Exception:
        save.abandon_run(run_id)
        raise


if __name__ == "__main__":
    main()
