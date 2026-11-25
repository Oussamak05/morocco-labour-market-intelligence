
"""
Centralized data-loading utilities for Morocco Labour Market Intelligence.

Responsibilities:
- Locate processed datasets.
- Load CSV files.
- Validate dataset schemas.
- Cache loaded data with Streamlit.
"""

from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

# data_loader.py is located inside dashboard/utils/.
# parents[2] takes us back to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"


# --------------------------------------------------
# 2. DATASET CONFIGURATION
# --------------------------------------------------

# Each dataset has a unique identifier, a CSV filename,
# and the columns that must exist in that dataset.

DATASET_CONFIGS = {
    "regional_unemployment": {
        "filename": "i_i3287_long.csv",
        "required_columns": [
            "Milieu",
            "Région",
            "Sexe",
            "Année",
            "Taux_chomage",
        ],
    },

    "age_unemployment": {
        "filename": "i_i4249_long.csv",
        "required_columns": [
            "Tranches d'âge",
            "Milieu",
            "Trimestre",
            "Taux_chomage",
            "Année",
            "Numero_trimestre",
            "Periode",
        ],
    },

    "provincial_unemployment": {
        "filename": "i_imt_txch_02_long.csv",
        "required_columns": [
            "Milieu",
            "Provinces/Préfectures",
            "Annee",
            "Taux_chomage",
        ],
    },

    "provincial_employment": {
        "filename": "i_imt_txemp_02_long.csv",
        "required_columns": [
            "Milieu",
            "Provinces/Préfectures",
            "Annee",
            "Taux_emploi",
        ],
    },

    "employment_unemployment": {
        "filename": "employment_unemployment_comparison_balanced.csv",
        "required_columns": [
            "Provinces/Préfectures",
            "Annee",
            "Taux_emploi",
            "Taux_chomage",
        ],
    },
}


# --------------------------------------------------
# 3. DATASET PATH MANAGEMENT
# --------------------------------------------------

def get_dataset_path(dataset_name: str) -> Path:
    """
    Return the absolute path of a configured dataset.
    """

    if dataset_name not in DATASET_CONFIGS:
        available = ", ".join(DATASET_CONFIGS.keys())

        raise ValueError(
            f"Unknown dataset '{dataset_name}'. "
            f"Available datasets: {available}"
        )

    filename = DATASET_CONFIGS[dataset_name]["filename"]

    return DATA_DIR / filename


# --------------------------------------------------
# 4. DATASET VALIDATION
# --------------------------------------------------

def validate_dataset(
    df: pd.DataFrame,
    dataset_name: str
) -> pd.DataFrame:
    """
    Validate that a dataset is not empty and contains
    all required columns.

    Missing observations are not automatically removed.
    """

    if dataset_name not in DATASET_CONFIGS:
        raise ValueError(
            f"Unknown dataset: '{dataset_name}'"
        )

    if df.empty:
        raise ValueError(
            f"The dataset '{dataset_name}' is empty."
        )

    required_columns = DATASET_CONFIGS[
        dataset_name
    ]["required_columns"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset '{dataset_name}' has an invalid schema. "
            f"Missing columns: {missing_columns}"
        )

    return df


# --------------------------------------------------
# 5. CACHED CSV READING
# --------------------------------------------------

@st.cache_data(show_spinner=False)
def _read_csv(
    file_path: str,
    modified_time_ns: int,
    file_size: int
) -> pd.DataFrame:
    """
    Read a CSV file and cache its content.

    File modification time and size are included in the
    cache key to help detect changes to the source file.
    """

    path = Path(file_path)

    try:
        return pd.read_csv(
            path,
            encoding="utf-8-sig"
        )

    except (UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Unable to read CSV file '{path.name}': {error}"
        ) from error


# --------------------------------------------------
# 6. MAIN DATASET LOADER
# --------------------------------------------------

def load_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Load and validate a processed dataset.
    """

    path = get_dataset_path(dataset_name)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {path}"
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"The dataset path is not a file: {path}"
        )

    # File metadata helps Streamlit identify source changes.
    file_stats = path.stat()

    df = _read_csv(
        str(path),
        file_stats.st_mtime_ns,
        file_stats.st_size
    )

    return validate_dataset(df, dataset_name)


# --------------------------------------------------
# 7. CONVENIENCE LOADING FUNCTIONS
# --------------------------------------------------

def load_regional_unemployment() -> pd.DataFrame:
    return load_dataset("regional_unemployment")


def load_age_unemployment() -> pd.DataFrame:
    return load_dataset("age_unemployment")


def load_provincial_unemployment() -> pd.DataFrame:
    return load_dataset("provincial_unemployment")


def load_provincial_employment() -> pd.DataFrame:
    return load_dataset("provincial_employment")


def load_employment_unemployment() -> pd.DataFrame:
    return load_dataset("employment_unemployment")
