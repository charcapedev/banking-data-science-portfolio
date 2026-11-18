# Bitácora de uso de IA

**Herramienta:** Claude Code en VS Code (modelo Opus 5.5). La usé para analizar alternativas y revisar el notebook. Las decisiones finales y la ejecución del análisis son mías.

## 1. Cómo particionar los datos

- **Qué pedí:** comparar train-test estratificado, validación cruzada, *out-of-time* y ventanas mensuales apiladas, con ventajas, riesgos y lo que no se puede validar con estos datos.
- **Qué respondió:** el impago existe para un solo mes, así que cualquier partición temporal obliga a inventar un objetivo sustituto que ya no es el impago de octubre. Recomendó train-test estratificado y validación cruzada en train, y sugirió una prueba temporal secundaria con ese objetivo sustituto.
- **Qué hice:**
  - *Acepté* la división estratificada 70/30 (la prueba se usa una sola vez) y la validación cruzada de 5 pliegues para todas las decisiones.
  - *Descarté* la prueba temporal, porque cambia lo que se predice y podía presentarse como si fuera una validación fuera de tiempo real.
  - La falta de prueba fuera de tiempo quedó escrita como limitación.

## 2. Si el modelo aporta más que una regla de atraso

- **Qué pedí:** pruebas para saber si el modelo vale la pena frente a reducir la línea a quien se atrasó, dado que el atraso concentra cerca del 50 % de la importancia.
- **Qué respondió:**
  - propuso comparar contra la regla con intervalos pareados;
  - propuso medir el Gini dentro de los clientes sin atraso;
  - propuso medir la concentración con SHAP y no con Gain, que la exagera;
  - recomendó no repartir el atraso en variables correlacionadas solo para bajar el porcentaje;
  - si el modelo no ordenaba a los clientes sin atraso, sugirió segmentar.
- **Qué hice:**
  - *Acepté* las pruebas y fijé de antemano el criterio para aprobar el modelo: mejorar el Gini y el costo con intervalos que excluyan el cero.
  - *Complementé* el análisis comparando Gain, Cover, Frequency y SHAP.
  - El modelo supera a la regla (Gini de 0.527 frente a 0.437 en prueba) y ordena a los clientes sin atraso (Gini de 0.278), así que *no fue necesario segmentar*.
  - La concentración (47.7 % del SHAP) quedó como excepción documentada y como variable a monitorear.

## 3. Estrategia de reducción de líneas

- **Qué pedí:** propuestas por segmentos, con ventajas, desventajas y recomendaciones, a partir del costo de cada alternativa.
- **Qué respondió:**
  - aclaró que, con un modelo calibrado y costos fijos, ningún corte por segmento puede costar menos que el corte único de 1/6;
  - propuso bandas de riesgo, cortes por exposición o por uso de la línea, y acciones graduadas como congelar la línea o recortar solo la parte no usada.
- **Qué hice:**
  - *Descarté* la segmentación y mantuve un solo corte: reducir si la PD supera 16.7 %.
  - Las razones: la acción es binaria (reducir o no) y no hay datos de exposición, severidad ni rentabilidad para justificar costos distintos por segmento.
  - Las propuestas que dependen de esos datos, y un piloto con grupo de control, quedaron como próximos pasos.
