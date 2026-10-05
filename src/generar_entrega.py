"""Generar resumen, plan de TF1 y presentación PDF desde resultados ejecutados.

Uso: python src/generar_entrega.py
No entrena modelos ni modifica decisiones usando el test.
"""

import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAVY, RED, GREY = "#15283e", "#cf1228", "#46546a"


def tabla_markdown(df, columnas, indice=True):
    data = df[columnas].copy()
    if indice:
        data = data.reset_index()
    headers = list(data.columns)
    rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in data.itertuples(index=False, name=None):
        rows.append("| " + " | ".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in row) + " |")
    return "\n".join(rows)


def escribir_documentos(config, cv, test):
    elegido, threshold = config["modelo"], config["umbral"]
    final, dummy = test.iloc[-1], test.iloc[0]
    referencia = test.iloc[1]
    mejora = final.ap - dummy.ap
    cv_tabla = tabla_markdown(cv, ["ap_mean", "ap_std", "precision_mean", "recall_mean", "f1_mean", "brecha_ap"])
    test_tabla = tabla_markdown(test, ["precision", "recall", "f1", "ap", "balanced_accuracy", "tp", "fp", "fn"])
    texto = f'''# Resultados preliminares y plan hacia el TF1

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

{cv_tabla}

AP es Average Precision. La media y desviación son entre cinco folds por edición. La desviación
no es un intervalo de confianza. `brecha_ap` = AP media de entrenamiento menos AP de validación:
una brecha positiva grande obliga a investigar sobreajuste o cambio entre ediciones.

La selección previa al test fue **{elegido}**, por mayor AP media entre los modelos reales.
No se hizo una búsqueda amplia de hiperparámetros. Se compararon configuraciones fijadas antes del test.

## Umbral y prueba de la decisión fijada

El umbral **{threshold:.6f}** maximiza F1 en OOF de train. OOF son predicciones de modelos
que no entrenaron con la edición de la fila predicha. Usar esas mismas etiquetas para escoger
modelo y umbral introduce sesgo de selección: la F1 ajustada OOF es una métrica de desarrollo,
no una evaluación independiente. No se ajusta el umbral con test.

{test_tabla}

En test se detectan **{int(final.tp)} de 435** casos de riesgo; **{int(final.fn)}** quedan
sin detectar y se producen **{int(final.fp)}** falsas alertas. Recall **{final.recall:.2%}**,
precision **{final.precision:.2%}** y F1 **{final.f1:.4f}**. AP **{final.ap:.4f}**, frente a
**{dummy.ap:.4f}** del dummy (diferencia {mejora:+.4f}).

Estas cifras muestran el intercambio entre detección y carga de seguimiento. No se inventan costos
monetarios ni una capacidad institucional de alertas. Un desempeño de test distinto del promedio CV
se reporta como limitación y no se utiliza para cambiar la selección retrospectivamente.

**El ajuste del umbral no garantiza una mejora fuera de train.** En este test, el umbral 0.5 logra
F1 {referencia.f1:.4f}, recall {referencia.recall:.2%} y {int(referencia.fp)} falsas alertas;
el umbral fijado con OOF logra F1 {final.f1:.4f}, recall {final.recall:.2%} y {int(final.fp)} falsas
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
'''
    (ROOT / "docs/plan-hacia-tf1.md").write_text(texto, encoding="utf-8")


def generar_presentacion(config, cv, test):
    elegido, threshold = config["modelo"], config["umbral"]
    fila = test.iloc[-1]
    mejor_cv = cv.loc[elegido]
    slides = [
        ("Anticipar el riesgo en capacitaciones", [
            "SERVIR / ENAP · Trabajo Parcial de Data Mining Tools",
            "Ronal Sebastian Cueto Ninaja · Sebastián Alonso Yparraguirre Aquino",
            "Docente: Carlos Fernando Montoya Cubas · UPC · 202620",
            "Pregunta: ¿podemos anticipar desaprobación o retiro al inscribirse?"], None,
            "Avance preliminar: datos → preparación → comparación → evaluación", 35),
        ("Problema, objetivo y datos", [
            "Una fila = una participación; la identidad está enmascarada.",
            "y=1: DESAPROBADO o RETIRADO. y=0: APROBADO en la población evaluable.",
            "Fuente: Datos Abiertos de SERVIR, reporte dic-2025 / may-2026; ODC-By.",
            "Original: 83 930 filas × 20 columnas; 2 170 positivos (2,59 %).",
            "Para modelar: 36 681 filas / 198 ediciones con evaluación; riesgo 5,92 %."], None,
            "El régimen se infiere de estados históricos; confirmar metadata antes de uso real.", 45),
        ("EDA: el curso y la edición importan", [], "09_ediciones.png",
            "El 10 % de las ediciones concentra 57 % del riesgo. Asociación no implica causa.", 45),
        ("Calidad: decisiones justificadas", [
            "Normalizar espacios, mayúsculas y variantes de escritura.",
            "Corregir y marcar 1 498 términos en 2015 incompatibles con inicios de 2025.",
            "Conservar duplicados: perfiles iguales pueden ser personas distintas.",
            "Conservar extremos válidos y excluir identificadores/estado de las predictoras.",
            "Diez entradas: perfil, tipo, modalidad, convocatoria, horas y calendario."], None,
            "Correcciones y población son supuestos explícitos; se conserva trazabilidad.", 45),
        ("Separar por edición, no por fila", [
            "Al azar: 100 % del test comparte edición con train; 82 % tiene perfil/edición equivalente.",
            "Por edición: ningún grupo se comparte entre train y test.",
            "Train: 29 336 filas / 158 ediciones. Test: 7 345 / 40.",
            "Validación: cinco folds guardados dentro de train; ningún grupo cruza folds.",
            "17 nombres de curso sí se comparten; cambia la composición por tipo."], None,
            "Se prueban ediciones nuevas; no exclusivamente cursos nuevos ni períodos futuros.", 45),
        ("Pipeline y modelos vistos en clase", [
            "ColumnTransformer: mediana para numéricas; SIN_DATO + one-hot para categorías.",
            "StandardScaler solo en regresión logística; fit solo dentro de cada entrenamiento.",
            "Dummy mayoritario como baseline; logística, árbol y random forest como alternativas.",
            "Pesos de clase; límites de profundidad/hoja; no se remuestrea test/validación.",
            "PredefinedSplit respeta FOLD. Configuraciones fijadas antes de evaluar test."], None,
            "Semanas 3 y 5: preprocesamiento + clasificador en un flujo reproducible.", 55),
        ("Comparación: media y dispersión", [], "14_comparacion_cv.png",
            f"Elegido por AP media: {elegido} ({mejor_cv.ap_mean:.3f} ± {mejor_cv.ap_std:.3f}). Desviación ≠ IC.", 65),
        ("Curvas: la clase positiva es rara", [], "15_curvas_oof.png",
            "AP resume precision–recall; ROC-AUC es complementaria. Estas curvas son OOF de desarrollo.", 45),
        ("Umbral fijado antes de leer test", [], "16_umbral_oof.png",
            f"Umbral {threshold:.3f}: máximo F1 OOF. F1 ajustada OOF tiene sesgo de selección; no es prueba independiente.", 55),
        ("Test: aciertos y errores concretos", [], "17_matrices_test.png",
            f"Detectados: {int(fila.tp)}/435 · Omitidos: {int(fila.fn)} · Falsas alertas: {int(fila.fp)} · Recall {fila.recall:.1%} · Precision {fila.precision:.1%}", 70),
        ("Qué permite concluir este corte", [
            f"Test: F1 {fila.f1:.3f}; AP {fila.ap:.3f} frente a {test.iloc[0].ap:.3f} del dummy.",
            f"F1 a 0.5: {test.iloc[1].f1:.3f}. El umbral OOF no mejoró F1 en este test.",
            "Superar una referencia no demuestra utilidad institucional ni causalidad.",
            "Pocos retirados y diferencias de composición entre train/test.",
            "EDA inicial observó todo el dataset. Scores ponderados no calibrados.",
            ], None,
            "Interpretar FP/FN y estabilidad según el propósito, como plantea la semana 6.", 50),
        ("TF1: mejorar y validar el uso", [
            "Confirmar régimen/fechas y encapsular limpieza desde el CSV crudo.",
            "Validación temporal y anidada por grupos; experimentos registrados.",
            "Calibración, costos de errores y capacidad real de seguimiento.",
            "Ampliar análisis por segmentos e interpretación sin causalidad.",
            "Aplicación de uso: entradas validadas, política de alertas y demo reproducible."], None,
            "Evidencia: notebooks 01–04, reports/metrics, documentación y código reproducible.", 45),
    ]
    path = ROOT / "reports/presentacion_tp1.pdf"
    with PdfPages(path, metadata={"Title": "TP1 · Riesgo en capacitaciones SERVIR", "Author": "Equipo Data Mining Tools UPC"}) as pdf:
        for i, (title, bullets, image, takeaway, segundos) in enumerate(slides, 1):
            fig = plt.figure(figsize=(16, 9), facecolor="#f8fafc")
            fig.text(0.055, 0.945, "UPC  /  DATA MINING TOOLS  /  TP1", color=RED, fontsize=12, weight="bold")
            fig.text(0.055, 0.86, title, color=NAVY, fontsize=31, weight="bold")
            if image:
                imagen = plt.imread(ROOT / "reports/figures" / image)
                ax = fig.add_axes([0.055, 0.22, 0.89, 0.57])
                ax.imshow(imagen)
                ax.axis("off")
            else:
                position = 0.73
                for bullet in bullets:
                    wrapped = textwrap.fill(bullet, width=91)
                    fig.text(0.062, position, "•", fontsize=23, color=RED, va="top")
                    fig.text(0.087, position, wrapped, fontsize=21, color=NAVY, va="top", linespacing=1.4)
                    position -= 0.085 + 0.044 * (len(wrapped.splitlines()) - 1)
            fig.text(0.055, 0.14, textwrap.fill(takeaway, width=113), color=GREY, fontsize=15, va="top")
            fig.text(0.055, 0.045, "Fuente: CSV SERVIR y ejecución del repositorio · Diapositivas del curso: semanas 3, 5 y 6", fontsize=10, color=GREY)
            fig.text(0.93, 0.045, f"{i:02d} / {len(slides)}", fontsize=10, color=GREY)
            pdf.savefig(fig)
            plt.close(fig)
    guion = ["# Guion de exposición TP1", "", "Duración sugerida: 10 minutos. Distribuir entre los dos integrantes y ensayar.",
             "No memorizar el texto: comprender las decisiones y abrir el notebook 04 si el docente solicita evidencia.", ""]
    for i, (title, bullets, image, takeaway, segundos) in enumerate(slides, 1):
        guion += [f"## Diapositiva {i}: {title} ({segundos} segundos)", "", takeaway, ""]
        if image:
            guion += [f"Figura: `reports/figures/{image}`. Explicar ejes y qué decisión respalda.", ""]
    guion += ["## Preguntas que deben poder responder", "",
              "- ¿Por qué la población baja de 83 930 a 36 681 y qué supuesto implica?",
              "- ¿Por qué conservar duplicados y separar por edición?",
              "- ¿Qué aprende fit del pipeline y por qué no se ajusta con test?",
              "- ¿Por qué AP y qué diferencia tiene frente a ROC-AUC/accuracy?",
              "- ¿Qué significa cada FP/FN y por qué el umbral OOF no es validación independiente?",
              "- ¿Qué falta para hablar de probabilidades calibradas y de utilidad real?", ""]
    (ROOT / "reports/guion_tp1.md").write_text("\n".join(guion), encoding="utf-8")
    print(f"Presentación: {path} ({len(slides)} diapositivas)")


if __name__ == "__main__":
    carpeta = ROOT / "reports/metrics"
    config = json.loads((carpeta / "seleccion.json").read_text(encoding="utf-8"))
    cv = pd.read_csv(carpeta / "cv_resumen.csv", index_col=0)
    test = pd.read_csv(carpeta / "test_metricas.csv", index_col=0)
    escribir_documentos(config, cv, test)
    generar_presentacion(config, cv, test)
