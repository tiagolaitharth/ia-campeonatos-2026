import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

st.title("📊 IA - Campeonatos 2026")

# =========================
# VERIFICAÇÃO
# =========================

if not os.path.exists("resultado_modelo.xlsx"):
    st.error("Arquivo não encontrado. Rode primeiro o modelo.py")
    st.stop()

df = pd.read_excel("resultado_modelo.xlsx")

# =========================
# TRATAMENTO
# =========================

df['Data'] = pd.to_datetime(df['Data'])
df['Data_str'] = df['Data'].dt.strftime('%d/%m/%Y')

df['Placar'] = df['Placar'].astype(str).str.strip()
df['Placar'] = df['Placar'].replace("-", "🔮")

df['Probabilidade (%)'] = (df['Probabilidade'] * 100).round(2)

# =========================
# RESULTADO VISUAL
# =========================

def resultado_flag(placar):
    if placar == "🔮":
        return "🔮"
    try:
        gols = int(placar.split('x')[0].strip())
        return "🟢 V" if gols > 0 else "🔴 X"
    except:
        return ""

df['Resultado'] = df['Placar'].apply(resultado_flag)

# =========================
# DATA HOJE
# =========================

hoje_str = datetime.today().strftime('%d/%m/%Y')

# =========================
# ABAS
# =========================

tab1, tab2, tab3 = st.tabs([
    "📊 Análise Geral",
    "🏆 Ligas",
    "📋 Tabelas"
])

# =========================
# ABA 1
# =========================

with tab1:

    if "min_prob" not in st.session_state:
        st.session_state.min_prob = 0
    if "max_prob" not in st.session_state:
        st.session_state.max_prob = 100
    if "slider_range" not in st.session_state:
        st.session_state.slider_range = (0, 100)

    if "busca_casa" not in st.session_state:
        st.session_state.busca_casa = ""
    if "busca_visit" not in st.session_state:
        st.session_state.busca_visit = ""
    if "busca_data" not in st.session_state:
        st.session_state.busca_data = ""

    def update_from_slider():
        st.session_state.min_prob = st.session_state.slider_range[0]
        st.session_state.max_prob = st.session_state.slider_range[1]

    def update_from_input():
        st.session_state.slider_range = (
            st.session_state.min_prob,
            st.session_state.max_prob
        )

    def limpar_range():
        st.session_state.slider_range = (0, 100)
        st.session_state.min_prob = 0
        st.session_state.max_prob = 100

    def limpar_filtros():
        st.session_state.busca_casa = ""
        st.session_state.busca_visit = ""
        st.session_state.busca_data = ""

    # SIDEBAR
    st.sidebar.header("Filtros")

    st.sidebar.slider(
        "Probabilidade (%)",
        0, 100,
        st.session_state.slider_range,
        key="slider_range",
        on_change=update_from_slider
    )

    st.sidebar.number_input("Min", 0, 100, key="min_prob", on_change=update_from_input)
    st.sidebar.number_input("Max", 0, 100, key="max_prob", on_change=update_from_input)

    st.sidebar.button("🔄 Limpar Range", on_click=limpar_range)

    threshold_min = st.session_state.min_prob
    threshold_max = st.session_state.max_prob

    st.sidebar.subheader("Filtros Avançados")

    todos_times = sorted(set(df['Time Casa']).union(set(df['Time Visitante'])))
    times_sidebar = st.sidebar.multiselect("Times", options=todos_times)

    todas_ligas = sorted(df['Liga'].dropna().unique())
    ligas_sidebar = st.sidebar.multiselect("Ligas", options=todas_ligas)

    placares = sorted(df['Placar'].dropna().unique())
    placar_sidebar = st.sidebar.multiselect("Placar", options=placares)

    # FILTRO BASE
    df_filtrado = df[
        (df['Probabilidade'] >= threshold_min / 100) &
        (df['Probabilidade'] <= threshold_max / 100)
    ]

    if times_sidebar:
        df_filtrado = df_filtrado[
            df_filtrado['Time Casa'].isin(times_sidebar) |
            df_filtrado['Time Visitante'].isin(times_sidebar)
        ]

    if ligas_sidebar:
        df_filtrado = df_filtrado[df_filtrado['Liga'].isin(ligas_sidebar)]

    if placar_sidebar:
        df_filtrado = df_filtrado[df_filtrado['Placar'].isin(placar_sidebar)]

    # FILTROS TABELA
    st.subheader("🔎 Filtros da tabela")

    c1, c2, c3, c4 = st.columns([1,1,1,1])

    c1.text_input("Time Casa", key="busca_casa")
    c2.text_input("Time Visitante", key="busca_visit")
    c3.text_input("Data", key="busca_data")

    c4.button("🔄 Limpar", on_click=limpar_filtros)

    def aplicar(df):
        if st.session_state.busca_casa:
            df = df[df['Time Casa'].str.contains(st.session_state.busca_casa, case=False)]
        if st.session_state.busca_visit:
            df = df[df['Time Visitante'].str.contains(st.session_state.busca_visit, case=False)]
        if st.session_state.busca_data:
            df = df[df['Data_str'].str.contains(st.session_state.busca_data)]
        return df

    df_filtrado = aplicar(df_filtrado)

    # MÉTRICAS
    df_passado = df_filtrado[df_filtrado['Placar'] != "🔮"]
    df_0x1 = df_passado[df_passado['Placar'] == "0 x 1"]

    total = len(df_passado)
    erros_0x1 = len(df_0x1)
    taxa_0x1 = (erros_0x1 / total * 100) if total > 0 else 0

    st.markdown("### 📊 Resultado do filtro atual")

    col1, col2, col3 = st.columns(3)
    col1.metric("Jogos no filtro", total)
    col2.metric("0x1", erros_0x1)
    col3.metric("Taxa 0x1", f"{taxa_0x1:.2f}%")

    # TABELA PRINCIPAL
    colunas = [
        'Liga',
        'Data_str',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Resultado',
        'Probabilidade (%)'
    ]

    st.dataframe(
        df_filtrado[colunas].sort_values(
            by='Probabilidade (%)',
            ascending=False
        ),
        use_container_width=True
    )

    # =========================
    # JOGOS DE HOJE
    # =========================

    df_hoje = df[df['Data_str'] == hoje_str]
    df_hoje_futuro = df_hoje[df_hoje['Placar'] == "🔮"]

    st.subheader("📅 Jogos de Hoje")

    if len(df_hoje_futuro) > 0:
        st.dataframe(
            df_hoje_futuro[colunas].sort_values(
                by='Probabilidade (%)',
                ascending=False
            ),
            use_container_width=True
        )
    else:
        st.info("Nenhum jogo futuro hoje")

# =========================
# ABA 2 (LIGAS)
# =========================

with tab2:

    st.subheader("🏆 Análise por Ligas")

    df_ligas = df[df['Placar'] != "🔮"].copy()

    resumo = df_ligas.groupby('Liga').agg(
        Jogos=('Liga', 'count'),
        Erros_0x1=('Placar', lambda x: (x == "0 x 1").sum())
    ).reset_index()

    resumo['Taxa_0x1 (%)'] = (
        resumo['Erros_0x1'] / resumo['Jogos'] * 100
    ).round(2)

    resumo = resumo.sort_values(by='Jogos', ascending=False)

    st.dataframe(resumo, use_container_width=True)

    liga_selecionada = st.selectbox(
        "Selecionar Liga",
        options=resumo['Liga']
    )

    df_detalhe = df[df['Liga'] == liga_selecionada]

    colunas = [
        'Data_str',
        'Time Casa',
        'Time Visitante',
        'Placar',
        'Resultado'
    ]

    st.subheader(f"📊 Todos os jogos da liga: {liga_selecionada}")

    st.dataframe(
        df_detalhe[colunas].sort_values(
            by='Data_str',
            ascending=False
        ),
        use_container_width=True
    )

    df_0x1 = df_detalhe[df_detalhe['Placar'] == "0 x 1"]

    st.subheader("❌ Jogos que terminaram 0 x 1")

    if len(df_0x1) > 0:
        st.dataframe(
            df_0x1[colunas].sort_values(
                by='Data_str',
                ascending=False
            ),
            use_container_width=True
        )
    else:
        st.info("Nenhum jogo 0x1 nessa liga 👍")

# =========================
# ABA 3 (TABELAS)
# =========================

# =========================
# ABA 3 (CLASSIFICAÇÕES)
# =========================

with tab3:

    st.subheader("📋 Classificação Geral")

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

        "🇸🇪 Ettan Norra":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/174277/season/89299/standings/Ettan%202026%2C%20Norra?widgetTitle=Ettan%202026%2C%20Norra&showCompetitionLogo=true&widgetTheme=dark",

        "🇸🇪 Ettan Sodra":
        "https://widgets.sofascore.com/pt-BR/embed/tournament/174278/season/89299/standings/Ettan%202026%2C%20Sodra?widgetTitle=Ettan%202026%2C%20Sodra&showCompetitionLogo=true&widgetTheme=dark",

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

        iframe = tabelas[liga_escolhida]

        codigo = f"""
        <iframe
        src="{iframe}"
        style="height:1123px!important;width:100%!important;border:none;"
        scrolling="no">
        </iframe>
        """

        components.html(codigo, height=1150)