import polars as pl

TRANSFORMED_SCHEMA = {
    "timestamp": pl.Datetime(time_unit="us", time_zone="UTC"),
    "norad_cat_id": pl.Int64,
    "name": pl.String,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "altitude": pl.Float64,
}

OUTPUT_SCHEMA = {
    **TRANSFORMED_SCHEMA,
    "partition_hour": pl.Datetime(time_unit="us", time_zone="UTC"),
}
