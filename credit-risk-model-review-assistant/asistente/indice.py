"""Índice híbrido: vectores densos (significado) y BM25 (palabras exactas), fusionados con RRF."""
import json
import re
import unicodedata

import numpy as np
from rank_bm25 import BM25Okapi

from .ingesta import huella
from .llm import embeber

PALABRAS_VACIAS = set('''a al como con cual cuales cuando de del el en entre es esta este estos estas la las le lo los mas
no o para por que qué se ser si sin son su sus un una uno y ya hay debe puede cómo cuál cuáles'''.split())


def tokenizar(texto):
    texto = unicodedata.normalize('NFKD', texto.lower())
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return [t for t in re.findall(r'[a-z0-9]+(?:[.,][0-9]+)?', texto) if t not in PALABRAS_VACIAS]


def texto_indexado(f):
    # Encabezado contextual: el fragmento lleva consigo de qué guía y sección viene
    return f"{f['ruta']}\n{f['texto']}"


class Indice:
    def __init__(self, fragmentos, matriz, modelo):
        self.fragmentos, self.matriz, self.modelo = fragmentos, matriz, modelo
        self.por_id = {f['id']: i for i, f in enumerate(fragmentos)}
        self.bm25 = BM25Okapi([tokenizar(texto_indexado(f)) for f in fragmentos])

    @classmethod
    def cargar_o_construir(cls, fragmentos, ruta, modelo, registro):
        ruta.mkdir(parents=True, exist_ok=True)
        meta_p, emb_p, frag_p = ruta / 'meta.json', ruta / 'embeddings.npy', ruta / 'fragmentos.json'
        h = huella(fragmentos)
        if meta_p.is_file():
            meta = json.loads(meta_p.read_text(encoding='utf-8'))
            if meta.get('huella') == h and meta.get('modelo') == modelo and emb_p.is_file():
                return cls(fragmentos, np.load(emb_p), modelo), False
        matriz = embeber([texto_indexado(f) for f in fragmentos], modelo, registro, 'ingesta: embeddings')
        np.save(emb_p, matriz)
        frag_p.write_text(json.dumps(fragmentos, ensure_ascii=False, indent=1), encoding='utf-8')
        meta_p.write_text(json.dumps({'huella': h, 'modelo': modelo, 'fragmentos': len(fragmentos)}), encoding='utf-8')
        return cls(fragmentos, matriz, modelo), True

    def _mascara(self, filtros):
        if not filtros:
            return np.ones(len(self.fragmentos), dtype=bool)
        return np.array([all(f.get(k) in (v if isinstance(v, (list, tuple, set)) else [v]) for k, v in filtros.items())
                         for f in self.fragmentos])

    def buscar_denso(self, vector, k, filtros=None):
        sim = self.matriz @ vector
        sim[~self._mascara(filtros)] = -np.inf
        orden = np.argsort(-sim)[:k]
        return [(self.fragmentos[i]['id'], float(sim[i])) for i in orden if np.isfinite(sim[i])]

    def buscar_bm25(self, consulta, k, filtros=None):
        puntaje = self.bm25.get_scores(tokenizar(consulta))
        puntaje[~self._mascara(filtros)] = -np.inf
        orden = np.argsort(-puntaje)[:k]
        return [(self.fragmentos[i]['id'], float(puntaje[i])) for i in orden if np.isfinite(puntaje[i]) and puntaje[i] > 0]

    def fragmento(self, id_):
        return self.fragmentos[self.por_id[id_]]


def rrf(listas, k=60):
    """Reciprocal Rank Fusion: suma 1 / (k + posición) de cada lista. No necesita que los puntajes sean comparables."""
    total = {}
    for lista in listas:
        for posicion, (id_, _) in enumerate(lista, start=1):
            total[id_] = total.get(id_, 0.0) + 1.0 / (k + posicion)
    return sorted(total.items(), key=lambda x: -x[1])
