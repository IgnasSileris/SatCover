from dotenv import load_dotenv
import json
import os
from pathlib import Path
import polars as pl
import shutil

from schema import OUTPUT_SCHEMA

load_dotenv()


def save_parquet(run_id: str, ts: int, df: pl.DataFrame) -> bool:
    output_path = os.getenv("OUTPUT_PATH")
    if not output_path:
        raise Exception("No OUTPUT_PATH environment variable defined.")

    df = df.match_to_schema(
        OUTPUT_SCHEMA,
        missing_columns="raise",
        extra_columns="raise",
        integer_cast="forbid",
        float_cast="forbid",
    )

    file_path = Path(output_path) / "staging" / run_id / f"{ts}.parquet"
    file_path.parent.mkdir(parents=True, exist_ok=True)
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
    run_id: str,
) -> dict:
    success_count_info = {"success": 0, "failed": 0}

    df = df.with_columns(pl.col("timestamp").dt.truncate("1h").alias("partition_hour"))

    for partition in df.partition_by("partition_hour"):
        unix_timestamp = int(partition["partition_hour"][0].timestamp())

        is_saved = save_parquet(run_id, unix_timestamp, partition)
        if is_saved == True:
            success_count_info["success"] += 1
        else:
            success_count_info["failed"] += 1

    return success_count_info


def promote_staging(run_id: str) -> None:
    output_path = os.getenv("OUTPUT_PATH")
    if not output_path:
        raise Exception("No OUTPUT_PATH environment variable defined.")

    # Move run files from staging to snapshot
    staging_path = Path(output_path) / "staging" / run_id
    snapshot_path = Path(output_path) / "snapshots" / run_id
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    staging_path.replace(snapshot_path)

    # Point the status file to the snaphot of the run
    current_path = Path(output_path) / "current.json"
    temp_path = current_path.with_suffix(".tmp")

    current = (
        json.loads(current_path.read_text(encoding="utf-8"))
        if current_path.exists()
        else {}
    )

    current["snapshot"] = run_id

    temp_path.write_text(json.dumps(current), encoding="utf-8")
    temp_path.replace(current_path)


def abandon_run(run_id: str) -> None:
    output_path = os.getenv("OUTPUT_PATH")
    if not output_path:
        raise RuntimeError("No OUTPUT_PATH environment variable defined.")

    run_folder = Path(output_path) / "staging" / run_id
    if run_folder.exists():
        shutil.rmtree(run_folder)
