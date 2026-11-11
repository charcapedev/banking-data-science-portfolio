# Guía de validación de modelos de riesgo

Guía técnica para equipos que desarrollan, revisan o utilizan modelos de riesgo. Describe cómo evaluar si un modelo es adecuado para la decisión que apoya, si sus resultados se pueden reproducir y si conserva su utilidad en el tiempo.

## Alcance e independencia

La validación comienza por identificar la decisión que apoya el modelo, la población a la que se aplica y las consecuencias de un error. El alcance abarca la metodología, los datos, la implementación y el uso. En un modelo de crédito, por ejemplo, conviene revisar tanto la capacidad de ordenar solicitudes por riesgo como el efecto de usar el puntaje para aprobar operaciones.

La evaluación debe quedar a cargo de personas con independencia funcional respecto del desarrollo y del uso. El equipo desarrollador explica sus decisiones y entrega evidencia reproducible. El equipo validador realiza sus propias comprobaciones y documenta su juicio técnico. Quienes autorizan el uso deciden cómo tratar el riesgo residual a partir de ese juicio. La profundidad de la revisión aumenta con la importancia del modelo, su complejidad y el impacto de una falla.

## Cuándo validar

La validación inicial examina el modelo antes de incorporarlo a una decisión operativa o de ampliar sustancialmente su alcance. Debe cubrir la evidencia de desarrollo y la equivalencia entre lo diseñado y lo implementado.

La validación periódica reevalúa el desempeño con datos recientes y comprueba si siguen siendo razonables los supuestos, las restricciones y los usos aprobados. Su frecuencia puede ajustarse según la criticidad del modelo y la evidencia del seguimiento.

Una revisión extraordinaria puede justificarse ante un deterioro persistente, un cambio relevante en la población, una sustitución de fuentes, una modificación del cálculo o una ampliación a otro producto. El evento que motiva la revisión orienta el alcance y la urgencia.

### Frecuencia de revisión por criticidad

| Nivel de criticidad | Intervalo máximo de referencia | Duración inicial y periódica de referencia |
| --- | --- | --- |
| Alta | 12 meses | 26 y 19 días hábiles |
| Media | 18 meses | 23 y 16 días hábiles |
| Menor | 24 meses | 19 y 13 días hábiles |

Cuenta el intervalo desde la emisión de la evaluación anterior. Los plazos de ejecución son estimaciones para planificar el trabajo.

## Plan de trabajo y evidencia

Antes de ejecutar pruebas, acuerda el propósito de la revisión, el período analizado, los entregables y la versión exacta del modelo. Reúne la descripción metodológica, el diccionario de datos, las reglas de población, las muestras, el código o una especificación equivalente, los resultados de desarrollo y la documentación de implementación. Para modelos operativos, agrega reportes de seguimiento y un historial de cambios.

Vincula cada prueba con el dato de entrada, la versión del código y el resultado obtenido. Cuando falte una evidencia, documenta qué conclusión queda limitada y qué comprobación permitiría resolverla. Una demostración de la ejecución ayuda a entender el proceso. La reproducción independiente permite verificarlo.

## Datos y población

Reconstruye la población a partir de los criterios de elegibilidad. Comprueba los filtros, las exclusiones, la unidad de observación y el momento en que cada dato estuvo disponible. Busca duplicados, claves sin correspondencia, valores ausentes, cambios de formato y discrepancias con la fuente. Para variables derivadas, verifica el cálculo con casos normales y casos límite.

Compara las muestras de desarrollo, prueba y operación por período y segmento. Si cambia la distribución, investiga si la causa es un cambio real en la población, una regla de selección diferente o un problema de captura. En crédito, verifica además que la etiqueta de incumplimiento utilice un horizonte definido y que las cuentas hayan tenido tiempo suficiente para observar el evento.

## Procedimiento detallado para validar la calidad de datos

1. **Reproducir la extracción.** Fija la versión de las fuentes, las fechas y la unidad de análisis. Reconstruye la población elegible y registra conteos antes y después de cada filtro. Compara el volumen y las claves con la base entregada. Calcula por separado cobertura del universo y coincidencia de registros.
2. **Revisar integridad y completitud.** Comprueba unicidad, llaves sin correspondencia y multiplicación de filas después de las uniones. Mide faltantes por variable, período y segmento. Separa ausencias explicadas por el diseño de faltantes inesperados en variables finalistas o en predicciones.
3. **Replicar variables y resultados.** Compara las variables finalistas registro a registro con la salida operativa. Usa la misma clave, fecha y precisión. Revisa casos con faltantes, valores extremos y valores cercanos a puntos de corte. Distingue errores de datos, diferencias de cálculo y cambios de precisión.
4. **Contrastar la estabilidad.** Usa cortes comparables para contrastar la población, las variables y el puntaje entre desarrollo y operación. Calcula el PSI del puntaje por deciles y localiza los grupos con mayor cambio. Investiga qué explica la diferencia y comprueba si altera el desempeño o la decisión.
5. **Documentar y repetir.** Por prueba, registra fuente, fecha, población, fórmula, umbral, resultado, hallazgo y evidencia. Solicita una corrección con un criterio de aceptación y vuelve a ejecutar la prueba para confirmar el cierre.

### Cortes para validar la calidad de datos

| Control | Umbral y acción |
| --- | --- |
| Cobertura de la reconstrucción | Al menos 99% de los registros de la base operativa. En coincidencia de registros, 100% es óptimo, 97–99% requiere sustento y menos de 97% exige escalar y corregir. |
| Faltantes en variables finalistas | Máximo de referencia de 5% fuera de las predicciones clave. La banda óptima es 0–3% según el control. En el esquema de escalamiento, superar el umbral definido en 3–5% requiere revisión y superarlo en más de 5% se considera crítico. |
| Faltantes en predicciones clave | 0%. Cualquier faltante en una salida clave, como la probabilidad de incumplimiento, se considera crítico. |
| Coincidencia de variables finales | 97% o más es óptimo, de 95% a menos de 97% requiere revisión y menos de 95% exige corregir. Como referencia, compara 2–3 meses en procesos mensuales o 2–3 días en procesos diarios. |
| Unicidad | Cero duplicados es óptimo. Uno o más duplicados indebidos requieren corrección. |

## Diseño y desempeño

Examina si la técnica responde al objetivo y si los supuestos se sostienen con evidencia. Revisa cómo se seleccionaron y transformaron las variables, cómo se ajustaron los parámetros y qué alternativas se evaluaron. Comprueba la coherencia económica de las relaciones y analiza si el resultado depende excesivamente de una variable o un segmento.

En modelos binarios, el AUC o el Gini permiten evaluar discriminación. En modelos que estiman probabilidades, compara las predicciones con las tasas observadas para evaluar calibración. Calcula los indicadores por período y por segmento cuando haya datos suficientes. Incluye una prueba con datos posteriores a los usados para desarrollar el modelo y describe las limitaciones de los grupos con pocos eventos.

### Validación independiente en carteras con pocos incumplimientos

Reproduce el AP o PR-AUC y confirma su método de cálculo. Verifica que incumplimiento sea la clase positiva, que la prevalencia corresponda a la población de evaluación y que todas las etiquetas tengan la misma ventana de maduración. Recalcula lift, precisión y recall para el mismo corte operativo y confirma el volumen seleccionado y los conteos. La referencia sin capacidad de ordenamiento es AP igual a la prevalencia y lift igual a 1.

Comprueba que los mínimos de precisión y recall se hayan fijado con base en el costo de los errores o la capacidad de revisión, que el corte se haya ajustado en validación y que se haya aplicado sin ajustes a la muestra fuera de tiempo. Revisa incertidumbre, estabilidad y calibración. Para selección bivariada, verifica que los puntajes de una variable se hayan estimado sin acceder a las etiquetas de la muestra usada para evaluarlos.

[Saito y Rehmsmeier](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) · [SAS](https://support.sas.com/kb/41/683.html) · [Ajuste del umbral](https://scikit-learn.org/stable/modules/classification_threshold.html)

Cuando los incumplimientos observados son demasiado escasos para una comparación histórica informativa, complementa la validación con comparaciones frente a referencias pertinentes y revisión cualitativa. Evalúa por separado la discriminación y la calibración de la probabilidad de incumplimiento. [Comité de Basilea, validación de carteras con pocos incumplimientos (2005)](https://www.bis.org/publications/200509-practices-validation-low-default-portfolios-basel-ii-framework) · [Guía consolidada de Basilea sobre riesgo de crédito](https://www.bis.org/committees/bcbs/basel-consolidated-guidelines/module/cri/30) · [Comité de Basilea, estudios sobre validación de sistemas de calificación](https://www.bis.org/publications/studies-validation-internal-rating-systems-revised)

## Validación de PD por grado en carteras con pocos incumplimientos

### 1. Preparar el contraste

Por grado y cosecha, fija la fecha de corte y la ventana de un año. Registra obligados, incumplimientos observados, PD media y suma de PD individuales como conteo esperado. Reporta observados/esperados cuando el esperado sea positivo. Comprueba el orden de la escala y contrasta por separado la mejor estimación y la PD con margen, según su propósito.

### 2. Aplicar la prueba binomial y el intervalo de Jeffreys

Si los obligados son independientes y tienen una PD común dentro del grado, compara el conteo observado con una binomial de n obligados y la PD asignada. Una cola superior permite evaluar subestimación del riesgo. Si las PD individuales difieren de forma material, bajo independencia usa una distribución Poisson-binomial para el conteo. Define el nivel de prueba y cómo tratar comparaciones múltiples entre grados y cosechas. Un resultado sin señal puede reflejar baja potencia.

Como contraste descriptivo, calcula un intervalo creíble de Jeffreys usando los cuantiles de Beta(d + 0,5, n − d + 0,5). Especifica si es central o unilateral y cómo tratas los extremos d = 0 y d = n. El intervalo describe la incertidumbre sobre la tasa del grado. Compáralo con la PD asignada junto con los conteos y el resultado de la prueba. [Brown, Cai y DasGupta, intervalos binomiales](https://doi.org/10.1214/ss/1009213286) · [Comité de Basilea, validación de sistemas de calificación](https://www.bis.org/publications/studies-validation-internal-rating-systems-revised)

### 3. Incorporar dependencia con un modelo de un factor

Si los incumplimientos comparten un factor sistemático, usa como contraste un modelo de tipo Vasicek. Condiciona la PD de cada obligado al factor común y a la correlación de activos, calcula la distribución del conteo condicional e integra o simula sobre el factor. Usa la distribución predictiva resultante para obtener bandas de conteo o probabilidades de cola. Justifica la correlación y prueba valores alternativos. Si hay cosechas solapadas o varios registros del mismo obligado, incorpora esa estructura o usa un remuestreo coherente con ella. [Pluto y Tasche, PD en carteras con pocos incumplimientos](https://arxiv.org/abs/cond-mat/0411699) · [Gordy, modelo de riesgo de un factor](https://www.federalreserve.gov/econres/feds/a-risk-factor-model-foundation-for-ratings-based-bank-capital-rules.htm)

### 4. Documentar el diagnóstico y las acciones

Incluye volumen, eventos, observados y esperados, intervalos, supuestos y señales persistentes. Contrasta cosechas de crisis, estabilidad de la escala, tendencia central y origen del margen. Verifica que el balanceo de clases se haya corregido y que el nivel de PD se haya evaluado en la población objetivo. Si la evidencia por grado es escasa, revisa grados adyacentes agrupados y referencias comparables, conservando el detalle original. Decide si hace falta ampliar historia, agrupar grados, recalibrar o ajustar el margen.

## Estabilidad, sensibilidad y uso

Compara las distribuciones de entradas, puntajes y decisiones a lo largo del tiempo. El índice de estabilidad poblacional (PSI) resume cambios entre dos distribuciones agrupadas. Interprétalo junto con el tamaño de la muestra, los segmentos utilizados y la evolución del desempeño. Una señal de deriva requiere examinar su origen y sus consecuencias sobre las decisiones.

Realiza pruebas de sensibilidad con cambios plausibles en las variables o el entorno. Registra qué casos producen resultados inesperados y si existe una forma de detectarlos en operación. Verifica que cada uso observado esté cubierto por la evidencia disponible y evalúa los efectos de las excepciones y las intervenciones manuales.

### Umbrales de estabilidad del puntaje

Agrupa el puntaje en deciles y compara la base de modelamiento con la base de implementación. **PSI < 0,10** indica estabilidad. De **0,10 a 0,25**, investiga la desviación y refuerza el seguimiento. Un **PSI > 0,25** amerita escalar el hallazgo.

## Verificación de la implementación

Ejecuta el modelo de referencia y la versión operativa sobre una misma población de prueba. Compara los insumos, las transformaciones intermedias y el resultado final. Incluye casos con datos ausentes, valores extremos y puntajes cercanos a puntos de corte. Las diferencias pueden originarse en redondeos, fechas, uniones de datos, versiones de librerías o reglas de negocio.

Comprueba que existan registros de ejecución, controles de calidad, versiones identificables y un mecanismo para recuperar una versión funcional ante una falla. Define los criterios de aceptación según la precisión necesaria para la decisión. Una diferencia pequeña en el puntaje puede importar si cambia la clasificación final.

## Hallazgos, decisión y seguimiento

Un hallazgo debe describir la evidencia, el impacto y la medida correctiva. Clasifica su gravedad según el efecto sobre el cálculo, la decisión, el cumplimiento y la capacidad de detectar el problema. Define quién verificará la corrección, cuál es el plazo y qué prueba acreditará el cierre.

La conclusión puede respaldar el uso, respaldarlo con condiciones o indicar que la evidencia disponible es insuficiente. Si se acepta una condición temporal, especifica los límites de uso y los indicadores que activarán una revisión. El seguimiento debe registrar qué acciones se completaron, qué riesgo sigue abierto y cuándo corresponde reevaluarlo.

### Cortes ilustrativos para calificar hallazgos

| Resultado | Referencia para la calificación |
| --- | --- |
| Satisfactorio | Cero hallazgos críticos o moderados. La matriz indica hasta 3 bajos y la descripción narrativa indica hasta 4. |
| Aceptable | Cero críticos y hasta 3 moderados. La descripción permite hasta 7 entre moderados y bajos. La matriz limita los bajos a 4. |
| Regular | Hasta 3 críticos o más de 3 moderados. La descripción permite hasta 8 entre críticos y moderados. La matriz indica hasta 5 moderados. |
| Deficiente | Más de 3 hallazgos críticos. |

Resuelve las diferencias entre la matriz y la descripción antes de automatizar una nota. Si calificas metodología e implementación por separado, la calificación final toma el resultado menos favorable.

## Documentación y revisión de la metodología

Conserva suficiente información para reconstruir qué se probó, con qué versión y cómo se llegó a la conclusión. Revisa la metodología de validación cuando cambien los modelos, las herramientas, las fuentes o el marco aplicable. Registra qué cambió y desde qué fecha se usa la metodología revisada.

**Frecuencia de revisión de la metodología.** Como referencia, revísala al menos **cada 2 años** y adelanta la revisión si un cambio relevante lo requiere.

## Umbrales de referencia para pruebas de validación

Los siguientes valores ilustran criterios para pruebas distintas. Para aplicarlos, define la población, el denominador y el período de comparación.

| Prueba | Criterios de referencia |
| --- | --- |
| Cobertura del universo reconstruido | La meta de cobertura es al menos 99% de los registros frente a la base operativa. Si se mide coincidencia de registros, 100% es óptimo, el tramo de 97% a 99% requiere documentar las diferencias y por debajo de 97% corresponde escalar y corregir. |
| Precisión de variables en la tabla final | En una comparación registro a registro, 97% o más se considera óptimo, de 95% a menos de 97% requiere revisión y menos de 95% exige corregir la lógica. |
| Completitud de variables finalistas | La tolerancia de referencia es de 0% a 3% según la variable. Un exceso de entre 3% y 5% sobre el umbral definido requiere revisión. Un exceso mayor al 5%, o cualquier valor faltante en predicciones clave, se trata como crítico. |
| Unicidad | Se esperan cero duplicados respecto a la clave definida. Uno o más registros duplicados requieren corrección. |
| Estabilidad del puntaje | Al comparar puntajes agrupados por deciles, un PSI inferior a 0,10 indica estabilidad, de 0,10 a 0,25 amerita investigar la desviación y por encima de 0,25 exige escalar el hallazgo. |

## Referencias externas

- Marco de la Superintendencia de Banca, Seguros y AFP del Perú sobre gestión del riesgo de modelo, riesgo de crédito y riesgo de mercado.
- DAMA International, *DAMA-DMBOK: Data Management Body of Knowledge*.
- Saito y Rehmsmeier (2015), curva precisión–recall y prevalencia de la clase positiva en datos desbalanceados. [Artículo en PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432)
- Davis y Goadrich (2006), relación entre ROC y PR y tratamiento de la interpolación. [Artículo de ICML](https://doi.org/10.1145/1143844.1143874)
- SAS, definición de lift y captura acumulada para resultados binarios. [Documentación de ganancias y lift](https://support.sas.com/kb/41/683.html)
- scikit-learn, definición de AP y ajuste del umbral de clasificación en datos separados. [Average precision](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html) · [Ajuste del umbral](https://scikit-learn.org/stable/modules/classification_threshold.html)
- [Comité de Basilea, validación de carteras con pocos incumplimientos (2005)](https://www.bis.org/publications/200509-practices-validation-low-default-portfolios-basel-ii-framework). Contexto prudencial para carteras con historial limitado.
- [Comité de Basilea, estudios sobre validación de sistemas de calificación](https://www.bis.org/publications/studies-validation-internal-rating-systems-revised). Métodos para evaluar discriminación y calibración.
- [Guía consolidada de Basilea sobre riesgo de crédito](https://www.bis.org/committees/bcbs/basel-consolidated-guidelines/module/cri/30). Comparación con referencias cuando el historial limita la validación.
- [Pluto y Tasche, PD en carteras con pocos incumplimientos](https://arxiv.org/abs/cond-mat/0411699).
- [Brown, Cai y DasGupta, intervalos binomiales](https://doi.org/10.1214/ss/1009213286).
- [Gordy, modelo de riesgo de un factor](https://www.federalreserve.gov/econres/feds/a-risk-factor-model-foundation-for-ratings-based-bank-capital-rules.htm).
- [EBA, guía de estimación de PD y LGD en el marco IRB](https://eba.europa.eu/activities/single-rulebook/regulatory-activities/model-validation/guidelines-pd-estimation-lgd?version=2018).
