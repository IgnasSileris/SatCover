from dotenv import load_dotenv
import os
from pathlib import Path
import polars as pl
from typing import Generator

load_dotenv()

# These columns are required for the transformation
REQUIRED_COLUMNS = [
    "OBJECT_ID",
    "OBJECT_NAME",
    "CLASSIFICATION_TYPE",
    "NORAD_CAT_ID",
    "EPOCH",
    "ARG_OF_PERICENTER",
    "BSTAR",
    "ECCENTRICITY",
    "ELEMENT_SET_NO",
    "EPHEMERIS_TYPE",
    "INCLINATION",
    "MEAN_ANOMALY",
    "MEAN_MOTION",
    "MEAN_MOTION_DDOT",
    "MEAN_MOTION_DOT",
    "RA_OF_ASC_NODE",
    "REV_AT_EPOCH",
]


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
    df = df.drop_nulls(subset=REQUIRED_COLUMNS)

    return df
