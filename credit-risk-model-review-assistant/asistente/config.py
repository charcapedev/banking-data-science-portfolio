"""Configuración del asistente: modelos, precios, rutas y parámetros de cada etapa."""
from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
RUTA_KB = RAIZ / 'knowledge_base'
RUTA_DATOS = RAIZ / 'data'
RUTA_EVALUACION = RAIZ / 'evaluacion'

# La clave se lee del .env del proyecto o del portafolio; nunca se escribe en el código
for candidato in (RAIZ / '.env', RAIZ.parent / '.env'):
    if candidato.is_file():
        load_dotenv(candidato, override=False)

MODELO_RAPIDO = 'gpt-6-luna'
MODELO_POTENTE = 'gpt-6-astra'
MODELO_EMBEDDINGS = 'text-embedding-3-small'

# USD por millón de tokens (entrada, salida). Precios públicos de OpenAI consultados el 2026-11-11.
# Los tokens de razonamiento se cobran como salida. Los tokens de entrada en caché se cobran a precio
# completo en este cálculo, por prudencia.
PRECIOS = {
    'gpt-6-luna': (0.10, 0.50),
    'gpt-6-astra': (10.00, 50.00),
    'text-embedding-3-small': (0.02, 0.0),
}


@dataclass
class Config:
    # Enrutamiento de modelos: el modelo pequeño hace el trabajo mecánico
    modelo_router: str = MODELO_RAPIDO
    modelo_reranker: str = MODELO_RAPIDO
    modelo_respuesta: str = MODELO_RAPIDO
    modelo_verificador: str = MODELO_RAPIDO
    modelo_escalamiento: str = MODELO_POTENTE
    modelo_embeddings: str = MODELO_EMBEDDINGS
    esfuerzo_router: str = 'none'
    esfuerzo_respuesta: str = 'low'
    esfuerzo_verificador: str = 'low'

    # Recuperación
    k_por_consulta: int = 20          # candidatos de cada buscador (denso y BM25) por consulta
    k_candidatos: int = 20            # candidatos que pasan al re-ranking
    k_final: int = 6                  # fragmentos que llegan al modelo
    n_reformulaciones: int = 3        # expansión de la consulta
    usar_expansion: bool = True
    usar_reranking: bool = True
    puntaje_minimo_rerank: int = 1    # de 0 a 3
    caracteres_por_fragmento: int = 1800

    # Guardrails y reflexión
    max_caracteres_pregunta: int = 2000
    umbral_fidelidad: float = 0.80    # parte de afirmaciones respaldadas para aprobar
    max_reflexiones: int = 1
    escalar_si_falla: bool = True     # la reflexión usa el modelo potente
    max_tokens_copiados: int = 40     # tramo textual máximo copiado de una guía

    # Caché semántico
    usar_cache: bool = True
    umbral_cache: float = 0.93      # entre 0.844 (distinta intención) y 0.948 (misma) en las pruebas

    # Observabilidad
    usar_langsmith: bool = False      # envía las trazas a LangSmith, otro servicio externo
    rutas: dict = field(default_factory=lambda: {
        'indice': RUTA_DATOS / 'indice', 'cache': RUTA_DATOS / 'cache.jsonl',
        'trazas': RUTA_DATOS / 'trazas.jsonl'})

    def __post_init__(self):
        RUTA_DATOS.mkdir(exist_ok=True)
        if self.usar_langsmith and os.environ.get('LANGSMITH_API_KEY'):
            os.environ['LANGSMITH_TRACING'] = 'true'
            os.environ.setdefault('LANGSMITH_PROJECT', 'asistente-guias-riesgo')
        else:
            os.environ['LANGSMITH_TRACING'] = 'false'


def verificar_clave():
    if not os.environ.get('OPENAI_API_KEY'):
        raise RuntimeError('Falta OPENAI_API_KEY. Agrégala al archivo .env del proyecto o del portafolio.')
