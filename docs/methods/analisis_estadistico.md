# Análisis estadístico

El procesamiento, limpieza y análisis estadístico de los datos se llevó a cabo en Python. Para la manipulación y estructuración de la base se emplearon `pandas` y `numpy`; para la visualización se utilizaron `matplotlib` y `seaborn`. Las pruebas estadísticas se implementaron con `scipy.stats`, el modelado multivariado con `statsmodels` y la evaluación del desempeño predictivo con `scikit-learn`.

## Procesamiento y limpieza de datos

La base original fue importada desde el archivo `BD_Analysis_Osteoporosis.xlsx` mediante `pandas.read_excel` con el motor `openpyxl`. Posteriormente, se estandarizaron los nombres de las columnas y se transformaron a formato numérico las variables continuas edad, peso, altura e índice de masa corporal (IMC). La variable dependiente binaria `alteracion_osea` se construyó a partir del diagnóstico óseo, codificando como 0 la salud ósea normal y como 1 la presencia de osteopenia u osteoporosis.

Se identificaron filas duplicadas exactas y, cuando correspondió, se eliminaron. Para los análisis posteriores se excluyeron los registros con valores faltantes en las variables críticas `alteracion_osea`, `edad` e `imc`. La base analítica final fue exportada en formato Parquet, con respaldo en Pickle cuando fue necesario para preservar los tipos de datos de `pandas`.

## Análisis descriptivo

La normalidad de las variables continuas edad, peso, altura e IMC se evaluó mediante la prueba de Shapiro-Wilk (`scipy.stats.shapiro`). Un valor p < 0.05 fue interpretado como evidencia de desviación estadísticamente significativa de la normalidad. Dado que las variables continuas evaluadas presentaron distribución no normal, se resumieron mediante mediana y rango intercuartílico, expresado como percentiles 25 y 75. Las variables categóricas se describieron mediante frecuencias absolutas y proporciones.

## Análisis bivariado

Las variables continuas se compararon entre participantes con salud ósea normal y participantes con alteración ósea mediante la prueba U de Mann-Whitney (`scipy.stats.mannwhitneyu`) con contraste bilateral. La magnitud de la diferencia entre grupos se cuantificó mediante delta de Cliff, estimado a partir del estadístico U. Los valores positivos de delta de Cliff indican valores mayores en el grupo con alteración ósea, mientras que los valores negativos indican valores mayores en el grupo con salud ósea normal. La magnitud del efecto se clasificó como trivial, pequeña, mediana o grande.

Las variables categóricas se analizaron mediante tablas de contingencia. La asociación con alteración ósea se evaluó con la prueba Chi-cuadrada de Pearson (`scipy.stats.chi2_contingency`). Cuando existieron frecuencias esperadas menores de 5 en tablas 2 x 2, se aplicó la prueba exacta de Fisher (`scipy.stats.fisher_exact`). Como tamaño de efecto para las asociaciones categóricas se estimó la V de Cramer.

## Modelo multivariado

Se ajustó un modelo de regresión logística binaria para estimar los factores asociados con la presencia de alteración ósea. El modelo principal fue preespecificado por plausibilidad clínica y epidemiológica, y no se basó en eliminación automática de variables por valor p. Se incluyeron edad, IMC, sexo, situación laboral, presencia de enfermedad y realización de actividad física.

Las variables sexo, situación laboral y actividad física fueron codificadas como binarias, usando como categorías de referencia hombre, no trabaja y no realiza actividad física, respectivamente. La variable enfermedad se incorporó en el modelo multivariado como presencia frente a ausencia de enfermedad. Esta decisión se adoptó por estabilidad estadística, debido a la presencia de una categoría con separación completa en la codificación politómica original. La categoría politómica de enfermedad se conservó para el análisis descriptivo y bivariado.

El modelo se implementó mediante `statsmodels.api.Logit`, utilizando el método de optimización BFGS, sin impresión iterativa y con un máximo de 200 iteraciones. La magnitud de las asociaciones independientes se reportó mediante razones de momios (odds ratio, OR), calculadas por exponenciación de los coeficientes logit, junto con intervalos de confianza del 95% y valores p de Wald.

Como análisis secundario de sensibilidad, se conservó un procedimiento de eliminación hacia atrás. En cada iteración se identificó la variable con mayor valor p de Wald, excluyendo el intercepto, y se eliminó cuando el valor p fue > 0.10. El procedimiento se detuvo cuando todas las variables restantes cumplieron el criterio de permanencia p <= 0.10. Este análisis no fue considerado el modelo principal.

## Diagnósticos y desempeño del modelo

La colinealidad entre covariables del modelo principal se evaluó mediante el factor de inflación de varianza (VIF). La linealidad del logit para edad e IMC se examinó mediante términos tipo Box-Tidwell, incorporando interacciones entre cada variable continua y su logaritmo natural; un valor p < 0.05 fue interpretado como evidencia de posible desviación de la linealidad en el logit.

La discriminación del modelo se evaluó mediante el área bajo la curva ROC (AUC), calculada a partir de las probabilidades predichas del modelo principal con `sklearn.metrics.roc_curve` y `sklearn.metrics.auc`. Se estimó un AUC aparente y un AUC corregido por optimismo mediante validación interna con remuestreo bootstrap. La calibración se evaluó mediante Brier score, intercepto y pendiente de calibración, así como mediante una tabla por deciles de probabilidad predicha. Las curvas ROC y de calibración fueron exportadas en formato PDF.

## Umbral de significancia

Para los análisis inferenciales se fijó un umbral de significancia estadística de p < 0.05 a dos colas. Para el análisis de sensibilidad con eliminación hacia atrás, el criterio operativo de permanencia fue p <= 0.10.
