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


df.loc[df["Descricao"] == "Variação do IPCA", "Ano"] = df.loc[df["Descricao"] == "Variação do IPCA", "Ano"] + 1

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
    value=(2019, 2025),
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

fig_linhas.update_xaxes(dtick=1)

st.plotly_chart(fig_linhas, use_container_width=True)



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

# Exportar dados filtrados
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
