import os
from pathlib import Path
import polars as pl
from typing import Generator

from schema import INPUT_SCHEMA

MINIMUM_SATELLITE_COUNT = 1_000


def load_and_filter_data(csv_path: Path) -> Generator[pl.DataFrame, None, None]:
    csv_path = Path(csv_path)

    for file_path in csv_path.glob("*.csv"):
        lazy_df = pl.scan_csv(file_path)
        lazy_df = validate_data(lazy_df)

        for batch in lazy_df.collect_batches(chunk_size=250):
            yield batch


def validate_data(df: pl.LazyFrame) -> pl.LazyFrame:
    df = df.match_to_schema(
        INPUT_SCHEMA,
        missing_columns="raise",
        extra_columns="ignore",
        integer_cast="forbid",
        float_cast="forbid",
    ).drop_nulls(subset=INPUT_SCHEMA.keys())

    statistics = (
        df.select(
            pl.len().alias("row_count"),
            pl.col("NORAD_CAT_ID").n_unique().alias("unique_norad_count"),
        )
        .collect()
        .row(0, named=True)
    )

    row_count = statistics["row_count"]
    if row_count == 0:
        raise ValueError("Input data contains no valid satellite records")

    if row_count < MINIMUM_SATELLITE_COUNT:
        raise ValueError(
            f"Input contains only {row_count} satellites; "
            f"expected at least {MINIMUM_SATELLITE_COUNT}"
        )

    if statistics["unique_norad_count"] != row_count:
        raise ValueError("Input contains duplicate NORAD catalogue IDs")

    return df
