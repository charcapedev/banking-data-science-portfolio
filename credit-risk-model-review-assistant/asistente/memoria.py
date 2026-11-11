"""Estado persistente: caché semántico de respuestas y registro de trazas."""
from dataclasses import asdict, is_dataclass
import json
import time

import numpy as np


class CacheSemantico:
    """Reutiliza una respuesta aprobada si una pregunta nueva es casi idéntica en significado.

    Se compara el embedding de la pregunta con los guardados. La clave incluye el modelo de respuesta
    y los filtros, para no devolver una respuesta producida con otra configuración.
    """

    def __init__(self, ruta, umbral):
        self.ruta, self.umbral = ruta, umbral
        self.entradas, self.vectores = [], []
        if ruta.is_file():
            for linea in ruta.read_text(encoding='utf-8').splitlines():
                e = json.loads(linea)
                self.entradas.append(e)
                self.vectores.append(np.asarray(e.pop('vector'), dtype=np.float32))

    def buscar(self, vector, clave):
        mejor, similitud = None, -1.0
        for e, v in zip(self.entradas, self.vectores):
            if e['clave'] != clave:
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
