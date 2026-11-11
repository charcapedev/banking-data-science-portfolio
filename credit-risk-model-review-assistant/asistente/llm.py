"""Llamadas a OpenAI con salida estructurada, reintento guiado y registro de costos."""
from functools import lru_cache
import time

import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import ValidationError

from .config import verificar_clave


@lru_cache(maxsize=16)
def _chat(modelo, esfuerzo):
    verificar_clave()
    return ChatOpenAI(model=modelo, reasoning_effort=esfuerzo, timeout=120, max_retries=2)


@lru_cache(maxsize=1)
def _cliente():
    verificar_clave()
    return OpenAI(timeout=60, max_retries=2)


def estructurado(esquema, sistema, usuario, modelo, esfuerzo, registro, etapa, intentos=2):
    """Pide una salida que cumpla el esquema Pydantic. Si no lo cumple, reenvía el error al modelo para que lo corrija."""
    llm = _chat(modelo, esfuerzo).with_structured_output(esquema, include_raw=True)
    mensajes = [SystemMessage(sistema), HumanMessage(usuario)]
    ultimo_error = None
    for intento in range(intentos):
        inicio = time.time()
        r = llm.invoke(mensajes)
        uso = r['raw'].usage_metadata or {}
        razonamiento = (uso.get('output_token_details') or {}).get('reasoning', 0)
        registro.registrar(etapa if intento == 0 else f'{etapa} (reintento)', modelo, uso.get('input_tokens', 0),
                           uso.get('output_tokens', 0), razonamiento, time.time() - inicio)
        if r['parsed'] is not None and r['parsing_error'] is None:
            return r['parsed']
        ultimo_error = r['parsing_error']
        mensajes.append(HumanMessage(f'Tu salida no cumple el esquema: {str(ultimo_error)[:500]}. Corrígela.'))
    raise ValueError(f'La salida de {etapa} no cumplió el esquema tras {intentos} intentos: {ultimo_error}')


def embeber(textos, modelo, registro, etapa, lote=256):
    """Embeddings normalizados (norma 1), de modo que el producto punto es la similitud coseno."""
    vectores = []
    for i in range(0, len(textos), lote):
        inicio = time.time()
        r = _cliente().embeddings.create(model=modelo, input=textos[i:i + lote])
        registro.registrar(etapa, modelo, r.usage.prompt_tokens, 0, 0, time.time() - inicio)
        vectores.extend(d.embedding for d in r.data)
    m = np.asarray(vectores, dtype=np.float32)
    return m / np.linalg.norm(m, axis=1, keepdims=True)


__all__ = ['estructurado', 'embeber', 'ValidationError']
