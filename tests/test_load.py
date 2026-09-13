"""Tests for PostGIS loading utilities."""

from unittest.mock import Mock

import geopandas as gpd
import pytest
from shapely.geometry import Point

from geospatial_etl.load import load_to_postgis


def test_load_to_postgis_calls_geodataframe_writer() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
        crs="EPSG:4326",
    )

    engine = Mock()

    dataset.to_postgis = Mock()

    load_to_postgis(
        dataset,
        engine,
        "features",
    )

    dataset.to_postgis.assert_called_once_with(
        name="features",
        con=engine,
        schema="public",
        if_exists="fail",
        index=False,
    )


def test_load_to_postgis_rejects_empty_dataset() -> None:
    dataset = gpd.GeoDataFrame(
        geometry=[],
        crs="EPSG:4326",
    )

    with pytest.raises(
        ValueError,
        match="empty dataset",
    ):
        load_to_postgis(
            dataset,
            Mock(),
            "features",
        )


def test_load_to_postgis_rejects_missing_crs() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
    )

    with pytest.raises(
        ValueError,
        match="CRS is undefined",
    ):
        load_to_postgis(
            dataset,
            Mock(),
            "features",
        )


def test_load_to_postgis_rejects_invalid_if_exists() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
        crs="EPSG:4326",
    )

    with pytest.raises(
        ValueError,
        match="if_exists",
    ):
        load_to_postgis(
            dataset,
            Mock(),
            "features",
            if_exists="invalid",
        )