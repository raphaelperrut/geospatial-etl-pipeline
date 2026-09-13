"""End-to-end tests for the complete geospatial ETL workflow."""

import os

import geopandas as gpd
import pytest
from shapely.geometry import Point
from sqlalchemy import text

from geospatial_etl.load import create_postgis_engine
from geospatial_etl.pipeline import run_etl_pipeline


POSTGIS_TEST_URL = os.getenv("POSTGIS_TEST_URL")

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    POSTGIS_TEST_URL is None,
    reason="POSTGIS_TEST_URL is not configured",
)
def test_complete_etl_pipeline_to_postgis(tmp_path) -> None:
    """Run the complete ETL workflow from GeoPackage to PostGIS."""

    source_path = tmp_path / "source.gpkg"

    source = gpd.GeoDataFrame(
        {
            "Feature Name": [
                "alpha",
                "beta",
                "gamma",
            ],
            "Source-ID": [
                100,
                200,
                300,
            ],
        },
        geometry=[
            Point(-47.8825, -15.7942),
            Point(-47.8750, -15.7900),
            Point(-47.8675, -15.7850),
        ],
        crs="EPSG:4326",
    )

    source.to_file(
        source_path,
        layer="features",
        driver="GPKG",
    )

    engine = create_postgis_engine(POSTGIS_TEST_URL)
    table_name = "e2e_features"

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f'DROP TABLE IF EXISTS public."{table_name}"'
                )
            )

        result = run_etl_pipeline(
            source_path=source_path,
            engine=engine,
            table_name=table_name,
            target_crs="EPSG:31983",
            schema="public",
            if_exists="replace",
        )

        assert result.source_inspection.feature_count == 3
        assert result.source_inspection.crs == "EPSG:4326"

        assert result.validation.is_valid is True

        assert result.normalized_inspection.feature_count == 3
        assert result.normalized_inspection.crs == "EPSG:31983"
        assert result.normalized_inspection.attribute_columns == (
            "feature_name",
            "source_id",
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

            columns = connection.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = :table_name
                    ORDER BY ordinal_position
                    """
                ),
                {"table_name": table_name},
            ).scalars().all()

        assert feature_count == 3
        assert srid == 31983
        assert geometry_type == "POINT"

        assert "feature_name" in columns
        assert "source_id" in columns
        assert "geometry" in columns

        assert result.report.destination_table == table_name
        assert result.report.destination_schema == "public"
        assert result.report.target_crs == "EPSG:31983"

    finally:
        with engine.begin() as connection:
            connection.execute(
                text(
                    f'DROP TABLE IF EXISTS public."{table_name}"'
                )
            )

        engine.dispose()