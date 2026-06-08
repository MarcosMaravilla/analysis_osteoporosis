import os
from pathlib import Path
from textwrap import wrap

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, shapiro
from sklearn.metrics import auc, brier_score_loss, roc_curve
from statsmodels.stats.outliers_influence import variance_inflation_factor


PROJECT_DIR = Path("/home/marcos-maravilla/análisis_estadístico_osteoporosis")
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
RESULTS_DIR = PROJECT_DIR / "results"
OUTPUT_PDF = RESULTS_DIR / "tablas_resultados_apa.pdf"
ROC_PDF = RESULTS_DIR / "curva_roc.pdf"
CALIBRATION_PDF = RESULTS_DIR / "calibracion_modelo.pdf"
SUMMARY_MD = RESULTS_DIR / "informe_resultados.md"
BOOTSTRAP_ITERATIONS = 200
RANDOM_SEED = 20260608


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


def median_iqr(values):
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        return "NA"
    q1 = values.quantile(0.25)
    median = values.median()
    q3 = values.quantile(0.75)
    return f"{median:.2f} ({q1:.2f}, {q3:.2f})"


def cliffs_delta(group_a, group_b):
    group_a = pd.to_numeric(group_a, errors="coerce").dropna().to_numpy()
    group_b = pd.to_numeric(group_b, errors="coerce").dropna().to_numpy()
    if len(group_a) == 0 or len(group_b) == 0:
        return np.nan
    u_statistic = mannwhitneyu(group_a, group_b, alternative="two-sided").statistic
    return (2 * u_statistic / (len(group_a) * len(group_b))) - 1


def interpret_cliffs_delta(delta):
    if pd.isna(delta):
        return "No estimable"
    absolute_delta = abs(delta)
    if absolute_delta < 0.147:
        return "Trivial"
    if absolute_delta < 0.33:
        return "Pequeño"
    if absolute_delta < 0.474:
        return "Mediano"
    return "Grande"


def build_continuous_bivariate_table(df, outcome="alteracion_osea"):
    continuous_variables = ["edad", "peso_(kg)", "altura_(cm)", "imc"]
    variable_labels = {
        "edad": "Edad (años)",
        "peso_(kg)": "Peso (kg)",
        "altura_(cm)": "Altura (cm)",
        "imc": "IMC",
    }
    rows = []
    outcome_values = pd.to_numeric(df[outcome].astype("string"), errors="coerce")

    for variable in continuous_variables:
        values = pd.to_numeric(df[variable], errors="coerce")
        altered = values.loc[outcome_values.eq(1)].dropna()
        normal = values.loc[outcome_values.eq(0)].dropna()
        u_statistic, p_value = mannwhitneyu(altered, normal, alternative="two-sided")
        delta = cliffs_delta(altered, normal)
        rows.append(
            {
                "Variable": variable_labels[variable],
                "Alteración ósea\nMediana (Q1, Q3)": median_iqr(altered),
                "Salud ósea normal\nMediana (Q1, Q3)": median_iqr(normal),
                "U": f"{u_statistic:.1f}",
                "p-value": format_p_value(p_value),
                "Delta de Cliff": f"{delta:.3f}",
                "Magnitud": interpret_cliffs_delta(delta),
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
        chi2_statistic, chi2_p, _, expected = chi2_contingency(counts)
        p_value = fisher_exact(counts.to_numpy())[1] if (expected < 5).any() and counts.shape == (2, 2) else chi2_p
        min_dimension = min(counts.shape) - 1
        cramers_v = np.sqrt(chi2_statistic / (counts.to_numpy().sum() * min_dimension)) if min_dimension > 0 else np.nan

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
                    "V de Cramer": f"{cramers_v:.3f}" if idx == 0 and not pd.isna(cramers_v) else "",
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
                        "V de Cramer": "",
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
                        "V de Cramer": row["V de Cramer"] if row_idx == 0 else "",
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


def prepare_model_matrix(df):
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
    model_data["enfermedad"] = model_data["enfermedad_cat"].gt(0).astype(int)

    y = model_data["alteracion_osea"].astype(int)
    x_encoded = model_data[["edad", "imc", "sexo", "trabaja", "enfermedad", "realiza_af"]].astype(float)

    x_full = sm.add_constant(x_encoded.astype(float), has_constant="add")
    return model_data, y, x_encoded.astype(float), x_full


def fit_logit(y, x):
    return sm.Logit(y, x).fit(method="bfgs", disp=False, maxiter=200)


def build_regression_table(model):
    labels = {
        "const": "Intercepto",
        "edad": "Edad",
        "imc": "IMC",
        "sexo": "Sexo: mujer vs hombre",
        "trabaja": "Trabaja: sí vs no",
        "realiza_af": "Actividad física: sí vs no",
        "enfermedad": "Enfermedad: sí vs sano",
    }
    params = model.params
    intervals = model.conf_int()
    return pd.DataFrame(
        {
            "Variable": [labels.get(variable, variable) for variable in params.index],
            "Coeficiente (B)": [f"{value:.3f}" for value in params.values],
            "Error Estándar": [f"{value:.3f}" for value in model.bse.values],
            "Valor p": [format_p_value(value, digits=3) for value in model.pvalues.values],
            "OR": [f"{value:.2f}" for value in np.exp(params).values],
            "IC 95% Inferior": [f"{value:.2f}" for value in np.exp(intervals[0]).values],
            "IC 95% Superior": [f"{value:.2f}" for value in np.exp(intervals[1]).values],
        }
    )


def build_backward_sensitivity_table(y, x_full):
    x_current = x_full.copy()
    history = []

    while True:
        model = fit_logit(y, x_current)
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
            break

        x_current = x_current.drop(columns=worst_variable)

    return pd.DataFrame(history)


def build_vif_table(x_encoded):
    x_vif = sm.add_constant(x_encoded, has_constant="add")
    rows = []
    for idx, variable in enumerate(x_vif.columns):
        if variable == "const":
            continue
        rows.append(
            {
                "Variable": variable,
                "VIF": f"{variance_inflation_factor(x_vif.values, idx):.2f}",
            }
        )
    return pd.DataFrame(rows)


def build_logit_linearity_table(model_data, x_encoded):
    x_linearity = x_encoded.copy()
    rows = []
    for variable in ["edad", "imc"]:
        values = pd.to_numeric(model_data[variable], errors="coerce").astype(float)
        interaction_name = f"{variable}_log"
        x_linearity[interaction_name] = values * np.log(values)
        rows.append({"Variable": variable, "Término": interaction_name})

    x_linearity = sm.add_constant(x_linearity, has_constant="add")
    model = fit_logit(model_data["alteracion_osea"].astype(int), x_linearity)

    for row in rows:
        p_value = model.pvalues[row["Término"]]
        row["Valor p"] = format_p_value(p_value)
        row["Interpretación"] = "Sin evidencia de no linealidad" if p_value >= 0.05 else "Posible no linealidad"

    return pd.DataFrame(rows)


def apparent_auc(y, predicted_probabilities):
    fpr, tpr, _ = roc_curve(y, predicted_probabilities)
    return auc(fpr, tpr)


def bootstrap_auc_metrics(y, x_full, model, n_bootstrap=BOOTSTRAP_ITERATIONS, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    y_series = pd.Series(y).reset_index(drop=True)
    x_reset = x_full.reset_index(drop=True)
    apparent_predictions = model.predict(x_full)
    auc_app = apparent_auc(y, apparent_predictions)
    auc_ci_values = []
    optimism_values = []

    for _ in range(n_bootstrap):
        indices = rng.integers(0, len(y_series), len(y_series))
        y_boot = y_series.iloc[indices]
        if y_boot.nunique() < 2:
            continue

        x_boot = x_reset.iloc[indices]
        try:
            bootstrap_model = fit_logit(y_boot, x_boot)
        except Exception:
            continue

        try:
            auc_boot = apparent_auc(y_boot, bootstrap_model.predict(x_boot))
            auc_original = apparent_auc(y_series, bootstrap_model.predict(x_reset))
            optimism_values.append(auc_boot - auc_original)
        except Exception:
            continue

        ci_indices = rng.integers(0, len(y_series), len(y_series))
        if y_series.iloc[ci_indices].nunique() >= 2:
            auc_ci_values.append(apparent_auc(y_series.iloc[ci_indices], apparent_predictions.iloc[ci_indices]))

    mean_optimism = float(np.mean(optimism_values)) if optimism_values else np.nan
    corrected_auc = auc_app - mean_optimism if not pd.isna(mean_optimism) else np.nan
    ci_low, ci_high = (np.percentile(auc_ci_values, [2.5, 97.5]) if auc_ci_values else [np.nan, np.nan])

    return pd.DataFrame(
        {
            "Métrica": [
                "AUC aparente",
                "IC 95% bootstrap del AUC aparente",
                "Optimismo promedio",
                "AUC corregida por optimismo",
                "Remuestreos exitosos",
            ],
            "Valor": [
                f"{auc_app:.3f}",
                f"{ci_low:.3f} - {ci_high:.3f}",
                f"{mean_optimism:.3f}",
                f"{corrected_auc:.3f}",
                f"{len(optimism_values)} / {n_bootstrap}",
            ],
        }
    )


def build_calibration_tables(y, predicted_probabilities, groups=10):
    predictions = pd.Series(predicted_probabilities).reset_index(drop=True)
    y_series = pd.Series(y).reset_index(drop=True)
    calibration_data = pd.DataFrame({"y": y_series, "predicted": predictions})
    calibration_data["decile"] = pd.qcut(
        calibration_data["predicted"],
        q=groups,
        labels=False,
        duplicates="drop",
    )
    grouped = calibration_data.groupby("decile", observed=True)
    calibration_table = grouped.agg(
        n=("y", "size"),
        probabilidad_media=("predicted", "mean"),
        proporcion_observada=("y", "mean"),
    ).reset_index()
    calibration_table["Decil"] = calibration_table["decile"].astype(int) + 1
    calibration_table = calibration_table[
        ["Decil", "n", "probabilidad_media", "proporcion_observada"]
    ].rename(
        columns={
            "n": "n",
            "probabilidad_media": "Probabilidad predicha media",
            "proporcion_observada": "Proporción observada",
        }
    )
    calibration_table["Probabilidad predicha media"] = calibration_table["Probabilidad predicha media"].map(lambda value: f"{value:.3f}")
    calibration_table["Proporción observada"] = calibration_table["Proporción observada"].map(lambda value: f"{value:.3f}")

    clipped = np.clip(predictions, 1e-6, 1 - 1e-6)
    logit_predictions = np.log(clipped / (1 - clipped))
    calibration_model = sm.Logit(y_series, sm.add_constant(logit_predictions, has_constant="add")).fit(
        method="bfgs",
        disp=False,
        maxiter=200,
    )
    summary_table = pd.DataFrame(
        {
            "Métrica": ["Brier score", "Intercepto de calibración", "Pendiente de calibración"],
            "Valor": [
                f"{brier_score_loss(y_series, predictions):.3f}",
                f"{calibration_model.params['const']:.3f}",
                f"{calibration_model.params[0]:.3f}",
            ],
        }
    )
    return calibration_table, summary_table


def build_model_outputs(df):
    model_data, y, x_encoded, x_full = prepare_model_matrix(df)
    model = fit_logit(y, x_full)
    predictions = model.predict(x_full)
    fpr, tpr, _ = roc_curve(y, predictions)
    return {
        "model_data": model_data,
        "y": y,
        "x_encoded": x_encoded,
        "x_full": x_full,
        "model": model,
        "predictions": predictions,
        "fpr": fpr,
        "tpr": tpr,
        "regression_table": build_regression_table(model),
        "backward_table": build_backward_sensitivity_table(y, x_full),
        "vif_table": build_vif_table(x_encoded),
        "linearity_table": build_logit_linearity_table(model_data, x_encoded),
        "auc_table": bootstrap_auc_metrics(y, x_full, model),
    }


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
                if col >= 2 or display_table.columns[col] in {
                    "n",
                    "W",
                    "p-value",
                    "p máximo",
                    "OR",
                    "U",
                    "Delta de Cliff",
                    "V de Cramer",
                    "VIF",
                    "Valor",
                }:
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


def export_roc_curve(model_outputs):
    fig, ax = plt.subplots(figsize=(7, 5))
    auc_value = auc(model_outputs["fpr"], model_outputs["tpr"])
    ax.plot(
        model_outputs["fpr"],
        model_outputs["tpr"],
        color="#0f766e",
        linewidth=2.5,
        label=f"Modelo preespecificado (AUC = {auc_value:.3f})",
    )
    ax.plot([0, 1], [0, 1], color="#6b7280", linestyle="--", linewidth=1.5, label="No discriminación")
    ax.set_title("Curva ROC - Regresión logística multivariada", fontsize=13, weight="bold")
    ax.set_xlabel("1 - Especificidad")
    ax.set_ylabel("Sensibilidad")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(alpha=0.25)
    fig.savefig(ROC_PDF, dpi=300, bbox_inches="tight")
    plt.close(fig)


def export_calibration_plot(calibration_table):
    plot_table = calibration_table.copy()
    plot_table["Probabilidad predicha media"] = pd.to_numeric(plot_table["Probabilidad predicha media"])
    plot_table["Proporción observada"] = pd.to_numeric(plot_table["Proporción observada"])

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot([0, 1], [0, 1], color="#6b7280", linestyle="--", linewidth=1.5, label="Calibración ideal")
    ax.plot(
        plot_table["Probabilidad predicha media"],
        plot_table["Proporción observada"],
        color="#0f766e",
        marker="o",
        linewidth=2,
        label="Deciles de riesgo",
    )
    ax.set_title("Calibración del modelo logístico", fontsize=13, weight="bold")
    ax.set_xlabel("Probabilidad predicha media")
    ax.set_ylabel("Proporción observada")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(alpha=0.25)
    fig.savefig(CALIBRATION_PDF, dpi=300, bbox_inches="tight")
    plt.close(fig)


def export_csv_outputs(tables):
    for name, table in tables.items():
        table.to_csv(RESULTS_DIR / f"{name}.csv", index=False)


def write_markdown_summary(model_outputs, calibration_summary):
    regression = model_outputs["regression_table"]
    auc_table = model_outputs["auc_table"]

    def get_row(variable):
        matched = regression.loc[regression["Variable"].eq(variable)]
        return matched.iloc[0] if not matched.empty else None

    age = get_row("Edad")
    bmi = get_row("IMC")
    sex = get_row("Sexo: mujer vs hombre")
    auc_apparent = auc_table.loc[auc_table["Métrica"].eq("AUC aparente"), "Valor"].iloc[0]
    auc_corrected = auc_table.loc[auc_table["Métrica"].eq("AUC corregida por optimismo"), "Valor"].iloc[0]
    brier = calibration_summary.loc[calibration_summary["Métrica"].eq("Brier score"), "Valor"].iloc[0]

    summary = [
        "# Informe de resultados del modelo multivariado",
        "",
        "*Modelo principal:* Se ajustó un modelo de regresión logística binaria preespecificado por plausibilidad clínica y epidemiológica. El modelo incluyó edad, IMC, sexo, situación laboral, enfermedad y realización de actividad física, sin eliminación automática de variables en el análisis principal.",
        "",
    ]

    if age is not None:
        summary.append(
            f"*Edad:* La edad se asoció con mayor probabilidad de alteración ósea (OR = {age['OR']}; IC 95%: {age['IC 95% Inferior']}-{age['IC 95% Superior']}; p = {age['Valor p']})."
        )
    if bmi is not None:
        summary.append(
            f"*IMC:* El IMC mostró una asociación inversa con la alteración ósea (OR = {bmi['OR']}; IC 95%: {bmi['IC 95% Inferior']}-{bmi['IC 95% Superior']}; p = {bmi['Valor p']})."
        )
    if sex is not None:
        summary.append(
            f"*Sexo:* El sexo femenino se asoció con mayores momios de alteración ósea frente al sexo masculino (OR = {sex['OR']}; IC 95%: {sex['IC 95% Inferior']}-{sex['IC 95% Superior']}; p = {sex['Valor p']})."
        )

    summary.extend(
        [
            "",
            f"*Discriminación y calibración:* El AUC aparente fue {auc_apparent} y el AUC corregido por optimismo mediante bootstrap fue {auc_corrected}. El Brier score fue {brier}.",
            "",
            "*Análisis de sensibilidad:* Se conservó un procedimiento de eliminación hacia atrás basado en p <= 0.10 únicamente como análisis secundario de sensibilidad, no como estrategia principal de inferencia.",
        ]
    )

    SUMMARY_MD.write_text("\n".join(summary), encoding="utf-8")


def export_pdf():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean_data()
    normality_table = build_normality_table(df)
    continuous_table = build_continuous_descriptive_table(df)
    continuous_bivariate_table = build_continuous_bivariate_table(df)
    categorical_table = prepare_grouped_categorical_table(df)
    model_outputs = build_model_outputs(df)
    calibration_table, calibration_summary = build_calibration_tables(
        model_outputs["y"],
        model_outputs["predictions"],
    )

    export_roc_curve(model_outputs)
    export_calibration_plot(calibration_table)
    export_csv_outputs(
        {
            "tabla_1_normalidad": normality_table,
            "tabla_2_descriptivo_continuas": continuous_table,
            "tabla_3_bivariado_continuas": continuous_bivariate_table,
            "tabla_4_bivariado_categoricas": categorical_table.drop(columns=["_section"]),
            "tabla_5_modelo_logistico_principal": model_outputs["regression_table"],
            "tabla_6_vif": model_outputs["vif_table"],
            "tabla_7_linealidad_logit": model_outputs["linearity_table"],
            "tabla_8_calibracion_deciles": calibration_table,
            "tabla_9_calibracion_resumen": calibration_summary,
            "tabla_10_auc_bootstrap": model_outputs["auc_table"],
            "tabla_s1_backward_sensibilidad": model_outputs["backward_table"],
        }
    )
    write_markdown_summary(model_outputs, calibration_summary)

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
        draw_table_page(
            pdf,
            continuous_bivariate_table,
            3,
            "Comparación de variables continuas según alteración ósea",
            "Las variables se compararon con la prueba U de Mann-Whitney. Delta de Cliff > 0 indica valores mayores en el grupo con alteración ósea.",
            column_widths=[0.16, 0.22, 0.22, 0.09, 0.10, 0.11, 0.10],
            wrap_widths={
                "Variable": 22,
                "Alteración ósea\nMediana (Q1, Q3)": 22,
                "Salud ósea normal\nMediana (Q1, Q3)": 22,
            },
        )

        for page_table, page_number in paginate_rows(categorical_table, rows_per_page=19):
            draw_table_page(
                pdf,
                page_table,
                4,
                "Características categóricas de los pacientes evaluados según alteración ósea (n = 405)",
                "Los porcentajes de las columnas con y sin alteración ósea corresponden a porcentajes por fila. Los valores p provienen de Chi-cuadrada o prueba exacta de Fisher cuando corresponde. La V de Cramer cuantifica tamaño de efecto.",
                page_suffix=f"continuación {page_number}" if page_number > 1 else None,
                column_widths=[0.15, 0.20, 0.12, 0.19, 0.19, 0.07, 0.08],
                wrap_widths={"Variable": 36, "Categoría": 30},
                header_wrap_widths={
                    "Variable": 18,
                    "Categoría": 18,
                    "Total (n, %)": 14,
                    "Con alteración ósea (n, %)": 22,
                    "Sin alteración ósea (n, %)": 22,
                    "p-value": 8,
                    "V de Cramer": 12,
                },
                section_column="_section",
            )

        draw_table_page(
            pdf,
            model_outputs["regression_table"],
            5,
            "Modelo de regresión logística multivariada preespecificado para alteración ósea",
            "B = coeficiente logit; OR = odds ratio; IC = intervalo de confianza. Categorías de referencia: sexo Hombre, trabaja No, actividad física No y enfermedad Sano.",
            column_widths=[0.25, 0.13, 0.13, 0.10, 0.10, 0.14, 0.15],
            wrap_widths={"Variable": 30},
        )
        draw_table_page(
            pdf,
            model_outputs["vif_table"],
            6,
            "Diagnóstico de colinealidad del modelo multivariado",
            "VIF = factor de inflación de varianza. Valores marcadamente elevados sugieren colinealidad relevante.",
            column_widths=[0.65, 0.20],
            wrap_widths={"Variable": 35},
        )
        draw_table_page(
            pdf,
            model_outputs["linearity_table"],
            7,
            "Evaluación de linealidad del logit para variables continuas",
            "Se usaron términos tipo Box-Tidwell para edad e IMC. p < 0.05 sugiere posible desviación de la linealidad en el logit.",
            column_widths=[0.25, 0.25, 0.15, 0.35],
            wrap_widths={"Interpretación": 35},
        )
        draw_table_page(
            pdf,
            calibration_summary,
            8,
            "Resumen de calibración del modelo",
            "El Brier score resume error de predicción probabilística; valores menores indican mejor desempeño.",
            column_widths=[0.55, 0.20],
            wrap_widths={"Métrica": 35},
        )
        draw_table_page(
            pdf,
            calibration_table,
            9,
            "Calibración por deciles de probabilidad predicha",
            "Cada decil compara la probabilidad predicha media con la proporción observada de alteración ósea.",
            column_widths=[0.12, 0.12, 0.34, 0.34],
            wrap_widths={"Probabilidad predicha media": 24, "Proporción observada": 24},
        )
        draw_table_page(
            pdf,
            model_outputs["auc_table"],
            10,
            "Discriminación y validación interna del modelo",
            "El AUC corregido por optimismo se estimó con remuestreo bootstrap.",
            column_widths=[0.60, 0.25],
            wrap_widths={"Métrica": 45},
        )
        draw_table_page(
            pdf,
            model_outputs["backward_table"],
            "S1",
            "Proceso de eliminación hacia atrás del modelo logístico como sensibilidad",
            "El criterio de permanencia fue p <= 0.10; este procedimiento se reporta como análisis secundario, no como modelo principal.",
            column_widths=[0.08, 0.48, 0.20, 0.12, 0.12],
            wrap_widths={"Variables": 70, "Variable con mayor p": 28},
        )

    return OUTPUT_PDF


if __name__ == "__main__":
    output_path = export_pdf()
    print(f"PDF de tablas generado: {output_path}")
