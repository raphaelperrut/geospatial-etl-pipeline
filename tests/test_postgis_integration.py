"""Integration tests for PostGIS loading."""

import os

import geopandas as gpd
import pytest
from shapely.geometry import Point
from sqlalchemy import text

from geospatial_etl.load import (
    create_postgis_engine,
    load_to_postgis,
)


POSTGIS_TEST_URL = os.getenv("POSTGIS_TEST_URL")

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    POSTGIS_TEST_URL is None,
    reason="POSTGIS_TEST_URL is not configured",
)
def test_load_dataset_into_postgis() -> None:
    engine = create_postgis_engine(POSTGIS_TEST_URL)

    table_name = "integration_features"

    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha", "beta"],
            "value": [10, 20],
        },
        geometry=[
            Point(-47.88, -15.79),
            Point(-47.87, -15.78),
        ],
        crs="EPSG:4326",
    )

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f'DROP TABLE IF EXISTS public."{table_name}"'
                )
            )

        load_to_postgis(
            dataset,
            engine,
            table_name,
            schema="public",
        )

        with engine.connect() as connection:
            feature_count = connection.execute(
                text(
                    f'SELECT COUNT(*) FROM public."{table_name}"'
                )
            ).scalar_one()

            srid = connection.execute(
                text(
                    f"""
                    SELECT ST_SRID(geometry)
                    FROM public."{table_name}"
                    LIMIT 1
                    """
                )
            ).scalar_one()

            geometry_type = connection.execute(
                text(
                    f"""
                    SELECT GeometryType(geometry)
                    FROM public."{table_name}"
                    LIMIT 1
                    """
                )
            ).scalar_one()

        assert feature_count == 2
        assert srid == 4326
        assert geometry_type == "POINT"

    finally:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f'DROP TABLE IF EXISTS public."{table_name}"'
                )
            )

        engine.dispose()