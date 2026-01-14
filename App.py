import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Reajustes Salariais",
    page_icon="🧑🏻‍💼",
    layout="wide"
)

st.title("📊 Reajustes Salariais")
st.write("Análise de dados salarial regional")

# -------------------------------------------------
# Carregar dados
# -------------------------------------------------
df = pd.read_excel("data/dados.xlsx")

# -------------------------------------------------
# Tratamento da coluna Valor (SEM arredondar dados)
# -------------------------------------------------
df["Valor"] = df["Valor"].astype(str)

df["Valor"] = (
    df["Valor"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce") * 100

# Garantir tipo correto do ano
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")

# -------------------------------------------------
# Filtrar período
# -------------------------------------------------
df_filtrado = df.loc[
    (df["Ano"] >= 2019) & (df["Ano"] <= 2025)
]

# -------------------------------------------------
# Exibir dados tratados (com formatação visual)
# -------------------------------------------------
st.subheader("📄 Dados tratados")

st.dataframe(
    df_filtrado,
    column_config={
        "Valor": st.column_config.NumberColumn(
            "Valor (%)",
            format="%.2f"
        ),
        "Fonte": st.column_config.LinkColumn(
            "Fonte",
            display_text="🔗 Abrir"
        ),
        "Outros": st.column_config.LinkColumn(
            "Outros",
            display_text="📄 Documento"
        ),
    },
    use_container_width=True,
)

# -------------------------------------------------
# Gráfico de barras (soma por descrição)
# -------------------------------------------------
df_agrupado = (
    df_filtrado
    .groupby("Descricao", as_index=False)["Valor"]
    .sum()
    .sort_values(by="Valor", ascending=False)
)

fig_bar = px.bar(
    df_agrupado,
    x="Descricao",
    y="Valor",
    color="Descricao",
    text_auto=".2f",
    title="Acumulados dos Reajustes",
    subtitle="IPCA - 2019 a 2025<br>Salarios 2020 a 2025",
)

fig_bar.update_layout(
    xaxis_title="Descrição",
    yaxis_title="Soma (%)",
    legend_title="Descrição",
)

fig_bar.update_yaxes(
    ticksuffix="%",
    tickformat=".2f"
)

st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------
# Gráfico de linhas (evolução por ano)
# -------------------------------------------------
df_linha = (
    df_filtrado
    .groupby(["Ano", "Descricao"], as_index=False)["Valor"]
    .sum()
)

fig_linhas = px.line(
    df_linha,
    x="Ano",
    y="Valor",
    color="Descricao",
    markers=True,
    title="Evolução dos Reajustes (2020–2025)",
    subtitle="IPCA - 2019 a 2025<br>Salarios 2020 a 2025",
)

fig_linhas.update_layout(
    xaxis_title="Ano",
    yaxis_title="Valor (%)",
    legend_title="Descrição",
)

fig_linhas.update_yaxes(
    ticksuffix="%",
    tickformat=".2f"
)

fig_linhas.update_xaxes(dtick=1)

st.plotly_chart(fig_linhas, use_container_width=True)
