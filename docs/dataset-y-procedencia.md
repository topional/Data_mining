# Dataset y procedencia

> Resumen en el [README](../README.md). Problema planteado en [definicion-problema.md](definicion-problema.md).

---

## 1. Fuente y procedencia

| Campo | Detalle |
|---|---|
| Nombre | Reporte de Servidores Civiles Capacitados |
| Recurso utilizado | Reporte de Servidores Civiles Capacitados – Diciembre 2025 a Mayo 2026 |
| Archivo | `Dataset_ENAP_RSCC_Dic_2025_May_2026.csv` |
| Publicador | Autoridad Nacional del Servicio Civil (SERVIR) |
| Portal | Plataforma Nacional de Datos Abiertos del Perú |
| Página del recurso | [datosabiertos.gob.pe](https://www.datosabiertos.gob.pe/dataset/reporte-de-servidores-civiles-capacitados/resource/f403f2e4-1eae-4300-987a-8e7b5e11a1fe) |
| Enlace directo al CSV | https://www.datosabiertos.gob.pe/sites/default/files/Dataset_ENAP_RSCC_Dic_2025_May_2026.csv |
| Identificador del dataset | `460cf1ab-0a11-42f6-9507-83cb19d67b73` |
| Fecha de lanzamiento | 2024-06-29 |
| Última modificación del dataset | 2026-06-24 |
| Frecuencia de actualización | Anual |
| Idioma | Español (Perú) |
| Contacto del publicador | datos_abiertos@servir.gob.pe |
| Fecha de descarga | 03/10/2026 |
| Copia de respaldo | [Google Drive](https://drive.google.com/file/d/1jnBumWW9EzCBGUq41UP1m8_YVCm1zdVl/view) |
| SHA-256 | `92360ae29b38caf41d73ce92dd9918136da242e616ca175f6c33b512b50b79df` |

El archivo se obtiene con `python src/utils/download_data.py`, que verifica el hash anterior para garantizar que todos los integrantes trabajan con exactamente los mismos datos.

### Recursos del dataset no utilizados

El portal publica además los reportes de **mayo 2024 a mayo 2025** y de **junio a noviembre 2025**, junto con el diccionario y la metadata. En este proyecto se trabaja únicamente con el período **diciembre 2025 – mayo 2026**. *[Justificar brevemente la decisión: por ejemplo, tamaño manejable, un solo corte temporal consistente o alcance viable en el semestre.]*

## 2. Número de observaciones y variables

| Característica        | Valor    |
|-----------------------|----------|
| Observaciones (filas) | 83 930   |
| Variables (columnas)  | 20       |
| Tamaño del archivo    | ~19.5 MB |

## 3. Período temporal

Capacitaciones registradas entre **diciembre de 2025 y mayo de 2026**. Las fechas de inicio y término de cada capacitación están en `FECHA_INICIO` y `FECHA_TERMINO` (formato `AAAAMMDD`). *[Completar con el rango real de fechas tras el EDA.]*

## 4. Variable objetivo

`ESTADO_CAPACITACION`: resultado final del participante en la capacitación.

| Categoría | Registros | Porcentaje |
|---|---|---|
| `APROBADO` | *[n]* | *[~95 %]* |
| `DESAPROBADO` | *[n]* | *[~5 %]* |
| `RETIRADO` | *[n]* | *[%]* |

Para el modelo, la clase de interés es `DESAPROBADO`. El tratamiento de `RETIRADO` está descrito en [definicion-problema.md](definicion-problema.md). *[Completar la tabla con `df["ESTADO_CAPACITACION"].value_counts()`.]*

## 5. Diccionario de variables

> Las descripciones se basan en los nombres de las columnas y en el diccionario oficial de SERVIR. *[Verificar contra el archivo `Diccionario - Reporte de Servidores Civiles Capacitados.xlsx` del portal.]* Los valores de ejemplo corresponden a las primeras filas del archivo y deben confirmarse en el EDA.

| Variable | Tipo | Descripción | Valores de ejemplo | Rol previsto |
|---|---|---|---|---|
| `NRO` | Numérico | Correlativo de la fila | 1, 2, 3… | Descartar (identificador) |
| `DEPARTAMENTO` | Categórica | Departamento del participante | LIMA, LORETO, PIURA | Predictora |
| `PROVINCIA` | Categórica | Provincia del participante | LIMA, MAYNAS | Predictora (evaluar cardinalidad) |
| `DISTRITO` | Categórica | Distrito del participante | JESÚS MARÍA, SAN ISIDRO | Predictora (alta cardinalidad) |
| `ANO_CAPACITACION` | Numérico | Año de la capacitación | 2025 | Evaluar (poca variación esperada) |
| `AREA` | Categórica | Área que ejecuta la capacitación | IMPLEMENTACIÓN | Predictora |
| `TIPO_DOCUMENTO` | Categórica | Tipo de documento de identidad | DNI | Evaluar utilidad |
| `NRO_DOCUMENTO` | Texto | Número de documento (enmascarado) | `*********` | Descartar |
| `BENEFICIARIO` | Texto | Nombre del participante (enmascarado) | `********************` | Descartar |
| `SEXO` | Categórica | Sexo del participante | HOMBRE, MUJER | Predictora (con análisis de sesgo) |
| `NIVEL_GOBIERNO` | Categórica | Nivel de gobierno de la entidad | NACIONAL, REGIONAL, LOCAL | Predictora |
| `ESTADO_CAPACITACION` | Categórica | Resultado final | APROBADO, DESAPROBADO, RETIRADO | **Objetivo** |
| `TRABAJA_ENTIDAD_PUBLICA` | Categórica | Si labora en una entidad pública | SI | Revisar varianza (posible descarte) |
| `TIPO_CAPACITACION` | Categórica | Formato de la capacitación | CURSO, TALLER, PROGRAMA | Predictora |
| `NOMBRE_CAPACITACION` | Categórica | Nombre de la capacitación | GESTIÓN PÚBLICA CON ENFOQUE DE GÉNERO | Evaluar (alta cardinalidad) |
| `HORAS_ACADEMICAS` | Numérico | Duración en horas académicas | 10, 28, 102 | Predictora |
| `FECHA_INICIO` | Fecha (`AAAAMMDD`) | Inicio de la capacitación | 20250904 | Derivar variables (mes, etc.) |
| `FECHA_TERMINO` | Fecha (`AAAAMMDD`) | Fin de la capacitación | 20250925 | Derivar duración; revisar fuga de información |
| `MODALIDAD` | Categórica | Modalidad de dictado | REMOTA, PRESENCIAL, B-LEARNING | Predictora |
| `TIPO_CONVOCATORIA` | Categórica | Forma de convocatoria | CONCURSO PÚBLICO, INVITACIÓN | Predictora |

## 6. Licencia y condiciones de uso

Los datos se publican bajo la **Open Data Commons Attribution License (ODC-By)**, que permite copiar, distribuir y adaptar los datos siempre que se atribuya la fuente (SERVIR).

Los datos personales vienen **anonimizados** por el publicador: `NRO_DOCUMENTO` y `BENEFICIARIO` están enmascarados. En este proyecto no se intenta reidentificar a ningún participante.

## 7. Limitaciones conocidas del dataset

1. **Desbalance severo** de la variable objetivo, que exige métricas y estrategias específicas (pesos de clase, ajuste de umbral, remuestreo) y hace engañoso el *accuracy*.
2. **Registros no independientes:** un mismo servidor puede aparecer en varias capacitaciones, pero la anonimización impide agruparlo. Al separar entrenamiento y prueba no se puede dividir por persona, lo que puede volver optimistas las métricas.
3. **Fuerte dependencia de la capacitación:** las filas del archivo están agrupadas por capacitación y la tasa de aprobación probablemente depende mucho de cada curso (su exigencia o diseño). Un modelo podría aprender "qué cursos desaprueban más" sin generalizar a cursos nuevos. Conviene que el EDA lo cuantifique y que la estrategia de validación lo considere.
4. **Pocas variables del participante:** no hay edad, cargo, antigüedad, nivel educativo ni carga laboral, que probablemente influyen en el resultado.
5. **Variables de alta cardinalidad** (`DISTRITO`, `NOMBRE_CAPACITACION`) y redundancia entre `DEPARTAMENTO`, `PROVINCIA` y `DISTRITO`.
6. **Variables con poca o nula varianza:** `TRABAJA_ENTIDAD_PUBLICA` parece ser casi siempre "SI", y `ANO_CAPACITACION` varía poco en el período. *[Confirmar en el EDA.]*
7. **Riesgo de fuga de información (*data leakage*):** variables conocidas solo al finalizar la capacitación no pueden usarse como predictoras. `FECHA_TERMINO` y cualquier dato posterior a la inscripción se revisarán antes de entrenar.
8. **Alcance acotado:** los datos describen únicamente a servidores capacitados por SERVIR/ENAP en un semestre; los resultados no se generalizan a otras capacitaciones, períodos o instituciones.
9. **Datos administrativos:** pueden contener errores de registro (categorías inconsistentes, ubicaciones mal escritas, valores faltantes). Su tratamiento se documentará en el notebook de calidad y preparación.
10. **Codificación y formato:** el CSV puede no estar en UTF-8; se verificará la codificación al cargarlo para evitar errores con tildes y eñes. *[Anotar la codificación detectada.]*

## 8. Justificación de por qué el dataset es adecuado

- **Pertinencia:** contiene directamente la variable de interés (`ESTADO_CAPACITACION`) junto con variables del participante y de la capacitación, lo que permite plantear una hipótesis predictiva concreta.
- **Tamaño y riqueza:** más de 83 mil registros con variables numéricas, categóricas y de fecha justifican un flujo con `Pipeline` y `ColumnTransformer`.
- **Reto metodológico relevante:** el desbalance de clases permite demostrar, con evidencia, por qué el *accuracy* es engañoso y por qué se necesitan métricas como *recall*, F1 y PR-AUC, además de un *baseline*.
- **Fuente oficial y abierta:** proviene de una entidad pública, con licencia clara, diccionario y metadata, lo que garantiza trazabilidad y reproducibilidad.
- **Utilidad real:** el problema tiene aplicación directa en la gestión de la capacitación del servicio civil.
- **Viabilidad en el semestre:** es un dataset tabular de ~20 MB, manejable sin infraestructura especial, que permite aplicar el flujo completo de herramientas del curso.