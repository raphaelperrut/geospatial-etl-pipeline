"""Tests for vector dataset ingestion."""

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Point

from geospatial_etl.ingest import read_vector_dataset


def test_read_vector_dataset_from_geopackage(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.gpkg"

    expected = gpd.GeoDataFrame(
        {
            "name": ["alpha", "beta"],
            "value": [10, 20],
        },
        geometry=[
            Point(0, 0),
            Point(1, 1),
        ],
        crs="EPSG:4326",
    )

    expected.to_file(input_path, driver="GPKG")

    result = read_vector_dataset(input_path)

    assert len(result) == 2
    assert list(result["name"]) == ["alpha", "beta"]
    assert result.crs is not None
    assert result.crs.to_epsg() == 4326


def test_read_vector_dataset_raises_for_missing_file(tmp_path: Path) -> None:
    input_path = tmp_path / "missing.gpkg"

    with pytest.raises(FileNotFoundError, match="Input dataset not found"):
        read_vector_dataset(input_path)


def test_read_vector_dataset_raises_for_unsupported_format(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "sample.txt"
    input_path.write_text("not a vector dataset", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported vector format"):
        read_vector_dataset(input_path)