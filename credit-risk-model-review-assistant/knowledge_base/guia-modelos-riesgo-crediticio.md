# Guía de desarrollo e implementación de modelos de riesgo crediticio

Guía técnica para diseñar, evaluar y poner en operación modelos que apoyan decisiones de crédito. Sus criterios se pueden adaptar al producto, la población y el impacto de cada decisión.

## Definir el problema y organizar el proyecto

Identifica primero la decisión que necesita apoyo. Un modelo de admisión puede estimar el riesgo de una solicitud nueva, mientras que uno de comportamiento puede priorizar la revisión de una cartera existente. Define quién utilizará el resultado, en qué momento lo recibirá y qué acción podrá tomar.

Formula el objetivo analítico en términos observables. Delimita la población, el resultado esperado, el horizonte de predicción y las restricciones de uso. Define cómo se evaluará el valor del modelo frente a la práctica actual, por ejemplo, mediante cambios en la aprobación, la mora o las pérdidas esperadas. En la reunión de inicio, acuerda responsables, fuentes, hitos, entregables y criterios de aceptación.

## Seleccionar y evaluar fuentes de datos

Combina únicamente fuentes pertinentes para el objetivo y disponibles en el momento de decisión. Entre las fuentes habituales se encuentran las solicitudes, el historial de pagos, las características de los créditos y, cuando su uso esté autorizado, la información de centrales de riesgo y registros públicos. Documenta la fecha de disponibilidad, la periodicidad de actualización y el desfase de cada fuente.

Evalúa completitud, exactitud, coherencia, unicidad, validez y oportunidad. Mide los problemas por período y segmento para distinguir una falla localizada de un cambio general. Documenta las reglas de enlace, la unidad de análisis y las limitaciones de cobertura. Una variable disponible durante el desarrollo solo es viable si puede calcularse a tiempo y con calidad suficiente en operación.

## Procedimiento detallado de calidad de datos

### 1. Definir la base y las reglas

Fija la unidad de análisis, la clave esperada, la fecha de observación y el horizonte de la etiqueta. Para cada fuente, documenta la cobertura, el desfase, los campos obligatorios, los tipos y rangos permitidos y la fecha en que la información quedó disponible para decidir. Define para cada prueba el denominador, los segmentos y la acción ante una falla.

### 2. Conciliar las fuentes y verificar las uniones

Cuenta los registros en la fuente, después de cada filtro y después de cada unión. Comprueba que la clave sea única al nivel esperado, busca registros sin correspondencia y detecta uniones que multipliquen filas. Distingue duplicados de eventos válidos repetidos. Reconcilia las diferencias por período y causa. Conserva el conteo antes y después de cada corrección.

### 3. Perfilar los campos y contrastar la etiqueta

Por variable, período y segmento, mide el número de observaciones válidas, faltantes, ceros, valores especiales y categorías distintas. Para campos numéricos, calcula media, mediana, moda cuando sea útil, desviación estándar, coeficiente de variación si la media permite interpretarlo, mínimo, máximo y percentiles. Por ejemplo, usa P1, P5, P25, P50, P75, P95 y P99 para examinar el centro y las colas. Para categorías, revisa la frecuencia de cada nivel y la concentración de la categoría dominante.

Compara la tasa de incumplimiento entre registros con y sin dato, usando casos con etiqueta observable. Distingue el porcentaje de valores faltantes sobre toda la población de la tasa de evento dentro del grupo con dato faltante. Si el faltante concentra incumplimientos, investiga si refleja el comportamiento de la población, una regla de captura o una falla de enlace.

### 4. Validar dominios, fechas y consistencia

Comprueba tipos, unidades, rangos, categorías permitidas y coherencia entre campos. Por ejemplo, compara saldo, estado y fecha de cancelación cuando describan el mismo crédito. Verifica que las variables usen únicamente información disponible en la fecha de observación y que el evento objetivo se calcule dentro de la ventana posterior definida. Reproduce manualmente algunos casos normales, extremos y con datos ausentes.

### 5. Evaluar estabilidad y decidir el tratamiento

Compara los volúmenes, la proporción de faltantes y la distribución de valores entre períodos y segmentos. Usa grupos fijos para calcular PSI y revisa qué grupos explican el cambio. Investiga primero si hubo cambios en la fuente, en las reglas de extracción o en la población.

Documenta si corresponde corregir en origen, ajustar la unión, separar los casos no aplicables, imputar, agrupar extremos o retirar una variable. Estima las reglas de tratamiento con los datos de entrenamiento y aplícalas de forma consistente a las demás muestras. Vuelve a ejecutar las pruebas y registra cómo cambió la cobertura, la tasa del evento y la distribución de la variable.

### 6. Establecer controles en operación

Usa el perfil de desarrollo o de certificación como línea base. Por cada ejecución, registra volúmenes, duplicados, faltantes, categorías nuevas y desviaciones de distribución. Si se activa una alerta, revisa primero las fuentes y las uniones. Luego cuantifica el impacto sobre la probabilidad de incumplimiento y los tramos de riesgo. Registra la evidencia, la causa, la corrección y el resultado de la nueva prueba. Para cada control, define cuándo alertar y cuándo suspender el cálculo.

### Umbrales de calidad antes del análisis de variables

| Control preliminar | Criterio de referencia |
| --- | --- |
| Completitud de variables candidatas | Menos del 85% de faltantes en el perfil preliminar. En el filtro univariado posterior, se descartan candidatas con más del 75% de faltantes. |
| Consistencia temporal de población, filtros, objetivo, segmentos y variables | El control preliminar usa PSI < 0,20 como referencia. Para decidir sobre filtros y variables en etapas posteriores, aplica las bandas de estabilidad de su respectivo capítulo. |
| Unicidad | Corrige duplicados indebidos según la clave de la unidad de análisis y documenta los registros retirados. |

## Construir la población elegible

Define si cada registro representa a una persona, una solicitud, una cuenta u otra unidad. Establece la fecha de observación y las reglas para resolver duplicados o múltiples registros del mismo caso. Registra los criterios de inclusión y exclusión y cuantifica cuántas observaciones se eliminan con cada regla.

Comprueba que la población de desarrollo represente el uso previsto. Analiza el volumen, la composición y la tasa del evento a lo largo del tiempo. Cuando el historial cubra principalmente solicitudes aprobadas, documenta el efecto que esa selección puede tener al aplicar el modelo a todas las solicitudes futuras.

### Estabilidad de población y filtros

Un **PSI ≤ 0,10** es una referencia de estabilidad. Con **0,10 < PSI ≤ 0,20**, revisa qué cambió y documenta el impacto. Un **PSI > 0,20** señala un cambio estructural que requiere revisar los filtros, las exclusiones o la población antes de seguir.

## Diseñar la variable objetivo

Define un evento verificable y un período de observación. El objetivo puede ser binario, multiclase, continuo o un tiempo hasta el evento. En un modelo binario de incumplimiento, especifica la condición que define el evento y desde qué fecha se mide el horizonte.

El análisis de transición entre tramos de mora (*roll rate*) ayuda a determinar cuándo un atraso se vuelve persistente. La curva de maduración del incumplimiento permite estimar cuánto tiempo necesita una cohorte para que su tasa observada se estabilice. Usa ambas comprobaciones para justificar el umbral y el horizonte elegidos.

Establece reglas para clasificar casos con evento, sin evento y de resultado indeterminado. Los casos con observación incompleta necesitan un tratamiento explícito. Contrasta la tasa del objetivo entre cohortes y examina cambios relacionados con políticas, eventos económicos o modificaciones en la captura de datos.

### Cortes ilustrativos para construir y revisar el objetivo

| Prueba | Referencia |
| --- | --- |
| Transiciones de mora | Pueden analizarse los tramos de 0, 1–30, 31–60, 61–90 y más de 90 días. Contrasta cortes de más de 30 o más de 60 días según la persistencia observada. |
| Maduración | Si el 95% de los eventos observados se acumula en los primeros 12 meses, ese horizonte puede servir como ventana de observación. |
| Clasificación en un horizonte de 6 meses | Ejemplo: sin evento cuando la mora no supera 3 días y no hay castigo. Con evento cuando supera 30 días o hay castigo. Entre 4 y 30 días sin castigo, o con observación incompleta y sin evento confirmado, la clasificación puede ser indeterminada. |
| Representatividad | Una proporción de indeterminados no mayor al 15% es una referencia orientativa. |
| Estabilidad del objetivo | PSI < 0,10 indica estabilidad. De 0,10 a 0,20 corresponde revisar. Por encima de 0,20, documenta el cambio y sustenta el uso. |

## Dividir las muestras y evaluar segmentos

Usa la muestra de entrenamiento para ajustar transformaciones y parámetros. Reserva datos de prueba para evaluar el rendimiento y una muestra posterior en el tiempo para comprobar la generalización temporal. Cuando existan registros repetidos de una persona o una cuenta, diseña la separación de modo que el mismo historial no contamine las comparaciones.

Evalúa si distintos grupos requieren modelos propios mediante diferencias en sus tasas de evento, patrones de comportamiento y disponibilidad de variables. Un modelo por segmento se justifica cuando hay suficiente evidencia y volumen para desarrollarlo, validarlo y mantenerlo. Compara esa opción con un modelo común que incorpore las diferencias observadas.

### Referencias para partición y segmentación

| Decisión | Criterio de referencia |
| --- | --- |
| Partición con menos de 10 000 observaciones | 60% entrenamiento y 40% prueba dentro del período de desarrollo. |
| Partición con más de 10 000 observaciones | 70% entrenamiento y 30% prueba dentro del período de desarrollo. |
| Casos cercanos al límite y carteras con pocos eventos | Elige la partición por el número de incumplimientos disponibles en cada muestra. Mantén aparte el período fuera de tiempo. |
| Evaluación de un segmento separado | Considera segmentar si la subpoblación representa más del 20% del total y la diferencia absoluta en tasas de incumplimiento entre subpoblaciones supera 6 puntos porcentuales. Comprueba también el número de eventos y el beneficio de segmentar. |

**Ajuste para *low default*.** Con una tasa de 0,5%, usa los cortes de 20% de tamaño y 6 puntos porcentuales de diferencia como antecedentes del procedimiento general. Para decidir si segmentar, compara diferencia absoluta y razón de tasas con intervalos, exige suficientes eventos por segmento y verifica si separar modelos mejora la calibración o la decisión fuera de tiempo. Con tablas escasas, usa una prueba exacta de Fisher si las observaciones son independientes o un método que respete la dependencia si se repiten obligados o cosechas.

## Preparar variables predictoras

Construye variables a partir de información disponible antes de la decisión. Documenta las ventanas, agregaciones, denominadores y reglas de unión. Si dos fuentes representan el mismo indicador, define cuál tiene prioridad y qué sucede si falla o llega tarde.

Distingue valores ausentes, ceros reales, casos no aplicables y errores de captura. Selecciona un tratamiento coherente con su significado. Aplica a las muestras de prueba y operación las reglas estimadas con la muestra de entrenamiento. Para valores extremos, revisa si reflejan errores o comportamientos reales antes de recortar, agrupar o transformar. Define también cómo se manejarán categorías nuevas en operación.

## Seleccionar variables

Comienza con pruebas univariadas de disponibilidad, variabilidad, concentración y estabilidad temporal. El PSI compara proporciones entre una distribución de referencia y otra de evaluación. Su lectura depende de la forma de agrupar las observaciones, el volumen de cada grupo y el efecto de la deriva en el modelo.

El análisis bivariado ayuda a identificar variables relacionadas con el objetivo. En una clasificación binaria, el Gini se puede expresar como 2 × AUC − 1. El peso de evidencia (WoE) se obtiene mediante el logaritmo de la razón entre la proporción de casos sin evento y con evento en un grupo. El valor de información (IV) agrega el aporte de los grupos a la separación entre ambas clases. Documenta la convención de signos y cómo se tratan grupos con proporciones nulas.

Al agrupar intervalos, procura que los tramos tengan volumen suficiente y un patrón interpretable. Revisa correlaciones y redundancia entre variables. La selección final debe equilibrar aporte predictivo, estabilidad, claridad, disponibilidad operativa y coherencia con el objetivo.

## Procedimiento detallado de selección de variables

### 1. Preparar el inventario y las muestras

Registra el nombre, la definición, la fuente, la ventana y la disponibilidad operativa de cada candidata. Elimina variables con fuga de información, campos que solo identifican registros y duplicados funcionales. Separa entrenamiento, prueba y muestra fuera de tiempo. Usa entrenamiento para elegir variables, cortes y parámetros. Reserva la muestra fuera de tiempo para comprobar el conjunto final.

**Presupuesto de parámetros.** Para una regresión logística, usa **10–20 incumplimientos por parámetro candidato** como referencia inicial de planificación. El extremo de 20 es un escenario prudente de sensibilidad. Cuenta grados de libertad de indicadores, tramos, interacciones y términos no lineales, y usa los incumplimientos de entrenamiento. Con 250 eventos en entrenamiento, la referencia equivale a **12–25 parámetros candidatos**. Si 250 es el total y 175 quedan en entrenamiento, la referencia baja a **8–17**. Ajusta el presupuesto al tamaño de muestra, la prevalencia, el desempeño esperado y la regularización. Para árboles, controla la complejidad con validación y estabilidad. [Riley y coautores, tamaño de muestra para modelos de predicción](https://doi.org/10.1136/bmj.m441)

### 2. Aplicar el filtro univariado

Por variable, calcula faltantes, concentración de la categoría dominante, desviación estándar y, cuando sea interpretable, coeficiente de variación. Usa los criterios de referencia de esta guía para decidir qué variables se descartan, cuáles requieren tratamiento y cuáles avanzan. Calcula el PSI con cortes fijos para comparar períodos y conserva el máximo observado junto con el período que lo produjo. Examina si un cambio de distribución coincide con una falla de calidad.

**Cortes del filtro.** Descarta una variable si una categoría concentra más del **85%**, su coeficiente de variación numérico es inferior al **4%**, su desviación estándar es **cero** o supera el **75% de faltantes**. Para PSI, **≤ 0,10** indica estabilidad, **> 0,10 y ≤ 0,20** requiere revisión y **> 0,20** es un corte de exclusión salvo justificación técnica.

### 3. Medir la relación con el objetivo

Compara la frecuencia y la tasa de evento por grupo. Calcula Gini e IV por muestra con reglas de agrupación consistentes. Para el IV, calcula el WoE de cada grupo y suma el producto de ese WoE por la diferencia entre las proporciones de no eventos y eventos del grupo. Si alguna proporción es cero, agrupa categorías o aplica un suavizado documentado. Registra el Gini y el IV mínimos entre muestras y la variabilidad del Gini. Un resultado fuerte en entrenamiento acompañado de una caída marcada fuera de muestra requiere investigación.

**Cortes bivariados de referencia.** Revisa el descarte si el **IV mínimo ≤ 2%**, el **Gini mínimo ≤ 3%** o el **coeficiente de variación del Gini ≥ 80%** entre entrenamiento, prueba y fuera de tiempo. La fuente también registra **«IV_GINI ≥ 80%»** como cuarto corte, con una denominación ambigua. Conserva la cifra como referencia documental y confirma la métrica antes de aplicar la regla.

### 3a. Selección bivariada con pocos incumplimientos

1. Para cada candidata, construye un puntaje univariado con entrenamiento. Puedes ordenar por la tasa de incumplimiento estimada de los grupos o ajustar un modelo de una variable. Fija el sentido del orden, los grupos, el tratamiento de faltantes y la regla de desempate antes de evaluar.
2. Aplica el puntaje a los mismos registros de validación para todas las candidatas. Reporta PR-AUC o AP, lift, precisión y recall al mismo porcentaje de revisión. Complementa con Gini e IV y guarda la prevalencia, la cantidad de eventos y los conteos al corte.
3. Usa AP > prevalencia y lift > 1 como señales iniciales de valor sobre una referencia aleatoria. Examina la magnitud de la mejora y su estabilidad. Si el intervalo de la mejora incluye cero o el del lift incluye 1, considera la evidencia inconclusa. Revisa la consistencia temporal, la calidad de la variable y su aporte incremental al modelo. Conserva la muestra fuera de tiempo para verificar la selección final.

**Incertidumbre del filtro bivariado.** Con alrededor de 250 incumplimientos en toda la base, revisa los eventos reales por muestra. Calcula intervalos por bootstrap para Gini, IV y las métricas PR. Para comparar candidatas en los mismos casos, remuestrea de forma pareada y conserva agrupaciones por obligado o bloques temporales cuando corresponda. Declara cómo se tratan las réplicas sin eventos. Reporta el CV del Gini junto a sus componentes. Si el Gini medio está cerca de cero, el CV pierde estabilidad y debe leerse junto con la dispersión y los intervalos. Los cortes de IV, Gini y CV son referencias de diagnóstico en este escenario. [Boyd, Eng y Page, incertidumbre del PR-AUC](https://scholars.duke.edu/publication/1393181)

### 4. Agrupar intervalos y revisar la coherencia

Para un modelo clásico, estima cortes con entrenamiento, revisa el tamaño de cada tramo y compara tasas de evento entre tramos adyacentes. Como ejemplo, con un solo corte puede exigirse que cada tramo cubra al menos el 3% de la muestra. Con más de dos cortes puede considerarse un mínimo del 8%. Una separación orientativa de 3 puntos porcentuales entre tasas de evento ayuda a detectar tramos difíciles de distinguir.

Agrupa tramos pequeños o con tasas similares y revisa si el patrón es monotónico cuando tenga sentido económico. Trata los faltantes como un grupo propio si su comportamiento es diferenciado y hay datos suficientes. Guarda los cortes, las frecuencias y el WoE. Para modelos de árboles, evalúa primero si el algoritmo puede capturar la relación con las variables sin agrupar y examina la dirección de su efecto.

**Ajuste para *low default*.** Sustituye la exigencia general de 3 puntos porcentuales entre tramos por evidencia de separación relativa, intervalos y relevancia para la decisión. Antes de fijar cortes, define un mínimo de eventos o una anchura máxima de intervalo para estimar la tasa con la precisión necesaria. Cuando un tramo tiene cero o pocos eventos, combina vecinos compatibles o usa estimación por grado con regularización. Los porcentajes de población del 3–8% ayudan a controlar el tamaño, pero la decisión depende también del número de eventos. [Brown, Cai y DasGupta, intervalos binomiales](https://doi.org/10.1214/ss/1009213286)

### 5. Eliminar redundancia antes del ajuste final

Calcula la matriz de correlaciones para las variables comparables. Agrupa candidatas que midan el mismo fenómeno y conserva la que combine mejor discriminación, estabilidad, calidad y disponibilidad. Usa el VIF sobre las variables finalistas de modelos clásicos para revisar colinealidad conjunta. Si conservas variables muy correlacionadas, documenta su aporte adicional y verifica si se mantiene tras el reentrenamiento.

**Cortes de redundancia.** Usa como referencias **0,60** de correlación para modelos clásicos y **0,85** para aprendizaje automático. En modelos clásicos, **VIF ≤ 5** se considera aceptable, **5 < VIF ≤ 10** requiere revisión y **VIF > 10** sugiere excluir o transformar.

### 6. Depurar las variables dentro del modelo

- **Regresión logística.** Ajusta un modelo inicial, compara el signo de los coeficientes con el esperado según la codificación y la tasa de evento, e investiga inversiones de signo. Revisa la significancia estadística, con 0,05 como referencia para el valor p. Retira de forma iterativa las variables de aporte insuficiente, vuelve a ajustar y comprueba el efecto en coeficientes, discriminación y estabilidad.
- **Modelos de árboles.** Ordena las variables por Gain y prueba un reentrenamiento con las que sumen el 95% acumulado. Como diagnóstico de concentración, revisa contribuciones individuales superiores al 15% o inferiores al 0,1% de Gain. Estos cortes sirven para examinar la distribución de importancia entre variables. Los topes por tipo de crédito de la sección de umbrales corresponden a la revisión del modelo final. Usa Tree SHAP para revisar dirección, magnitud y consistencia por segmento. Si el comportamiento contradice la relación esperada, investiga el dato, las interacciones y el efecto de excluir la variable.

**Referencias adicionales de importancia.** Si se aplica el filtro por pesos, una contribución inferior al **2%** indica aporte marginal. Los topes de importancia del modelo final son **40%** en crédito grupal y **30%** en crédito individual. La guía de origen contempla hasta **5 puntos porcentuales** adicionales con sustento técnico para el Gain del modelo final.

### 7. Confirmar y documentar la selección

Compara el conjunto reducido con un modelo de referencia usando las mismas muestras y métricas. Evalúa discriminación, calibración, estabilidad por segmento y sensibilidad. Confirma que cada variable final se pueda calcular en operación con las mismas ventanas y reglas. Conserva una tabla con la decisión por variable, la prueba que la respalda, los valores medidos y la justificación de las excepciones. Si modificas la selección después de mirar la muestra fuera de tiempo, reserva un período adicional para verificar el modelo resultante.

## Entrenar y comparar modelos

Construye una referencia sencilla antes de evaluar técnicas más complejas. Para regresión logística, revisa la estabilidad de los coeficientes, el sentido de las relaciones y el efecto de la colinealidad. Para modelos de árboles, examina la importancia de variables, la sensibilidad a los hiperparámetros y el comportamiento en grupos poco representados. Ajusta la complejidad usando datos de desarrollo y valida con muestras reservadas.

Compara modelos con los mismos cortes temporales y criterios. Considera la facilidad de reproducir resultados y de explicar decisiones. Documenta las versiones, los parámetros, las variables finales y las razones para elegir el modelo que pasará a evaluación independiente.

## Medir desempeño, sensibilidad y explicabilidad

Mide la capacidad de discriminación con AUC, Gini u otras métricas pertinentes. Si el modelo genera probabilidades, evalúa su calibración comparando predicciones con tasas observadas. Para elegir un punto de corte, analiza el equilibrio entre precisión, cobertura de casos con evento y volumen de decisiones. Presenta resultados por período y por segmentos relevantes.

Prueba perturbaciones razonables en los insumos, en la mezcla de población y en los puntos de corte. Examina casos individuales y patrones globales. Los coeficientes y las contribuciones de variables pueden ayudar a explicar un modelo clásico. En modelos de árboles, herramientas como SHAP pueden describir contribuciones a una predicción bajo supuestos que deben quedar explícitos. Examina disparidades entre grupos cuando sea pertinente y conforme al marco aplicable.

### Métricas para carteras con pocos incumplimientos

Define incumplimiento como clase positiva y calcula su prevalencia observada π = eventos / registros evaluables. Usa muestras representativas con etiquetas maduras. Si balanceaste las clases para entrenar, calcula las métricas con la prevalencia representativa de evaluación o usa ponderaciones justificadas. Reporta la prevalencia por muestra, porque cambia la línea base de precisión y PR-AUC.

- **PR-AUC o AP.** La línea base sin capacidad de ordenamiento es π. Usa un método fijo de cálculo y nómbralo en el reporte. Si usas el promedio de precisión (AP), reporta AP como el resumen de la curva PR. AP y el área trapezoidal son cálculos diferentes. Reporta AP − π como mejora absoluta sobre la línea base.
- **Precisión y recall.** Precisión = VP/(VP + FP). Recall = VP/(VP + FN). Repórtalos al corte de decisión o para el mismo porcentaje superior de casos ordenados por riesgo. Incluye los conteos de verdaderos positivos, falsos positivos y falsos negativos.
- **Lift acumulado.** Para el porcentaje superior q de casos, lift@q = precisión@q / π. La referencia aleatoria es lift = 1 y recall@q = q en expectativa. Cuando se selecciona exactamente la fracción q de la muestra, recall@q = q × lift@q. Fija una regla reproducible para los empates y reporta la fracción realmente seleccionada.
- **Soporte e incertidumbre.** Reporta número de eventos y, cuando el soporte lo permita, intervalos de confianza. Al comparar dos puntuaciones sobre los mismos casos, usa remuestreo pareado y respeta agrupaciones o dependencias temporales pertinentes. Si hay cero incumplimientos, no evalúes capacidad de detección con estas métricas. Con pocos casos positivos, informa la incertidumbre y reúne más evidencia antes de aplicar un corte estricto.

Las líneas base se derivan de las definiciones y de la prevalencia. Los mínimos de aceptación deben derivarse del problema de decisión, la capacidad de revisión y el costo de los errores. En un caso ilustrativo con prevalencia de 1% y capacidad para revisar el 10%, capturar 30% de los incumplimientos implica lift@10% = 3 y precisión@10% = 3%. Son valores coherentes entre sí para ese escenario.

Fuentes: [Saito y Rehmsmeier](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432), [Davis y Goadrich](https://doi.org/10.1145/1143844.1143874), [SAS](https://support.sas.com/kb/41/683.html) y [definición de AP](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html).

Al reportar PR-AUC, documenta tanto el estimador como el método de intervalo de confianza. Distintos métodos pueden producir estimaciones e intervalos diferentes. [Boyd, Eng y Page (2013)](https://scholars.duke.edu/publication/1393181)

### Evaluar el modelo cuando el incumplimiento es raro

1. Calcula la curva PR y AP o PR-AUC en validación y fuera de tiempo. Usa el mismo método para el modelo candidato y el vigente, sobre las mismas observaciones. Reporta también discriminación global y, si el resultado es una probabilidad de incumplimiento, evalúa la calibración.
2. En validación, fija el punto operativo. Puedes maximizar recall sujeto a un mínimo de precisión y a la capacidad de revisión, o maximizar precisión sujeto a una captura mínima. Estima esos mínimos con el costo de falsos positivos y falsos negativos o con los resultados de la práctica vigente.
3. Congela el corte o la regla de selección por capacidad y compruébala fuera de tiempo. Reporta AP o PR-AUC, lift, precisión, recall, proporción marcada, prevalencia y conteos, por período y segmento cuando haya soporte. Acepta el resultado si la mejora frente a la referencia es relevante y se cumplen los mínimos operativos predefinidos. Documenta la incertidumbre si los eventos son escasos.

El corte se ajusta en datos de validación separados del ajuste del modelo. [Documentación sobre ajuste del umbral](https://scikit-learn.org/stable/modules/classification_threshold.html)

### Cortes para evaluación del desempeño

| Población y alcance | Gini para evento específico | Gini para evento agregado o complejo |
| --- | --- | --- |
| Uso, subpoblación de aplicación | 25–35% | 25–30% |
| Uso, población total | 30–40% | 25–30% |
| Construcción, subpoblación de aplicación | 35–45% | 25–30% |
| Construcción, población total | 40–50% | 30–35% |

En la prueba de sensibilidad con **10 particiones**, el primer cuartil del Gini debe superar el mínimo adoptado para el caso. En carteras con pocos incumplimientos, reporta también AP o PR-AUC, lift, precisión y recall con los criterios del apartado anterior.

## Calibración de PD con pocos incumplimientos

### 1. Definir la PD y la población de referencia

Para una PD a un año, forma cosechas comparables con una fecha de entrada y 12 meses de observación. Por grado y cosecha registra obligados elegibles, incumplimientos, tasa observada y PD esperada. Controla la maduración y el conteo por obligado. Si un obligado aparece en más de una cosecha o las ventanas se solapan, incorpora esa dependencia en la incertidumbre. Define si la PD debe reflejar las condiciones actuales (PIT) o una tendencia de largo plazo, según el uso.

### 2. Estimar la PD de grados con cero o pocos eventos

**Pluto–Tasche.** Ordena los grados de menor a mayor riesgo. Bajo independencia, para cada grado agrupa sus obligados con los de los grados de peor calidad considerados y usa el conteo agregado de incumplimientos. Invierte la cola inferior binomial para obtener una cota superior unilateral: encuentra la PD común de referencia para la que la probabilidad de observar ese número de eventos o menos es igual a 1 menos el nivel de confianza. El método usa el orden de riesgo para construir cotas prudentes por grado. Documenta la agrupación, la confianza y la sensibilidad a la correlación.

Para ilustrar un conjunto de **1 000 obligados sin incumplimientos** e independencia, una cota superior unilateral del **95%** se obtiene con 1 − 0,05^(1/1000), aproximadamente **0,30%**. La cota describe la incertidumbre que permite esa muestra. El 95% es un nivel ilustrativo, y el resultado depende del conjunto agrupado.

**Actualización bayesiana Beta.** Con d incumplimientos en n obligados y un prior Beta(a, b), la posterior bajo independencia es Beta(a + d, b + n − d). La media posterior es (a + d)/(a + b + n). Reporta también un intervalo creíble o un cuantil superior, según el uso. Documenta el origen de la media previa a/(a + b) y la fuerza previa a + b. Puedes partir de historia comparable, datos externos justificados o un modelo jerárquico que comparta información entre grados. Prueba cuánto cambia la PD con otros priors y evita reutilizar las mismas observaciones para construir el prior y actualizarlo sin ajustar el método. [Pluto y Tasche, PD en carteras con pocos incumplimientos](https://arxiv.org/abs/cond-mat/0411699) · [Tasche, estimación bayesiana de PD](https://arxiv.org/abs/1112.5550)

### 3. Estimar la tendencia central y el margen de conservadurismo

Calcula tasas anuales comparables con ventanas de un año. Usa una serie que represente períodos favorables y adversos, incluidas las cosechas de crisis pertinentes. Verifica cambios de originación, composición, definición de incumplimiento y maduración. Documenta el esquema de ponderación de años y su sensibilidad. Si faltan años adversos o una crisis está sobrerrepresentada, contrasta la serie con evidencia comparable y justifica el ajuste para representar el ciclo. Para una PD PIT, conserva una referencia coherente con el período que se pretende predecir.

Distingue la mejor estimación de la PD del **margen de conservadurismo** por deficiencias de datos o método y por incertidumbre de estimación. Cuantifica cada componente, documenta su origen y evita volver a cargar el mismo riesgo si ya quedó cubierto por un ajuste o una cota conservadora. Muestra la PD antes y después del margen y revisa el efecto por grado. Las guías IRB citadas sirven de referencia metodológica. [EBA, guía de estimación de PD y LGD en el marco IRB](https://eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd?version=2018) · [Comité de Basilea, validación de sistemas de calificación](https://www.bis.org/publications/studies-validation-internal-rating-systems-revised)

### 4. Construir una escala maestra monotónica

Ordena el puntaje de menor a mayor riesgo y define grados con cortes reproducibles. Usa evidencia de cada grado para decidir si conviene agrupar vecinos con poco soporte o aplicar una calibración monotónica, como regresión isotónica ponderada. Registra por grado el intervalo de puntaje, el número de obligados, los eventos, la tasa observada, la PD base, el margen y la PD final.

Contrasta la PD media de la escala con la tendencia central objetivo usando ponderaciones de la población de referencia. Cuando proceda, ajusta un desplazamiento común en escala logit hasta alcanzar la media objetivo. El desplazamiento conserva el orden. Comprueba la monotonía después de añadir el margen y documenta por separado cualquier diferencia entre la media de la mejor estimación y la media final conservadora. Verifica el resultado por cosecha y fuera de tiempo. [Pluto y Tasche, PD en carteras con pocos incumplimientos](https://arxiv.org/abs/cond-mat/0411699) · [EBA, guía de estimación de PD y LGD en el marco IRB](https://eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd?version=2018)

### 5. Recalibrar después de balancear clases

Para una regresión logística ajustada con muestreo que depende solo de la clase y con un cambio de prevalencia entre muestra y población, corrige el intercepto sumando **logit(prevalencia objetivo) − logit(prevalencia de entrenamiento)**. Por ejemplo, pasar de una muestra balanceada al 50% a una población de 0,5% implica un desplazamiento de aproximadamente **−5,293**. Verifica la calibración de las probabilidades en datos representativos.

Con SMOTE, ponderaciones complejas, selección que también depende de predictores o cambios de composición, usa una muestra representativa separada para ajustar y verificar la calibración. Puedes empezar por un ajuste de intercepto con el puntaje como término fijo. Si hay soporte suficiente, estima también una pendiente de calibración. Evalúa intercepto, pendiente y observados/esperados fuera de tiempo. [King y Zeng, regresión logística con eventos raros](https://dash.harvard.edu/entities/publication/73120378-8901-6bd4-e053-0100007fdf3b)

## Traducir el puntaje a una decisión

Define cómo se utilizarán las probabilidades o los puntajes. Si existen tramos de riesgo, comprueba que el riesgo observado siga el orden esperado y que cada grupo permita una acción concreta. Evalúa el impacto estimado en aprobaciones, mora o pérdidas y describe los supuestos de la simulación.

Determina quién puede aplicar una excepción y cómo se registrará. Si cambian la población, el producto o la decisión, revisa si la evidencia original cubre el uso propuesto. Define indicadores que permitan detectar rápidamente un deterioro tras la implementación.

## Preparar la documentación de revisión

Entrega una descripción del objetivo, la población, las muestras y la variable objetivo. Incluye el diccionario de datos, la lógica de transformación, los resultados de evaluación y las limitaciones conocidas. Conserva código versionado o una especificación reproducible, junto con las instrucciones para reconstruir los resultados. Documenta también las dependencias, los supuestos y las pruebas de sensibilidad.

Si el modelo forma parte de un sistema de IA, registra su finalidad, las personas afectadas, la supervisión prevista y los riesgos relevantes. El nivel de documentación y control debe guardar proporción con el alcance y el impacto del sistema.

## Certificar la implementación

Compara la ejecución de referencia con la operativa usando los mismos registros. Verifica las variables de entrada, las transformaciones, el puntaje o la probabilidad y la clasificación final. Prueba casos límite y documenta qué diferencias son aceptables para la decisión. Investiga las discrepancias y conserva evidencia de las correcciones.

Establece reglas de precisión, fechas, unidades, nombres de campos y control de versiones. Registra los cambios de código, la versión desplegada y la evidencia de pruebas. Verifica la integridad de las transferencias entre entornos y define controles para datos faltantes, duplicados, errores de formato y fallas de ejecución.

### Umbrales de certificación y precisión numérica

La certificación toma **99% de coincidencia** como referencia mínima entre la ejecución de referencia y la operativa. Por debajo de ese valor, documenta la causa, el impacto y la corrección. Para reproducir el cálculo, la referencia de precisión numérica es de **hasta 7 decimales** para variables, transformaciones y salidas relevantes.

## Autorizar el uso y monitorear

La revisión previa al uso debe considerar la evidencia metodológica, la calidad de la implementación y las condiciones de operación. Define un plan de contingencia para fallas de datos o de ejecución y un procedimiento para recuperar la última versión funcional.

Organiza el calendario por entregables, desde la definición del problema hasta las pruebas de operación. Estima tiempos según la disponibilidad de datos, la complejidad de las pruebas y la necesidad de revisión independiente. Una vez operativo, monitorea la calidad de datos, la estabilidad de la población, el desempeño y el impacto de las decisiones. Registra los cambios y establece cuándo investigar, recalibrar, rediseñar o retirar el modelo.

### Umbrales de estabilidad en operación

| PSI de la probabilidad de incumplimiento o de los segmentos | Acción |
| --- | --- |
| Hasta 0,10 | Registrar en el seguimiento habitual. |
| Más de 0,10 y hasta 0,20 | Investigar los cambios principales y reforzar el seguimiento. |
| Más de 0,20 | Analizar población y variables, y evaluar si hace falta ajustar, resegmentar o recalibrar. |

Para **faltantes en producción**, define una línea base por variable o familia con datos de desarrollo o certificación. Investiga los aumentos bruscos y los excesos sobre su límite de alerta.

## Umbrales de referencia para selección y desempeño

Estos valores son ejemplos metodológicos. Su aplicación depende del producto, del tamaño de las muestras y del costo de los errores de decisión.

- **Completitud y variabilidad.** En una revisión preliminar de datos, un criterio de referencia es menos del 85% de valores faltantes. En el filtro univariado, más del 75% de faltantes es motivo de exclusión. También se descartan variables con desviación estándar de cero, con una categoría que concentra más del 85% de las observaciones o, para variables numéricas, con un coeficiente de variación inferior al 4%.
- **Estabilidad univariada.** Un PSI de hasta 0,10 indica estabilidad aceptable. Entre más de 0,10 y hasta 0,20 se revisa el aporte de la variable. Un PSI superior a 0,20 es criterio de exclusión, salvo justificación técnica. Para calcularlo, usa grupos comparables entre ambas muestras y suma (p − q) × ln(p/q) por grupo, donde p y q son sus proporciones respectivas.
- **Selección bivariada.** Considerando entrenamiento, prueba y una muestra posterior en el tiempo, los cortes de descarte ilustrativos son IV mínimo ≤ 2%, Gini mínimo ≤ 3% o coeficiente de variación del Gini ≥ 80%. El cuarto corte figura en el procedimiento bivariado con su denominación original y requiere aclaración antes de aplicarse.
- **Redundancia.** Los límites de referencia para correlación son 0,60 en modelos clásicos y 0,85 en aprendizaje automático. En el diagnóstico de colinealidad, un VIF de hasta 5 se considera aceptable, más de 5 y hasta 10 amerita revisión y más de 10 sugiere transformar o excluir la variable.
- **Importancia en modelos de árboles.** Puede probarse un modelo reentrenado con las variables que acumulan el 95% del Gain. Como referencia para limitar la dependencia de una sola variable, se usan topes de Gain relativo de 40% en crédito grupal y 30% en crédito individual, con hasta 5 puntos porcentuales adicionales cuando haya justificación técnica.
- **Casos indeterminados.** Una proporción de hasta 15% es un ejemplo orientativo para revisar la representatividad. Ajusta este valor a la definición del evento y al período de observación.

### Rangos ilustrativos de Gini

| Población evaluada | Alcance de la evaluación | Evento específico | Evento agregado o complejo |
| --- | --- | --- | --- |
| De uso | Subpoblación que cumple la pauta de aplicación | 25–35% | 25–30% |
| De uso | Población total | 30–40% | 25–30% |
| De construcción | Subpoblación que cumple la pauta de aplicación | 35–45% | 25–30% |
| De construcción | Población total | 40–50% | 30–35% |

En una prueba de sensibilidad con validación cruzada de 10 particiones, puede exigirse que el primer cuartil del Gini supere el mínimo adoptado para el caso de uso. Para clasificación, la precisión es VP/(VP + FP), la exhaustividad (*recall*) es VP/(VP + FN) y F1 es la media armónica de ambas. Define la clase positiva según la decisión antes de interpretar estas métricas.

### Coincidencia en la certificación

Un ejemplo de aceptación es exigir al menos 99% de coincidencia entre la ejecución de referencia y la operativa. Si la coincidencia cae por debajo del 99%, investiga la causa, cuantifica el efecto sobre el puntaje o la decisión y documenta la corrección. Este valor corresponde a la certificación de la implementación.

## Referencias externas

- Superintendencia de Banca, Seguros y AFP del Perú, marco de gestión del riesgo de modelo y del riesgo de crédito.
- Naeem Siddiqi, *Credit Risk Scorecards: Developing and Implementing Intelligent Credit Scoring*.
- Max Kuhn y Kjell Johnson, *Applied Predictive Modeling*.
- DAMA International, *DAMA-DMBOK: Data Management Body of Knowledge*.
- Saito y Rehmsmeier (2015), curva precisión–recall y prevalencia de la clase positiva en datos desbalanceados. [Artículo en PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432)
- Davis y Goadrich (2006), relación entre ROC y PR y tratamiento de la interpolación. [Artículo de ICML](https://doi.org/10.1145/1143844.1143874)
- SAS, definición de lift y captura acumulada para resultados binarios. [Documentación de ganancias y lift](https://support.sas.com/kb/41/683.html)
- scikit-learn, definición de AP y ajuste del umbral de clasificación en datos separados. [Average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html) · [Ajuste del umbral](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [Boyd, Eng y Page (2013)](https://scholars.duke.edu/publication/1393181). Estimación puntual e intervalos de confianza para el área bajo la curva precisión–recall.
- [Pluto y Tasche, PD en carteras con pocos incumplimientos](https://arxiv.org/abs/cond-mat/0411699).
- [Tasche, estimación bayesiana de PD](https://arxiv.org/abs/1112.5550).
- [EBA, guía de estimación de PD y LGD en el marco IRB](https://eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd?version=2018).
- [Brown, Cai y DasGupta, intervalos binomiales](https://doi.org/10.1214/ss/1009213286).
- [Riley y coautores, tamaño de muestra para modelos de predicción](https://doi.org/10.1136/bmj.m441).
- [King y Zeng, regresión logística con eventos raros](https://dash.harvard.edu/entities/publication/73120378-8901-6bd4-e053-0100007fdf3b).
