# Definición del problema

> Resumen de esta sección en el [README](../README.md).

---

## 1. Contexto del problema

La Autoridad Nacional del Servicio Civil (SERVIR), a través de la Escuela Nacional de Administración Pública (ENAP), ofrece capacitaciones a servidores civiles del Estado peruano: cursos, talleres y programas. Estas se dictan en distintas modalidades (remota, presencial y b-learning), bajo distintos tipos de convocatoria (concurso público, invitación) y llegan a servidores de los tres niveles de gobierno (nacional, regional y local) en todo el territorio.

Cada participante termina la capacitación con un estado final registrado: **aprobado**, **desaprobado** o **retirado**. SERVIR publica estos registros, anonimizados, como datos abiertos en el *Reporte de Servidores Civiles Capacitados*.

## 2. Necesidad o situación que se desea abordar

Cada capacitación supone una inversión pública (docentes, plataformas, tiempo del servidor y de su entidad). Cuando un participante desaprueba, esa inversión no se traduce en una competencia certificada.

Hoy los registros muestran *cuántos* aprueban, pero no está claro **qué características del participante o de la capacitación se asocian con un mayor riesgo de no aprobar**. Responder esto permitiría:

- identificar configuraciones de capacitación (modalidad, duración, tipo de convocatoria) con mayor riesgo;
- focalizar acompañamiento o seguimiento en los perfiles de mayor riesgo;
- orientar decisiones de diseño de la oferta formativa con evidencia y no solo con intuición.

## 3. Unidad de análisis

Un **registro de participación**: un servidor civil inscrito en una capacitación específica (cada fila del dataset).

Un mismo servidor puede aparecer en más de una capacitación, pero su documento está anonimizado, por lo que no es posible agrupar sus registros. Esto se discute como limitación en [dataset-y-procedencia.md](dataset-y-procedencia.md).

## 4. Pregunta principal del proyecto

> **¿Es posible predecir si un servidor civil aprobará o desaprobará una capacitación de SERVIR a partir de sus características (sexo, ubicación, nivel de gobierno) y de las características de la capacitación (tipo, duración, modalidad, tipo de convocatoria, área)? ¿Qué factores se asocian más con el riesgo de no aprobar?**

Preguntas secundarias que guiarán el EDA:

1. ¿Qué proporción de participantes aprueba, desaprueba o se retira, y cómo varía según el tipo de capacitación, la modalidad y el nivel de gobierno?
2. ¿Existen diferencias en la tasa de desaprobación entre grupos (sexo, departamento, tipo de convocatoria)?
3. ¿Cuánto del resultado depende de la capacitación específica y cuánto del perfil del participante?

## 5. Tipo de problema de Data Science

| Aspecto | Definición |
|---|---|
| Tipo | Aprendizaje supervisado: **clasificación binaria** |
| Variable objetivo | `ESTADO_CAPACITACION` |
| Clase de interés (positiva) | `DESAPROBADO` (es la que se desea detectar) |
| Desafío principal | **Desbalance severo de clases** (aprox. 95 % / 5 %, por confirmar en el EDA) |
| Variables predictoras | Solo las conocidas **al momento de la inscripción** (perfil del participante y características de la capacitación) |

### Decisiones de definición del objetivo

- **Tratamiento de `RETIRADO`:** *[decisión pendiente, confirmar tras el EDA]*. La opción provisional es excluir estos registros del modelo binario, porque abandonar una capacitación es un fenómeno distinto a desaprobarla; se reportará cuántos son y se reevaluará si su peso es relevante. La alternativa es agruparlos con `DESAPROBADO` bajo "no aprobó".
- **Control de fuga de información (*data leakage*):** no se usarán como predictoras variables que solo se conocen una vez finalizada la capacitación o que codifiquen el resultado. Cada variable se revisará con esta pregunta: *¿se sabría este dato antes de que el participante empiece?*

## 6. Utilidad esperada de la solución

Que SERVIR cuente con una herramienta y un análisis que permitan:

- **Estimar el riesgo** de no aprobación de un participante en una capacitación dada, para apoyar decisiones de seguimiento o acompañamiento.
- **Identificar factores asociados** a la desaprobación (por ejemplo, modalidad o duración), para revisar el diseño de la oferta.

La salida del modelo es una **probabilidad o alerta de riesgo**, no una decisión automática sobre las personas.

## 7. Criterios bajo los cuales se considerará útil el resultado

### Por qué el *accuracy* no basta

Con cerca de 95 % de aprobados, un modelo trivial que siempre predice "aprobado" alcanza ~95 % de *accuracy* sin detectar a un solo desaprobado. Por eso el *baseline* servirá justamente para demostrar que esa métrica es engañosa en este problema.

### Criterios de éxito

| # | Criterio | Cómo se mide | Umbral |
|---|---|---|---|
| 1 | El modelo supera al baseline | `DummyClassifier` (clase mayoritaria y estratificado) frente a los modelos, en métricas de la clase minoritaria | Mejora clara en PR-AUC y F1 de `DESAPROBADO` |
| 2 | Detecta una parte relevante de los desaprobados | *Recall* de `DESAPROBADO` | ≥ *[definir tras ver el baseline]* |
| 3 | Las alertas son aprovechables | *Precision* de `DESAPROBADO` | ≥ *[definir según capacidad de seguimiento]* |
| 4 | El resultado es estable | Validación cruzada estratificada (media y desviación) | Variación no mayor a *[definir]* |
| 5 | Los factores identificados son coherentes | Importancia de variables y análisis crítico | Explicaciones compatibles con el contexto, interpretadas como **asociaciones** |

### Métricas a reportar

*Recall*, *precision* y F1 de la clase `DESAPROBADO`, PR-AUC, *balanced accuracy* y matriz de confusión. El *accuracy* se reporta solo como referencia comparativa.

La elección entre priorizar *recall* o *precision* depende del costo de cada error: un falso negativo es un desaprobado que no se detectó; un falso positivo es un participante que recibe acompañamiento que quizá no necesitaba. Esta discusión se desarrollará con los resultados del baseline.

## 8. Alcance y límites

El proyecto **no pretende**:

- establecer relaciones causales (los resultados son asociaciones observadas en datos administrativos);
- evaluar o sancionar a personas ni a entidades;
- generalizar a otras capacitaciones, años o instituciones distintas a las del dataset.

Variables como sexo o ubicación son sensibles: se incluirán para analizar posibles diferencias entre grupos, pero se revisará el desempeño del modelo por segmento para no reproducir ni amplificar sesgos.