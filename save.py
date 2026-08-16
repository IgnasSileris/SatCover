from dotenv import load_dotenv
import os
from pathlib import Path
import polars as pl

load_dotenv()


def save_parquet(ts: int, df: pl.DataFrame) -> bool:
    parquet_path = os.getenv("PARQUET_DATA_PATH")

    if not parquet_path:
        raise Exception("No PARQUET_DATA_PATH environment variable defined.")

    file_path = Path(parquet_path + f"/{ts}.parquet")
    if file_path.exists():
        # If parquet exists, load and append it
        try:
            existing_df = pl.read_parquet(file_path)
            existing_df = existing_df.extend(df)
            existing_df.write_parquet(file_path)
        except Exception as e:
            print(f"Could update parquet file at {file_path}: {e}")
            return False
    else:
        # Create a new parquet
        try:
            df.write_parquet(file_path)
        except Exception as e:
            print(f"Could not write parquet file at {file_path}: {e}")
            return False

    return True


def save_processed_data(
    df: pl.DataFrame,
) -> None:
    df = df.with_columns(pl.col("timestamp").dt.truncate("1h").alias("partition_hour"))

    for partition in df.partition_by("partition_hour"):
        unix_timestamp = int(partition["timestamp"][0].timestamp())

        save_parquet(unix_timestamp, partition.drop("partition_hour"))
