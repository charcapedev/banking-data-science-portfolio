"""Guardrails de entrada y de salida.

Entrada: tamaño, patrones de inyección y anonimización de datos personales antes de enviar texto a OpenAI.
Salida: citas válidas, verificación de fidelidad contra los fragmentos y control de copia textual.
"""
from dataclasses import dataclass, field
import re

from .esquemas import Verificacion
from .indice import tokenizar
from .llm import estructurado

PATRONES_INYECCION = [
    (r'ignor\w*\s+(\w+\s+){0,3}(instrucciones|reglas|indicaciones)', 'pide ignorar las instrucciones'),
    (r'olvid\w*\s+(\w+\s+){0,3}(instrucciones|reglas|todo)', 'pide olvidar las reglas'),
    (r'ignore\s+(all\s+|previous\s+|your\s+)*(instructions|rules)', 'pide ignorar las instrucciones (inglés)'),
    (r'(prompt|mensaje|instrucciones)\s+(del\s+)?sistema|system\s+prompt', 'busca el prompt del sistema'),
    (r'(muestra|copia|imprime|reproduce|transcribe|dame|pega)\w*\s+(\w+\s+){0,3}(gu[ií]as?|documentos?|archivos?|base de conocimiento|pdf)\s+(\w+\s+){0,2}(complet|[íi]ntegr|literal|enter|textual)',
     'pide copiar documentos completos'),
    (r'(copia|transcribe|reproduce)\w*\s+(\w+\s+){0,2}(literal|textual)mente', 'pide copiar texto literal'),
    (r'modo\s+(desarrollador|dios|sin\s+restricciones)|jailbreak|\bDAN\b', 'intenta un modo sin restricciones'),
    (r'act[uú]a\s+como\s+(si\s+)?(no\s+tuvieras|otro|un\s+sistema)', 'intenta cambiar el rol del asistente'),
    (r'(api[\s_-]?key|clave\s+de\s+(la\s+)?api|contraseña|\.env)', 'busca credenciales'),
    (r'base64|rot13|codifica\w*\s+tu\s+respuesta', 'intenta evadir filtros con codificación'),
]

PATRONES_PII = [
    (r'[\w.+-]+@[\w-]+\.[\w.]+', '[CORREO]'),
    (r'\b(?:\d[ -]?){13,16}\b', '[TARJETA]'),
    (r'\b\d{11}\b', '[RUC]'),
    (r'\b\d{8}\b', '[DNI]'),
    (r'\b9\d{2}[ -]?\d{3}[ -]?\d{3}\b', '[TELÉFONO]'),
]

SECRETOS = re.compile(r'sk-[A-Za-z0-9_-]{20,}|lsv2_[A-Za-z0-9_]{20,}')


@dataclass
class ResultadoEntrada:
    aprobado: bool
    texto: str
    motivo: str = ''
    alertas: list = field(default_factory=list)


def revisar_entrada(texto, max_caracteres):
    texto = (texto or '').strip()
    if not texto:
        return ResultadoEntrada(False, texto, 'La consulta está vacía.')
    if len(texto) > max_caracteres:
        return ResultadoEntrada(False, texto[:max_caracteres], f'La consulta supera {max_caracteres} caracteres.')
    for patron, motivo in PATRONES_INYECCION:
        if re.search(patron, texto, re.I):
            return ResultadoEntrada(False, texto, f'Bloqueada por la capa de reglas: {motivo}.', [motivo])
    alertas, limpio = [], texto
    for patron, reemplazo in PATRONES_PII:
        limpio, n = re.subn(patron, reemplazo, limpio)
        if n:
            alertas.append(f'{n} dato(s) {reemplazo} anonimizado(s) antes de enviar a OpenAI')
    return ResultadoEntrada(True, limpio, '', alertas)


def validar_citas(respuesta, n_fragmentos):
    """Validación estructural: toda afirmación cita fragmentos que existen."""
    problemas = []
    if respuesta.sin_respaldo:
        return problemas
    if not respuesta.afirmaciones:
        problemas.append('La respuesta no declara afirmaciones verificables.')
    for i, a in enumerate(respuesta.afirmaciones, start=1):
        if not a.citas:
            problemas.append(f'La afirmación {i} no tiene citas.')
        fuera = [c for c in a.citas if c > n_fragmentos]
        if fuera:
            problemas.append(f'La afirmación {i} cita fragmentos inexistentes: {fuera}.')
    # Acepta [1], [1, 3] y [1][3]
    citadas = {int(n) for grupo in re.findall(r'\[(\d+(?:\s*[,;]\s*\d+)*)\]', respuesta.respuesta)
               for n in re.findall(r'\d+', grupo)}
    if not citadas:
        problemas.append('El texto de la respuesta no incluye citas [n].')
    elif max(citadas) > n_fragmentos:
        problemas.append('El texto cita un fragmento que no existe.')
    return problemas


SISTEMA_VERIFICADOR = """Eres un verificador de hechos. Recibes fragmentos numerados de guías y una lista de afirmaciones.
Para cada afirmación decide, usando SOLO los fragmentos citados:
- respaldada: el fragmento dice lo mismo (las cifras coinciden).
- parcial: el fragmento respalda una parte, o la afirmación generaliza más de lo que dice.
- no_respaldada: el fragmento no lo dice o lo contradice.
Sé estricto con cifras, umbrales y a qué contexto se aplican."""


def verificar_fidelidad(respuesta, fragmentos, config, registro, modelo=None):
    """Devuelve la fidelidad (0 a 1) y el veredicto por afirmación."""
    if respuesta.sin_respaldo or not respuesta.afirmaciones:
        return 1.0, []
    citados = sorted({c for a in respuesta.afirmaciones for c in a.citas if c <= len(fragmentos)})
    contexto = '\n\n'.join(f"[{n}] {fragmentos[n - 1]['ruta']}\n{fragmentos[n - 1]['texto']}" for n in citados)
    lista = '\n'.join(f'{i}. {a.texto} (cita {a.citas})' for i, a in enumerate(respuesta.afirmaciones, start=1))
    salida = estructurado(Verificacion, SISTEMA_VERIFICADOR, f'Fragmentos:\n{contexto}\n\nAfirmaciones:\n{lista}',
                          modelo or config.modelo_verificador, config.esfuerzo_verificador, registro, 'verificación de fidelidad')
    valor = {'respaldada': 1.0, 'parcial': 0.5, 'no_respaldada': 0.0}
    veredictos = {v.indice: v for v in salida.veredictos}
    puntajes = [valor[veredictos[i].veredicto] if i in veredictos else 0.0 for i in range(1, len(respuesta.afirmaciones) + 1)]
    return sum(puntajes) / len(puntajes), salida.veredictos


def mayor_copia(texto, fragmentos):
    """Tramo más largo de palabras consecutivas copiado de algún fragmento (control de fuga del documento)."""
    a = tokenizar(texto)
    mejor = 0
    for f in fragmentos:
        b = tokenizar(f['texto'])
        if not a or not b:
            continue
        posiciones = {}
        for j, t in enumerate(b):
            posiciones.setdefault(t, []).append(j)
        previo = {}
        for i, t in enumerate(a):
            actual = {}
            for j in posiciones.get(t, []):
                actual[j] = previo.get(j - 1, 0) + 1
                mejor = max(mejor, actual[j])
            previo = actual
    return mejor


def revisar_salida(texto, fragmentos, config):
    alertas = []
    if SECRETOS.search(texto):
        return False, ['La respuesta contenía una credencial y se bloqueó.']
    copia = mayor_copia(texto, fragmentos)
    if copia > config.max_tokens_copiados:
        return False, [f'La respuesta copiaba {copia} palabras seguidas de una guía (máximo {config.max_tokens_copiados}).']
    if re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', texto):
        alertas.append('La respuesta incluye un correo electrónico.')
    return True, alertas
