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
