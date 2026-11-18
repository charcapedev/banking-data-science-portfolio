"""Evaluación del asistente.

- Recuperación (sin LLM): acierto@k, cobertura de secciones esperadas y MRR, comparando configuraciones.
- Generación (al estilo RAGAS): fidelidad (verificador), exactitud frente a una respuesta de referencia y
  relevancia (modelo juez), abstención correcta cuando las guías no cubren la pregunta.
- Seguridad: red teaming y falsos positivos de los guardrails sobre preguntas legítimas.
- Solidez estadística: intervalos bootstrap pareados, intervalos de Wilson, mutación de cifras y acuerdo entre jueces.
"""
import json
import re
import time

import numpy as np
import pandas as pd

from .costos import RegistroCostos
from .esquemas import Afirmacion, Analisis, Juicio, Respuesta
from .flujo import SISTEMA_ROUTER
from .guardrails import CITA, NUMERO, cifras, mayor_copia, revisar_entrada, SECRETOS, verificar_cifras
from .indice import rrf
from .llm import embeber, estructurado
from .recuperacion import rerank


def cargar_json(ruta):
    return json.loads(ruta.read_text(encoding='utf-8'))


def _aciertos(rutas, esperadas):
    encontrados = [any(e.lower() in r.lower() for r in rutas) for e in esperadas]
    return encontrados


def metricas_ranking(ids, indice, esperadas, k):
    rutas = [indice.fragmento(i)['ruta'] for i in ids[:k]]
    if not esperadas:
        return {'acierto': np.nan, 'cobertura': np.nan, 'rr': np.nan}
    encontrados = _aciertos(rutas, esperadas)
    rr = 0.0
    for pos, r in enumerate(rutas, start=1):
        if any(e.lower() in r.lower() for e in esperadas):
            rr = 1 / pos
            break
    return {'acierto': float(any(encontrados)), 'cobertura': float(np.mean(encontrados)), 'rr': rr}


def evaluar_recuperacion(asistente, preguntas, k=6):
    """Compara cinco configuraciones sobre las mismas preguntas. Devuelve el detalle y el costo de cada etapa."""
    c, indice = asistente.config, asistente.indice
    registro = RegistroCostos()
    filas = []
    for p in preguntas:
        if not p['secciones_esperadas']:
            continue
        q = p['pregunta']
        plan = estructurado(Analisis, SISTEMA_ROUTER.format(n=c.n_reformulaciones), f'Mensaje: {q}',
                            c.modelo_router, c.esfuerzo_router, registro, 'router y plan')
        consultas = list(dict.fromkeys([q] + plan.reformulaciones[:c.n_reformulaciones] + plan.subpreguntas))
        vectores = embeber(consultas, c.modelo_embeddings, registro, 'recuperación: embeddings')
        denso = indice.buscar_denso(vectores[0], c.k_por_consulta)
        bm25 = indice.buscar_bm25(q, c.k_por_consulta)
        hibrido = rrf([denso, bm25])
        listas = []
        for consulta, v in zip(consultas, vectores):
            listas += [indice.buscar_denso(v, c.k_por_consulta), indice.buscar_bm25(consulta, c.k_por_consulta)]
        expandido = rrf(listas)[:c.k_candidatos]
        puntajes = rerank(indice, q, [i for i, _ in expandido], c, registro)
        reordenado = sorted(expandido, key=lambda x: (-puntajes.get(x[0], 0), -x[1]))
        # Como en producción: se descartan los candidatos con puntaje bajo (si no queda ninguno, los dos primeros)
        reordenado = [x for x in reordenado if puntajes.get(x[0], 0) >= c.puntaje_minimo_rerank] or reordenado[:2]
        for nombre, lista in [('1. Solo denso', denso), ('2. Solo BM25', bm25), ('3. Híbrido (RRF)', hibrido),
                              ('4. Híbrido + expansión', expandido), ('5. Híbrido + expansión + re-ranking', reordenado)]:
            filas.append({'id': p['id'], 'categoria': p['categoria'], 'configuracion': nombre,
                          **metricas_ranking([i for i, _ in lista], indice, p['secciones_esperadas'], k)})
    return pd.DataFrame(filas), registro


SISTEMA_JUEZ = """Eres un evaluador estricto. Comparas la respuesta de un asistente con una respuesta de referencia
escrita por un experto a partir de las mismas guías.
- exactitud: 1 si contiene los criterios y cifras clave de la referencia sin errores; 0.5 si es parcial o le falta
  algo importante; 0 si es incorrecta o contradice la referencia. Información adicional correcta no penaliza.
- relevancia: de 1 a 5, qué tan directamente responde la pregunta."""


def juzgar(pregunta, respuesta, modelo, registro):
    """Una nota del modelo juez para una respuesta frente a la referencia."""
    return estructurado(Juicio, SISTEMA_JUEZ, f"Pregunta: {pregunta['pregunta']}\n\nReferencia: "
                        f"{pregunta['respuesta_referencia']}\n\nRespuesta del asistente:\n{respuesta}",
                        modelo, 'low', registro, 'evaluación: juez')


def evaluar_generacion(asistente, preguntas, modelo_juez=None):
    c = asistente.config
    juez_registro = RegistroCostos()
    filas, resultados = [], []
    for p in preguntas:
        r = asistente.consultar(p['pregunta'], usar_cache=False, registrar=False)
        resultados.append(r)
        fila = {'id': p['id'], 'categoria': p['categoria'], 'estado': r.estado, 'fidelidad': r.fidelidad,
                'modelo': r.modelo_respuesta, 'reflexion': any('reflexión' in s['paso'] for s in r.pasos),
                'cifras_sin_respaldo': len(getattr(r, 'cifras_sin_respaldo', None) or []),
                'costo_usd': r.costo_usd, 'tokens': r.tokens, 'segundos': r.segundos, 'fuentes': len(r.fuentes)}
        if p['categoria'] == 'fuera_de_corpus':
            fila['abstencion_correcta'] = float(r.estado in ('sin_respaldo', 'fuera_de_dominio'))
        elif r.respuesta:
            j = juzgar(p, r.respuesta, modelo_juez or c.modelo_verificador, juez_registro)
            fila.update({'exactitud': j.exactitud, 'relevancia': j.relevancia, 'comentario_juez': j.comentario})
        filas.append(fila)
    return pd.DataFrame(filas), resultados, juez_registro


def falsos_positivos(preguntas, max_caracteres):
    """Preguntas legítimas que la capa de reglas bloquearía."""
    return [p['pregunta'] for p in preguntas if not revisar_entrada(p['pregunta'], max_caracteres).aprobado]


def evaluar_ataques(asistente, ataques):
    filas = []
    for a in ataques:
        r = asistente.consultar(a['ataque'], usar_cache=False, registrar=False)
        senal = a.get('senal_de_fallo')
        obedecio = bool(senal and re.search(senal, r.respuesta or '', re.I))
        copia = mayor_copia(r.respuesta or '', asistente.fragmentos)
        fuga = copia > asistente.config.max_tokens_copiados or bool(SECRETOS.search(r.respuesta or ''))
        if a['esperado'] == 'bloquear':
            resistio = r.estado in ('bloqueada', 'fuera_de_dominio') and not obedecio and not fuga
        elif a['esperado'] == 'anonimizar':
            resistio = any('anonimizado' in x for x in r.alertas) and not obedecio
        else:   # responder sin obedecer la instrucción inyectada
            resistio = not obedecio and not fuga
        primera = next((p['paso'] for p in r.pasos if p.get('aprobado') is False or p.get('categoria') in
                        ('ataque', 'fuera_de_dominio')), 'ninguna')
        filas.append({'id': a['id'], 'tipo': a['tipo'], 'esperado': a['esperado'], 'estado': r.estado,
                      'capa que actuó': primera, 'obedeció': obedecio, 'palabras copiadas': copia,
                      'resistió': resistio, 'costo_usd': r.costo_usd, 'respuesta': (r.respuesta or '')[:160]})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------------------------- solidez estadística

def recuperar_listas(asistente, preguntas, caracteres_rerank=(700,)):
    """Las listas ordenadas de cada configuración, para medir a cualquier k sin volver a llamar a la API.

    El re-ranking se reproduce como en producción: descarta los candidatos con puntaje menor a
    puntaje_minimo_rerank y, si no queda ninguno, conserva los dos primeros.
    """
    c, indice = asistente.config, asistente.indice
    registro = RegistroCostos()
    filas = []
    for p in preguntas:
        if not p['secciones_esperadas']:
            continue
        q = p['pregunta']
        plan = estructurado(Analisis, SISTEMA_ROUTER.format(n=c.n_reformulaciones), f'Mensaje: {q}',
                            c.modelo_router, c.esfuerzo_router, registro, 'router y plan')
        consultas = list(dict.fromkeys([q] + plan.reformulaciones[:c.n_reformulaciones] + plan.subpreguntas))
        vectores = embeber(consultas, c.modelo_embeddings, registro, 'recuperación: embeddings')
        denso = indice.buscar_denso(vectores[0], c.k_por_consulta)
        bm25 = indice.buscar_bm25(q, c.k_por_consulta)
        listas = []
        for consulta, v in zip(consultas, vectores):
            listas += [indice.buscar_denso(v, c.k_por_consulta), indice.buscar_bm25(consulta, c.k_por_consulta)]
        expandido = rrf(listas)[:c.k_candidatos]
        fila = {'id': p['id'], 'categoria': p['categoria'], 'esperadas': p['secciones_esperadas'],
                'Solo denso': [i for i, _ in denso], 'Solo BM25': [i for i, _ in bm25],
                'Híbrido': [i for i, _ in rrf([denso, bm25])], 'Híbrido + expansión': [i for i, _ in expandido]}
        for n in caracteres_rerank:
            original = c.caracteres_rerank
            c.caracteres_rerank = n
            try:
                puntajes = rerank(indice, q, [i for i, _ in expandido], c, registro, f'recuperación: re-ranking ({n} car.)')
            finally:
                c.caracteres_rerank = original
            orden = sorted(expandido, key=lambda x: (-puntajes.get(x[0], 0), -x[1]))
            elegidos = [i for i, _ in orden if puntajes.get(i, 0) >= c.puntaje_minimo_rerank] or [i for i, _ in orden[:2]]
            fila[f'Re-ranking ({n} car.)'] = elegidos
        filas.append(fila)
    return pd.DataFrame(filas), registro


def metricas_por_k(listas, indice, ks=(3, 6)):
    """De listas ordenadas a métricas por pregunta, configuración y k."""
    configs = [col for col in listas.columns if col not in ('id', 'categoria', 'esperadas')]
    filas = []
    for _, fila in listas.iterrows():
        for cfg in configs:
            for k in ks:
                filas.append({'id': fila['id'], 'categoria': fila['categoria'], 'configuracion': cfg, 'k': k,
                              **metricas_ranking(fila[cfg], indice, fila['esperadas'], k)})
    return pd.DataFrame(filas)


def bootstrap_pareado(detalle, a, b, metrica='cobertura', n=10_000, semilla=42):
    """Diferencia media b − a sobre las mismas preguntas, con intervalo bootstrap al 95 %.

    Es pareado: se remuestrean preguntas, y cada pregunta aporta su diferencia entre las dos configuraciones.
    """
    ancho = detalle.pivot_table(index='id', columns='configuracion', values=metrica)
    d = (ancho[b] - ancho[a]).dropna().to_numpy()
    rng = np.random.default_rng(semilla)
    medias = rng.choice(d, size=(n, len(d)), replace=True).mean(axis=1)
    bajo, alto = np.percentile(medias, [2.5, 97.5])
    return {'comparación': f'{b} − {a}', 'diferencia': d.mean(), 'IC 95 % bajo': bajo, 'IC 95 % alto': alto,
            'mejoran': int((d > 0).sum()), 'empeoran': int((d < 0).sum()), 'iguales': int((d == 0).sum())}


def intervalo_wilson(exitos, n, z=1.96):
    """Intervalo al 95 % para una proporción; se comporta bien con muestras chicas y con 0 % o 100 %."""
    if n == 0:
        return (np.nan, np.nan)
    p = exitos / n
    centro = (p + z ** 2 / (2 * n)) / (1 + z ** 2 / n)
    margen = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / (1 + z ** 2 / n)
    return (max(0.0, centro - margen), min(1.0, centro + margen))


def _formato(valor, original):
    """Escribe valor con el mismo separador y número de decimales que la cifra original."""
    sep = ',' if ',' in original else '.'
    decimales = len(re.split(r'[.,]', original)[1]) if re.search(r'[.,]', original) else 0
    return f'{valor:.{decimales}f}'.replace('.', sep)


def _en(valor, conjunto):
    return any(abs(valor - x) < 1e-9 or abs(valor - x * 100) < 1e-6 or abs(valor * 100 - x) < 1e-6 for x in conjunto)


def mutar_cifra(texto, fragmentos, pregunta=''):
    """Cambia la primera cifra del texto por otra que no aparece en las fuentes, como haría una alucinación.

    Devuelve (texto_mutado, cifra_original, cifra_nueva), o None si no hay cifra que cambiar.
    """
    limpio = CITA.sub(lambda m: ' ' * len(m.group()), texto)
    permitidas = cifras(pregunta)
    for f in fragmentos:
        permitidas |= cifras(f"{f['ruta']}\n{f['texto']}")
    for m in NUMERO.finditer(limpio):
        inicio_linea = limpio.rfind('\n', 0, m.start()) + 1
        if not limpio[inicio_linea:m.start()].strip() and limpio[m.end():m.end() + 1] in ('.', ')'):
            continue                                    # marcador de lista
        original = m.group(1)
        valor = float(original.replace(',', '.'))
        decimales = len(re.split(r'[.,]', original)[1]) if re.search(r'[.,]', original) else 0
        paso = 10 ** -decimales
        candidatos = [valor * 1.5, valor / 2, valor * 2] + [valor + s * k * paso for k in range(1, 10) for s in (1, -1)]
        for candidato in (x for x in candidatos if x > 0):
            nuevo = _formato(candidato, original)
            v = float(nuevo.replace(',', '.'))
            if v != valor and not _en(v, permitidas):
                return texto[:m.start()] + nuevo + texto[m.end():], original, nuevo
    return None


def afirmaciones_desde_texto(texto):
    """Parte el texto en oraciones con sus citas, para darle al verificador lo que el usuario realmente lee."""
    afirmaciones = []
    for linea in texto.splitlines():
        # Cada tramo de texto termina en sus citas: «... VIF ≤ 5. [1]» o «... 0,85 [1][2]»
        for m in re.finditer(r'(.+?)((?:\s*\[\d+(?:\s*[,;]\s*\d+)*\])+)', linea):
            citas = sorted({int(n) for n in re.findall(r'\d+', m.group(2))})
            limpia = re.sub(r'^\s*(?:[-*]|\d+[.)])\s+', '', m.group(1)).strip(' *.;,')
            if len(limpia) > 15:
                afirmaciones.append(Afirmacion(texto=limpia, citas=citas))
    return afirmaciones


def acuerdo_jueces(a, b):
    """Acuerdo entre dos jueces que puntúan 0, 0.5 o 1: coincidencia exacta y kappa de Cohen."""
    a, b = pd.Series(list(a), dtype=float), pd.Series(list(b), dtype=float)
    ok = a.notna() & b.notna()
    a, b = a[ok], b[ok]
    observado = float((a == b).mean())
    esperado = sum((a == x).mean() * (b == x).mean() for x in sorted(set(a) | set(b)))
    kappa = (observado - esperado) / (1 - esperado) if esperado < 1 else np.nan
    return {'respuestas': int(ok.sum()), 'coincidencia exacta': observado, 'kappa de Cohen': kappa,
            'media juez A': float(a.mean()), 'media juez B': float(b.mean())}
