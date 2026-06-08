from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


DEFAULT_PROJECT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR_VALUE = Path(os.getenv("ANALYSIS_PROJECT_DIR", str(DEFAULT_PROJECT_DIR))).expanduser()
PROJECT_DIR = (
    PROJECT_DIR_VALUE if PROJECT_DIR_VALUE.is_absolute() else DEFAULT_PROJECT_DIR / PROJECT_DIR_VALUE
).resolve()


def project_path(value: str | None, default: Path) -> Path:
    if not value:
        return default

    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_DIR / path


DATA_RAW_DIR = project_path(os.getenv("DATA_RAW_DIR"), PROJECT_DIR / "data" / "raw")
DATA_PROCESSED_DIR = project_path(os.getenv("DATA_PROCESSED_DIR"), PROJECT_DIR / "data" / "processed")
RESULTS_DIR = project_path(os.getenv("RESULTS_DIR"), PROJECT_DIR / "results")

RAW_CSV_PATH = project_path(os.getenv("RAW_CSV_PATH"), DATA_RAW_DIR / "datos_osteoporosis.csv")
RAW_EXCEL_PATH = project_path(os.getenv("RAW_EXCEL_PATH"), DATA_RAW_DIR / "BD_Analysis_Osteoporosis.xlsx")
CLEAN_CSV_PATH = project_path(os.getenv("CLEAN_CSV_PATH"), DATA_PROCESSED_DIR / "datos_osteoporosis_limpios.csv")
CLEAN_PARQUET_PATH = project_path(os.getenv("CLEAN_PARQUET_PATH"), DATA_PROCESSED_DIR / "BD_Clean_Osteoporosis.parquet")
CLEAN_PICKLE_PATH = project_path(os.getenv("CLEAN_PICKLE_PATH"), DATA_PROCESSED_DIR / "BD_Clean_Osteoporosis.pkl")

BOOTSTRAP_ITERATIONS = int(os.getenv("BOOTSTRAP_ITERATIONS", "200"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "20260608"))

MPLCONFIGDIR = project_path(os.getenv("MPLCONFIGDIR"), PROJECT_DIR / ".cache" / "matplotlib")
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
