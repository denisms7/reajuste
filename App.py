import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Reposição Salarial",
    page_icon="🧑🏻‍💼",
    layout="wide"
)

st.title("📊 Reposição Salarial")
st.write("Análise de dados salarial regional")


# -------------------------------------------------
# Carregar dados
# -------------------------------------------------
df = pd.read_excel("data/dados.xlsx")

df = df.dropna(subset=["Descricao"])

df["Descricao"] = df["Descricao"].astype(str)
df["Valor"] = df["Valor"].astype(str)

df[["Fonte", "Outros"]] = df[["Fonte", "Outros"]].fillna("")

df["Valor"] = (
    df["Valor"]
    .str.replace("%", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce") * 100
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")


df.loc[df["Descricao"] == "IPCA", "Ano"] = df.loc[df["Descricao"] == "IPCA", "Ano"] + 1


# -------------------------------------------------
# Filtrar período
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

ano_min = int(df["Ano"].min())
ano_max = int(df["Ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Selecione o intervalo de anos",
    min_value=ano_min,
    max_value=ano_max,
    value=(2020, 2025),
    step=1,
)


df_filtrado = df.loc[
    (df["Ano"] >= ano_inicio) & (df["Ano"] <= ano_fim)
]

# -------------------------------------------------
# Exibir dados tratados (com formatação visual)
# -------------------------------------------------
opcoes_descricao = sorted(
    df["Descricao"].dropna().unique().tolist()
)

descricoes_selecionadas = st.sidebar.multiselect(
    "Descrição",
    options=opcoes_descricao,
    default=[],
    placeholder="Todos Dados",
)

# Se nenhuma descrição for selecionada, mantém todos os dados
if descricoes_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado["Descricao"].isin(descricoes_selecionadas)
    ]


st.subheader("📄 Dados Tratados")

st.dataframe(
    df_filtrado,
    column_config={
        "Valor": st.column_config.NumberColumn(
            "Valor (%)",
            format="%.2f"
        ),
        "Fonte": st.column_config.LinkColumn(
            "Fonte",
            display_text="🔗 Abrir",
        ),
        "Outros": st.column_config.LinkColumn(
            "Outros",
            display_text="📄 Documento",
        ),
    },
    width="stretch",
)


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
    subtitle=f"Periodo: {ano_inicio} - {ano_fim}",
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

fig_linhas.update_traces(
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Ano: %{x}<br>"
        "Valor: %{y:.2f}%"
        "<extra></extra>"
    )
)

fig_linhas.update_xaxes(dtick=1)

st.plotly_chart(fig_linhas, width="stretch")


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
    subtitle=f"Periodo: {ano_inicio} - {ano_fim}",
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

fig_bar.update_traces(
    textposition="inside",
    texttemplate="%{y:.2f}%",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Valor: %{y:.2f}%"
        "<extra></extra>"
    )
)

st.plotly_chart(fig_bar, width="stretch")


# -------------------------------------------------
# Gráfico de barras composição
# -------------------------------------------------
df_agrupado2 = (
    df_filtrado
    .groupby(["Descricao", "Ano"], as_index=False)["Valor"]
    .sum()
)

df_agrupado2 = df_agrupado2.sort_values(by="Valor", ascending=False)


fig_bar2 = px.bar(
    df_agrupado2,
    x="Descricao",
    y="Valor",
    color="Descricao",
    text_auto=".2f",
    title="Composição do Acúmulo<br>",
    subtitle=f"Periodo: {ano_inicio} - {ano_fim}",
    custom_data=["Ano"],
)

fig_bar2.update_traces(
    textposition="inside",
    texttemplate="%{y:.2f}%",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Ano: %{customdata[0]}<br>"
        "Valor: %{y:.2f}%"
        "<extra></extra>"
    )
)

fig_bar2.update_layout(
    xaxis_title="Descrição",
    yaxis_title="Soma (%)",
    legend_title="Ano",
)

fig_bar2.update_yaxes(
    ticksuffix="%",
    tickformat=".2f"
)

st.plotly_chart(fig_bar2, use_container_width=True)



# -------------------------------------------------
# Informações adicionais
# -------------------------------------------------
st.info(
    """
    **📌 Critério de ajuste do IPCA no ano de referência**

    O índice de **Variação do IPCA** utilizado neste painel refere-se ao
    **ano de apuração da inflação**, enquanto o **reajuste salarial**
    ocorre **no ano subsequente**.

    Para tornar a análise mais didática e alinhada à realidade do reajuste
    salarial, foi adotado o seguinte critério:

    • O **IPCA de um determinado ano (ex.: 2019)** é considerado como
      referência para o **reajuste aplicado no ano seguinte (ex.: 2020)**.

    Dessa forma, neste painel:
    - O IPCA originalmente apurado em **2019** é apresentado como
      **IPCA de 2020**;
    - O IPCA de **2020** é apresentado como **2021**, e assim sucessivamente.

    Esse ajuste garante que o índice inflacionário esteja associado ao
    **mesmo ano em que o salário foi efetivamente reajustado**, permitindo
    uma comparação mais clara e coerente entre **inflação e reajuste
    salarial**.
    """
)


# -------------------------------------------------
# Exportar dados
# -------------------------------------------------
def dataframe_to_csv(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig"
    ).encode("utf-8-sig")


st.sidebar.subheader("Exportar Dados", divider=True)


st.sidebar.download_button(
    label="📥 Dados Brutos",
    data=dataframe_to_csv(df),
    file_name="Reajustes.csv",
    mime="text/csv",
)


# -------------------------------------------------
# Rodapé
# -------------------------------------------------
st.markdown(
    "<p style='text-align: center;'>Desenvolvido por Denis Muniz Silva</p>",
    unsafe_allow_html=True,
)
