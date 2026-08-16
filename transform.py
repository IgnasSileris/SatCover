from datetime import datetime
import numpy as np
import polars as pl
from skyfield.api import EarthSatellite, Time, Timescale, wgs84


def transform_data(
    df: pl.DataFrame,
    ts: Timescale,
    datetimes: list[datetime],
    times: Time,
) -> pl.DataFrame:
    # Pre-allocate
    num_sats = len(df)
    num_times = len(times)
    names = []
    latitudes = np.empty(num_sats * num_times, dtype=np.float64)
    longitudes = np.empty(num_sats * num_times, dtype=np.float64)
    altitudes = np.empty(num_sats * num_times, dtype=np.float64)
    for i, row in enumerate(df.iter_rows(named=True)):
        satellite = EarthSatellite.from_omm(ts, row)
        positions = satellite.at(times)
        subpoints = wgs84.subpoint(positions)

        lats = subpoints.latitude.degrees
        longs = subpoints.longitude.degrees
        alts = subpoints.elevation.km

        names.extend([str(satellite.name)] * num_times)
        start_index = num_times * i
        latitudes[start_index : start_index + num_times] = lats
        longitudes[start_index : start_index + num_times] = longs
        altitudes[start_index : start_index + num_times] = alts

    df = pl.DataFrame(
        {
            "timestamp": datetimes * num_sats,
            "name": names,
            "latitude": latitudes,
            "longitude": longitudes,
            "altitude": altitudes,
        }
    )

    return df
