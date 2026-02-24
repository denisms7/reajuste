import streamlit as st
import pandas as pd
import plotly.express as px
from map.map import Mapa

# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(
    page_title="Reposição Salarial",
    page_icon="🧑🏻‍💼",
    layout="wide"
)


st.title("🧑🏻‍💼 Reposição Salarial")
st.subheader("Análise de dados salarial regional")


if "toast_mostrado" not in st.session_state:
    st.toast("Todos os componentes deste painel são interativos")
    st.session_state.toast_mostrado = True


# -------------------------------------------------
# Carregar dados
# -------------------------------------------------
@st.cache_data
def load_data():
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

    df = df.drop(columns=["Outros"])

    return df


with st.spinner("⌛ Carregando dados..."):
    df = load_data()

# -------------------------------------------------
# Filtrar período
# -------------------------------------------------
st.sidebar.subheader("🎯 Filtros", divider=True)

ano_min = int(df["Ano"].min())
ano_max = int(df["Ano"].max())

ano_inicio, ano_fim = st.sidebar.slider(
    "Intervalo de anos:",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, 2025),
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
    "Descrição:",
    options=opcoes_descricao,
    default=[],
    placeholder="Todos Dados",
)

# Se nenhuma descrição for selecionada, mantém todos os dados
if descricoes_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado["Descricao"].isin(descricoes_selecionadas)
    ]

df_tratado = df_filtrado[["Descricao", "Ano", "Valor", "Fonte"]]


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
    title="Reajustes",
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


# -------------------------------------------------
# Gráfico de barras composição
# -------------------------------------------------
df_agrupado2 = (
    df_filtrado
    .groupby(["Descricao", "Ano"], as_index=False)["Valor"]
    .sum()
)

df_merge = df_agrupado2.merge(
    df_agrupado,
    on="Descricao",
    how="left",
    suffixes=("", "_Total")
)

df_merge = df_merge.sort_values(by=["Valor_Total", "Ano"], ascending=False)


fig_bar2 = px.bar(
    df_merge,
    x="Descricao",
    y="Valor",
    color="Descricao",
    text_auto=".2f",
    title="Composição do Acúmulo",
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
    legend_title="Descrição",
)

fig_bar2.update_yaxes(
    ticksuffix="%",
    tickformat=".2f"
)


# -------------------------------------------------
# GERAR PAGINA
# -------------------------------------------------
opcao = st.segmented_control(
    "Visualização:",
    options=["📄 Fonte de Dados", "🗺️ Municípios Selecionados"],
    default="📄 Fonte de Dados",
)

if opcao == "🗺️ Municípios Selecionados":
    fig_mapa = Mapa(df_filtrado)
    st.plotly_chart(fig_mapa, width="stretch")
else:
    st.dataframe(
        df_tratado,
        width="stretch",
        hide_index=True,
        column_config={
            "Descricao": st.column_config.TextColumn(
                "Descrição"
            ),
            "Ano": st.column_config.NumberColumn(
                "Ano"
            ),
            "Valor": st.column_config.NumberColumn(
                "Valor (%)",
                format="%.2f",
            ),
            "Fonte": st.column_config.LinkColumn(
                "Fonte",
                display_text="🔗 Abrir",
            ),
        },
    )

st.plotly_chart(fig_linhas, width="stretch")



opcao2 = st.segmented_control(
    "Visualização:",
    options=["📈 Acumulados dos Reajustes", "🧩 Composição do Acúmulo"],
    default="📈 Acumulados dos Reajustes",
)


if opcao2 == "📈 Acumulados dos Reajustes":
    st.plotly_chart(fig_bar, width="stretch")
else:
    st.plotly_chart(fig_bar2, use_container_width=True)




# -------------------------------------------------
# Informações adicionais
# -------------------------------------------------
st.info(
    """
    **📌 Critério de vinculação do IPCA ao ano do reajuste**

    O índice de variação do IPCA apresentado neste painel refere-se
    ao **ano de apuração da inflação**, enquanto o **reajuste salarial**
    ocorre **no exercício seguinte**.

    Para alinhar a análise ao ano em que o reajuste foi efetivamente aplicado,
    adotou-se o seguinte critério:

    - O **IPCA apurado em determinado ano (ex.: 2019)** é considerado
      como referência para o **reajuste concedido no ano subsequente (ex.: 2020)**.

    Assim, neste painel:
    - O IPCA originalmente apurado em **2019** é exibido como **IPCA de 2020**;
    - O IPCA de **2020** é exibido como **2021**, e assim sucessivamente.

    Esse procedimento assegura que o índice inflacionário esteja associado
    ao **mesmo exercício financeiro do reajuste**, proporcionando uma
    comparação mais coerente entre **inflação** e **reajuste salarial**.
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


st.sidebar.subheader("📦 Exportar Dados", divider=True)


st.sidebar.download_button(
    label="📥 Dados Brutos",
    data=dataframe_to_csv(df),
    file_name="Reajustes.csv",
    mime="text/csv",
)
