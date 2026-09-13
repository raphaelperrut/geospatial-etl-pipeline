# Geospatial ETL Pipeline

[![Tests](https://github.com/raphaelperrut/geospatial-etl-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/raphaelperrut/geospatial-etl-pipeline/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A reproducible Python ETL pipeline for ingesting, inspecting, validating, normalizing, transforming and loading heterogeneous geospatial vector datasets into PostgreSQL/PostGIS.

## Status

Version `0.1.0` is release-ready.

The pipeline is validated end-to-end against PostgreSQL/PostGIS, including:

- vector dataset ingestion;
- dataset inspection and validation;
- attribute normalization;
- CRS reprojection;
- PostGIS loading;
- spatial metadata verification;
- JSON ETL reporting;
- command-line execution;
- Docker-backed integration testing;
- automated GitHub Actions CI.

Current test suite:

```text
37 passed
```

## Overview

Geospatial data pipelines often need to handle heterogeneous source files, inconsistent schemas, different coordinate reference systems and spatial database loading in a reproducible way.

Geospatial ETL Pipeline provides a compact Python workflow for processing vector datasets through a defined sequence:

```text
Vector dataset
      |
      v
  Ingestion
      |
      v
  Inspection
      |
      v
  Validation
      |
      v
Normalization
      |
      v
CRS transformation
      |
      v
PostGIS loading
      |
      v
  ETL report
```

The project focuses on a transparent and testable ETL architecture rather than workflow orchestration infrastructure.

Version `0.1.0` supports GeoPackage, GeoJSON and Shapefile inputs and PostgreSQL/PostGIS as the destination.

## Features

### Vector data ingestion

Supported input formats:

- GeoPackage (`.gpkg`)
- GeoJSON (`.geojson`, `.json`)
- ESRI Shapefile (`.shp`)

Input datasets are loaded as GeoPandas `GeoDataFrame` objects for subsequent processing.

### Dataset inspection

The inspection stage extracts structured metadata and geometry-quality information, including:

- feature count;
- coordinate reference system;
- geometry column;
- geometry types;
- attribute columns;
- null geometry count;
- empty geometry count;
- invalid geometry count;
- dataset bounds.

Example inspection:

```text
feature_count: 3
crs: EPSG:4326
geometry_column: geometry
geometry_types: Point
attribute_columns: Feature Name, Source-ID
null_geometry_count: 0
empty_geometry_count: 0
invalid_geometry_count: 0
```

### Dataset validation

Datasets are validated before transformation and database loading.

The current validation rules detect:

- empty datasets;
- missing CRS definitions;
- null geometries;
- empty geometries;
- invalid geometries.

Validation failures stop the pipeline before data is written to PostGIS.

### Attribute normalization

Attribute column names are normalized to lowercase `snake_case`.

For example:

```text
Feature Name  -> feature_name
Source-ID     -> source_id
```

The geometry column is preserved.

Normalization also detects collisions where multiple original fields would produce the same normalized column name.

### CRS transformation

Datasets can optionally be reprojected to a target CRS before loading.

For example:

```text
EPSG:4326 -> EPSG:31983
```

Reprojection requires the source dataset to have a defined CRS.

### PostGIS loading

Validated and normalized datasets can be loaded directly into PostgreSQL/PostGIS.

Supported table behaviors are:

- `fail`
- `replace`
- `append`

Spatial geometries retain their CRS/SRID when written to PostGIS.

GeoPandas/PostGIS integration also creates a spatial GiST index for the geometry column.

### ETL reporting

Successful pipeline executions produce a structured report containing:

- source path;
- destination schema and table;
- target CRS;
- UTC start and finish timestamps;
- source inspection;
- validation result;
- normalized dataset inspection.

Reports can optionally be written to JSON.

Example:

```json
{
  "source_path": "examples/generated/sample_points.gpkg",
  "destination_table": "sample_points",
  "destination_schema": "public",
  "target_crs": "EPSG:31983",
  "source_inspection": {
    "feature_count": 3,
    "crs": "EPSG:4326"
  },
  "validation": {
    "is_valid": true,
    "issues": []
  },
  "normalized_inspection": {
    "feature_count": 3,
    "crs": "EPSG:31983"
  }
}
```

## Technology stack

The project uses:

- Python 3.12+
- GeoPandas
- PyProj
- Shapely
- SQLAlchemy
- GeoAlchemy2
- Psycopg
- Typer
- PostgreSQL
- PostGIS
- pytest
- Docker Compose
- GitHub Actions

## Requirements

- Python 3.12 or newer
- PostgreSQL with PostGIS, or Docker for the provided development database
- Git

Docker Desktop with the WSL 2 backend can be used on Windows.

## Installation

Clone the repository:

```bash
git clone https://github.com/raphaelperrut/geospatial-etl-pipeline.git
cd geospatial-etl-pipeline
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

The CLI entry point is then available as:

```bash
geospatial-etl
```

## Quick start

### 1. Generate the example dataset

The repository includes a deterministic example generator:

```bash
python examples/generate_example.py
```

It creates:

```text
examples/generated/sample_points.gpkg
```

The generated GeoPackage contains three point features in `EPSG:4326` with deliberately non-normalized attribute names.

Generated example artifacts are excluded from version control.

### 2. Start PostGIS with Docker

Start the development database:

```bash
docker compose up -d
```

Check its status:

```bash
docker compose ps
```

The provided Docker Compose configuration creates:

```text
Database: geospatial_etl
User:     geospatial_etl
Password: geospatial_etl
Port:     5432
```

These credentials are intended for local development and testing only.

### 3. Run the ETL pipeline

Example:

```bash
geospatial-etl run \
  examples/generated/sample_points.gpkg \
  --database-url "postgresql+psycopg://geospatial_etl:geospatial_etl@localhost:5432/geospatial_etl" \
  --table sample_points \
  --schema public \
  --target-crs EPSG:31983 \
  --if-exists replace \
  --report examples/generated/etl_report.json
```

PowerShell:

```powershell
geospatial-etl run `
  examples/generated/sample_points.gpkg `
  --database-url "postgresql+psycopg://geospatial_etl:geospatial_etl@localhost:5432/geospatial_etl" `
  --table sample_points `
  --schema public `
  --target-crs EPSG:31983 `
  --if-exists replace `
  --report examples/generated/etl_report.json
```

Expected output:

```text
ETL completed successfully: 3 features loaded into public.sample_points
Report written to: examples/generated/etl_report.json
```

The resulting PostGIS table contains normalized attributes and reprojected geometry:

```text
feature_name | text
source_id    | bigint
geometry     | geometry(Point,31983)
```

## CLI reference

The main command is:

```bash
geospatial-etl run SOURCE [OPTIONS]
```

### Required arguments and options

`SOURCE`

Path to the input vector dataset.

`--database-url`

SQLAlchemy PostgreSQL connection URL.

`--table`

Destination PostGIS table name.

### Optional options

`--schema`

Destination schema.

Default:

```text
public
```

`--target-crs`

Optional target coordinate reference system.

Example:

```text
EPSG:31983
```

If omitted, the source CRS is preserved.

`--if-exists`

Controls how an existing destination table is handled.

Supported values:

```text
fail
replace
append
```

Default:

```text
fail
```

`--report`

Optional path for a JSON ETL report.

Example:

```text
etl_report.json
```

## Python API

The pipeline can also be executed directly from Python.

```python
from geospatial_etl.load import create_postgis_engine
from geospatial_etl.pipeline import run_etl_pipeline


engine = create_postgis_engine(
    "postgresql+psycopg://geospatial_etl:"
    "geospatial_etl@localhost:5432/geospatial_etl"
)

try:
    result = run_etl_pipeline(
        source_path="data/input.gpkg",
        engine=engine,
        table_name="features",
        target_crs="EPSG:31983",
        schema="public",
        if_exists="replace",
    )

    print(result.validation.is_valid)
    print(result.normalized_inspection.crs)
finally:
    engine.dispose()
```

The result provides access to:

```text
source_inspection
validation
normalized_inspection
report
```

## Testing

Run the complete test suite:

```bash
pytest -v
```

The current release-ready checkpoint is:

```text
37 passed
```

The test suite covers:

- vector ingestion;
- unsupported and missing input handling;
- dataset inspection;
- missing CRS detection;
- null, empty and invalid geometries;
- validation behavior;
- attribute normalization;
- duplicate normalized column detection;
- CRS reprojection;
- PostGIS loading behavior;
- pipeline orchestration;
- ETL report generation;
- JSON report output;
- CLI execution;
- real PostGIS integration;
- complete end-to-end ETL execution.

### PostGIS integration tests

Integration tests use the `POSTGIS_TEST_URL` environment variable.

PowerShell:

```powershell
$env:POSTGIS_TEST_URL = "postgresql+psycopg://geospatial_etl:geospatial_etl@localhost:5432/geospatial_etl"
pytest -v
```

Linux/macOS:

```bash
export POSTGIS_TEST_URL="postgresql+psycopg://geospatial_etl:geospatial_etl@localhost:5432/geospatial_etl"
pytest -v
```

Without this variable, tests requiring external PostGIS infrastructure are skipped.

## End-to-end validation

The end-to-end integration test validates the complete workflow against a real PostGIS database:

```text
GeoPackage
    |
    v
Ingestion
    |
    v
Inspection
    |
    v
Validation
    |
    v
Attribute normalization
    |
    v
CRS reprojection
EPSG:4326 -> EPSG:31983
    |
    v
PostGIS load
    |
    v
SQL verification
```

The database verification checks:

- feature count;
- geometry type;
- SRID;
- normalized attribute names;
- persisted spatial geometry.

The complete CLI workflow has also been validated against the Docker-backed PostGIS environment.

## Continuous integration

GitHub Actions automatically runs the test suite on pushes to `main` and pull requests.

The CI environment provisions a PostgreSQL/PostGIS service container and executes both unit and integration tests.

This means the PostGIS loading and end-to-end workflow are validated against real spatial database infrastructure in CI rather than being limited to mocked database calls.

## Docker development environment

The repository includes a `docker-compose.yml` configuration for a reproducible local PostGIS environment.

Start it with:

```bash
docker compose up -d
```

Inspect the service:

```bash
docker compose ps
```

Stop it:

```bash
docker compose down
```

To stop the environment and remove its persistent development volume:

```bash
docker compose down -v
```

The `-v` option deletes the database volume and should only be used when a complete local database reset is intended.

## Project structure

```text
geospatial-etl-pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
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
│   ├── test_e2e.py
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

The implementation separates the ETL workflow into small modules with explicit responsibilities:

```text
ingest.py
    |
    v
inspect.py
    |
    v
validation.py
    |
    v
normalization.py
    |
    v
load.py
    |
    v
PostGIS
```

`pipeline.py` orchestrates these stages and builds the execution result.

`report.py` provides structured execution reporting.

`cli.py` exposes the workflow through the command line.

This separation keeps the individual stages independently testable while providing a single high-level ETL operation.

## Design principles

The project follows a few deliberate constraints:

- explicit ETL stages rather than hidden processing;
- validation before database writes;
- immutable structured inspection and validation results;
- deterministic schema normalization;
- explicit CRS handling;
- reproducible database infrastructure;
- automated unit, integration and end-to-end testing;
- minimal orchestration overhead.

The initial release intentionally avoids external workflow orchestrators such as Airflow, Prefect, Dagster or Celery. The objective is to keep the core geospatial ETL behavior small, transparent and reusable.

## Version 0.1.0 scope

The initial release provides:

- [x] GeoPackage ingestion
- [x] GeoJSON ingestion
- [x] Shapefile ingestion
- [x] structured dataset inspection
- [x] geometry-quality validation
- [x] missing CRS validation
- [x] attribute column normalization
- [x] CRS reprojection
- [x] PostgreSQL/PostGIS loading
- [x] configurable existing-table behavior
- [x] structured ETL execution results
- [x] JSON ETL reports
- [x] command-line interface
- [x] deterministic example dataset
- [x] unit tests
- [x] PostGIS integration tests
- [x] end-to-end ETL test
- [x] Docker Compose development environment
- [x] PostGIS-backed GitHub Actions CI

## Future work

Potential future versions may explore:

- explicit GeoPackage layer selection;
- richer schema validation rules;
- configurable field mappings;
- geometry repair strategies;
- batch ingestion;
- additional spatial database targets;
- database connection configuration through environment variables;
- richer execution metrics and logging;
- larger dataset performance testing.

These features are intentionally outside the `v0.1.0` scope.

## License

This project is licensed under the MIT License.