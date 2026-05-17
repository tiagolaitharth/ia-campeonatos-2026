import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import re

from datetime import datetime
from datetime import timedelta

from collections import Counter

usuarios = {

    "tiago": {

        "senha": "123",

        "tipo": "admin",

        "expira": "2099-12-31"
    }
}

# =========================
# CONFIG
# =========================

st.set_page_config(
    layout="wide",
    page_title="IA - Campeonatos 2026"
)

st.title("📊 IA - Campeonatos 2026")

# =========================
# LOGIN
# =========================

if "logado" not in st.session_state:

    st.session_state.logado = False

if not st.session_state.logado:

    st.subheader("🔐 Login")

    usuario = st.text_input(
        "Usuário"
    )

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        if usuario in usuarios:

            dados_usuario = usuarios[
                usuario
            ]

            senha_correta = (
                dados_usuario["senha"]
            )

            data_expiracao = datetime.strptime(

                dados_usuario["expira"],

                "%Y-%m-%d"

            ).date()

            hoje = (
                datetime.today().date()
            )

            if senha == senha_correta:

                if hoje <= data_expiracao:

                    st.session_state.logado = True

                    st.session_state.usuario = usuario

                    st.session_state.tipo = (
                        dados_usuario["tipo"]
                    )

                    st.rerun()

                else:

                    st.error(
                        "Acesso expirado"
                    )

            else:

                st.error(
                    "Senha incorreta"
                )

        else:

            st.error(
                "Usuário não encontrado"
            )

    st.stop()

# =========================
# VERIFICAÇÃO
# =========================

if not os.path.exists(
    "resultado_modelo.xlsx"
):

    st.error(
        "Arquivo não encontrado"
    )

    st.stop()

# =========================
# LEITURA
# =========================

df = pd.read_excel(
    "resultado_modelo.xlsx"
)

# =========================
# DATA
# =========================

df['Data'] = pd.to_datetime(
    df['Data']
)

df['Data_str'] = (
    df['Data']
    .dt.strftime('%d/%m/%Y')
)

# =========================
# HORA
# =========================

df['Hora'] = (

    df['Hora']
    .astype(str)
    .str.slice(0, 5)
)

# =========================
# PLACAR
# =========================

df['Placar'] = (

    df['Placar']
    .astype(str)
    .str.strip()
)

df['Placar'] = (

    df['Placar']
    .replace("-", "🔮")
)

# =========================
# PROBABILIDADE
# =========================

df['Probabilidade (%)'] = (

    df['Probabilidade']
    .astype(float)
    * 100

).round(2)

# =========================
# RESULTADO VISUAL
# =========================

def resultado_flag(placar):

    if placar == "🔮":

        return "🔮"

    try:

        gols = int(

            placar
            .split('x')[0]
            .strip()
        )

        return (

            "🟢 V"

            if gols > 0

            else "🔴 X"
        )

    except:

        return ""

df['Resultado'] = (

    df['Placar']
    .apply(resultado_flag)
)

# =========================
# NORMALIZAR
# =========================

def normalizar_placar(placar):

    placar = (
        str(placar)
        .strip()
        .lower()
    )

    if not placar:

        return None

    m = re.match(

        r"^\s*(\d+)\D+(\d+)\s*$",

        placar
    )

    if not m:

        return None

    a, b = m.groups()

    return f"{int(a)} x {int(b)}"

# =========================
# HOJE
# =========================

hoje_br = (
    datetime.utcnow() - timedelta(hours=3)
)

hoje_str = hoje_br.strftime(
    '%d/%m/%Y'
)

# =========================
# ABAS
# =========================

tab1, tab2, tab3, tab4 = st.tabs([

    "⚽ Jogos do Dia",

    "🧠 Análise Manual",

    "⚽ Placares Processados",

    "🏆 Ligas + Tabelas"
])

# =========================
# TAB 1
# =========================

with tab1:

    st.subheader("📅 Jogos do Dia")

    # =========================
    # SESSION
    # =========================

    if "analise_jogo" not in st.session_state:

        st.session_state.analise_jogo = None

    # =========================
    # BUSCA
    # =========================

    busca_time = st.text_input(
        "🔎 Buscar Time",
        key="tab1_busca"
    )

    filtro_oportunidade = st.selectbox(

        "🎯 Filtrar Oportunidades",

        [

            "Todos",

            "🔥 ELITE 0x1",
            "🔥 ELITE 1x0",

            "🚀 TOP 0x1",
            "🚀 TOP 1x0",

            "✅ BOM 0x1",
            "✅ BOM 1x0",

            "⚠️ MÉDIO 0x1",
            "⚠️ MÉDIO 1x0"
        ],

        key="tab1_filtro"
    )

    # =========================
    # JOGOS FUTUROS
    # =========================

    df_jogos = df[

        df['Placar'] == "🔮"

    ].copy()

    # =========================
    # BUSCA
    # =========================

    if busca_time:

        df_jogos = df_jogos[

            df_jogos['Time Casa']
            .astype(str)
            .str.lower()
            .str.contains(
                busca_time.lower(),
                na=False
            )

            |

            df_jogos['Time Visitante']
            .astype(str)
            .str.lower()
            .str.contains(
                busca_time.lower(),
                na=False
            )
        ]

    # =========================
    # ORDENA
    # =========================

    df_jogos = df_jogos.sort_values(

        by='Probabilidade (%)',

        ascending=False
    )

    # =========================
    # LOOP
    # =========================

    for _, row in df_jogos.iterrows():

        liga = row['Liga']

        casa = row['Time Casa']

        fora = row['Time Visitante']

        prob = row['Probabilidade (%)']

        hora = row['Hora']

        jogo_id = f"{casa}_{fora}"

        # =========================
        # RANGE 0x1
        # =========================

        min_range_0x1 = int(prob)

        max_range_0x1 = 100

        df_range_0x1 = df[

            (df['Probabilidade (%)'] >= min_range_0x1) &

            (df['Probabilidade (%)'] <= max_range_0x1) &

            (df['Placar'] != "🔮")

        ].copy()

        # =========================
        # RANGE 1x0
        # =========================

        min_range_1x0 = 0

        max_range_1x0 = int(prob)

        df_range_1x0 = df[

            (df['Probabilidade (%)'] >= min_range_1x0) &

            (df['Probabilidade (%)'] <= max_range_1x0) &

            (df['Placar'] != "🔮")

        ].copy()

        # =========================
        # 0x1
        # =========================

        total_jogos_0x1 = len(
            df_range_0x1
        )

        total_0x1 = len(

            df_range_0x1[
                df_range_0x1['Placar'] == "0 x 1"
            ]
        )

        pct_0x1 = (

            total_0x1 / total_jogos_0x1 * 100

        ) if total_jogos_0x1 > 0 else 0

        lay_0x1 = 100 - pct_0x1

        # =========================
        # 1x0
        # =========================

        total_jogos_1x0 = len(
            df_range_1x0
        )

        total_1x0 = len(

            df_range_1x0[
                df_range_1x0['Placar'] == "1 x 0"
            ]
        )

        pct_1x0 = (

            total_1x0 / total_jogos_1x0 * 100

        ) if total_jogos_1x0 > 0 else 0

        lay_1x0 = 100 - pct_1x0

        # =========================
        # STATUS
        # =========================

        status_0x1 = ""

        status_1x0 = ""

        # =========================
        # ELITE GLOBAL
        # =========================

        if lay_0x1 >= 99:

            status_0x1 = "🔥 ELITE 0x1"

        if lay_1x0 >= 99:

            status_1x0 = "🔥 ELITE 1x0"

        # =========================
        # FAIXA 93-100
        # =========================

        if prob >= 93:

            if not status_0x1:

                if lay_0x1 >= 96:

                    status_0x1 = "🚀 TOP 0x1"

                elif lay_0x1 >= 91:

                    status_0x1 = "✅ BOM 0x1"

            if not status_1x0:

                if lay_1x0 >= 96:

                    status_1x0 = "🚀 TOP 1x0"

                elif lay_1x0 >= 91:

                    status_1x0 = "✅ BOM 1x0"

        # =========================
        # FAIXA 90-92
        # =========================

        elif prob >= 90:

            if not status_0x1:

                if lay_0x1 >= 98:

                    status_0x1 = "🚀 TOP 0x1"

                elif lay_0x1 >= 95:

                    status_0x1 = "✅ BOM 0x1"

                elif lay_0x1 >= 91:

                    status_0x1 = "⚠️ MÉDIO 0x1"

            if not status_1x0:

                if lay_1x0 >= 98:

                    status_1x0 = "🚀 TOP 1x0"

                elif lay_1x0 >= 95:

                    status_1x0 = "✅ BOM 1x0"

                elif lay_1x0 >= 91:

                    status_1x0 = "⚠️ MÉDIO 1x0"

                # =========================
        # FILTRO
        # =========================

        mostrar = False

        if filtro_oportunidade == "Todos":

            mostrar = True

        elif filtro_oportunidade == status_0x1:

            mostrar = True

        elif filtro_oportunidade == status_1x0:

            mostrar = True

        if not mostrar:

            continue

        # =========================
        # CARD
        # =========================

        with st.container(border=True):

            st.markdown(
                f"### ⚽ {casa} x {fora}"
            )

            st.write(
                f"🏆 {liga}"
            )

            st.write(
                f"🕒 {hora}"
            )

            st.write(
                f"📊 {prob:.2f}%"
            )

            if status_0x1:

                st.success(status_0x1)

            if status_1x0:

                st.success(status_1x0)

            # =========================
            # BOTÃO
            # =========================

            if st.button(

                "🔍 Análise Completa",

                key=jogo_id
            ):

                st.session_state.analise_jogo = jogo_id

            # =========================
            # ABRIR
            # =========================

            if st.session_state.analise_jogo == jogo_id:

                st.divider()

                st.subheader(
                    "📊 Análise Completa"
                )

                if st.button(

                    "❌ Fechar Análise",

                    key=f"fechar_{jogo_id}"
                ):

                    st.session_state.analise_jogo = None

                    st.rerun()

                st.write(
                    f"📚 {total_jogos_0x1} jogos analisados 0x1"
                )

                st.write(
                    f"0x1 → {total_0x1} vezes ({pct_0x1:.2f}%)"
                )

                st.write(
                    f"📚 {total_jogos_1x0} jogos analisados 1x0"
                )

                st.write(
                    f"1x0 → {total_1x0} vezes ({pct_1x0:.2f}%)"
                )

                # =========================
                # PREVISÃO
                # =========================

                def extrair_gols(
                    lista,
                    lado
                ):

                    gols = []

                    for linha in lista:

                        p = normalizar_placar(
                            linha
                        )

                        if p:

                            a, b = map(

                                int,

                                p.split(" x ")
                            )

                            if lado == "casa":

                                gols.append(a)

                            else:

                                gols.append(b)

                    return gols

                lista_casa = df[

                    (df['Time Casa'] == casa) &

                    (df['Placar'] != "🔮")

                ]['Placar'].tolist()

                lista_fora = df[

                    (df['Time Visitante'] == fora) &

                    (df['Placar'] != "🔮")

                ]['Placar'].tolist()

                gols_casa = extrair_gols(
                    lista_casa,
                    "casa"
                )

                gols_fora = extrair_gols(
                    lista_fora,
                    "fora"
                )

                if gols_casa and gols_fora:

                    freq_casa = Counter(
                        gols_casa
                    )

                    freq_fora = Counter(
                        gols_fora
                    )

                    total_casa = sum(
                        freq_casa.values()
                    )

                    total_fora = sum(
                        freq_fora.values()
                    )

                    prob_casa = {

                        g: freq_casa[g] / total_casa

                        for g in freq_casa
                    }

                    prob_fora = {

                        g: freq_fora[g] / total_fora

                        for g in freq_fora
                    }

                    resultados = []

                    for g1 in prob_casa:

                        for g2 in prob_fora:

                            probabilidade = (

                                prob_casa[g1] *

                                prob_fora[g2]
                            )

                            resultados.append(

                                (
                                    f"{g1} x {g2}",
                                    probabilidade
                                )
                            )

                    resultados = sorted(

                        resultados,

                        key=lambda x: x[1],

                        reverse=True
                    )

                    st.markdown(
                        "### ⚽ Previsão de Placares"
                    )

                    for placar, probabilidade in resultados[:10]:

                        st.write(
                            f"{placar} → {probabilidade*100:.2f}%"
                        )

                    st.warning(

                        "⚠️ Esses placares não são garantias de lucro. A previsão representa apenas tendências estatísticas do confronto."
                    )

# =========================
# TAB 2
# =========================

with tab2:

    st.subheader("🧠 Análise Manual")

    # =========================
    # SESSION RANGE
    # =========================

    if "manual_min" not in st.session_state:

        st.session_state.manual_min = 0

    if "manual_max" not in st.session_state:

        st.session_state.manual_max = 100

    if "manual_data_inicio" not in st.session_state:

        st.session_state.manual_data_inicio = (
        df['Data'].min().date()
    )

    if "manual_data_final" not in st.session_state:

        st.session_state.manual_data_final = (
            df['Data'].max().date()
        )

    # =========================
    # LIMPAR
    # =========================

    def limpar_range_manual():

        st.session_state.manual_min = 0

        st.session_state.manual_max = 100

        st.session_state.manual_casa = ""

        st.session_state.manual_fora = ""

        st.session_state.manual_data_inicio = (
            df['Data'].min().date()
        )

        st.session_state.manual_data_final = (
            df['Data'].max().date()
        )

    # =========================
    # FILTROS
    # =========================

    c1, c2 = st.columns(2)

    with c1:

        filtro_casa = st.text_input(
            "🏠 Time Casa",
            key="manual_casa"
        )

    with c2:

        filtro_fora = st.text_input(
            "✈️ Time Fora",
            key="manual_fora"
        )

    

    # =========================
    # DATAS
    # =========================

    d1, d2 = st.columns(2)

    with d1:

        data_inicio = st.date_input(
            "📅 Data Inicial",
            value=df['Data'].min().date(),
            format="DD/MM/YYYY"
        )

    with d2:

        data_final = st.date_input(
            "📅 Data Final",
            value=df['Data'].max().date(),
            format="DD/MM/YYYY"
        )

    # =========================
    # RANGE
    # =========================

    r1, r2 = st.columns(2)

    with r1:

        min_range = st.number_input(
            "Range mínimo (%)",
            0,
            100,
            key="manual_min"
        )

    with r2:

        max_range = st.number_input(
            "Range máximo (%)",
            0,
            100,
            key="manual_max"
        )

    # =========================
    # HOJE
    # =========================

    hoje = datetime.today().date()

    # =========================
    # BOTÕES
    # =========================

    b1, b2, b3 = st.columns(3)

    with b1:

        aplicar = st.button(
            "🔍 Aplicar Filtros",
            use_container_width=True,
            key="manual_aplicar"
        )

    with b2:

        limpar = st.button(
            "🧹 Limpar Filtros",
            use_container_width=True,
            key="manual_limpar",
            on_click=limpar_range_manual
        )

    with b3:

        hoje_btn = st.button(
            "📅 Jogos de Hoje",
            use_container_width=True,
            key="manual_hoje"
        )

    if hoje_btn:

        data_inicio = hoje

        data_final = hoje

    st.divider()

    # =========================
    # DF MANUAL
    # =========================

    df_manual = df.copy()

    df_manual = df_manual[

        (df_manual['Probabilidade (%)'] >= min_range) &

        (df_manual['Probabilidade (%)'] <= max_range)
    ]

    df_manual = df_manual[

        (df_manual['Data'].dt.date >= data_inicio) &

        (df_manual['Data'].dt.date <= data_final)
    ]

    if filtro_casa:

        df_manual = df_manual[

            df_manual['Time Casa']
            .astype(str)
            .str.lower()
            .str.contains(
                filtro_casa.lower(),
                na=False
            )
        ]

    if filtro_fora:

        df_manual = df_manual[

            df_manual['Time Visitante']
            .astype(str)
            .str.lower()
            .str.contains(
                filtro_fora.lower(),
                na=False
            )
        ]

    # =========================
    # MÉTRICAS
    # =========================

    df_passado = df_manual.copy()

    total = len(df_passado)

    total_0x1 = len(

        df_passado[
            df_passado['Placar'] == "0 x 1"
        ]
    )

    pct_0x1 = (

        total_0x1 / total * 100

    ) if total > 0 else 0

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Jogos",
            total
        )

    with c2:

        st.metric(
            "0x1",
            total_0x1
        )

    with c3:

        st.metric(
            "Taxa 0x1",
            f"{pct_0x1:.2f}%"
        )

    # =========================
    # PROCESSAR
    # =========================

    if st.button(

        "⚽ Processar Placares",

        use_container_width=True
    ):

        placares_processados = df_manual[

            df_manual['Placar'] != "🔮"

        ]['Placar'].dropna().tolist()

        st.session_state[
            "placares_processados"
        ] = placares_processados

        st.success(
            "Placares processados"
        )

    # =========================
    # RESULTADO VISUAL
    # =========================

    df_manual['Green/Red'] = (
        df_manual['Resultado']
    )

    # =========================
    # TABELA
    # =========================

    st.dataframe(

        df_manual[[

            'Liga',
            'Data_str',
            'Hora',
            'Time Casa',
            'Time Visitante',
            'Placar',
            'Green/Red',
            'Probabilidade (%)'
        ]],

        use_container_width=True,
        hide_index=True
    )

# =========================
# TAB 3
# =========================

with tab3:

    st.subheader("⚽ Placares Processados")

    if "placares_processados" not in st.session_state:

        st.info(
            "Nenhum placar processado"
        )

    else:

        lista_placares = (

            st.session_state[
                "placares_processados"
            ]
        )

        # =========================
        # NORMALIZA
        # =========================

        placares_validos = []

        invalidos = 0

        for linha in lista_placares:

            p = normalizar_placar(
                linha
            )

            if p:

                placares_validos.append(p)

            else:

                invalidos += 1

        # =========================
        # VALIDAÇÃO
        # =========================

        if not placares_validos:

            st.warning(
                "Nenhum placar válido"
            )

        else:

            freq = Counter(
                placares_validos
            )

            total = sum(
                freq.values()
            )

            casa = []

            empate = []

            fora = []

            # =========================
            # CLASSIFICAR
            # =========================

            def classificar(placar):

                a, b = map(

                    int,

                    placar.split(" x ")
                )

                if a > b:

                    return "casa"

                elif a == b:

                    return "empate"

                else:

                    return "fora"

            # =========================
            # LOOP
            # =========================

            for placar, qtd in freq.items():

                perc = (
                    qtd / total
                ) * 100

                tipo = classificar(
                    placar
                )

                item = (
                    placar,
                    qtd,
                    perc
                )

                if tipo == "casa":

                    casa.append(item)

                elif tipo == "empate":

                    empate.append(item)

                else:

                    fora.append(item)

            # =========================
            # TOTAIS
            # =========================

            total_casa = sum(
                q for _, q, _ in casa
            )

            total_empate = sum(
                q for _, q, _ in empate
            )

            total_fora = sum(
                q for _, q, _ in fora
            )

            # =========================
            # ORDENAÇÃO
            # =========================

            casa = sorted(

                casa,

                key=lambda x: x[1],

                reverse=True
            )

            empate = sorted(

                empate,

                key=lambda x: x[1],

                reverse=True
            )

            fora = sorted(

                fora,

                key=lambda x: x[1],

                reverse=True
            )

            # =========================
            # MÉTRICAS
            # =========================

            st.subheader(
                "📌 Resumo Geral"
            )

            r1, r2, r3 = st.columns(3)

            with r1:

                st.metric(

                    "🏠 Casa",

                    f"{total_casa}",

                    f"{(total_casa/total)*100:.2f}%"
                )

            with r2:

                st.metric(

                    "🤝 Empate",

                    f"{total_empate}",

                    f"{(total_empate/total)*100:.2f}%"
                )

            with r3:

                st.metric(

                    "🚗 Fora",

                    f"{total_fora}",

                    f"{(total_fora/total)*100:.2f}%"
                )

            # =========================
            # LISTAS
            # =========================

            c1, c2, c3 = st.columns(3)

            with c1:

                st.subheader(
                    "🏠 Casa"
                )

                for p, q, pc in casa:

                    st.write(
                        f"{p} → {q} ({pc:.2f}%)"
                    )

            with c2:

                st.subheader(
                    "🤝 Empate"
                )

                for p, q, pc in empate:

                    st.write(
                        f"{p} → {q} ({pc:.2f}%)"
                    )

            with c3:

                st.subheader(
                    "🚗 Fora"
                )

                for p, q, pc in fora:

                    st.write(
                        f"{p} → {q} ({pc:.2f}%)"
                    )

            st.success(

                f"Total válido: {total} | Inválidos: {invalidos}"
            )

    # =========================
    # PREVISÃO MANUAL
    # =========================

    st.divider()

    st.header(
        "📊 Previsão Manual"
    )

    if "lista_casa" not in st.session_state:

        st.session_state.lista_casa = ""

    if "lista_fora" not in st.session_state:

        st.session_state.lista_fora = ""

    b1, b2 = st.columns(2)

    with b1:

        gerar = st.button(
            "Gerar previsão"
        )

    with b2:

        if st.button(
            "Limpar previsão"
        ):

            st.session_state.lista_casa = ""

            st.session_state.lista_fora = ""

            st.rerun()

    lista_casa = st.text_area(

        "Lista CASA:",

        height=150,

        key="lista_casa"
    )

    lista_fora = st.text_area(

        "Lista FORA:",

        height=150,

        key="lista_fora"
    )

    if gerar:

        def extrair_gols(lista):

            gols = []

            for linha in lista.splitlines():

                p = normalizar_placar(
                    linha
                )

                if p:

                    a, b = map(

                        int,

                        p.split(" x ")
                    )

                    gols.append(a)

            return gols

        gols_casa = extrair_gols(
            lista_casa
        )

        gols_fora = extrair_gols(
            lista_fora
        )

        if not gols_casa or not gols_fora:

            st.warning(
                "Preencha corretamente"
            )

        else:

            freq_casa = Counter(
                gols_casa
            )

            freq_fora = Counter(
                gols_fora
            )

            total_casa = sum(
                freq_casa.values()
            )

            total_fora = sum(
                freq_fora.values()
            )

            prob_casa = {

                g: freq_casa[g] / total_casa

                for g in freq_casa
            }

            prob_fora = {

                g: freq_fora[g] / total_fora

                for g in freq_fora
            }

            resultados = []

            for g1 in prob_casa:

                for g2 in prob_fora:

                    prob = (

                        prob_casa[g1] *

                        prob_fora[g2]
                    )

                    resultados.append(
                        (
                            f"{g1} x {g2}",
                            prob
                        )
                    )

            resultados = sorted(

                resultados,

                key=lambda x: x[1],

                reverse=True
            )

            st.subheader(
                "📊 Top placares previstos"
            )

            for placar, prob in resultados[:15]:

                st.write(
                    f"{placar} → {prob*100:.2f}%"
                )

# =========================
# TAB 4
# =========================

with tab4:

    st.subheader("🏆 Ligas + Tabelas")

    # =========================
    # LIGAS
    # =========================

    df_ligas = df[
        df['Placar'] != "🔮"
    ].copy()

    resumo = df_ligas.groupby('Liga').agg(

        Jogos=('Liga', 'count'),

        Erros_0x1=(

            'Placar',

            lambda x: (
                x == "0 x 1"
            ).sum()
        )

    ).reset_index()

    resumo['Taxa_0x1 (%)'] = (

        resumo['Erros_0x1']

        / resumo['Jogos']

        * 100

    ).round(2)

    resumo = resumo.sort_values(

        by='Jogos',

        ascending=False
    )

    st.dataframe(

        resumo,

        use_container_width=True,
        hide_index=True
    )

    # =========================
    # SELECT LIGA
    # =========================

    liga_selecionada = st.selectbox(

        "Selecionar Liga",

        options=resumo['Liga']
    )

    # =========================
    # DF DETALHE
    # =========================

    df_detalhe = df[

        df['Liga'] == liga_selecionada
    ]

    colunas = [

        'Data_str',
        'Hora',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Resultado',
        'Probabilidade (%)'
    ]

    st.subheader(

        f"📊 Jogos da liga: {liga_selecionada}"
    )

    st.dataframe(

        df_detalhe[colunas].sort_values(

            by='Probabilidade (%)',

            ascending=False
        ),

        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 0X1
    # =========================

    df_0x1 = df_detalhe[

        df_detalhe['Placar'] == "0 x 1"
    ]

    st.subheader(
        "❌ Jogos que terminaram 0 x 1"
    )

    if len(df_0x1) > 0:

        st.dataframe(

            df_0x1[colunas].sort_values(

                by='Probabilidade (%)',

                ascending=False
            ),

            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Nenhum jogo 0x1 nessa liga"
        )

    st.divider()

    # =========================
    # SOFASCORE
    # =========================

    st.subheader("📋 Tabelas SofaScore")

    tabelas = {

        "🇧🇷 Brasileirão Série A":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/83/season/87678/standings/Brasileiro%20Serie%20A%202026?widgetTitle=Brasileiro%20Serie%20A%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇧🇷 Brasileirão Série B":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/1449/season/89840/standings/Brasileiro%20Serie%20B%202026?widgetTitle=Brasileiro%20Serie%20B%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇦🇷 Argentina":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/143625/season/87913/standings/Apertura%2C%20Group%20B?widgetTitle=Apertura%2C%20Group%20B&showCompetitionLogo=true&widgetTheme=dark",

        "🇨🇳 China":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/652/season/90049/standings/Chinese%20Super%20League%202026?widgetTitle=Chinese%20Super%20League%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇨🇴 Colômbia A":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/19232/season/88503/standings/Apertura?widgetTitle=Apertura&showCompetitionLogo=true&widgetTheme=dark",

        "🇨🇴 Colômbia B":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/57659/season/89001/standings/Apertura?widgetTitle=Apertura&showCompetitionLogo=true&widgetTheme=dark",

        "🇫🇮 Finlândia":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/31/season/87930/standings/Veikkausliiga%202026?widgetTitle=Veikkausliiga%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇰🇷 Coreia":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/3284/season/88606/standings/K-League%201%202026?widgetTitle=K-League%201%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇳🇴 Noruega Elite":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/5/season/87809/standings/Eliteserien%202026?widgetTitle=Eliteserien%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇳🇴 Noruega 1":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/6/season/87867/standings/1.%20Division%202026?widgetTitle=1.%20Division%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇵🇾 Paraguai":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/3133/season/69799/standings/Division%20de%20Honor%2C%20Apertura?widgetTitle=Division%20de%20Honor%2C%20Apertura&showCompetitionLogo=true&widgetTheme=dark",

        "🇮🇪 Irlanda":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/718/season/87698/standings/First%20Division%202026?widgetTitle=First%20Division%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇸🇪 Allsvenskan":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/24/season/87925/standings/Allsvenskan%202026?widgetTitle=Allsvenskan%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇸🇪 Superettan":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/27/season/87924/standings/Superettan%202026?widgetTitle=Superettan%202026&showCompetitionLogo=true&widgetTheme=dark",

        "🇺🇾 Uruguai":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/57657/season/89288/standings/Primera%20Division%202026%2C%20Overall?widgetTitle=Primera%20Division%202026%2C%20Overall&showCompetitionLogo=true&widgetTheme=dark"
    }

    col1, col2 = st.columns([1, 5])

    with col1:

        liga_escolhida = st.radio(

            "Ligas",

            list(tabelas.keys())
        )

    with col2:

        iframe = tabelas[
            liga_escolhida
        ]

        codigo = f'''
        <iframe
        src="{iframe}"
        style="height:1123px!important;width:100%!important;border:none;"
        scrolling="no">
        </iframe>
        '''

        components.html(
            codigo,
            height=1150
        )