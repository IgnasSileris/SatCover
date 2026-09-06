from datetime import datetime
import numpy as np
import polars as pl
from skyfield.api import EarthSatellite, Time, Timescale, wgs84

from schema import TRANSFORMED_SCHEMA


def transform_data(
    df: pl.DataFrame,
    ts: Timescale,
    datetimes: list[datetime],
    times: Time,
) -> pl.DataFrame:
    # Pre-allocate
    num_sats = len(df)
    num_times = len(times)
    names: list[str] = []
    norad_cat_ids: list[str] = []
    latitudes = np.empty(num_sats * num_times, dtype=np.float64)
    longitudes = np.empty(num_sats * num_times, dtype=np.float64)
    altitudes = np.empty(num_sats * num_times, dtype=np.float64)

    successful_count = 0
    for row in df.iter_rows(named=True):
        try:
            satellite = EarthSatellite.from_omm(ts, row)
            positions = satellite.at(times)
            subpoints = wgs84.subpoint(positions)

            start = successful_count * num_times
            end = start + num_times

            latitudes[start:end] = subpoints.latitude.degrees
            longitudes[start:end] = subpoints.longitude.degrees
            altitudes[start:end] = subpoints.elevation.km

            names.extend([str(satellite.name)] * num_times)
            norad_cat_ids.extend([row["NORAD_CAT_ID"]] * num_times)

            successful_count += 1
        except Exception as e:
            print(
                f"Had an issue processing and input row. Skipping. Row: {row}, Error: {e}"
            )
            continue

    output_size = successful_count * num_times

    if output_size == 0:
        return pl.DataFrame()

    output_df = pl.DataFrame(
        {
            "timestamp": datetimes * successful_count,
            "norad_cat_id": norad_cat_ids,
            "name": names,
            "latitude": latitudes[:output_size],
            "longitude": longitudes[:output_size],
            "altitude": altitudes[:output_size],
        },
        schema=TRANSFORMED_SCHEMA,
    )

    return output_df
