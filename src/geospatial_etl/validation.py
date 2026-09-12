"""Validation utilities for geospatial datasets."""

from geospatial_etl.models import (
    DatasetInspection,
    DatasetValidation,
    ValidationIssue,
)


def validate_dataset(
    inspection: DatasetInspection,
) -> DatasetValidation:
    """Validate a dataset from its inspection summary.

    Parameters
    ----------
    inspection
        Structured dataset inspection result.

    Returns
    -------
    DatasetValidation
        Validation result containing all detected issues.
    """

    issues: list[ValidationIssue] = []

    if inspection.feature_count == 0:
        issues.append(
            ValidationIssue(
                code="empty_dataset",
                message="Dataset contains no features.",
            )
        )

    if inspection.crs is None:
        issues.append(
            ValidationIssue(
                code="missing_crs",
                message="Dataset has no defined CRS.",
            )
        )

    if inspection.null_geometry_count > 0:
        issues.append(
            ValidationIssue(
                code="null_geometries",
                message=(
                    f"Dataset contains "
                    f"{inspection.null_geometry_count} null geometries."
                ),
            )
        )

    if inspection.empty_geometry_count > 0:
        issues.append(
            ValidationIssue(
                code="empty_geometries",
                message=(
                    f"Dataset contains "
                    f"{inspection.empty_geometry_count} empty geometries."
                ),
            )
        )

    if inspection.invalid_geometry_count > 0:
        issues.append(
            ValidationIssue(
                code="invalid_geometries",
                message=(
                    f"Dataset contains "
                    f"{inspection.invalid_geometry_count} invalid geometries."
                ),
            )
        )

    return DatasetValidation(
        is_valid=not issues,
        issues=tuple(issues),
    )