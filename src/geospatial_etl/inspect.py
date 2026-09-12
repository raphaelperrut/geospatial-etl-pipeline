"""Geospatial dataset inspection utilities."""

import math

import geopandas as gpd

from geospatial_etl.models import DatasetInspection


def inspect_dataset(dataset: gpd.GeoDataFrame) -> DatasetInspection:
    """Inspect a GeoDataFrame and return a structured dataset summary.

    Parameters
    ----------
    dataset
        Geospatial dataset to inspect.

    Returns
    -------
    DatasetInspection
        Structured metadata and geometry-quality summary.
    """

    geometry_column = dataset.geometry.name

    geometry_types = tuple(
        sorted(
            {
                geometry_type
                for geometry_type in dataset.geom_type.dropna().unique()
                if geometry_type
            }
        )
    )

    attribute_columns = tuple(
        column for column in dataset.columns if column != geometry_column
    )

    null_geometry_count = int(dataset.geometry.isna().sum())

    non_null_geometry = dataset.geometry[~dataset.geometry.isna()]

    empty_geometry_count = int(non_null_geometry.is_empty.sum())

    non_empty_geometry = non_null_geometry[~non_null_geometry.is_empty]

    invalid_geometry_count = int((~non_empty_geometry.is_valid).sum())

    bounds = _extract_bounds(dataset)

    crs = _format_crs(dataset)

    return DatasetInspection(
        feature_count=len(dataset),
        crs=crs,
        geometry_column=geometry_column,
        geometry_types=geometry_types,
        attribute_columns=attribute_columns,
        null_geometry_count=null_geometry_count,
        empty_geometry_count=empty_geometry_count,
        invalid_geometry_count=invalid_geometry_count,
        bounds=bounds,
    )


def _format_crs(dataset: gpd.GeoDataFrame) -> str | None:
    """Return a stable textual representation of the dataset CRS."""

    if dataset.crs is None:
        return None

    epsg = dataset.crs.to_epsg()

    if epsg is not None:
        return f"EPSG:{epsg}"

    return dataset.crs.to_string()


def _extract_bounds(
    dataset: gpd.GeoDataFrame,
) -> tuple[float, float, float, float] | None:
    """Return dataset bounds when finite geometry bounds are available."""

    if dataset.empty:
        return None

    non_null_geometry = dataset.geometry[~dataset.geometry.isna()]

    if non_null_geometry.empty:
        return None

    non_empty_geometry = non_null_geometry[~non_null_geometry.is_empty]

    if non_empty_geometry.empty:
        return None

    minx, miny, maxx, maxy = non_empty_geometry.total_bounds

    values = (float(minx), float(miny), float(maxx), float(maxy))

    if not all(math.isfinite(value) for value in values):
        return None

    return values