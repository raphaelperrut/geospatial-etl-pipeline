"""PostGIS loading utilities."""

from __future__ import annotations

import geopandas as gpd
from sqlalchemy import Engine, create_engine


def create_postgis_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL/PostGIS."""

    if not database_url.strip():
        raise ValueError("Database URL cannot be empty.")

    return create_engine(database_url)


def load_to_postgis(
    dataset: gpd.GeoDataFrame,
    engine: Engine,
    table_name: str,
    *,
    schema: str = "public",
    if_exists: str = "fail",
) -> None:
    """Load a GeoDataFrame into a PostGIS table.

    Parameters
    ----------
    dataset
        Geospatial dataset to load.
    engine
        SQLAlchemy database engine.
    table_name
        Destination table name.
    schema
        Destination database schema.
    if_exists
        Behavior when the destination table already exists.
        Accepted values are ``fail``, ``replace`` and ``append``.

    Raises
    ------
    ValueError
        If the dataset is empty, has no CRS or an invalid loading option is
        provided.
    """

    if dataset.empty:
        raise ValueError("Cannot load an empty dataset.")

    if dataset.crs is None:
        raise ValueError("Cannot load dataset because its CRS is undefined.")

    if not table_name.strip():
        raise ValueError("Table name cannot be empty.")

    if not schema.strip():
        raise ValueError("Schema name cannot be empty.")

    if if_exists not in {"fail", "replace", "append"}:
        raise ValueError(
            "if_exists must be one of: fail, replace, append."
        )

    dataset.to_postgis(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
    )