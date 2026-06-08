from pathlib import Path

import pandas as pd

from config import CLEAN_CSV_PATH, RAW_CSV_PATH


class DataCleaner:
    """Carga, limpia y exporta un CSV para el flujo inicial del proyecto."""

    def __init__(
        self,
        input_path: str | Path = RAW_CSV_PATH,
        output_path: str | Path = CLEAN_CSV_PATH,
    ) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.data: pd.DataFrame | None = None

    def load_data(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise FileNotFoundError(f"No existe el archivo de entrada: {self.input_path}")

        self.data = pd.read_csv(self.input_path)
        return self.data

    def clean_data(self) -> pd.DataFrame:
        if self.data is None:
            raise RuntimeError("Primero carga los datos con load_data().")

        clean_df = self.data.drop_duplicates().copy()

        numeric_columns = clean_df.select_dtypes(include="number").columns
        categorical_columns = clean_df.select_dtypes(exclude="number").columns

        for column in numeric_columns:
            clean_df[column] = clean_df[column].fillna(clean_df[column].median())

        for column in categorical_columns:
            mode = clean_df[column].mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else "Desconocido"
            clean_df[column] = clean_df[column].fillna(fill_value)

        self.data = clean_df
        return self.data

    def save_data(self) -> None:
        if self.data is None:
            raise RuntimeError("No hay datos limpios para guardar.")

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.data.to_csv(self.output_path, index=False)

    def run(self) -> pd.DataFrame:
        self.load_data()
        self.clean_data()
        self.save_data()
        return self.data


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.run()
    print("Limpieza de datos completada.")
