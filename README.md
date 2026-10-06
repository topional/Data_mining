<div align="center">

---

![Logo de la UPC](docs/images/upc_logo.png "Universidad Peruana de Ciencias Aplicadas")

Universidad Peruana de Ciencias Aplicadas

Carrera de Ciencias de la Computación

### 1ACC0209

### Data Mining Tools

### NRC

17496

### Informe del Trabajo Parcial

### Docente

Montoya Cubas, Carlos Fernando

### Proyecto

Predicción del resultado de capacitaciones de servidores civiles en el Perú

### Integrantes

| Código     | Alumno                               |
| :--------: | :----------------------------------: |
| u202413604 | Cueto Ninaja, Ronal Sebastian        |
| u20241e121 | Yparraguirre Aquino Sebastián Alonso |

### Período 202620

### Octubre 2026

---

</div>

## Problema y alcance del TP1

Anticipar el riesgo de **desaprobar o retirarse** de una capacitación de SERVIR/ENAP con información disponible al inscribirse. Una fila representa una participación, no necesariamente una persona única.

El archivo original contiene **83 930 filas × 20 columnas**, con 2 170 casos de riesgo (2,59 %). El modelamiento se limita a **36 681 participaciones de 198 ediciones con evaluación**, con 2 170 positivos (5,92 %). En esa población, `y=0` es APROBADO y `y=1` es DESAPROBADO/RETIRADO. Las participaciones acreditadas solo por asistencia se excluyen. El régimen se infiere de resultados históricos y debe confirmarse antes de uso real.

El TP1 compara un baseline y tres modelos preliminares con validación por edición. No es un despliegue ni una validación institucional de alertas.

## Documentación

| Documento | Contenido |
|---|---|
| [Definición del problema](docs/definicion-problema.md) | Pregunta, objetivo, alcance y criterios |
| [Dataset y procedencia](docs/dataset-y-procedencia.md) | Fuente, diccionario, licencia y población |
| [Decisiones de herramientas](docs/decisiones-herramientas.md) | Elecciones y alternativas, vinculadas a semanas 3, 5 y 6 |
| [Resultados y plan hacia el TF1](docs/plan-hacia-tf1.md) | Métricas ejecutadas, interpretación y pendientes |

## Estructura y orden de ejecución

```text
Data_mining/
├── data/raw/                        # CSV original, fuera de git
├── data/processed/                  # limpio, roles, particiones y predicciones; fuera de git
├── notebooks/
│   ├── 01_eda.ipynb                 # preguntas, gráficos y calidad
│   ├── 02_preprocesamiento.ipynb     # limpieza y población
│   ├── 03_separacion_datos.ipynb     # train/test y cinco folds por edición
│   └── 04_modelamiento.ipynb        # pipeline, baseline, modelos y evaluación
├── src/
│   └── utils/download_data.py       # descarga con respaldo y hash
├── models/                          # pipeline regenerable, fuera de git
├── reports/figures/                 # gráficos del análisis y evaluación
├── reports/metrics/                 # tablas CV/test y configuración
├── docs/
├── tests/
└── requirements.txt
```

## Ejecutar en Arch Linux / Linux / macOS

Se ejecutó y verificó con **Python 3.14.7**, scikit-learn 1.9.1 y pandas 3.0.6. Los notebooks originales se desarrollaron con Python 3.13. Se necesita internet para instalar dependencias y descargar los datos; después se trabaja localmente.

Desde la raíz del repositorio `Data_mining`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/utils/download_data.py
jupyter notebook notebooks/
```

Ejecutar los notebooks **01 → 02 → 03 → 04**, reiniciando el kernel y ejecutando todas las celdas en orden. En Windows se activa con `.venv\Scripts\Activate.ps1`.

En Jupyter, abrir cada notebook y seleccionar **Kernel → Restart Kernel and Run All Cells** (reiniciar y ejecutar todas las celdas). Guardar el notebook al finalizar para conservar tablas y gráficos. Todo el código de modelamiento está en el notebook 04; no requiere scripts adicionales. El Random Forest usa dos trabajadores.

Para ejecutar solo el notebook 04, deben existir los archivos de train, test y roles generados por los notebooks 02 y 03.

Comprobaciones de comportamiento del pipeline:

```bash
python -m unittest discover -s tests -v
python -m pip check
```

## Descarga y trazabilidad de datos

- Fuente: [Reporte de Servidores Civiles Capacitados](https://www.datosabiertos.gob.pe/dataset/reporte-de-servidores-civiles-capacitados/resource/f403f2e4-1eae-4300-987a-8e7b5e11a1fe).
- Archivo: `Dataset_ENAP_RSCC_Dic_2025_May_2026.csv`, aproximadamente 20 MB.
- Destino: `data/raw/`, ignorado por git.
- Respaldo: [Google Drive](https://drive.google.com/file/d/1jnBumWW9EzCBGUq41UP1m8_YVCm1zdVl/view).
- SHA-256: `92360ae29b38caf41d73ce92dd9918136da242e616ca175f6c33b512b50b79df`.

El script comprueba el hash de una descarga nueva. Si el archivo ya existe, no lo vuelve a descargar ni revalida automáticamente. `python src/utils/download_data.py --force` descarga nuevamente.

## Evaluación reproducible

Train tiene 29 336 filas / 158 ediciones y test 7 345 / 40. Los cinco folds de train se conservan mediante `PredefinedSplit` de `FOLD`. Ninguna edición cruza train/test ni folds.

Se comparan **DummyClassifier, regresión logística, árbol de decisión y random forest** mediante `ColumnTransformer` + `Pipeline`. La mediana, escala y categorías se aprenden únicamente con cada parte de entrenamiento. No se usan identificadores, estado final, edición, fold ni duración en días como predictoras.

Se reportan accuracy, precision, recall, F1, balanced accuracy, **Average Precision (AP)** y ROC-AUC con media y desviación entre folds. AP es un resumen de precision–recall y no se confunde con integración trapezoidal.

Se elige el modelo por AP media; después se fija el umbral por máximo F1 de OOF de train. La F1 ajustada OOF es desarrollo y tiene sesgo de selección. El test se lee después de fijar la decisión y no se utiliza para cambiarla. El resumen ejecutado está en [plan-hacia-tf1.md](docs/plan-hacia-tf1.md) y las tablas en [reports/metrics/](reports/metrics/).

El pipeline exportado recibe las diez columnas preparadas; no incluye toda la limpieza administrativa del CSV crudo. Los scores ponderados no están calibrados.

## Entregables y estado

- [x] Puntos 1–5: problema, fuente, EDA, calidad y separación.
- [x] Punto 6: flujo reproducible de preparación y clasificación.
- [x] Punto 7: baseline ejecutado.
- [x] Punto 8: al menos dos modelos (se comparan tres).
- [x] Punto 9: evaluación preliminar e interpretación.
- [x] Punto 10: hallazgos, limitaciones y plan TF1.
- [x] Cuatro notebooks ejecutados, README y dependencias.

Los integrantes deben revisar las conclusiones, comprender el código, ensayar y proporcionar acceso al repositorio al docente. Esos pasos académicos no se sustituyen por la generación de archivos.

## Limitaciones principales

Población inferida de estados finales; identidades enmascaradas; EDA y decisiones administrativas con observación del dataset completo; 17 nombres de curso compartidos entre train/test; composición distinta por tipos; solo 110 retirados; scores no calibrados; falta validación temporal e institucional. Las asociaciones e importancias no son causas. Detalle y mejoras en el plan TF1.

## Licencia y atribución

Datos: © Autoridad Nacional del Servicio Civil (SERVIR), Plataforma Nacional de Datos Abiertos, bajo [Open Data Commons Attribution License (ODC-By)](https://opendatacommons.org/licenses/by/1-0/).
