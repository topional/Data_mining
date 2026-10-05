# Resultados preliminares y plan hacia el TF1

## Estado del TP1

Se completaron problema, procedencia, EDA, calidad, separación por edición, pipeline, baseline,
tres alternativas de clasificación y evaluación preliminar. Los cuatro notebooks están ejecutados.
La presentación y su guion están en `reports/`.

Este corte no es un despliegue ni una validación institucional. La utilidad del seguimiento debe
discutirse con responsables de capacitación; no se declara éxito solo por superar un baseline.

## Hallazgos de datos

- Original: 83 930 participaciones, 20 variables; 2 170 desenlaces de riesgo (2,59 %).
- Población de modelamiento: 36 681 participaciones de 198 ediciones con evaluación;
  2 170 positivos (5,92 %). Las 47 249 filas con ASISTIÓ se excluyen de esta población.
- Se normalizaron textos y se marcaron 1 498 fechas de término corregidas por un año incoherente.
  La corrección es una regla inferida, no confirmada por el publicador.
- Los duplicados se conservan porque los identificadores están enmascarados.
- Train: 29 336 filas / 158 ediciones; test: 7 345 / 40. Cinco folds de train respetan la edición.
- El riesgo está concentrado en algunas ediciones. Las asociaciones del EDA no son causas.

## Comparación con validación (umbral 0.5)

| modelo | ap_mean | ap_std | precision_mean | recall_mean | f1_mean | brecha_ap |
|---|---|---|---|---|---|---|
| Random forest | 0.1688 | 0.0316 | 0.1428 | 0.5716 | 0.2187 | 0.0708 |
| Árbol de decisión | 0.1506 | 0.0535 | 0.1333 | 0.5303 | 0.2036 | 0.0746 |
| Regresión logística | 0.1410 | 0.0446 | 0.1313 | 0.5995 | 0.2109 | 0.0293 |
| Dummy mayoritario | 0.0592 | 0.0019 | 0.0000 | 0.0000 | 0.0000 | -0.0000 |

AP es Average Precision. La media y desviación son entre cinco folds por edición. La desviación
no es un intervalo de confianza. `brecha_ap` = AP media de entrenamiento menos AP de validación:
una brecha positiva grande obliga a investigar sobreajuste o cambio entre ediciones.

La selección previa al test fue **Random forest**, por mayor AP media entre los modelos reales.
No se hizo una búsqueda amplia de hiperparámetros. Se compararon configuraciones fijadas antes del test.

## Umbral y prueba de la decisión fijada

El umbral **0.639369** maximiza F1 en OOF de train. OOF son predicciones de modelos
que no entrenaron con la edición de la fila predicha. Usar esas mismas etiquetas para escoger
modelo y umbral introduce sesgo de selección: la F1 ajustada OOF es una métrica de desarrollo,
no una evaluación independiente. No se ajusta el umbral con test.

| evaluacion | precision | recall | f1 | ap | balanced_accuracy | tp | fp | fn |
|---|---|---|---|---|---|---|---|---|
| Dummy mayoritario | 0.0000 | 0.0000 | 0.0000 | 0.0592 | 0.5000 | 0 | 0 | 435 |
| Random forest · umbral 0.5 | 0.1757 | 0.5609 | 0.2675 | 0.2217 | 0.6976 | 244 | 1145 | 191 |
| Random forest · umbral OOF | 0.1988 | 0.3862 | 0.2625 | 0.2217 | 0.6441 | 168 | 677 | 267 |

En test se detectan **168 de 435** casos de riesgo; **267** quedan
sin detectar y se producen **677** falsas alertas. Recall **38.62%**,
precision **19.88%** y F1 **0.2625**. AP **0.2217**, frente a
**0.0592** del dummy (diferencia +0.1625).

Estas cifras muestran el intercambio entre detección y carga de seguimiento. No se inventan costos
monetarios ni una capacidad institucional de alertas. Un desempeño de test distinto del promedio CV
se reporta como limitación y no se utiliza para cambiar la selección retrospectivamente.

**El ajuste del umbral no garantiza una mejora fuera de train.** En este test, el umbral 0.5 logra
F1 0.2675, recall 56.09% y 1145 falsas alertas;
el umbral fijado con OOF logra F1 0.2625, recall 38.62% y 677 falsas
alertas. Se conservan ambos resultados. No se cambia el umbral para favorecer la F1 observada en test:
se debe evaluar el compromiso de errores y revisar la selección en una validación futura independiente.

## Limitaciones y problemas pendientes

1. **Población:** se infiere régimen de evaluación a partir de resultados finales. Confirmar mediante
   metadata previa a la inscripción; no generalizar este modelo a eventos acreditados por asistencia.
2. **Evaluación externa:** EDA, variantes de categorías y selección inicial de columnas observaron todo
   el dataset. El test se reservó para elegir modelos/umbral, pero no es un dataset externo desconocido.
3. **Identidades:** no se puede separar por persona porque sus identificadores están enmascarados.
4. **Curso/edición:** 17 nombres de cursos se comparten entre train y test; son ediciones diferentes.
5. **Composición:** CURSO representa 5,5 % de train y 31,7 % de test; PROGRAMA, 19,1 % y 1,7 %.
   La tasa global cercana no implica la misma dificultad en cada segmento.
6. **Desbalance y heterogeneidad:** DESAPROBADO y RETIRADO no son el mismo desenlace. Solo hay
   110 retirados; no se atribuye estabilidad a métricas de grupos con pocos casos.
7. **Scores:** los modelos ponderados no están calibrados. No se ofrecen porcentajes de riesgo absoluto.
8. **Umbral:** F1 es un compromiso técnico preliminar; no sustituye costos ni capacidad de intervención.
9. **Preparación:** el joblib recibe las diez columnas ya preparadas; no encapsula toda la limpieza del CSV crudo.
10. **Generalización:** no hay prueba temporal ni causal; no se afirman impactos de una intervención.

El diagnóstico por sexo, nivel de gobierno y tipo de capacitación está en `reports/metrics/test_segmentos.csv`.
No se trata como prueba de equidad ni se modifica el modelo usando ese diagnóstico del test.

## Actividades hacia el TF1

| Actividad | Evidencia que se entregará | Dependencia |
|---|---|---|
| Confirmar régimen de evaluación, fechas y horas conocidas al inscribirse | Diccionario/reglas revisadas con fuente institucional | Metadata disponible |
| Encapsular limpieza y esquema de entrada | Transformación reutilizable desde datos crudos | Reglas administrativas fijadas |
| Evaluación temporal y por curso | Métricas de períodos/cursos nuevos, sin mezclar grupos | Datos y fechas consistentes |
| Selección con CV anidada por grupos | Separación entre elección de parámetros/umbral y evaluación | Grupos suficientes |
| Ajustar y registrar experimentos | Tabla de configuraciones, semillas, métricas y versiones | Estrategia de validación fijada |
| Evaluar calibración | Curvas de calibración y Brier score en datos reservados | Predicciones de validación adecuadas |
| Definir costos y capacidad de acompañamiento | Política de alertas justificada | Responsables del dominio |
| Ampliar análisis de errores y segmentos | Incertidumbre por edición/grupo y limitaciones | Positivos suficientes |
| Interpretar predicciones con cautela | Importancias/permutaciones y casos documentados | Modelo elegido sin consultar prueba final |
| Crear aplicación de uso | Entrada validada, score/alerta, documentación y demo | Pipeline y política de alertas fijados |

## Reproducibilidad y evidencia

- `notebooks/04_modelamiento.ipynb`: ejecución, gráficos e interpretación.
- `src/modelamiento.py`: pipelines, métricas, OOF y exportación.
- `reports/metrics/`: resultados por fold, resumen, test, segmentos y selección.
- `data/processed/`: particiones y predicciones detalladas, regenerables y fuera de git.
- `models/modelo_tp1.joblib`: pipeline y umbral, regenerable y fuera de git.
- `src/generar_entrega.py`: genera este cierre y la presentación a partir de resultados reales.
