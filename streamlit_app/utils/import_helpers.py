"""Helpers for importing Jobs/Candidates from CSV/Excel with schema validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class ImportSchema:
    name: str
    required_columns: Tuple[str, ...]
    optional_columns: Tuple[str, ...] = ()

    @property
    def all_columns(self) -> Tuple[str, ...]:
        return self.required_columns + self.optional_columns


JOBS_SCHEMA = ImportSchema(
    name="jobs",
    required_columns=("external_job_id", "external_company_id", "company_name", "raw_description"),
    optional_columns=(),
)

CANDIDATES_SCHEMA = ImportSchema(
    name="candidates",
    required_columns=("external_student_id", "skills"),
    optional_columns=(
        "education_level",
        "education_field",
        "university",
        "preferred_locations",
        "preferred_job_types",
        "industries",
    ),
)


def normalize_column_name(col: str) -> str:
    return col.strip()


def validate_columns(
    columns: Iterable[str],
    schema: ImportSchema,
) -> Tuple[bool, List[str], List[str]]:
    cols = [normalize_column_name(c) for c in columns]
    missing = [c for c in schema.required_columns if c not in cols]
    extra = [c for c in cols if c not in schema.all_columns]
    return (len(missing) == 0, missing, extra)


def split_csvish(value: Optional[str]) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    # Allow comma or semicolon separators
    raw = s.replace(";", ",").split(",")
    return [x.strip() for x in raw if x.strip()]


def candidate_profile_from_row(row: Dict[str, object]) -> Dict[str, object]:
    skills = split_csvish(str(row.get("skills", "") or ""))
    edu_level = str(row.get("education_level", "") or "").strip() or None
    edu_field = str(row.get("education_field", "") or "").strip() or None
    university = str(row.get("university", "") or "").strip() or None

    locations = split_csvish(
        str(row.get("preferred_locations", "") or "")
    )
    job_types = split_csvish(
        str(row.get("preferred_job_types", "") or "")
    )
    industries = split_csvish(str(row.get("industries", "") or ""))

    profile: Dict[str, object] = {"skills": skills}
    profile["education"] = {
        "level": edu_level,
        "field": edu_field,
        "university": university,
    }
    profile["preferences"] = {
        "locations": locations,
        "job_types": job_types,
        "industries": industries,
    }
    return profile


