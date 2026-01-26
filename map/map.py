import json
import streamlit as st
import plotly.express as px


# -------------------------------------------------
# MAPA - Destaque de Municípios
# -------------------------------------------------
def Mapa(df_filtrado):

    df_filtrado = df_filtrado.copy()

    map_json = "map/geojs-41-mun.json"

    if {"cod_ibge", "Descricao"}.issubset(df_filtrado.columns):

        df_mapa = (
            df_filtrado[["cod_ibge", "Descricao", "Populacao"]]
            .dropna(subset=["cod_ibge"])
            .drop_duplicates()
            .assign(dummy=1)  # coluna técnica
        )

        df_mapa["cod_ibge"] = df_mapa["cod_ibge"].astype("Int64")

        try:
            with open(map_json, encoding="utf-8") as f:
                geojson = json.load(f)

            fig_mapa = px.choropleth_mapbox(
                df_mapa,
                geojson=geojson,
                locations="cod_ibge",
                featureidkey="properties.id",
                color="dummy",
                hover_name="Descricao",
                hover_data={"Populacao": True, "dummy": False, "cod_ibge": False},
                color_continuous_scale=["#2a9d8f", "#2a9d8f"],
                mapbox_style="carto-positron",
                opacity=0.7,
            )

            fig_mapa.update_layout(
                margin=dict(r=0, t=0, l=0, b=0),
                height=600,
                coloraxis_showscale=False,  # remove legenda
            )

            fig_mapa.update_layout(
                mapbox=dict(
                    center={
                        "lat": -22.8207,
                        "lon": -51.5967,
                    },
                    zoom=8.5,  # ajuste conforme necessário
                )
            )

            fig_mapa.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>População: %{customdata[0]:,.0f}<extra></extra>"
            )

        except Exception as e:
            return st.error(f"❌ Erro ao carregar o mapa: {e}")

    else:
        return st.info("ℹ️ Necessário possuir as colunas 'cod_ibge' e 'Descricao'")

    return fig_mapa