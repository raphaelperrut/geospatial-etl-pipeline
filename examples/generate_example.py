"""Generate a deterministic GeoPackage example dataset."""

from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point


OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_PATH = OUTPUT_DIR / "sample_points.gpkg"


def main() -> None:
    """Generate a small deterministic vector dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset = gpd.GeoDataFrame(
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

    dataset.to_file(
        OUTPUT_PATH,
        layer="features",
        driver="GPKG",
    )

    print(f"Example dataset written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()