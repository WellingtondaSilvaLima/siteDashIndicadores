import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
import io
import plotly.io as pio
import streamlit.components.v1 as components

def botao_download_png(fig, nome_arquivo_png: str, label="Baixar PNG"):
    # exige o pacote 'kaleido'
    img_bytes = pio.to_image(fig, format="png", scale=2)  # scale aumenta a qualidade
    st.download_button(
        label=f"{label} — {nome_arquivo_png}",
        data=img_bytes,
        file_name=nome_arquivo_png,
        mime="image/png",
        use_container_width=True
    )

st.set_page_config(
    page_title="Indicadores - Grupo Linhares",
    page_icon="📊",
    layout="wide"
)

# caminhos das logos (troque pelos seus arquivos ou URLs)
LOGO_ESQ = Path(__file__).parent / "logo_grupo_linhares.png"
LOGO_DIR = Path(__file__).parent / "liliauto-logo.png"

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

# === Título ===
st.markdown("## INDICADORES DO SETOR DE DESENVOLVIMENTO DO GRUPO LINHARES")

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
botao_download_png(fig_dias, "media_dias_por_desenvolvedor.png")

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
botao_download_png(fig_econ, "economia_por_automacao.png")

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
botao_download_png(fig_econ_dev, "economia_media_por_desenvolvedor.png")

# === Tabela de dados ===
st.markdown("### Dados detalhados")
st.dataframe(
    filtered.style.format({
        "Dias Desenvolvimento": "{:.0f}",
        "Horas Economizadas": "{:.2f}",
        "Economia (%)": "{:.2f}"
    }),
    use_container_width=True
)

components.html(
    """
    <div style="display:flex;justify-content:flex-end;margin:12px 0;">
      <button id="btn-pdf" style="
        background:#0A4D8C;color:#fff;border:none;border-radius:8px;
        padding:10px 14px;cursor:pointer;font-weight:600;">
        Baixar PDF da página
      </button>
    </div>

    <!-- libs para capturar e gerar PDF -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
            integrity="sha512-BNa5l1QF3fSCD8VdV6k9wqfC8e0mGQq9Vyk+fD1N8z8w7w3g8v8oJc8C+3b0WQ0fQ3T1o4rcz2c1JmQ3+J9wkw=="
            crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"
            integrity="sha512-YkG3gJqK9i0b9oQ3m4qH4Q0T9Zb0m1f1m0XxV3O1o+Vn3cO2QwK9T9m0o6x3dY0V9pQmWk1Y6m0qYIYwVBsHyg=="
            crossorigin="anonymous" referrerpolicy="no-referrer"></script>

    <script>
      const btn = document.getElementById("btn-pdf");
      btn?.addEventListener("click", async () => {
        const { jsPDF } = window.jspdf;

        // captura do corpo inteiro (aumente scale para maior qualidade)
        const canvas = await html2canvas(document.body, { scale: 2, useCORS: true });
        const imgData = canvas.toDataURL("image/png");

        const pdf = new jsPDF("p", "mm", "a4");
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();

        const imgWidth = pageWidth;
        const imgHeight = canvas.height * imgWidth / canvas.width;

        let heightLeft = imgHeight;
        let position = 0;

        pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight, "", "FAST");
        heightLeft -= pageHeight;

        // adiciona páginas se necessário (conteúdo maior que 1 página)
        while (heightLeft > 0) {
          position = heightLeft - imgHeight;
          pdf.addPage();
          pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight, "", "FAST");
          heightLeft -= pageHeight;
        }

        pdf.save("indicadores_grupo_linhares.pdf");
      });
    </script>
    """,
    height=80,
)

st.caption("Grupo Linhares · Indicadores de Desenvolvimento • Powered by Streamlit")
