from dotenv import load_dotenv
import os
from pathlib import Path
import polars as pl
from typing import Generator

load_dotenv()


def load_and_filter_data() -> Generator[pl.DataFrame, None, None]:
    csv_path = os.getenv("CSV_DATA_PATH")

    if not csv_path:
        raise Exception("No CSV_DATA_PATH environment variable defined.")

    csv_path = Path(csv_path)

    for file_path in csv_path.glob("*.csv"):
        lazy_df = pl.scan_csv(file_path)
        lazy_df = filter_data(lazy_df)

        for batch in lazy_df.collect_batches(chunk_size=250):
            yield batch


def filter_data(df: pl.LazyFrame) -> pl.LazyFrame:
    # Filter by missing data
    df = df.filter(pl.any_horizontal(pl.all().is_not_null()))

    return df
