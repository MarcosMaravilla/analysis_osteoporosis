from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency, fisher_exact, shapiro


PROJECT_DIR = Path("/home/marcos-maravilla/análisis_estadístico_osteoporosis")
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
RESULTS_DIR = PROJECT_DIR / "results"
OUTPUT_PDF = RESULTS_DIR / "tablas_resultados_apa.pdf"


def load_clean_data():
    parquet_path = PROCESSED_DIR / "BD_Clean_Osteoporosis.parquet"
    pickle_path = PROCESSED_DIR / "BD_Clean_Osteoporosis.pkl"

    try:
        return pd.read_parquet(parquet_path)
    except Exception:
        return pd.read_pickle(pickle_path)


def format_p_value(value, digits=4):
    if value == "" or pd.isna(value):
        return ""
    value = float(value)
    return "< 0.001" if value < 0.001 else f"{value:.{digits}f}"


def wrap_text(value, width):
    if value == "" or pd.isna(value):
        return ""
    return "\n".join(wrap(str(value), width=width, break_long_words=False))


def build_normality_table(df):
    continuous_variables = ["edad", "peso_(kg)", "altura_(cm)", "imc"]
    variable_labels = {
        "edad": "Edad (años)",
        "peso_(kg)": "Peso (kg)",
        "altura_(cm)": "Altura (cm)",
        "imc": "IMC",
    }
    rows = []

    for variable in continuous_variables:
        values = pd.to_numeric(df[variable], errors="coerce").dropna()
        statistic, p_value = shapiro(values)
        rows.append(
            {
                "Variable": variable_labels[variable],
                "n": len(values),
                "W": f"{statistic:.4f}",
                "p-value": format_p_value(p_value),
                "Interpretación": "No normal" if p_value < 0.05 else "Normal",
            }
        )

    return pd.DataFrame(rows)


def build_continuous_descriptive_table(df):
    continuous_variables = ["edad", "peso_(kg)", "altura_(cm)", "imc"]
    variable_labels = {
        "edad": "Edad (años)",
        "peso_(kg)": "Peso (kg)",
        "altura_(cm)": "Altura (cm)",
        "imc": "IMC",
    }
    rows = []

    for variable in continuous_variables:
        values = pd.to_numeric(df[variable], errors="coerce").dropna()
        q1 = values.quantile(0.25)
        median = values.median()
        q3 = values.quantile(0.75)
        rows.append(
            {
                "Variable": variable_labels[variable],
                "n": len(values),
                "Mediana (Q1, Q3)": f"{median:.2f} ({q1:.2f}, {q3:.2f})",
                "RIC": f"{q1:.2f} - {q3:.2f}",
                "Mínimo - Máximo": f"{values.min():.2f} - {values.max():.2f}",
                "Valores nulos": int(df[variable].isna().sum()),
            }
        )

    return pd.DataFrame(rows)


VARS_CAT = [
    "edad_cat",
    "sexo",
    "e_civil",
    "l_resid_municipio",
    "escolaridad",
    "trabaja",
    "ing_mensual_cat",
    "derechohabiente_cat",
    "enfermedad_cat",
    "vive_con_cat",
    "ayuda_enf_cod",
    "grupo_externo_enf",
    "realiza_af",
    "frecuencia_af",
    "plan_alimenticio",
    "lacteos_frecuentes",
    "imc_cat",
]

COLUMN_ALIASES = {
    "e_civil": "estado_civil",
    "l_resid_municipio": "lugar_residencia_municipio",
    "ayuda_enf_cod": "ayuda_enf_cat",
}

VARIABLE_GROUPS = {
    "Características demográficas": ["edad_cat", "sexo", "e_civil", "l_resid_municipio"],
    "Condiciones materiales de la vida": ["escolaridad", "trabaja", "ing_mensual_cat"],
    "Sistema sanitario": ["derechohabiente_cat", "enfermedad_cat"],
    "Cohesión social": ["vive_con_cat", "ayuda_enf_cod", "grupo_externo_enf"],
    "Estilo de vida": ["realiza_af", "frecuencia_af", "plan_alimenticio", "frecuencia_lacteos_cat", "imc_cat"],
}

VARIABLE_LABELS = {
    "edad_cat": "Edad",
    "sexo": "Sexo",
    "e_civil": "Estado civil",
    "l_resid_municipio": "Lugar de residencia",
    "escolaridad": "Escolaridad",
    "trabaja": "Situación laboral",
    "ing_mensual_cat": "Situación económica",
    "derechohabiente_cat": "Derechohabiente",
    "enfermedad_cat": "Enfermedad",
    "vive_con_cat": "Convivencia",
    "ayuda_enf_cod": "Apoyo en enfermedad",
    "grupo_externo_enf": "Participación en grupos de ayuda mutua",
    "realiza_af": "Actividad física",
    "frecuencia_af": "Frecuencia de actividad física",
    "plan_alimenticio": "Plan alimenticio",
    "frecuencia_lacteos_cat": "Consumo de lácteos",
    "imc_cat": "Clasificación IMC",
}

CATEGORY_LABELS = {
    "edad_cat": {"1": "50-59", "2": "60 a 69", "3": "70 y más"},
    "sexo": {"0": "Hombre", "1": "Mujer"},
    "e_civil": {"0": "Sin pareja", "1": "En pareja"},
    "l_resid_municipio": {"0": "Municipios de Jalisco", "1": "Zona Metropolitana de Guadalajara"},
    "escolaridad": {"0": "Sin estudios", "1": "Con estudios"},
    "trabaja": {"0": "Desempleado", "1": "Con trabajo"},
    "ing_mensual_cat": {"0": "Sin información", "1": "Nivel bajo", "2": "Nivel medio", "3": "Nivel alto"},
    "derechohabiente_cat": {"0": "Sin cobertura", "1": "Con cobertura"},
    "enfermedad_cat": {"0": "Sano", "1": "Síndrome metabólico", "2": "Otras enfermedades"},
    "vive_con_cat": {"0": "Vive solo", "1": "Acompañado"},
    "ayuda_enf_cod": {"0": "Autocuidado", "1": "Tiene apoyo"},
    "grupo_externo_enf": {"0": "No participa", "1": "Sí participa"},
    "realiza_af": {"0": "No realiza", "1": "Sí realiza"},
    "frecuencia_af": {"0": "No aplica", "1": "1 vez", "2": "2-3 veces", "3": "4-5 veces", "4": "6+ veces"},
    "plan_alimenticio": {"0": "Sin plan alimenticio", "1": "Con plan alimenticio"},
    "imc_cat": {"1": "Normal", "2": "Sobrepeso", "3": "Obesidad"},
}

CATEGORY_ORDERS = {
    "edad_cat": ["1", "2", "3"],
    "sexo": ["0", "1"],
    "e_civil": ["1", "0"],
    "l_resid_municipio": ["0", "1"],
    "escolaridad": ["1", "0"],
    "trabaja": ["1", "0"],
    "ing_mensual_cat": ["1", "2", "3", "0"],
    "derechohabiente_cat": ["0", "1"],
    "enfermedad_cat": ["1", "2", "0"],
    "vive_con_cat": ["1", "0"],
    "ayuda_enf_cod": ["0", "1"],
    "grupo_externo_enf": ["0", "1"],
    "realiza_af": ["0", "1"],
    "frecuencia_af": ["4", "3", "2", "1", "0"],
    "plan_alimenticio": ["1", "0"],
    "frecuencia_lacteos_cat": ["Alta (5-7 días)", "Media (3-4 días)", "Baja (0-2 días)"],
    "imc_cat": ["1", "2", "3"],
}


def build_categorical_bivariate_table(df, variables, outcome="alteracion_osea"):
    rows = []
    outcome_values = pd.to_numeric(df[outcome].astype("string"), errors="coerce")
    total_n = len(df)

    for variable in variables:
        column = COLUMN_ALIASES.get(variable, variable)
        categories = df[column].astype("string").fillna("Sin dato")
        counts = pd.crosstab(categories, outcome_values)

        for outcome_value in [0, 1]:
            if outcome_value not in counts.columns:
                counts[outcome_value] = 0

        counts = counts[[0, 1]].sort_index()
        row_percent = counts.div(counts.sum(axis=1), axis=0).mul(100)
        _, chi2_p, _, expected = chi2_contingency(counts)
        p_value = fisher_exact(counts.to_numpy())[1] if (expected < 5).any() and counts.shape == (2, 2) else chi2_p

        for idx, category in enumerate(counts.index):
            normal_n = int(counts.loc[category, 0])
            altered_n = int(counts.loc[category, 1])
            category_n = normal_n + altered_n
            category_pct = category_n / total_n * 100
            rows.append(
                {
                    "Variable": variable if idx == 0 else "",
                    "Categoría": category,
                    "Total (n, %)": f"{category_n} ({category_pct:.1f})",
                    "Con alteración ósea (n, %)": f"{altered_n} ({row_percent.loc[category, 1]:.1f})",
                    "Sin alteración ósea (n, %)": f"{normal_n} ({row_percent.loc[category, 0]:.1f})",
                    "p-value": format_p_value(p_value) if idx == 0 else "",
                }
            )

    return pd.DataFrame(rows)


def prepare_grouped_categorical_table(df):
    df_bivariate = df.copy()
    df_bivariate["frecuencia_lacteos_cat"] = pd.cut(
        pd.to_numeric(df_bivariate["frecuencia_lacteos"], errors="coerce"),
        bins=[-np.inf, 1, 2, np.inf],
        labels=["Baja (0-2 días)", "Media (3-4 días)", "Alta (5-7 días)"],
    )
    variables = ["frecuencia_lacteos_cat" if variable == "lacteos_frecuentes" else variable for variable in VARS_CAT]
    table = build_categorical_bivariate_table(df_bivariate, variables)
    table["_variable_key"] = table["Variable"].replace("", pd.NA).ffill()
    rows = []

    for section, variables_in_group in VARIABLE_GROUPS.items():
        rows.append(
            {
                "Variable": section,
                "Categoría": "",
                "Total (n, %)": "",
                "Con alteración ósea (n, %)": "",
                "Sin alteración ósea (n, %)": "",
                "p-value": "",
                "_section": True,
            }
        )

        for variable in variables_in_group:
            variable_rows = table.loc[table["_variable_key"] == variable].copy()
            if variable_rows.empty:
                continue

            order = CATEGORY_ORDERS.get(variable)
            if order is not None:
                order_map = {value: idx for idx, value in enumerate(order)}
                variable_rows["_order"] = variable_rows["Categoría"].astype(str).map(order_map)
                variable_rows = variable_rows.sort_values("_order", na_position="last")

            for row_idx, (_, row) in enumerate(variable_rows.iterrows()):
                category = str(row["Categoría"])
                rows.append(
                    {
                        "Variable": VARIABLE_LABELS.get(variable, variable) if row_idx == 0 else "",
                        "Categoría": CATEGORY_LABELS.get(variable, {}).get(category, category),
                        "Total (n, %)": row["Total (n, %)"],
                        "Con alteración ósea (n, %)": row["Con alteración ósea (n, %)"],
                        "Sin alteración ósea (n, %)": row["Sin alteración ósea (n, %)"],
                        "p-value": row["p-value"] if row_idx == 0 else "",
                        "_section": False,
                    }
                )

    return pd.DataFrame(rows)


def code_binary(series, mapping, variable_name):
    values = series.astype("string").str.strip().str.lower()
    coded = values.map(mapping)
    if coded.isna().any():
        unmapped = sorted(values.loc[coded.isna()].dropna().unique())
        raise ValueError(f"Valores no mapeados en {variable_name}: {unmapped}")
    return coded.astype(int)


def build_logistic_tables(df):
    predictors = ["edad", "imc", "sexo", "trabaja", "enfermedad_cat", "realiza_af"]
    model_data = df[["alteracion_osea", *predictors]].copy()
    binary_maps = {
        "sexo": {"0": 0, "0.0": 0, "hombre": 0, "1": 1, "1.0": 1, "mujer": 1},
        "trabaja": {"0": 0, "0.0": 0, "no": 0, "1": 1, "1.0": 1, "sí": 1, "si": 1},
        "realiza_af": {"0": 0, "0.0": 0, "no": 0, "1": 1, "1.0": 1, "sí": 1, "si": 1},
    }

    for variable in ["alteracion_osea", "edad", "imc", "enfermedad_cat"]:
        model_data[variable] = pd.to_numeric(model_data[variable], errors="coerce")

    for variable in ["sexo", "trabaja", "realiza_af"]:
        model_data[variable] = code_binary(model_data[variable], binary_maps[variable], variable)

    model_data = model_data.dropna().copy()
    y = model_data["alteracion_osea"].astype(int)
    x_base = model_data[["edad", "imc", "sexo", "trabaja", "realiza_af"]].astype(float)

    if model_data["enfermedad_cat"].nunique() > 2:
        enfermedad_dummies = pd.get_dummies(
            model_data["enfermedad_cat"].astype(int).astype("category"),
            prefix="enfermedad_cat",
            drop_first=True,
            dtype=float,
        )
        x_encoded = pd.concat([x_base, enfermedad_dummies], axis=1)
    else:
        x_encoded = x_base.assign(enfermedad_cat=model_data["enfermedad_cat"].astype(float))

    x_current = sm.add_constant(x_encoded.astype(float), has_constant="add")
    history = []

    while True:
        model = sm.Logit(y, x_current).fit(method="bfgs", disp=False, maxiter=200)
        p_values = model.pvalues.drop("const")
        worst_variable = p_values.idxmax()
        p_max = float(p_values.max())
        action = "Eliminar" if p_max > 0.10 else "Detener"
        history.append(
            {
                "Iteración": len(history) + 1,
                "Variables": ", ".join(x_current.columns.drop("const")),
                "Variable con mayor p": worst_variable,
                "p máximo": format_p_value(p_max),
                "Acción": action,
            }
        )

        if p_max <= 0.10:
            final_model = model
            break

        x_current = x_current.drop(columns=worst_variable)

    labels = {
        "const": "Intercepto",
        "edad": "Edad",
        "imc": "IMC",
        "sexo": "Sexo: mujer vs hombre",
        "trabaja": "Trabaja: sí vs no",
        "realiza_af": "Actividad física: sí vs no",
        "enfermedad_cat": "Enfermedad",
        "enfermedad_cat_1": "Enfermedad: síndrome metabólico vs sano",
        "enfermedad_cat_2": "Enfermedad: otras enfermedades vs sano",
    }
    params = final_model.params
    intervals = final_model.conf_int()
    regression_table = pd.DataFrame(
        {
            "Variable": [labels.get(variable, variable) for variable in params.index],
            "Coeficiente (B)": [f"{value:.3f}" for value in params.values],
            "Error Estándar": [f"{value:.3f}" for value in final_model.bse.values],
            "Valor p": [format_p_value(value, digits=3) for value in final_model.pvalues.values],
            "OR": [f"{value:.2f}" for value in np.exp(params).values],
            "IC 95% Inferior": [f"{value:.2f}" for value in np.exp(intervals[0]).values],
            "IC 95% Superior": [f"{value:.2f}" for value in np.exp(intervals[1]).values],
        }
    )

    return pd.DataFrame(history), regression_table


def paginate_rows(table, rows_per_page):
    for start in range(0, len(table), rows_per_page):
        yield table.iloc[start : start + rows_per_page].copy(), start // rows_per_page + 1


def draw_table_page(
    pdf,
    table,
    number,
    title,
    note=None,
    page_suffix=None,
    column_widths=None,
    wrap_widths=None,
    header_wrap_widths=None,
    section_column=None,
):
    fig, ax = plt.subplots(figsize=(13, 8.5))
    ax.axis("off")

    table_label = f"Tabla {number}" if page_suffix is None else f"Tabla {number} ({page_suffix})"
    ax.text(0.03, 0.96, table_label, ha="left", va="top", fontsize=11, fontweight="bold", family="serif")
    ax.text(0.03, 0.925, title, ha="left", va="top", fontsize=11, fontstyle="italic", family="serif")

    display_table = table.copy()
    if section_column and section_column in display_table.columns:
        sections = display_table[section_column].tolist()
        display_table = display_table.drop(columns=[section_column])
    else:
        sections = [False] * len(display_table)

    if wrap_widths is None:
        wrap_widths = {column: 18 for column in display_table.columns}
    if header_wrap_widths is None:
        header_wrap_widths = {column: 16 for column in display_table.columns}

    column_labels = [
        wrap_text(column, header_wrap_widths.get(column, 16))
        for column in display_table.columns
    ]

    cell_text = [
        [wrap_text(row[column], wrap_widths.get(column, 18)) for column in display_table.columns]
        for _, row in display_table.iterrows()
    ]

    if column_widths is None:
        column_widths = [1 / len(display_table.columns)] * len(display_table.columns)

    max_height = 0.76 if note else 0.80
    table_height = max_height if len(display_table) > 12 else min(max_height, 0.07 * (len(display_table) + 1) + 0.05)
    table_top = 0.84
    bbox = [0.03, table_top - table_height, 0.94, table_height]
    table_artist = ax.table(
        cellText=cell_text,
        colLabels=column_labels,
        cellLoc="left",
        colLoc="center",
        colWidths=column_widths,
        bbox=bbox,
    )
    table_artist.auto_set_font_size(False)
    table_artist.set_fontsize(7.8)

    for (row, col), cell in table_artist.get_celld().items():
        cell.set_facecolor("white")
        cell.set_edgecolor("black")
        cell.PAD = 0.03
        cell.get_text().set_fontfamily("serif")

        if row == 0:
            cell.visible_edges = "TB"
            cell.set_linewidth(0.8)
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_ha("center")
        else:
            is_section = bool(sections[row - 1])
            if is_section:
                cell.visible_edges = "TB"
                cell.set_linewidth(0.6)
                cell.get_text().set_fontstyle("italic")
                cell.get_text().set_fontweight("bold")
                if col > 0:
                    cell.get_text().set_text("")
            else:
                cell.visible_edges = ""
                cell.set_linewidth(0)
                if col >= 2 or display_table.columns[col] in {"n", "W", "p-value", "p máximo", "OR"}:
                    cell.get_text().set_ha("right")
                else:
                    cell.get_text().set_ha("left")

    last_row = len(display_table)
    for col in range(len(display_table.columns)):
        table_artist[(last_row, col)].visible_edges = "B"
        table_artist[(last_row, col)].set_linewidth(0.8)

    if note:
        ax.text(0.03, 0.075, f"Nota. {note}", ha="left", va="top", fontsize=8.5, family="serif", wrap=True)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def export_pdf():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean_data()
    normality_table = build_normality_table(df)
    continuous_table = build_continuous_descriptive_table(df)
    categorical_table = prepare_grouped_categorical_table(df)
    backward_table, regression_table = build_logistic_tables(df)

    with PdfPages(OUTPUT_PDF) as pdf:
        draw_table_page(
            pdf,
            normality_table,
            1,
            "Pruebas de normalidad para variables continuas",
            "Prueba de Shapiro-Wilk; p < 0.05 indica desviación estadísticamente significativa de la normalidad.",
            column_widths=[0.28, 0.10, 0.14, 0.14, 0.24],
            wrap_widths={"Variable": 24, "Interpretación": 18},
        )
        draw_table_page(
            pdf,
            continuous_table,
            2,
            "Descripción global de variables continuas",
            "Las variables se resumen con mediana y rango intercuartílico por la evidencia de no normalidad.",
            column_widths=[0.20, 0.08, 0.22, 0.18, 0.22, 0.10],
            wrap_widths={"Variable": 22, "Mediana (Q1, Q3)": 20, "Mínimo - Máximo": 18},
        )

        for page_table, page_number in paginate_rows(categorical_table, rows_per_page=19):
            draw_table_page(
                pdf,
                page_table,
                3,
                "Características categóricas de los pacientes evaluados según alteración ósea (n = 405)",
                "Los porcentajes de las columnas con y sin alteración ósea corresponden a porcentajes por fila. Los valores p provienen de Chi-cuadrada o prueba exacta de Fisher cuando corresponde.",
                page_suffix=f"continuación {page_number}" if page_number > 1 else None,
                column_widths=[0.17, 0.22, 0.13, 0.21, 0.21, 0.06],
                wrap_widths={"Variable": 36, "Categoría": 30},
                header_wrap_widths={
                    "Variable": 18,
                    "Categoría": 18,
                    "Total (n, %)": 14,
                    "Con alteración ósea (n, %)": 22,
                    "Sin alteración ósea (n, %)": 22,
                    "p-value": 8,
                },
                section_column="_section",
            )

        draw_table_page(
            pdf,
            backward_table,
            "S1",
            "Proceso de eliminación hacia atrás del modelo logístico",
            "El criterio de permanencia fue p <= 0.10; la variable con mayor valor p se eliminó en cada iteración.",
            column_widths=[0.08, 0.48, 0.20, 0.12, 0.12],
            wrap_widths={"Variables": 70, "Variable con mayor p": 28},
        )
        draw_table_page(
            pdf,
            regression_table,
            4,
            "Modelo de regresión logística multivariada para alteración ósea",
            "B = coeficiente logit; OR = odds ratio; IC = intervalo de confianza. La categoría de referencia para sexo es Hombre (0); para trabaja y actividad física es No (0). El modelo final proviene de eliminación hacia atrás con criterio p <= 0.10.",
            column_widths=[0.25, 0.13, 0.13, 0.10, 0.10, 0.14, 0.15],
            wrap_widths={"Variable": 30},
        )

    return OUTPUT_PDF


if __name__ == "__main__":
    output_path = export_pdf()
    print(f"PDF de tablas generado: {output_path}")
