"""Ingesta: documentos → fragmentos con metadatos.

La fragmentación es semántica: sigue los títulos del documento y nunca corta una tabla ni un paso
numerado. Solo si una sección supera el tamaño máximo se divide entre párrafos.
"""
from pathlib import Path
import hashlib
import re

from pypdf import PdfReader

TITULOS_EXCLUIDOS = {'Referencias externas'}
ETAPA = {'guia-modelos-riesgo-crediticio': 'desarrollo', 'guia-validacion-modelos': 'validacion'}


def inventario(ruta_kb):
    """Los archivos de la base de conocimiento. Si un documento existe en .md y .pdf, se usa el .md."""
    archivos = sorted(p for p in Path(ruta_kb).iterdir() if p.suffix.lower() in ('.md', '.pdf'))
    elegidos = {}
    for p in archivos:
        if p.stem not in elegidos or p.suffix.lower() == '.md':
            elegidos[p.stem] = p
    filas = []
    for p in archivos:
        contenido = p.read_bytes()
        filas.append({'archivo': p.name, 'formato': p.suffix[1:], 'kb': round(len(contenido) / 1024, 1),
                      'sha256': hashlib.sha256(contenido).hexdigest()[:12],
                      'paginas': len(PdfReader(p).pages) if p.suffix.lower() == '.pdf' else None,
                      'se usa': elegidos[p.stem] == p})
    return filas, list(elegidos.values())


def limpiar(texto):
    texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)        # enlaces markdown → solo el texto
    texto = re.sub(r'\*\*([^*]+)\*\*', r'\1', texto)               # negritas
    texto = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', texto)      # cursivas
    return texto.strip()


def _bloques(lineas):
    """Agrupa líneas en bloques: párrafos, tablas completas y listas completas."""
    bloques, actual, tipo = [], [], None
    for linea in lineas + ['']:
        t = 'tabla' if linea.startswith('|') else 'lista' if re.match(r'^(\d+\.|-)\s', linea) else 'texto'
        if not linea.strip():
            if actual:
                bloques.append(('\n'.join(actual), tipo)); actual, tipo = [], None
            continue
        if actual and t != tipo and not (tipo == 'lista' and t == 'texto' and linea.startswith('  ')):
            bloques.append(('\n'.join(actual), tipo)); actual = []
        actual.append(linea); tipo = t
    return bloques


def _tipo_fragmento(texto, ruta):
    cifras = len(re.findall(r'\d+(?:[,.]\d+)?\s?%|[<>≤≥]\s?\d', texto))
    if ('|' in texto and '---' in texto) or re.search(r'umbral|corte|rangos', ruta, re.I) or (cifras >= 3 and len(texto) < 700):
        return 'umbral'
    if re.search(r'procedimiento|^\d+\.|paso', ruta + texto[:3], re.I | re.M):
        return 'procedimiento'
    return 'concepto'


def fragmentar_markdown(ruta, max_caracteres=1800):
    texto = Path(ruta).read_text(encoding='utf-8')
    doc_id = Path(ruta).stem
    titulo, seccion, subseccion = doc_id, '', ''
    secciones, lineas = [], []

    def cerrar():
        if lineas and seccion not in TITULOS_EXCLUIDOS:
            secciones.append((seccion, subseccion, list(lineas)))
        lineas.clear()

    for linea in texto.splitlines():
        if linea.startswith('# '):
            titulo = linea[2:].strip()
        elif linea.startswith('## '):
            cerrar(); seccion, subseccion = linea[3:].strip(), ''
        elif linea.startswith('### '):
            cerrar(); subseccion = linea[4:].strip()
        elif seccion:
            lineas.append(linea)
    cerrar()

    fragmentos = []
    for seccion, subseccion, lineas in secciones:
        partes, actual = [], []
        for bloque, _ in _bloques(lineas):
            bloque = limpiar(bloque)
            # Se corta solo si lo acumulado ya es un fragmento útil (300+ caracteres)
            if actual and sum(len(b) for b in actual) >= 300 and sum(len(b) for b in actual) + len(bloque) > max_caracteres:
                partes.append(actual); actual = []
            actual.append(bloque)
        if actual:
            partes.append(actual)
        for j, parte in enumerate(partes):
            cuerpo = '\n\n'.join(parte)
            ruta_txt = ' › '.join(x for x in (titulo, seccion, subseccion) if x)
            fragmentos.append({
                'id': f'{doc_id}#{len(fragmentos) + 1:02d}', 'documento': titulo, 'doc_id': doc_id,
                'etapa': ETAPA.get(doc_id, 'otra'), 'seccion': seccion, 'subseccion': subseccion,
                'ruta': ruta_txt + (f' (parte {j + 1})' if len(partes) > 1 else ''),
                'tipo': _tipo_fragmento(cuerpo, ruta_txt), 'texto': cuerpo,
                'caracteres': len(cuerpo), 'fuente': 'interna'})
    return fragmentos


def fragmentar_pdf(ruta, max_caracteres=1800):
    """Respaldo para documentos sin versión .md: corta por párrafos sin conocer los títulos."""
    lector = PdfReader(ruta)
    texto = '\n'.join(p.extract_text() or '' for p in lector.pages)
    parrafos = [p.strip() for p in re.split(r'\n\s*\n|(?<=\.)\n(?=[A-ZÁÉÍÓÚ])', texto) if p.strip()]
    fragmentos, actual = [], []
    for p in parrafos + ['']:
        if (not p or sum(len(x) for x in actual) + len(p) > max_caracteres) and actual:
            cuerpo = ' '.join(actual)
            fragmentos.append({'id': f'{Path(ruta).stem}#{len(fragmentos) + 1:02d}', 'documento': Path(ruta).stem,
                               'doc_id': Path(ruta).stem, 'etapa': ETAPA.get(Path(ruta).stem, 'otra'), 'seccion': '',
                               'subseccion': '', 'ruta': f'{Path(ruta).stem} (página aproximada)', 'tipo': 'concepto',
                               'texto': cuerpo, 'caracteres': len(cuerpo), 'fuente': 'interna'})
            actual = []
        if p:
            actual.append(p)
    return fragmentos


def fragmentar_fijo(ruta, tamano=800):
    """Fragmentación ingenua por número de caracteres, solo para comparar."""
    texto = limpiar(Path(ruta).read_text(encoding='utf-8'))
    return [texto[i:i + tamano] for i in range(0, len(texto), tamano)]


def construir_fragmentos(ruta_kb, max_caracteres=1800):
    _, archivos = inventario(ruta_kb)
    fragmentos = []
    for p in archivos:
        f = fragmentar_markdown(p, max_caracteres) if p.suffix.lower() == '.md' else fragmentar_pdf(p, max_caracteres)
        fragmentos.extend(f)
    return fragmentos


def huella(fragmentos):
    return hashlib.sha256(''.join(f['id'] + f['texto'] for f in fragmentos).encode('utf-8')).hexdigest()[:16]
