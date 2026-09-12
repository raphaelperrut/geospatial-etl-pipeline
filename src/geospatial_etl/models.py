"""Data models for geospatial dataset inspection and validation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetInspection:
    """Structured summary of a geospatial vector dataset."""

    feature_count: int
    crs: str | None
    geometry_column: str
    geometry_types: tuple[str, ...]
    attribute_columns: tuple[str, ...]
    null_geometry_count: int
    empty_geometry_count: int
    invalid_geometry_count: int
    bounds: tuple[float, float, float, float] | None


@dataclass(frozen=True)
class ValidationIssue:
    """Single validation issue found in a dataset."""

    code: str
    message: str


@dataclass(frozen=True)
class DatasetValidation:
    """Structured result of dataset validation."""

    is_valid: bool
    issues: tuple[ValidationIssue, ...]