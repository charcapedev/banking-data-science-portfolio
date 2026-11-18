"""Estado persistente: caché semántico de respuestas y registro de trazas."""
from dataclasses import asdict, is_dataclass
import json
import time

import numpy as np

from .guardrails import cifras


class CacheSemantico:
    """Reutiliza una respuesta aprobada si una pregunta nueva es casi idéntica en significado.

    Se compara el embedding de la pregunta con los guardados. La clave incluye la versión de las guías,
    el modelo de respuesta y los filtros, para no devolver una respuesta producida con otras guías u otra
    configuración. Con mismas_cifras, además, la pregunta nueva debe mencionar las mismas cifras que la
    guardada: «¿VIF mayor a 5?» y «¿VIF mayor a 10?» se parecen en significado, pero no en la respuesta.
    """

    def __init__(self, ruta, umbral, mismas_cifras=True):
        self.ruta, self.umbral, self.mismas_cifras = ruta, umbral, mismas_cifras
        self.entradas, self.vectores = [], []
        if ruta.is_file():
            for linea in ruta.read_text(encoding='utf-8').splitlines():
                e = json.loads(linea)
                self.entradas.append(e)
                self.vectores.append(np.asarray(e.pop('vector'), dtype=np.float32))

    def buscar(self, vector, clave, pregunta=None):
        mejor, similitud = None, -1.0
        for e, v in zip(self.entradas, self.vectores):
            if e['clave'] != clave:
                continue
            if self.mismas_cifras and pregunta is not None and cifras(e['pregunta']) != cifras(pregunta):
                continue
            s = float(v @ vector)
            if s > similitud:
                mejor, similitud = e, s
        return (mejor, similitud) if mejor is not None and similitud >= self.umbral else (None, similitud)

    def guardar(self, pregunta, vector, clave, resultado):
        entrada = {'pregunta': pregunta, 'clave': clave, 'resultado': resultado, 'instante': time.time()}
        self.entradas.append(entrada)
        self.vectores.append(vector)
        with self.ruta.open('a', encoding='utf-8') as f:
            f.write(json.dumps({**entrada, 'vector': [round(float(x), 6) for x in vector]}, ensure_ascii=False) + '\n')

    def limpiar(self):
        self.entradas, self.vectores = [], []
        if self.ruta.is_file():
            self.ruta.unlink()


def _serializable(x):
    if is_dataclass(x):
        return asdict(x)
    if hasattr(x, 'model_dump'):
        return x.model_dump()
    return str(x)


def registrar_traza(ruta, traza):
    with ruta.open('a', encoding='utf-8') as f:
        f.write(json.dumps(traza, ensure_ascii=False, default=_serializable) + '\n')


def leer_trazas(ruta):
    if not ruta.is_file():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding='utf-8').splitlines() if l.strip()]
