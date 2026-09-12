"""Normalization utilities for geospatial datasets."""

import re

import geopandas as gpd


def normalize_dataset(
    dataset: gpd.GeoDataFrame,
    target_crs: str | None = None,
) -> gpd.GeoDataFrame:
    """Normalize a geospatial dataset.

    Parameters
    ----------
    dataset
        Input geospatial dataset.
    target_crs
        Optional target CRS. If provided, the dataset is reprojected.

    Returns
    -------
    geopandas.GeoDataFrame
        Normalized copy of the input dataset.

    Raises
    ------
    ValueError
        If reprojection is requested for a dataset without a CRS.
    """

    normalized = dataset.copy()

    normalized = _normalize_column_names(normalized)

    if target_crs is not None:
        normalized = _normalize_crs(normalized, target_crs)

    return normalized


def _normalize_crs(
    dataset: gpd.GeoDataFrame,
    target_crs: str,
) -> gpd.GeoDataFrame:
    """Reproject a dataset to the requested target CRS."""

    if dataset.crs is None:
        raise ValueError(
            "Cannot reproject dataset because the source CRS is undefined."
        )

    return dataset.to_crs(target_crs)


def _normalize_column_names(
    dataset: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Normalize attribute column names while preserving geometry."""

    geometry_column = dataset.geometry.name

    rename_map: dict[str, str] = {}

    for column in dataset.columns:
        if column == geometry_column:
            continue

        normalized_name = _normalize_column_name(column)

        rename_map[column] = normalized_name

    if len(set(rename_map.values())) != len(rename_map.values()):
        raise ValueError(
            "Column normalization produced duplicate column names."
        )

    return dataset.rename(columns=rename_map)


def _normalize_column_name(name: str) -> str:
    """Convert a column name to lowercase snake_case."""

    normalized = name.strip().lower()

    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)

    normalized = normalized.strip("_")

    if not normalized:
        raise ValueError(
            f"Column name cannot be normalized: {name!r}"
        )

    return normalized