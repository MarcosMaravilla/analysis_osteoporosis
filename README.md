# Análisis Estadístico
Descripción, objetivos y metodología del proyecto.

## Configuración del entorno

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Ejecución del script de limpieza

Coloca el archivo de entrada en `data/raw/datos_osteoporosis.csv` y ejecuta:

```bash
python src/01_limpieza_datos.py
```

El archivo limpio se exportará a `data/processed/datos_osteoporosis_limpios.csv`.

## Regeneración de tablas, figuras e informe

El flujo estadístico reproducible del manuscrito se concentra en:

```bash
.venv/bin/python src/export_tables_pdf.py
```

Este comando regenera las tablas en `results/tablas_resultados_apa.pdf`, la curva ROC, la curva de calibración, las tablas CSV y el informe multivariado en Markdown.
