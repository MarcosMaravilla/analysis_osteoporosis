# Analisis estadistico de osteoporosis

Proyecto reproducible para limpieza de datos, analisis estadistico, tablas, figuras e informe del analisis de osteoporosis.

## Configuracion del entorno

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m ipykernel install --user --name osteoporosis-analysis --display-name "Python (osteoporosis-analysis)"
```

El proyecto usa `.env` para rutas locales y parametros reproducibles. El archivo `.env` no se versiona; `.env.example` queda como plantilla.

```powershell
Copy-Item .env.example .env
```

## Limpieza de datos

Coloca el archivo de entrada en `data/raw/datos_osteoporosis.csv` o ajusta `RAW_CSV_PATH` en `.env`.

```powershell
.\.venv\Scripts\python.exe src/01_limpieza_datos.py
```

El archivo limpio se exportara por defecto a `data/processed/datos_osteoporosis_limpios.csv`.

## Regeneracion de tablas, figuras e informe

El flujo estadistico reproducible del manuscrito se concentra en:

```powershell
.\.venv\Scripts\python.exe src/export_tables_pdf.py
```

Este comando regenera las tablas en `results/tablas_resultados_apa.pdf`, la curva ROC, la curva de calibracion, las tablas CSV y el informe multivariado en Markdown.
