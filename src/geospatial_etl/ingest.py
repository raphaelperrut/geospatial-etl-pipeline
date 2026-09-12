"""Vector dataset ingestion utilities."""

from pathlib import Path

import geopandas as gpd


SUPPORTED_VECTOR_EXTENSIONS = {
    ".gpkg",
    ".geojson",
    ".json",
    ".shp",
}


def read_vector_dataset(path: str | Path) -> gpd.GeoDataFrame:
    """Read a supported vector dataset into a GeoDataFrame.

    Parameters
    ----------
    path
        Path to the input vector dataset.

    Returns
    -------
    geopandas.GeoDataFrame
        Loaded geospatial dataset.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If the file extension is not supported or the dataset cannot be read.
    """

    input_path = Path(path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_path}")

    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    extension = input_path.suffix.lower()

    if extension not in SUPPORTED_VECTOR_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_VECTOR_EXTENSIONS))
        raise ValueError(
            f"Unsupported vector format '{extension}'. "
            f"Supported formats: {supported}"
        )

    try:
        dataset = gpd.read_file(input_path)
    except Exception as exc:
        raise ValueError(f"Failed to read vector dataset: {input_path}") from exc

    return dataset