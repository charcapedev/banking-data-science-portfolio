"""Registro de tokens, costo y latencia por llamada al modelo."""
from dataclasses import dataclass, asdict
import time

import pandas as pd

from .config import PRECIOS


def costo_usd(modelo, tokens_entrada, tokens_salida):
    entrada, salida = PRECIOS.get(modelo, (0.0, 0.0))
    return (tokens_entrada * entrada + tokens_salida * salida) / 1e6


@dataclass
class Llamada:
    etapa: str
    modelo: str
    tokens_entrada: int
    tokens_salida: int
    tokens_razonamiento: int
    costo_usd: float
    segundos: float
    instante: float


class RegistroCostos:
    """Acumula cada llamada. Un registro por consulta y otro para toda la sesión."""

    def __init__(self):
        self.llamadas: list[Llamada] = []

    def registrar(self, etapa, modelo, tokens_entrada, tokens_salida, tokens_razonamiento=0, segundos=0.0):
        llamada = Llamada(etapa, modelo, int(tokens_entrada), int(tokens_salida), int(tokens_razonamiento),
                          costo_usd(modelo, tokens_entrada, tokens_salida), float(segundos), time.time())
        self.llamadas.append(llamada)
        return llamada

    def extender(self, otro):
        self.llamadas.extend(otro.llamadas)

    @property
    def total_usd(self):
        return sum(l.costo_usd for l in self.llamadas)

    @property
    def tokens(self):
        return sum(l.tokens_entrada + l.tokens_salida for l in self.llamadas)

    def tabla(self):
        return pd.DataFrame([asdict(l) for l in self.llamadas])

    def por_etapa(self):
        t = self.tabla()
        if t.empty:
            return t
        r = t.groupby(['etapa', 'modelo']).agg(llamadas=('costo_usd', 'size'), tokens_entrada=('tokens_entrada', 'sum'),
                                                tokens_salida=('tokens_salida', 'sum'),
                                                tokens_razonamiento=('tokens_razonamiento', 'sum'),
                                                costo_usd=('costo_usd', 'sum'), segundos=('segundos', 'sum'))
        r['% del costo'] = r['costo_usd'] / r['costo_usd'].sum() * 100
        return r.sort_values('costo_usd', ascending=False)


def proyectar(costo_por_consulta, consultas_por_mes, tasa_cache=0.0):
    """Costo mensual estimado: las consultas que acierta el caché solo pagan el embedding."""
    costo_cache = costo_usd('text-embedding-3-small', 30, 0)
    return consultas_por_mes * ((1 - tasa_cache) * costo_por_consulta + tasa_cache * costo_cache)
