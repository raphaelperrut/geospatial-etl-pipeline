# Geospatial ETL Pipeline

[![Tests](https://github.com/raphaelperrut/geospatial-etl-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/raphaelperrut/geospatial-etl-pipeline/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A reproducible Python ETL pipeline for ingesting, inspecting, validating, normalizing and loading heterogeneous geospatial vector datasets into PostgreSQL/PostGIS.

## Status

🚧 **v0.1.0 in development**

The core ETL workflow is implemented and covered by automated tests.

PostGIS loading is implemented, while the final Docker-backed integration and end-to-end validation remain pending before the v0.1.0 release.

## Pipeline

```text
Vector dataset
      ↓
   Ingest
      ↓
   Inspect
      ↓
  Validate
      ↓
 Normalize
      ↓
 PostGIS load
      ↓
 JSON report
```

## Current capabilities

- Read GeoPackage, GeoJSON and Shapefile datasets
- Inspect spatial metadata and geometry quality
- Detect missing CRS
- Detect null, empty and invalid geometries
- Report dataset bounds, geometry types and attribute columns
- Normalize attribute column names
- Detect collisions caused by column-name normalization
- Reproject datasets to a target CRS
- Load GeoDataFrames into PostgreSQL/PostGIS
- Control existing-table behavior with `fail`, `replace` and `append`
- Produce structured ETL execution reports
- Export execution reports as JSON
- Execute the workflow through a command-line interface
- Generate a deterministic example dataset
- Validate individual components and pipeline orchestration with automated tests

## Tech stack

`Python` · `GeoPandas` · `Shapely` · `PyProj` · `SQLAlchemy` · `GeoAlchemy2` · `psycopg` · `PostgreSQL` · `PostGIS` · `Typer` · `pytest` · `Docker`

## Requirements

- Python 3.12+
- PostgreSQL/PostGIS for real database execution
- Docker Desktop will be used for the reproducible PostGIS development environment

Docker/PostGIS setup is not required to run the unit test suite.

## Installation

Clone the repository:

```powershell
git clone https://github.com/raphaelperrut/geospatial-etl-pipeline.git
cd geospatial-etl-pipeline
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Upgrade `pip` and install the project with development dependencies:

```powershell
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Generate the example dataset

The repository includes a deterministic example generator.

Run:

```powershell
python examples/generate_example.py
```

This creates:

```text
examples/generated/sample_points.gpkg
```

The generated GeoPackage contains:

```text
CRS: EPSG:4326
Geometry: Point
Features: 3
Layer: features
```

The source attributes intentionally contain names that require normalization:

```text
Feature Name
Source-ID
```

The `examples/generated/` directory is ignored by Git because these files are reproducible outputs.

## Command-line interface

The package installs the following command:

```powershell
geospatial-etl
```

Show the available commands:

```powershell
geospatial-etl --help
```

Show the ETL execution options:

```powershell
geospatial-etl run --help
```

The `run` command accepts:

```text
SOURCE
--database-url
--table
--schema
--target-crs
--if-exists
--report
```

### Example execution

With a PostgreSQL/PostGIS database available, a complete execution can be started with:

```powershell
geospatial-etl run `
    examples\generated\sample_points.gpkg `
    --database-url "postgresql+psycopg://USER:PASSWORD@localhost:5432/DATABASE" `
    --table sample_points `
    --target-crs EPSG:31983 `
    --report examples\generated\etl_report.json
```

The pipeline then performs:

```text
GeoPackage
    ↓
read_vector_dataset()
    ↓
inspect_dataset()
    ↓
validate_dataset()
    ↓
normalize_dataset()
    ↓
load_to_postgis()
    ↓
ETLReport
    ↓
JSON report
```

## Ingestion

The ingestion layer currently accepts:

- GeoPackage (`.gpkg`)
- GeoJSON (`.geojson`, `.json`)
- Shapefile (`.shp`)

Input paths and supported file extensions are validated before the dataset is passed to GeoPandas.

## Dataset inspection

Each dataset is inspected before transformation or loading.

The structured inspection result contains:

- feature count
- CRS
- geometry column
- geometry types
- attribute columns
- null geometry count
- empty geometry count
- invalid geometry count
- dataset bounding box

Example:

```text
DatasetInspection(
    feature_count=3,
    crs="EPSG:4326",
    geometry_column="geometry",
    geometry_types=("Point",),
    attribute_columns=("Feature Name", "Source-ID"),
    null_geometry_count=0,
    empty_geometry_count=0,
    invalid_geometry_count=0,
    bounds=(...)
)
```

## Validation

The validation stage currently detects:

- empty datasets
- missing CRS
- null geometries
- empty geometries
- invalid geometries

Validation produces a structured result:

```text
DatasetValidation(
    is_valid=True,
    issues=()
)
```

When problems are detected, individual validation issues contain a stable code and a human-readable message.

For example:

```text
ValidationIssue(
    code="missing_crs",
    message="Dataset has no defined CRS."
)
```

Invalid datasets are stopped before normalization and PostGIS loading.

## Normalization

The normalization stage currently performs:

- attribute column-name normalization
- optional CRS reprojection

For example:

```text
Feature Name  → feature_name
Source-ID     → source_id
```

The geometry column is preserved.

Column normalization also detects collisions. For example, two source columns that both normalize to the same destination name cause the operation to fail instead of silently overwriting data.

When a target CRS is provided:

```powershell
--target-crs EPSG:31983
```

the dataset is reprojected before being loaded.

A dataset without a defined source CRS cannot be reprojected.

## PostGIS loading

Normalized GeoDataFrames are loaded through GeoPandas and SQLAlchemy into PostgreSQL/PostGIS.

The destination can be configured with:

```text
table
schema
if_exists
```

Supported existing-table behaviors are:

```text
fail
replace
append
```

The loader rejects:

- empty datasets
- datasets without a CRS
- empty table names
- empty schema names
- unsupported `if_exists` values

## ETL execution report

A successful pipeline execution produces an `ETLReport`.

The report contains:

- source path
- destination table
- destination schema
- target CRS
- UTC start timestamp
- UTC finish timestamp
- source dataset inspection
- validation result
- normalized dataset inspection

Reports can optionally be written as JSON through:

```powershell
--report examples\generated\etl_report.json
```

A report has the following general structure:

```json
{
  "source_path": "examples/generated/sample_points.gpkg",
  "destination_table": "sample_points",
  "destination_schema": "public",
  "target_crs": "EPSG:31983",
  "started_at": "2026-09-12T20:00:00+00:00",
  "finished_at": "2026-09-12T20:00:01+00:00",
  "source_inspection": {
    "feature_count": 3,
    "crs": "EPSG:4326",
    "geometry_column": "geometry",
    "geometry_types": [
      "Point"
    ],
    "attribute_columns": [
      "Feature Name",
      "Source-ID"
    ],
    "null_geometry_count": 0,
    "empty_geometry_count": 0,
    "invalid_geometry_count": 0,
    "bounds": [
      -47.8825,
      -15.7942,
      -47.8675,
      -15.785
    ]
  },
  "validation": {
    "is_valid": true,
    "issues": []
  },
  "normalized_inspection": {
    "feature_count": 3,
    "crs": "EPSG:31983",
    "geometry_column": "geometry",
    "geometry_types": [
      "Point"
    ],
    "attribute_columns": [
      "feature_name",
      "source_id"
    ],
    "null_geometry_count": 0,
    "empty_geometry_count": 0,
    "invalid_geometry_count": 0,
    "bounds": [
      190000.0,
      8250000.0,
      192000.0,
      8252000.0
    ]
  }
}
```

The coordinates shown for the normalized bounds above are illustrative; actual values are calculated from the transformed dataset.

## Tests

Run the complete test suite with:

```powershell
pytest -v
```

The current development suite covers:

- vector ingestion
- dataset inspection
- validation
- normalization
- PostGIS loader behavior
- ETL orchestration
- structured reporting
- JSON report export
- command-line interface
- integration between pipeline stages

At the current development checkpoint:

```text
35 passed
1 skipped
```

The skipped test is the real PostGIS integration test. It is intentionally disabled when no PostGIS test database is configured.

### PostGIS integration test

The integration test becomes active when `POSTGIS_TEST_URL` is defined.

For example:

```powershell
$env:POSTGIS_TEST_URL = "postgresql+psycopg://USER:PASSWORD@localhost:5432/DATABASE"
pytest tests/test_postgis_integration.py -v
```

Before the v0.1.0 release, this test will be validated against the Docker-backed PostGIS environment.

## Docker/PostGIS

The repository includes:

```text
docker-compose.yml
```

for a reproducible PostgreSQL/PostGIS development environment.

Docker setup and the final database-backed validation are part of the remaining v0.1.0 hardening work.

Once Docker is configured, the intended development workflow is:

```powershell
docker compose up -d
docker compose ps
```

followed by configuration of `POSTGIS_TEST_URL` and execution of the integration suite.

## Project structure

```text
geospatial-etl-pipeline/
├── examples/
│   └── generate_example.py
├── src/
│   └── geospatial_etl/
│       ├── __init__.py
│       ├── cli.py
│       ├── ingest.py
│       ├── inspect.py
│       ├── load.py
│       ├── models.py
│       ├── normalization.py
│       ├── pipeline.py
│       ├── report.py
│       └── validation.py
├── tests/
│   ├── test_cli.py
│   ├── test_ingest.py
│   ├── test_inspect.py
│   ├── test_load.py
│   ├── test_normalization.py
│   ├── test_pipeline.py
│   ├── test_pipeline_orchestrator.py
│   ├── test_postgis_integration.py
│   ├── test_report.py
│   └── test_validation.py
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── pyproject.toml
└── README.md
```

## Architecture

The project keeps each ETL responsibility isolated:

```text
ingest.py
    │
    ▼
inspect.py
    │
    ▼
validation.py
    │
    ▼
normalization.py
    │
    ▼
load.py
```

The high-level workflow is coordinated by:

```text
pipeline.py
```

Execution metadata is handled by:

```text
report.py
```

and the user-facing command-line interface by:

```text
cli.py
```

This keeps ingestion, spatial quality assessment, transformation, persistence and presentation concerns separated while maintaining a small codebase.

## Roadmap to v0.1.0

Remaining work before the first release:

- Add continuous integration with GitHub Actions
- Install and validate the Docker development environment
- Start the PostgreSQL/PostGIS container
- Run the real PostGIS integration test
- Add a complete GeoPackage → validation → normalization → PostGIS end-to-end test
- Validate the reproducible CLI example against PostGIS
- Run the complete test suite
- Perform final README and repository review
- Publish `v0.1.0`

## License

MIT
