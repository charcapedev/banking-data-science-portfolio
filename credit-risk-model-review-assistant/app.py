"""Consola visual del asistente de consulta de guías de riesgo. Ejecutar con: streamlit run app.py"""
import json

import pandas as pd
import streamlit as st

from asistente import Asistente, Config, MODELO_POTENTE, MODELO_RAPIDO
from asistente.config import RUTA_DATOS, RUTA_EVALUACION
from asistente.memoria import leer_trazas

st.set_page_config(page_title='Consulta de guías de riesgo', page_icon='📑', layout='wide')

ESTADOS = {'aprobada': ('🟢', 'Aprobada: todas las afirmaciones verificadas'), 'cache': ('⚡', 'Respuesta reutilizada del caché'),
           'dudosa': ('🟠', 'Dudosa: requiere revisión humana'), 'sin_respaldo': ('⚪', 'Las guías no cubren la pregunta'),
           'bloqueada': ('🔴', 'Bloqueada por un guardrail'), 'fuera_de_dominio': ('⚪', 'Fuera del alcance'),
           'conversacion': ('💬', 'Conversación')}


@st.cache_resource(show_spinner='Cargando guías e índice…')
def cargar_asistente():
    return Asistente(Config())


asistente = cargar_asistente()
cfg = asistente.config

# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    st.header('Configuración')
    cfg.modelo_respuesta = st.selectbox('Modelo de respuesta', [MODELO_RAPIDO, MODELO_POTENTE],
                                        help='El potente cuesta unas 100 veces más por token.')
    cfg.usar_reranking = st.toggle('Re-ranking', value=True)
    cfg.usar_expansion = st.toggle('Expansión de la consulta', value=True)
    cfg.usar_cache = st.toggle('Caché semántico', value=True)
    etapa = st.radio('Buscar en', ['Ambas guías', 'Solo desarrollo', 'Solo validación'])
    filtros = {'Solo desarrollo': {'etapa': 'desarrollo'}, 'Solo validación': {'etapa': 'validacion'}}.get(etapa)
    st.divider()
    st.metric('Costo de esta sesión (USD)', f'{asistente.registro_sesion.total_usd:.5f}')
    st.caption(f'{len(asistente.fragmentos)} fragmentos de {len({f["doc_id"] for f in asistente.fragmentos})} guías')
    if st.button('Vaciar caché'):
        asistente.cache.limpiar()
        st.toast('Caché vaciado')

consulta_tab, evaluacion_tab, trazas_tab = st.tabs(['💬 Consulta', '📊 Evaluación', '🔎 Observabilidad'])

# ------------------------------------------------------------------ consulta
with consulta_tab:
    if 'chat' not in st.session_state:
        st.session_state.chat = []
    chat_col, panel_col = st.columns([3, 2])
    with chat_col:
        for turno in st.session_state.chat:
            with st.chat_message(turno['rol']):
                st.markdown(turno['texto'])
        pregunta = st.chat_input('Pregunta sobre las guías, por ejemplo: ¿qué PSI se considera estable?')
        if pregunta:
            historial = [(t['rol'], t['texto']) for t in st.session_state.chat[-4:]]
            with st.spinner('Buscando y verificando…'):
                r = asistente.consultar(pregunta, historial=historial or None, filtros=filtros)
            icono, texto_estado = ESTADOS.get(r.estado, ('', r.estado))
            st.session_state.chat += [{'rol': 'user', 'texto': pregunta},
                                      {'rol': 'assistant', 'texto': f'{r.respuesta}\n\n_{icono} {texto_estado}_'}]
            st.session_state.ultimo = r
            st.rerun()
    with panel_col:
        r = st.session_state.get('ultimo')
        if r is None:
            st.info('Las fuentes, la traza y el costo de cada respuesta aparecen aquí.')
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Fidelidad', '—' if r.fidelidad is None else f'{r.fidelidad:.0%}')
            c2.metric('Costo (USD)', f'{r.costo_usd:.5f}')
            c3.metric('Tokens', f'{r.tokens:,}')
            c4.metric('Segundos', r.segundos)
            for a in r.alertas:
                st.warning(a)
            if r.contradicciones:
                st.error('**Criterios distintos entre fuentes**\n\n' + '\n'.join(f'- {c}' for c in r.contradicciones))
            st.subheader('Fuentes citadas')
            for f in r.fuentes:
                with st.expander(f"[{f['n']}] {f['ruta'].split(' › ', 1)[-1]}  ·  relevancia {f['puntaje_rerank']}/3"):
                    st.caption(f"{f['id']} · {f['etapa']} · {f['tipo']}")
                    st.markdown(f['texto'])
            if r.veredictos:
                st.subheader('Verificación de afirmaciones')
                st.dataframe(pd.DataFrame(r.veredictos), hide_index=True, width='stretch')
            st.subheader('Traza')
            for p in r.pasos:
                detalle = {k: v for k, v in p.items() if k not in ('paso', 'segundos', 'puntajes_rerank')}
                st.markdown(f"**{p['paso']}** · {p['segundos']} s")
                st.caption(json.dumps(detalle, ensure_ascii=False)[:400])
            st.subheader('Costo por llamada')
            st.dataframe(pd.DataFrame(r.costos)[['etapa', 'modelo', 'tokens_entrada', 'tokens_salida', 'tokens_razonamiento',
                                                 'costo_usd', 'segundos']], hide_index=True, width='stretch')

# ------------------------------------------------------------------ evaluación
with evaluacion_tab:
    ruta = RUTA_DATOS / 'evaluacion'
    if not (ruta / 'generacion.pkl').is_file():
        st.info('Ejecuta el notebook nb_01 para generar las evaluaciones.')
    else:
        rec, _ = pd.read_pickle(ruta / 'recuperacion.pkl')
        gen, _, _ = pd.read_pickle(ruta / 'generacion.pkl')
        ata = pd.read_pickle(ruta / 'ataques.pkl')
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Exactitud media', f"{gen['exactitud'].mean():.2f}")
        c2.metric('Fidelidad media', f"{gen['fidelidad'].mean():.2f}")
        c3.metric('Ataques resistidos', f"{ata['resistió'].sum()} de {len(ata)}")
        c4.metric('Costo medio por consulta', f"${gen['costo_usd'].mean():.4f}")
        st.subheader('Recuperación por configuración')
        st.dataframe(rec.groupby('configuracion')[['acierto', 'cobertura', 'rr']].mean().round(3), width='stretch')
        st.subheader('Respuestas por tipo de pregunta')
        st.dataframe(gen.groupby('categoria')[['exactitud', 'relevancia', 'fidelidad', 'costo_usd', 'segundos']].mean().round(3),
                     width='stretch')
        st.subheader('Red teaming')
        st.dataframe(ata.drop(columns=['respuesta']), hide_index=True, width='stretch')

# ------------------------------------------------------------------ observabilidad
with trazas_tab:
    trazas = pd.DataFrame(leer_trazas(cfg.rutas['trazas']))
    if trazas.empty:
        st.info('Aún no hay consultas registradas.')
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric('Consultas registradas', len(trazas))
        c2.metric('Costo total (USD)', f"{trazas['costo_usd'].sum():.4f}")
        c3.metric('Latencia mediana (s)', f"{trazas['segundos'].median():.1f}")
        st.bar_chart(trazas['estado'].value_counts())
        st.dataframe(trazas[['pregunta', 'estado', 'fidelidad', 'modelo_respuesta', 'costo_usd', 'tokens', 'segundos']].iloc[::-1],
                     hide_index=True, width='stretch')
        st.caption('Cada consulta se guarda en data/trazas.jsonl. Con usar_langsmith=True también se envía a LangSmith.')
