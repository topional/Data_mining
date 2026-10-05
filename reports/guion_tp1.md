# Guion de exposición TP1

Duración sugerida: 10 minutos. Distribuir entre los dos integrantes y ensayar.
No memorizar el texto: comprender las decisiones y abrir el notebook 04 si el docente solicita evidencia.

## Diapositiva 1: Anticipar el riesgo en capacitaciones (35 segundos)

Avance preliminar: datos → preparación → comparación → evaluación

## Diapositiva 2: Problema, objetivo y datos (45 segundos)

El régimen se infiere de estados históricos; confirmar metadata antes de uso real.

## Diapositiva 3: EDA: el curso y la edición importan (45 segundos)

El 10 % de las ediciones concentra 57 % del riesgo. Asociación no implica causa.

Figura: `reports/figures/09_ediciones.png`. Explicar ejes y qué decisión respalda.

## Diapositiva 4: Calidad: decisiones justificadas (45 segundos)

Correcciones y población son supuestos explícitos; se conserva trazabilidad.

## Diapositiva 5: Separar por edición, no por fila (45 segundos)

Se prueban ediciones nuevas; no exclusivamente cursos nuevos ni períodos futuros.

## Diapositiva 6: Pipeline y modelos vistos en clase (55 segundos)

Semanas 3 y 5: preprocesamiento + clasificador en un flujo reproducible.

## Diapositiva 7: Comparación: media y dispersión (65 segundos)

Elegido por AP media: Random forest (0.169 ± 0.032). Desviación ≠ IC.

Figura: `reports/figures/14_comparacion_cv.png`. Explicar ejes y qué decisión respalda.

## Diapositiva 8: Curvas: la clase positiva es rara (45 segundos)

AP resume precision–recall; ROC-AUC es complementaria. Estas curvas son OOF de desarrollo.

Figura: `reports/figures/15_curvas_oof.png`. Explicar ejes y qué decisión respalda.

## Diapositiva 9: Umbral fijado antes de leer test (55 segundos)

Umbral 0.639: máximo F1 OOF. F1 ajustada OOF tiene sesgo de selección; no es prueba independiente.

Figura: `reports/figures/16_umbral_oof.png`. Explicar ejes y qué decisión respalda.

## Diapositiva 10: Test: aciertos y errores concretos (70 segundos)

Detectados: 168/435 · Omitidos: 267 · Falsas alertas: 677 · Recall 38.6% · Precision 19.9%

Figura: `reports/figures/17_matrices_test.png`. Explicar ejes y qué decisión respalda.

## Diapositiva 11: Qué permite concluir este corte (50 segundos)

Interpretar FP/FN y estabilidad según el propósito, como plantea la semana 6.

## Diapositiva 12: TF1: mejorar y validar el uso (45 segundos)

Evidencia: notebooks 01–04, reports/metrics, documentación y código reproducible.

## Preguntas que deben poder responder

- ¿Por qué la población baja de 83 930 a 36 681 y qué supuesto implica?
- ¿Por qué conservar duplicados y separar por edición?
- ¿Qué aprende fit del pipeline y por qué no se ajusta con test?
- ¿Por qué AP y qué diferencia tiene frente a ROC-AUC/accuracy?
- ¿Qué significa cada FP/FN y por qué el umbral OOF no es validación independiente?
- ¿Qué falta para hablar de probabilidades calibradas y de utilidad real?
