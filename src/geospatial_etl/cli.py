"""Command-line interface for the geospatial ETL pipeline."""

from pathlib import Path

import typer

from geospatial_etl.load import create_postgis_engine
from geospatial_etl.pipeline import run_etl_pipeline
from geospatial_etl.report import write_etl_report


app = typer.Typer(
    help="Run reproducible geospatial ETL workflows into PostGIS."
)


@app.callback()
def main() -> None:
    """Geospatial ETL Pipeline CLI."""


@app.command()
def run(
    source: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Input vector dataset.",
    ),
    database_url: str = typer.Option(
        ...,
        "--database-url",
        help="SQLAlchemy PostgreSQL connection URL.",
    ),
    table: str = typer.Option(
        ...,
        "--table",
        help="Destination PostGIS table.",
    ),
    schema: str = typer.Option(
        "public",
        "--schema",
        help="Destination database schema.",
    ),
    target_crs: str | None = typer.Option(
        None,
        "--target-crs",
        help="Optional target CRS, for example EPSG:31983.",
    ),
    if_exists: str = typer.Option(
        "fail",
        "--if-exists",
        help="Existing table behavior: fail, replace or append.",
    ),
    report: Path | None = typer.Option(
        None,
        "--report",
        help="Optional output path for the JSON ETL report.",
    ),
) -> None:
    """Run the ETL pipeline and load the result into PostGIS."""

    engine = create_postgis_engine(database_url)

    try:
        result = run_etl_pipeline(
            source_path=source,
            engine=engine,
            table_name=table,
            target_crs=target_crs,
            schema=schema,
            if_exists=if_exists,
        )

        if report is not None:
            write_etl_report(
                result.report,
                report,
            )

        typer.echo(
            f"ETL completed successfully: "
            f"{result.normalized_inspection.feature_count} features "
            f"loaded into {schema}.{table}"
        )

        if report is not None:
            typer.echo(f"Report written to: {report}")

    except ValueError as exc:
        typer.echo(
            f"ETL failed: {exc}",
            err=True,
        )
        raise typer.Exit(code=1) from exc

    finally:
        engine.dispose()