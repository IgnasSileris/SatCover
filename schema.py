import polars as pl

INPUT_SCHEMA = {
    "OBJECT_NAME": pl.String,
    "OBJECT_ID": pl.String,
    "EPOCH": pl.String,
    "MEAN_MOTION": pl.Float64,
    "ECCENTRICITY": pl.Float64,
    "INCLINATION": pl.Float64,
    "RA_OF_ASC_NODE": pl.Float64,
    "ARG_OF_PERICENTER": pl.Float64,
    "MEAN_ANOMALY": pl.Float64,
    "EPHEMERIS_TYPE": pl.Int64,
    "CLASSIFICATION_TYPE": pl.String,
    "NORAD_CAT_ID": pl.Int64,
    "ELEMENT_SET_NO": pl.Int64,
    "REV_AT_EPOCH": pl.Int64,
    "BSTAR": pl.Float64,
    "MEAN_MOTION_DOT": pl.Float64,
    "MEAN_MOTION_DDOT": pl.Float64,
}

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
