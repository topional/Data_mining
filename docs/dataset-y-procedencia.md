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

El archivo se obtiene con `python src/utils/download_data.py`, que verifica el hash anterior para garantizar que se trabaje con exactamente los mismos datos.

### Recursos del dataset no utilizados

El portal publica además los reportes de **mayo 2024 a mayo 2025** y de **junio a noviembre 2025**, junto con el diccionario y la metadata. En este proyecto se trabaja únicamente con el reporte **diciembre 2025 – mayo 2026**.

## 2. Número de observaciones y variables

| Característica        | Valor    |
|-----------------------|----------|
| Observaciones (filas) | 83 930   |
| Variables (columnas)  | 20       |
| Tamaño del archivo    | ~19.5 MB |

## 3. Período temporal

El archivo se rotula como el reporte de **diciembre de 2025 a mayo de 2026**. Las fechas de cada capacitación están en `FECHA_INICIO` y `FECHA_TERMINO` (formato `AAAAMMDD`).

## 4. Variable objetivo

`ESTADO_CAPACITACION`: resultado final del participante en la capacitación. Tiene **cuatro categorías**, que se agrupan en una variable binaria `y` para el problema (ver [definicion-problema.md](definicion-problema.md)).

| Categoría | Registros | Porcentaje | Clase `y` |
|---|---|---|---|
| `ASISTIÓ` | 47249 | 56.296% | 0 |
| `APROBADO` | 34511 | 41.119% | 0 |
| `DESAPROBADO` | 2060 | 2.454% | 1 |
| `RETIRADO` | 110 | 0.131% | 1 |
| **Total** | 83 930 | 100 % | |

Según el conteo preliminar, la **clase 0** (`ASISTIÓ` + `APROBADO`) reúne 81 760 registros (97.41 %) y la **clase 1** (`DESAPROBADO` + `RETIRADO`) reúne 2 170 (2.59 %).

## 5. Diccionario de variables

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
| `ESTADO_CAPACITACION` | Categórica | Resultado final | ASISTIÓ, APROBADO, DESAPROBADO, RETIRADO | **Origen del objetivo** (se binariza en `y`) |
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

1. **Desbalance muy severo** de la variable objetivo (≈ 97.4 % / 2.6 %, solo ~2 170 casos positivos de 83 930), que exige métricas y estrategias específicas (pesos de clase, ajuste de umbral, remuestreo aplicado únicamente dentro del entrenamiento) y hace engañoso el *accuracy*.
2. **Clase positiva heterogénea:** `DESAPROBADO` (rendimiento) y `RETIRADO` (abandono) son desenlaces distintos que se agrupan por razones prácticas.
3. **Regímenes de evaluación posiblemente distintos:** `ASISTIÓ` y `APROBADO` pueden corresponder a capacitaciones acreditadas por asistencia o por nota. Si ciertos tipos de capacitación solo admiten algunos desenlaces, parte de las diferencias entre tipos puede ser estructural.
4. **Registros no independientes:** un mismo servidor puede aparecer en varias capacitaciones, pero la anonimización impide agruparlo. Al separar entrenamiento y prueba no se puede dividir por persona, lo que puede volver optimistas las métricas.
5. **Pocas variables del participante:** no hay edad, cargo, antigüedad, nivel educativo ni carga laboral, que probablemente influyen en el resultado.
6. **Variables de alta cardinalidad** (`DISTRITO`, `NOMBRE_CAPACITACION`) y redundancia entre `DEPARTAMENTO`, `PROVINCIA` y `DISTRITO`.
7. **Variables con poca o nula varianza:** `TRABAJA_ENTIDAD_PUBLICA` parece ser casi siempre "SI", y `ANO_CAPACITACION` varía poco en el período.
8. **Riesgo de fuga de información (*data leakage*):** variables conocidas solo al finalizar la capacitación no pueden usarse como predictoras. `FECHA_TERMINO` y cualquier dato posterior a la inscripción se revisarán antes de entrenar.
9. **Alcance acotado:** los datos describen únicamente a servidores capacitados por SERVIR/ENAP en un reporte semestral; los resultados no se generalizan a otras capacitaciones, períodos o instituciones.
10. **Datos administrativos:** pueden contener errores de registro (categorías inconsistentes, ubicaciones mal escritas, valores faltantes). Su tratamiento se documentará en el notebook de calidad y preparación.
11. **Codificación y formato:** el CSV puede no estar en UTF-8; se verificará la codificación al cargarlo para evitar errores con tildes y eñes.

## 8. Justificación de por qué el dataset es adecuado

- **Pertinencia:** contiene directamente la variable de interés (`ESTADO_CAPACITACION`) junto con variables del participante y de la capacitación, lo que permite plantear una hipótesis predictiva concreta.
- **Tamaño y riqueza:** más de 83 mil registros con variables numéricas, categóricas y de fecha justifican un flujo con `Pipeline` y `ColumnTransformer`.
- **Reto metodológico relevante:** el desbalance muy severo permite demostrar, con evidencia, por qué el *accuracy* es engañoso y por qué se necesitan métricas como *recall*, F1 y PR-AUC, además de un *baseline*.
- **Fuente oficial y abierta:** proviene de una entidad pública, con licencia clara, diccionario y metadata, lo que garantiza trazabilidad y reproducibilidad.
- **Utilidad real:** el problema tiene aplicación directa en la gestión de la capacitación del servicio civil.

## 9. Población y datos preparados del TP1

El análisis selecciona 36 681 participaciones de 198 ediciones con evaluación. Se conservan 34 511 aprobados, 2 060 desaprobados y 110 retirados; prevalencia positiva 5,92 %. Las 47 249 participaciones de solo asistencia quedan fuera de esta población. El régimen se infiere de resultados históricos: no equivale a metadata confirmada de inscripción.

El CSV limpio tiene 22 columnas con roles distintos; diez son predictoras candidatas. Se excluyen identificadores, estado final y duración en días de las entradas. Train contiene 29 336 filas / 158 ediciones, test 7 345 / 40; la validación usa cinco folds dentro de train. Hay 17 nombres de cursos presentes en ambos conjuntos y diferencias de composición por tipos de capacitación.

La ventana del reporte no coincide con todas las fechas de inicio: el archivo contiene inicios desde febrero de 2025. Se corrigieron y marcaron 1 498 fechas de término en 2015 mediante una regla temporal plausible; esa corrección no está confirmada por el publicador.
