# Definición del problema

> Resumen de esta sección en el [README](../README.md).

---

## 1. Contexto del problema

La Autoridad Nacional del Servicio Civil (SERVIR), a través de la Escuela Nacional de Administración Pública (ENAP), ofrece capacitaciones a servidores civiles del Estado peruano: cursos, talleres y programas. Estas se dictan en distintas modalidades (remota, presencial y b-learning), bajo distintos tipos de convocatoria (concurso público, invitación) y llegan a servidores de los tres niveles de gobierno (nacional, regional y local) en todo el territorio.

Cada participante termina la capacitación con un estado final registrado: **aprobado**, **asistió**, **desaprobado** o **retirado**. SERVIR publica estos registros, anonimizados, como datos abiertos en el *Reporte de Servidores Civiles Capacitados*.

## 2. Necesidad o situación que se desea abordar

Cada capacitación supone una inversión pública (docentes, plataformas, tiempo del servidor y de su entidad). Cuando un participante desaprueba o se retira, esa inversión no se traduce en una capacitación culminada satisfactoriamente.

Hoy los registros muestran *cuántos* culminan, pero no está claro **qué características del participante o de la capacitación se asocian con un mayor riesgo de no culminar satisfactoriamente**. Responder esto permitiría:

- identificar configuraciones de capacitación (modalidad, duración, tipo de convocatoria) con mayor riesgo
- focalizar acompañamiento o seguimiento en los perfiles de mayor riesgo
- orientar decisiones de diseño de la oferta formativa con evidencia y no solo con intuición

## 3. Unidad de análisis

Un **registro de participación**: un servidor civil inscrito en una capacitación específica (cada fila del dataset).

Un mismo servidor puede aparecer en más de una capacitación, pero su documento está anonimizado, por lo que no es posible agrupar sus registros. Esto se discute como limitación en [dataset-y-procedencia.md](dataset-y-procedencia.md).

## 4. Pregunta principal del proyecto

> **¿Es posible identificar, al momento de la inscripción, a los servidores civiles con mayor riesgo de no culminar satisfactoriamente una capacitación de SERVIR/ENAP (es decir, de desaprobar o retirarse), a partir de su perfil (sexo, ubicación, nivel de gobierno) y de las características de la capacitación (tipo, duración, modalidad, tipo de convocatoria, área)? ¿Qué factores se asocian más con ese riesgo?**

Aquí, **riesgo** significa pertenecer a la clase positiva definida en la sección 5: `DESAPROBADO` o `RETIRADO`.

Preguntas secundarias que guiarán el EDA:

1. ¿Qué proporción de participantes culmina satisfactoriamente (aprueba o asiste) y qué proporción cae en riesgo (desaprueba o se retira), y cómo varía según el tipo de capacitación, la modalidad y el nivel de gobierno?
2. ¿Existen diferencias en la tasa de riesgo entre grupos (sexo, departamento, tipo de convocatoria, área)?
3. ¿Cuánto del resultado depende de la capacitación específica y cuánto del perfil del participante?

## 5. Tipo de problema de Data Science

| Aspecto                     | Definición |
|-----------------------------|------------|
| Tipo                        | Aprendizaje supervisado: **clasificación binaria** |
| Variable original           | `ESTADO_CAPACITACION` (4 categorías) |
| Variable objetivo           | Variable binaria derivada `y` |
| Clase de interés (positiva) | `y = 1`: el servidor **no culmina satisfactoriamente** |
| Desafío principal           | **Desbalance muy severo de clases** (≈ 97.4 % / 2.6 %) |
| Variables predictoras       | Solo las conocidas **al momento de la inscripción** (perfil del participante y características de la capacitación) |

### Definición de la variable objetivo

| Estado original | Clase `y` | Interpretación |
|---|---|---|
| `APROBADO` | 0 | Culminó satisfactoriamente |
| `ASISTIÓ` | 0 | Culminó (acreditación por asistencia) |
| `DESAPROBADO` | **1** | No aprobó |
| `RETIRADO` | **1** | Abandonó la capacitación |

La clase positiva es el **riesgo** (`y = 1`), porque es el evento que se desea anticipar. Según el conteo preliminar, `ASISTIÓ` + `APROBADO` suman 81 760 registros (97.41 %) y `DESAPROBADO` + `RETIRADO` suman 2 170 (2.59 %), de un total de 83 930.

### Decisiones de definición del objetivo

- **Agrupación de `DESAPROBADO` y `RETIRADO` en la clase positiva.** Se consideró como caso de riesgo (y = 1) a los participantes con estado DESAPROBADO o RETIRADO, porque en ambos casos la capacitación no culminó satisfactoriamente. Los estados APROBADO y ASISTIÓ se consideraron culminación satisfactoria (y = 0).

- **`ASISTIÓ` y `APROBADO` en la clase 0.** Ambos estados se interpretan como culminación satisfactoria de la capacitación. La diferencia entre ellos puede deberse al régimen de evaluación: en algunos casos la acreditación se realiza por asistencia y en otros por evaluación de rendimiento. Por ello, se agruparon en la clase 0 para no tratar como riesgo un resultado que, para la institución, representa una culminación válida.

- **Control de fuga de información (*data leakage*):** no se usarán como predictoras variables que solo se conocen una vez finalizada la capacitación o que codifiquen el resultado. Cada variable se revisará con esta pregunta: *¿se sabría este dato antes de que el participante empiece?*

## 6. Utilidad esperada de la solución

Que SERVIR y las entidades responsables de la capacitación cuenten con una herramienta y un análisis que permitan:

- **Estimar el riesgo** de no culminar satisfactoriamente una capacitación, para apoyar decisiones de seguimiento o acompañamiento.
- **Identificar factores asociados** a ese riesgo (por ejemplo, modalidad o duración), para revisar el diseño de la oferta.

La salida del modelo es una **probabilidad o alerta de riesgo**, no una decisión automática sobre las personas.

## 7. Criterios bajo los cuales se considerará útil el resultado

### Por qué el *accuracy* no basta

Como aproximadamente el 97.4% de los participantes pertenece a la clase 0 (sin riesgo), un modelo muy simple que siempre predice “no riesgo” alcanzaría alrededor de 97.4% de exactitud **(accuracy)**, aunque no identificaría a ningún participante en riesgo. Por ello, se incluirá este modelo simple como punto de comparación **(baseline)**. Su objetivo es mostrar que la exactitud puede ser una medida engañosa cuando una clase es mucho más frecuente que la otra.

Para evaluar el desempeño real del modelo se dará especial atención a su capacidad para identificar los casos de riesgo, y no solo a la proporción total de aciertos.

### Criterios de éxito

Se considerará que el modelo es útil si logra identificar participantes en riesgo mejor que un modelo simple que siempre predice “sin riesgo”. La evaluación revisará tanto los casos de riesgo detectados como la proporción de alertas que resultan correctas. Asimismo, se comprobará que los resultados sean similares al evaluar el modelo en distintas particiones de los datos y que las variables asociadas al riesgo tengan una interpretación razonable en el contexto de las capacitaciones.

### Métricas a reportar

Se evaluará principalmente la capacidad del modelo para identificar a los participantes con riesgo de no culminar satisfactoriamente la capacitación. Para ello se reportarán:

- Recall de la clase positiva: indica qué proporción de los participantes que realmente presentaron riesgo fue identificada por el modelo.

- Precision de la clase positiva: indica qué proporción de los participantes señalados por el modelo como “en riesgo” realmente presentó riesgo.

- F1 de la clase positiva: resume el equilibrio entre recall y precision.

- PR-AUC: resume el desempeño del modelo al comparar la proporción de alertas correctas y la proporción de casos de riesgo detectados bajo distintos niveles de alerta.

- Balanced accuracy: resume el desempeño considerando por igual a los participantes con riesgo y sin riesgo; evita que la clase mayoritaria tenga demasiado peso en la evaluación.

- Matriz de confusión: muestra la cantidad de casos correctamente clasificados y los errores cometidos por el modelo.

## 8. Alcance y límites

El proyecto **no pretende**:

- establecer relaciones causales (los resultados son asociaciones observadas en datos administrativos)
- evaluar o sancionar a personas ni a entidades
- generalizar a otras capacitaciones, años o instituciones distintas a las del dataset.

Con las variables disponibles (no hay edad, cargo, antigüedad ni nivel educativo) y una clase positiva de solo ~2.6 %, es posible que el poder predictivo sea **limitado**. El proyecto reportará con honestidad cuánto mejora el modelo frente al baseline y qué no puede concluirse.

Variables como sexo o ubicación son sensibles: se incluirán para analizar posibles diferencias entre grupos, pero se revisará el desempeño del modelo por segmento para no reproducir ni amplificar sesgos.