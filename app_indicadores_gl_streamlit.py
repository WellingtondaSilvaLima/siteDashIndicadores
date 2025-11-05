import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
import plotly.graph_objects as go
from datetime import timedelta

ICON_PATH = Path(__file__).parent / "favicon-liliauto.ico"

st.set_page_config(
    page_title="Indicadores - Grupo Linhares",
    page_icon=str(ICON_PATH),
    layout="wide"
)

# caminhos das logos (troque pelos seus arquivos ou URLs)
LOGO_ESQ = Path(__file__).parent / "logo_grupo_linhares.png"
LOGO_DIR = Path(__file__).parent / "logo-liliauto.png"

# faixa de cabeçalho com duas logos e o título central
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    if LOGO_ESQ.exists():
        st.image(str(LOGO_ESQ), use_container_width=True)
with c2:
    st.markdown(
        "<h2 style='text-align:center;margin:0'>INDICADORES DO SETOR DE DESENVOLVIMENTO DO GRUPO LINHARES</h2>",
        unsafe_allow_html=True
    )
with c3:
    if LOGO_DIR.exists():
        st.image(str(LOGO_DIR), use_container_width=True)

st.markdown("<hr style='margin-top:6px;margin-bottom:12px'/>", unsafe_allow_html=True)

# === Cores institucionais (opcional) ===
COLOR_PRIMARY = "#0A4D8C"  # azul principal
COLOR_ACCENT = "#1E88E5"
COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#0A4D8C"

st.markdown(
    f"""
    <style>
        .big-metric {{
            font-size: 36px;
            font-weight: 700;
            color: {COLOR_PRIMARY};
        }}
        .sub-metric {{
            font-size: 14px;
            color: #455A64;
        }}
        header, .stApp {{
            background:{COLOR_BG};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# === Carregar base ===
DATA_PATH = Path(__file__).parent / "indicadores_grupo_linhares.xlsx"
if not DATA_PATH.exists():
    st.error(f"Arquivo de dados não encontrado: {DATA_PATH.name}. Coloque-o na mesma pasta do app.")
    st.stop()

df = pd.read_excel(DATA_PATH)

# Normalizações (garantir nomes esperados)
colmap = {
    "Automação": "Automação",
    "Desenvolvedor": "Desenvolvedor",
    "Dias Desenvolvimento": "Dias Desenvolvimento",
    "Horas Economizadas": "Horas Economizadas",
    "Economia (%)": "Economia (%)"
}
df = df.rename(columns=colmap)

# Tipos de dados
df["Dias Desenvolvimento"] = pd.to_numeric(df["Dias Desenvolvimento"], errors="coerce")
df["Horas Economizadas"] = pd.to_numeric(df["Horas Economizadas"], errors="coerce")
df["Economia (%)"] = pd.to_numeric(df["Economia (%)"], errors="coerce")

# === Sidebar (filtro) ===
st.sidebar.header("Filtros")
devs = sorted(df["Desenvolvedor"].dropna().unique().tolist())
selected_devs = st.sidebar.multiselect("Desenvolvedor", devs, default=devs)

filtered = df[df["Desenvolvedor"].isin(selected_devs)] if selected_devs else df.copy()

# === KPIs (topo) ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    dias_medios = filtered["Dias Desenvolvimento"].mean()
    st.markdown("<div class='sub-metric'>Média de dias de desenvolvimento</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-metric'>{dias_medios:,.2f} dias</div>", unsafe_allow_html=True)

with col2:
    econ_media = filtered["Economia (%)"].mean() / 100.0  # apresentar em formato %
    st.markdown("<div class='sub-metric'>Economia média (%)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-metric'>{econ_media:.2%}</div>", unsafe_allow_html=True)

with col3:
    horas_total = filtered["Horas Economizadas"].sum()
    st.markdown("<div class='sub-metric'>Horas economizadas (total)</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-metric'>{horas_total:,.2f} h</div>", unsafe_allow_html=True)

with col4:
    qtd_autos = filtered["Automação"].nunique()
    st.markdown("<div class='sub-metric'>Quantidade de automações</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big-metric'>{qtd_autos}</div>", unsafe_allow_html=True)

st.markdown("---")

# === Gráfico 1: Média de dias por Desenvolvedor ===
dias_por_dev = (
    filtered.groupby("Desenvolvedor", as_index=False)["Dias Desenvolvimento"]
    .mean()
    .sort_values("Dias Desenvolvimento", ascending=False)
)
fig_dias = px.bar(
    dias_por_dev,
    x="Desenvolvedor",
    y="Dias Desenvolvimento",
    title="Média de dias de desenvolvimento por Desenvolvedor",
)
fig_dias.update_layout(
    title_x=0.02,
    plot_bgcolor="#F9FBFF",
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
)
st.plotly_chart(fig_dias, use_container_width=True)

# === Gráfico 2: Economia (%) por Automação ===
econ_por_auto = (
    filtered[["Automação", "Economia (%)"]]
    .sort_values("Economia (%)", ascending=False)
)
fig_econ = px.bar(
    econ_por_auto,
    x="Automação",
    y="Economia (%)",
    title="Economia (%) por Automação",
    text="Economia (%)"
)
fig_econ.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig_econ.update_layout(
    title_x=0.02,
    plot_bgcolor="#F9FBFF",
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    yaxis_ticksuffix="%"
)
st.plotly_chart(fig_econ, use_container_width=True)

# === (Opcional) Gráfico 3: Economia média (%) por Desenvolvedor ===
econ_dev = (
    filtered.groupby("Desenvolvedor", as_index=False)["Economia (%)"]
    .mean()
    .sort_values("Economia (%)", ascending=False)
)
fig_econ_dev = px.bar(
    econ_dev,
    x="Desenvolvedor",
    y="Economia (%)",
    title="Economia média (%) por Desenvolvedor",
    text="Economia (%)"
)
fig_econ_dev.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
fig_econ_dev.update_layout(
    title_x=0.02,
    plot_bgcolor="#F9FBFF",
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    yaxis_ticksuffix="%"
)
st.plotly_chart(fig_econ_dev, use_container_width=True)

# --- Cálculo das colunas Manual (h) e Robô (h) ---
tmp = filtered.copy()
tmp["Economia_frac"] = pd.to_numeric(tmp["Economia (%)"], errors="coerce") / 100.0

def _manual_h(row):
    frac = row["Economia_frac"]
    he = row["Horas Economizadas"]
    if pd.notna(frac) and frac not in (0, None) and pd.notna(he):
        return he / frac
    return None

tmp["Manual (h)"] = tmp.apply(_manual_h, axis=1)
tmp["Robô (h)"] = tmp["Manual (h)"] - tmp["Horas Economizadas"]

# Ajustes
tmp["Manual (h)"] = tmp["Manual (h)"].round(4)
tmp["Robô (h)"] = tmp["Robô (h)"].clip(lower=0).round(4)
tmp["Economia (%)"] = tmp["Economia (%)"].round(2)
tmp = tmp.sort_values("Economia (%)", ascending=False)

# Função para converter decimal de horas para hh:mm:ss
def horas_para_hhmmss(valor_horas):
    if pd.isna(valor_horas):
        return ""
    segundos = int(valor_horas * 3600)
    return str(timedelta(seconds=segundos))

# --- Gráfico: Manual vs Robô com UM rótulo % ---
fig_red = go.Figure()

# Barras - Manual
fig_red.add_bar(
    name="Manual (h)",
    x=tmp["Automação"],
    y=tmp["Manual (h)"],
    marker_color="#0A4D8C",
    text=[horas_para_hhmmss(v) for v in tmp["Manual (h)"]],
    textposition="outside"
)

# Barras - Robô
fig_red.add_bar(
    name="Robô (h)",
    x=tmp["Automação"],
    y=tmp["Robô (h)"],
    marker_color="#81D4FA",
    text=[horas_para_hhmmss(v) for v in tmp["Robô (h)"]],
    textposition="outside"
)

# Rótulo único de porcentagem por automação (acima do maior valor)
y_top = (tmp[["Manual (h)", "Robô (h)"]].max(axis=1) * 1.08).tolist()
fig_red.add_trace(go.Scatter(
    x=tmp["Automação"],
    y=y_top,
    mode="text",
    text=[f"{p:.2f}%" if pd.notna(p) else "" for p in tmp["Economia (%)"]],
    textfont=dict(color="#0A4D8C", size=12),
    showlegend=False,
    hoverinfo="skip"
))

fig_red.update_layout(
    barmode="group",
    title="Redução real de tempo por automação (Manual vs Robô) • % de economia",
    title_x=0.02,
    plot_bgcolor="#F9FBFF",
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    yaxis_title="Horas (decimais)",
    xaxis_title="Automação",
    legend_title_text="Tempo",
    uniformtext_minsize=10,
    uniformtext_mode="hide",
    margin=dict(t=70, r=20, b=60, l=60)
)

st.plotly_chart(fig_red, use_container_width=True)


# === Tabela de dados ===
st.markdown("### Dados detalhados")
cols_show = ["Automação", "Desenvolvedor", "Dias Desenvolvimento",
             "Manual (h)", "Robô (h)", "Horas Economizadas", "Economia (%)"]

# se por acaso não houver as colunas novas (edge cases), cai no filtered
if all(c in tmp.columns for c in cols_show):
    view = tmp[cols_show].copy()
else:
    view = filtered.copy()

st.dataframe(
    view.style.format({
        "Dias Desenvolvimento": "{:.0f}",
        "Manual (h)": "{:.2f}",
        "Robô (h)": "{:.2f}",
        "Horas Economizadas": "{:.2f}",
        "Economia (%)": "{:.2f}"
    }),
    use_container_width=True
)

st.caption("Grupo Linhares · Indicadores de Desenvolvimento • Powered by Streamlit")
