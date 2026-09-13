"""Tests for the high-level ETL pipeline orchestrator."""

from pathlib import Path
from unittest.mock import Mock, patch

import geopandas as gpd
import pytest
from shapely.geometry import Point

from geospatial_etl.pipeline import run_etl_pipeline


def test_run_etl_pipeline_executes_complete_flow(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "sample.gpkg"

    source = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha", "beta"],
        },
        geometry=[
            Point(-47.88, -15.79),
            Point(-47.87, -15.78),
        ],
        crs="EPSG:4326",
    )

    source.to_file(
        source_path,
        layer="features",
        driver="GPKG",
    )

    engine = Mock()

    with patch(
        "geospatial_etl.pipeline.load_to_postgis"
    ) as load_mock:
        result = run_etl_pipeline(
            source_path,
            engine,
            "features",
            target_crs="EPSG:31983",
        )

    assert result.report.destination_table == "features"
    assert result.report.destination_schema == "public"
    assert result.report.target_crs == "EPSG:31983"
    assert result.report.validation.is_valid is True
    
    assert result.validation.is_valid is True

    assert result.source_inspection.crs == "EPSG:4326"

    assert result.normalized_inspection.crs == "EPSG:31983"
    assert (
        result.normalized_inspection.attribute_columns
        == ("feature_name",)
    )

    load_mock.assert_called_once()

    loaded_dataset = load_mock.call_args.args[0]

    assert loaded_dataset.crs is not None
    assert loaded_dataset.crs.to_epsg() == 31983
    assert tuple(loaded_dataset.columns) == (
        "feature_name",
        "geometry",
    )

    assert load_mock.call_args.args[1] is engine
    assert load_mock.call_args.args[2] == "features"

    assert load_mock.call_args.kwargs == {
        "schema": "public",
        "if_exists": "fail",
    }


def test_run_etl_pipeline_stops_when_validation_fails(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "missing_crs.gpkg"

    source = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
    )

    source.to_file(
        source_path,
        layer="features",
        driver="GPKG",
    )

    with patch(
        "geospatial_etl.pipeline.load_to_postgis"
    ) as load_mock:
        with pytest.raises(
            ValueError,
            match="Dataset validation failed: missing_crs",
        ):
            run_etl_pipeline(
                source_path,
                Mock(),
                "features",
            )

    load_mock.assert_not_called()