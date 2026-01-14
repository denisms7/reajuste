import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Reajustes Salarial",
    page_icon="🧑🏻‍💼",
    layout="wide"
)

st.title("📊 Reajustes Salarial")
st.write("Aplicação de análise de dados salarial regional")

# Carregar dados
df = pd.read_excel("data/dados.xlsx")

# Garantir string
df["Valor"] = df["Valor"].astype(str)

# Limpeza de porcentagem
df["Valor"] = (
    df["Valor"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
)

# Converter para float
df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

# Filtrar anos
df_filtrado = df.loc[
    (df["Ano"] >= 2020) & (df["Ano"] <= 2025)
]

st.subheader("📄 Dados tratados (2020–2025)")
st.dataframe(df_filtrado)

# Agrupar
df_agrupado = (
    df_filtrado
    .groupby("Descricao", as_index=False)["Valor"]
    .sum()
    .sort_values(by="Valor", ascending=False)
)

# Gráfico
fig = px.bar(
    df_agrupado,
    x="Descricao",
    y="Valor",
    color="Descricao",
    text_auto=".2f",
    title="Porcentagem (2020–2025)",
    subtitle="Soma dos reajustes salariais",
)

fig.update_layout(
    xaxis_title="Descrição",
    yaxis_title="Soma (%)",
    legend_title="Descrição",
)

fig.update_yaxes(ticksuffix="%")

st.plotly_chart(fig, use_container_width=True)




# Grafico de linhas 


fig_linhas = px.line(
    df_filtrado,
    x="Ano",
    y="Valor",
    color="Descricao",
    markers=True,
    title="Evolução dos Reajustes (2020–2025)",
)

fig_linhas.update_layout(
    xaxis_title="Ano",
    yaxis_title="Valor (%)",
    legend_title="Descrição",
)

fig_linhas.update_yaxes(ticksuffix="%")

st.plotly_chart(fig_linhas, use_container_width=True)