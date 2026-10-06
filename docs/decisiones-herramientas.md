# Decisiones de herramientas — TP1

## Referencias del curso

Se siguieron las diapositivas proporcionadas por el docente Carlos Fernando Montoya Cubas:

- **Semana 3, Preparación y calidad:** distinguir outlier de error (26–28), imputación (11–13), escalado según algoritmo (29–33), one-hot (34–38), ajuste solo con train (41–42).
- **Semana 5, Clasificación y pipelines:** ColumnTransformer (13–21), Pipeline (22–25), regresión logística, árbol y random forest (26–30), comparación y sentido de los errores (34–44).
- **Semana 6, Evaluación:** matriz y FP/FN (5–9), precision/recall/F1 (13–20), umbrales y curvas (20–27), baseline (28–29), sobreajuste (30–32), CV y dispersión (33–39).

Las diapositivas son material de referencia, no una dependencia de ejecución del repositorio.

## Matriz de herramientas

| Etapa | Elección | Justificación | Alternativa y motivo de no usarla en este corte |
|---|---|---|---|
| Tablas | pandas / NumPy | Operaciones explícitas y dataset manejable en memoria | Spark: no se justifica distribución para ~84 mil filas |
| Exploración | matplotlib / seaborn | Figuras exportables y análisis por pregunta | Dashboard: se reserva para aplicación del TF1 |
| Calidad administrativa | Reglas pandas documentadas en notebook 02 | Conserva trazabilidad de cambios y banderas | Borrar duplicados/extremos: podría eliminar participantes o casos válidos |
| Faltantes numéricos | SimpleImputer con mediana | Robusta ante horas asimétricas; ajustada por fold | Media/KNN: no hay evidencia que justifique complejidad; actualmente no hay nulos en predictoras |
| Faltantes categóricos | Constante SIN_DATO | Conserva que la categoría no fue observada | Moda: ocultaría el significado de una ausencia |
| Encoding | OneHotEncoder, handle_unknown=ignore | No impone orden a modalidades o departamentos; tolera categorías nuevas | Label/ordinal encoding: impondría un orden artificial |
| Escalado | StandardScaler solo en regresión logística | Hace comparables horas y calendario para el ajuste regularizado | Escalar árboles: no es necesario por sus reglas de corte |
| Flujo | ColumnTransformer + Pipeline | Aprende imputación, escala y categorías dentro de cada fold | get_dummies y escalado global: podrían generar inconsistencias/leakage |
| Validación | PredefinedSplit de FOLD | Respeta las cinco particiones por edición ya guardadas | cv=5 / StratifiedKFold por filas: podría mezclar una edición entre train y validación |
| Baseline | DummyClassifier most_frequent | Muestra la exactitud engañosa de predecir siempre sin riesgo | Solo accuracy del modelo real: no ofrece una referencia de utilidad |
| Modelos | LogisticRegression, DecisionTree, RandomForest | Familias vistas en semana 5; lineal, reglas y ensamble | Boosting: alternativa para TF1, sin añadir dependencias ni búsqueda extensa al TP1 |
| Desbalance | class_weight balanced/balanced_subsample | Aumenta peso de positivos sin cambiar validación/test | SMOTE: exigiría otro pipeline y validación adicional; no se remuestrea aquí |
| Selección | AP media entre folds | Prioriza ranking de casos raros | Accuracy / escoger con test: no representan el objetivo o contaminan la evaluación |
| Umbral | Máximo F1 OOF de train | Criterio preliminar explícito sin costos institucionales inventados | Elegir con test: daría una evaluación optimista |
| Evidencia | cross_validate, CSV, JSON y notebooks ejecutados | Media, desviación, configuración y resultados verificables | Una sola métrica sin interpretación: insuficiente según enunciado |

## Parámetros fijados antes del test

- Regresión logística: `C=1`, regularización L2, `max_iter=2000`, pesos balanceados.
- Árbol: profundidad 6, mínimo 50 registros por hoja, pesos balanceados.
- Random forest: 150 árboles, profundidad 10, mínimo 20 registros por hoja, pesos balanceados por bootstrap, dos trabajadores.
- Semilla 42. Las particiones del notebook 03 conservan su propia semilla test 34.

No se ofrece una búsqueda de hiperparámetros exhaustiva. Se compara el baseline y tres familias con límites de complejidad razonables. La selección final y versiones se guardan en `reports/metrics/seleccion.json`.

## AP, curvas y comparabilidad

Se reporta **Average Precision (AP)** mediante `average_precision_score`, no un área trapezoidal llamada indistintamente PR-AUC. La AP del dummy constante equivale a la prevalencia de positivos. Se incluyen curvas precision–recall y ROC, y ROC-AUC como complemento.

Las métricas CV se presentan a umbral 0.5 con media y desviación entre folds. Después se explora el umbral con OOF del modelo elegido. La F1 ajustada OOF es una métrica de desarrollo con sesgo de selección; la evaluación posterior del test corresponde a la decisión congelada. No se afirma que sea validación anidada.

## Fuentes técnicas

- [ColumnTransformer con tipos mixtos](https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html).
- [OneHotEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html).
- [cross_validate](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_validate.html).
- [Average Precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html).
- [Validación cruzada y particiones predefinidas](https://scikit-learn.org/stable/modules/cross_validation.html).
