import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

df = pd.read_excel(r"C:\Users\Pichau\OneDrive\Documentos\CAMP 2026.xlsx", header=9)

df_treino = df[df["Placar"] != "-"].copy()

df_futuros = df[df["Placar"] == "-"].copy()

saiu_gol = []

for i in range(len(df_treino)):

    placar = df_treino["Placar"].iloc[i]

    partes = placar.split(" x ")

    gols_casa = int(partes[0])
    gols_fora = int(partes[1])

    if gols_casa + gols_fora > 0:
        saiu_gol.append(1)
    else:
        saiu_gol.append(0)

df_treino["SAIU_GOL"] = saiu_gol


features = [

    "ODD CASA",
    "ODD FORA",
    "MÉDIA CHUTES NO GOL CASA",
    "MÉDIA CHUTES NO GOL FORA",
    "% Marca Gol Casa",
    "% Marca Gol Visit",
    "MÉDIA GOL A FAVOR CASA",
    "MÉDIA GOLS A FAVOR FORA",
    "MÉDIA GOLS CONTRA CASA",
    "MÉDIA GOLS CONTRA FORA"
]

X = df_treino[features]


y = df_treino["SAIU_GOL"]

# =========================
# TREINO E TESTE
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# PADRONIZAÇÃO
# =========================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

# =========================
# RANDOM FOREST
# =========================

modelo = RandomForestClassifier(
    n_estimators=500,
    random_state=42
)

modelo.fit(X_train, y_train)

# =========================
# PROBABILIDADES
# =========================

X_completo = scaler.transform(X)

probabilidades = modelo.predict_proba(X_completo)[:,1]

df_teste = pd.DataFrame()

df_teste["Probabilidade"] = probabilidades * 100

df_teste["SAIU_GOL"] = y.values

# =========================
# TABELA DE RANGES
# =========================

resumo = []

faixas = [

    (95, 100),
    (90, 95),
    (85, 90),
    (80, 85),
    (75, 80),
    (70, 75),
    (65, 70),
    (60, 65),
    (55, 60),
    (50, 55),
    (45, 50),
    (40, 45),
    (35, 40),
    (30, 35),
    (25, 30),
    (20, 25),
    (15, 20),
    (10, 15),
    (5, 10),
    (0, 5)

]

for minimo, maximo in faixas:

    df_faixa = df_teste[
        (df_teste["Probabilidade"] >= minimo)
        &
        (df_teste["Probabilidade"] < maximo)
    ]

    total = len(df_faixa)

    acertos = len(
        df_faixa[
            df_faixa["SAIU_GOL"] == 1
        ]
    )

    erros = len(
        df_faixa[
            df_faixa["SAIU_GOL"] == 0
        ]
    )

    taxa_acerto = (
        acertos / total * 100
    ) if total > 0 else 0

    resumo.append({

        "Range": f"{minimo}-{maximo}%",

        "Jogos": total,

        "Acertos": acertos,

        "0x0": erros,

        "Taxa Acerto (%)": round(
            taxa_acerto,
            2
        )

    })

df_resumo = pd.DataFrame(resumo)

# =========================
# JOGOS FUTUROS
# =========================

X_futuros = df_futuros[features]

X_futuros = scaler.transform(X_futuros)

df_futuros["Probabilidade (%)"] = modelo.predict_proba(X_futuros)[:,1] * 100

# =========================
# RANGE DOS JOGOS FUTUROS
# =========================

df_futuros["Range"] = "0-5%"

df_futuros.loc[df_futuros["Probabilidade (%)"] >= 5, "Range"] = "5-10%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 10, "Range"] = "10-15%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 15, "Range"] = "15-20%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 20, "Range"] = "20-25%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 25, "Range"] = "25-30%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 30, "Range"] = "30-35%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 35, "Range"] = "35-40%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 40, "Range"] = "40-45%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 45, "Range"] = "45-50%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 50, "Range"] = "50-55%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 55, "Range"] = "55-60%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 60, "Range"] = "60-65%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 65, "Range"] = "65-70%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 70, "Range"] = "70-75%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 75, "Range"] = "75-80%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 80, "Range"] = "80-85%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 85, "Range"] = "85-90%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 90, "Range"] = "90-95%"
df_futuros.loc[df_futuros["Probabilidade (%)"] >= 95, "Range"] = "95-100%"

# =========================
# EXPORTAR EXCEL
# =========================

resultado = df_futuros[[

    "Liga",
    "Data",
    "Hora",
    "Time Casa",
    "Time Visitante",
    "HT",
    "Placar",
    "Probabilidade (%)",
    "Range"

]]

with pd.ExcelWriter(
    "resultado_saiu_gol.xlsx"
) as writer:

    resultado.to_excel(
        writer,
        sheet_name="Jogos do Dia",
        index=False
    )

    df_resumo.to_excel(
        writer,
        sheet_name="Ranges",
        index=False
    )


