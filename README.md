# Geospatial ETL Pipeline

A reproducible Python ETL pipeline for ingesting, validating, transforming and loading heterogeneous geospatial datasets into PostGIS.

## Status

🚧 Early development

## Planned capabilities

- Ingest vector geospatial datasets from multiple formats
- Inspect and validate spatial schemas and geometries
- Detect and handle CRS inconsistencies
- Normalize attributes and geometry types
- Transform datasets into a common target CRS
- Load processed datasets into PostgreSQL/PostGIS
- Produce structured ETL execution reports
- Expose the workflow through a command-line interface
- Support reproducible execution with Docker
- Validate the pipeline with automated tests

## Tech stack

`Python` · `GeoPandas` · `GDAL` · `PyProj` · `Shapely` · `PostgreSQL` · `PostGIS` · `SQLAlchemy` · `Docker`

## License

MIT
