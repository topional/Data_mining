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

## Resumen

Este proyecto busca predecir si un servidor civil **aprobará o desaprobará** una capacitación de SERVIR, a partir de sus características y las de la capacitación, y entender qué factores se asocian al riesgo de no aprobar. Se trata de un problema de **clasificación binaria con desbalance severo de clases (~95/5)**, lo que obliga a evaluar con métricas distintas al accuracy.

El TP1 y el TF1 corresponden al mismo proyecto: el TP1 es el primer corte (problema, EDA, preparación, baseline y modelos preliminares) y el TF1 presenta la solución integrada, evaluada y desplegada.

## Contenido

| Sección | Descripción | Documento |
|---|---|---|
| Definición del problema | Contexto, necesidad, unidad de análisis, pregunta y criterios de éxito | [docs/definicion-problema.md](docs/definicion-problema.md) |
| Dataset y procedencia | Fuente, licencia, variables, limitaciones y justificación | [docs/dataset-y-procedencia.md](docs/dataset-y-procedencia.md) |
| Decisiones de herramientas | Matriz de herramientas elegidas y alternativas | [docs/decisiones-herramientas.md](docs/decisiones-herramientas.md) |
| Plan hacia el TF1 | Hallazgos, pendientes y próximos pasos | [docs/plan-hacia-tf1.md](docs/plan-hacia-tf1.md) |
| Uso de IA generativa | Declaración de uso | [docs/uso-ia-generativa.md](docs/uso-ia-generativa.md) |
| Análisis (EDA, calidad, modelos) | Notebooks ejecutados | [notebooks/](notebooks/) |

## 1. Problemática inicial

- **Contexto:** SERVIR y la ENAP capacitan a servidores civiles de los tres niveles de gobierno, en distintas modalidades y en todo el país.
- **Necesidad:** cada capacitación implica una inversión pública; si el participante no aprueba, no se obtiene una competencia certificada. Hoy no se sabe qué factores se asocian a ese riesgo.
- **Unidad de análisis:** un registro de participación (un servidor en una capacitación).
- **Pregunta principal:** ¿se puede predecir si un servidor civil aprobará o desaprobará una capacitación a partir de sus características y las de la capacitación, y qué factores se asocian más al riesgo de no aprobar?
- **Tipo de problema:** clasificación binaria (`ESTADO_CAPACITACION`).
- **Criterio de utilidad:** el modelo debe superar a un baseline en recall, F1 y PR-AUC de la clase minoritaria; el accuracy por sí solo no es criterio.

Detalle completo en: [docs/definicion-problema.md](docs/definicion-problema.md)

## 2. Dataset y procedencia

| Campo | Detalle |
|---|---|
| Nombre | Reporte de Servidores Civiles Capacitados |
| Publicador | Autoridad Nacional del Servicio Civil (SERVIR) |
| Portal | Plataforma Nacional de Datos Abiertos del Perú |
| Período | Diciembre 2025 – Mayo 2026 |
| Tamaño | 83930 filas × 20 columnas |
| Variable objetivo | `ESTADO_CAPACITACION` |
| Licencia | Open Data Commons Attribution License (ODC-By) |
| Enlace | https://www.datosabiertos.gob.pe/dataset/reporte-de-servidores-civiles-capacitados/resource/f403f2e4-1eae-4300-987a-8e7b5e11a1fe |

Los datos personales (`NRO_DOCUMENTO`, `BENEFICIARIO`) vienen anonimizados por el publicador. Variables, limitaciones y justificación en [docs/dataset-y-procedencia.md](docs/dataset-y-procedencia.md).

## Estructura del proyecto

```
Data_mining/
├── data/
│   ├── raw/             # CSV originales de SERVIR
│   └── processed/       # datos tras limpieza y preparación
├── notebooks/           # EDA, calidad de datos, baseline y modelos
├── src/                 # código reutilizable (pipelines, utilidades)
├── models/              # modelos entrenados
├── reports/             # presentaciones y reportes
├── docs/                # documentación detallada por sección
├── README.md
└── requirements.txt
```

## Cómo ejecutar el proyecto

**Requisitos:** Python 3.13 (versión usada en el desarrollo), Git y conexión a internet para descargar el dataset (~20 MB).

```bash
# Clonar el repositorio
git clone https://github.com/topional/Data_mining.git
cd Data_mining

# Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate       # Linux / macOS

# Instalar dependencias
pip install -r requirements.txt

# Descargar el dataset (se guarda en data/raw/)
python src/utils/download_data.py

# Abrir los notebooks
jupyter notebook notebooks/
```

> **Windows:** si PowerShell bloquea la activación del entorno, ejecuta una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

### Sobre la descarga de datos

El script `src/utils/download_data.py`:

1. Descarga el CSV desde el **portal oficial de Datos Abiertos** de SERVIR.
2. Si el portal falla, usa una **copia de respaldo en Google Drive**.
3. Verifica la integridad del archivo con **SHA-256**, de modo que todos trabajen con exactamente los mismos datos.
4. Si el archivo ya existe en `data/raw/`, no lo vuelve a descargar. Usa `--force` para reemplazarlo:

```bash
python src/utils/download_data.py --force
```

| Dato | Valor |
|---|---|
| Archivo | `Dataset_ENAP_RSCC_Dic_2025_May_2026.csv` |
| Destino | `data/raw/` (ignorado por git) |
| Fuente oficial | [Página del recurso](https://www.datosabiertos.gob.pe/dataset/reporte-de-servidores-civiles-capacitados/resource/f403f2e4-1eae-4300-987a-8e7b5e11a1fe) |
| Respaldo | [Google Drive](https://drive.google.com/file/d/1jnBumWW9EzCBGUq41UP1m8_YVCm1zdVl/view) |
| SHA-256 | `92360ae29b38caf41d73ce92dd9918136da242e616ca175f6c33b512b50b79df` |
| Fecha de descarga | 03/10/2026 |

## Estado del proyecto

- [x] Definición del problema y dataset
- [ ] EDA
- [ ] Calidad y preparación de datos
- [ ] Separación train/validation/test y pipeline
- [ ] Baseline y modelos preliminares
- [ ] Evaluación y plan hacia el TF1

## Uso de IA generativa

Se utilizaron herramientas de IA generativa como apoyo técnico. El detalle está en [docs/uso-ia-generativa.md](docs/uso-ia-generativa.md).

## Licencia y atribución

- **Datos:** © Autoridad Nacional del Servicio Civil (SERVIR), publicados en la Plataforma Nacional de Datos Abiertos bajo la [Open Data Commons Attribution License (ODC-By)](https://opendatacommons.org/licenses/by/1-0/).