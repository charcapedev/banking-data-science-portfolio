# Portafolio de proyectos de ciencia de datos e IA para banca

Proyectos aplicados a decisiones típicas de la banca: a quién contactar, cómo medir el efecto de una acción, cómo segmentar clientes, cómo optimizar operaciones, cómo medir el riesgo de crédito y cómo consultar guías con IA generativa.

Cada proyecto parte de una pregunta de negocio y termina en una recomendación, con sus supuestos y limitaciones a la vista.

## Proyectos

| Proyecto | Pregunta de negocio | Enfoque | Hallazgo |
|---|---|---|---|
| [Propensión a contratar un depósito](deposit-subscription-propensity/README.md) | ¿A quién llamar primero con una capacidad limitada? | Clasificación, validación temporal y AutoML | Un modelo de 2 variables logra 75.6 % de contratación con un cupo de 10 %, frente a 52.1 % al azar |
| [Medición del impacto de campañas con experimentos A/B](ad-conversion-ab-test/README.md) | ¿Una campaña aumenta realmente la conversión? | Inferencia, auditoría del experimento y decisión económica | +0.77 pp de conversión, rentable si cuesta menos de unos 385 por 1,000 usuarios con un margen ilustrativo |
| [Segmentación de tarjetas de crédito](credit-card-customer-segmentation/README.md) | ¿Qué grupos de clientes existen y cómo atenderlos? | Clustering, estabilidad y reglas operativas | 4 segmentos estables, que 4 reglas simples reproducen en 96.9 % de los casos |
| [Reposición de efectivo en cajeros](atm-cash-replenishment-optimization/README.md) | ¿Cuánto efectivo cargar en cada cajero? | Optimización entera y simulación con datos sintéticos | Una regla de nivel fijo ahorra 14.4 % frente al reparto uniforme y empata con la optimización |
| [PD hipotecaria de bajo default](mortgage-low-default-pd-model/README.md) | ¿Qué PD asignar cuando casi nadie incumple, sin subestimar un año malo? | Scorecard con WoE, calibración al ciclo, Pluto–Tasche, Vasicek y SHAP | Una logística de 11 variables logra un Gini de 0.776 fuera de tiempo; calibrada al ciclo, la PD media pasa de 0.56 % a 1.28 % |
| [Asistente de consulta de guías de riesgo](credit-risk-model-review-assistant/README.md) | ¿Cómo consultar las guías de modelos de riesgo sin que el asistente invente criterios? | RAG híbrido, guardrails, verificación de fidelidad y control de costos | Exactitud de 0.913 y fidelidad de 0.982, con 12 de 12 ataques resistidos, a $0.00125 por consulta |


## Criterios de trabajo

- **Primero la decisión de negocio,** y después el modelo.
- **Validación acorde al uso real,** sin información que no existiría al momento de decidir.
- **Comparación contra alternativas simples** antes de aceptar más complejidad.
- **Resultados reproducibles,** con semillas y versiones de librerías definidas.
- **Limitaciones explícitas,** incluidas las que debilitan el resultado.

## Organización del repositorio

```
banking-data-science-portfolio/
├── deposit-subscription-propensity/       Propensión a contratar un depósito
├── ad-conversion-ab-test/                 Medición del impacto de campañas
├── credit-card-customer-segmentation/     Segmentación de clientes
├── atm-cash-replenishment-optimization/   Reposición de efectivo en cajeros
├── mortgage-low-default-pd-model/         PD hipotecaria de bajo default
└── credit-risk-model-review-assistant/    Asistente RAG de consulta de guías
```

Cada proyecto tiene sus propias dependencias. Los datos y los entornos virtuales no se versionan, y las instrucciones para obtener los datos están en el README de cada proyecto.
