# dashboard.py
# Ejecutar en OTRA terminal con: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuración
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Contoso Retail", layout="wide")
st.title("📊 Dashboard Empresarial - Arquitectura Desacoplada")

# Función para conectar con tu API
@st.cache_data(ttl=300) # Cache de 5 minutos
def fetch_api(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            # Si falla, mostramos el error que manda el backend
            st.error(f"Error en {endpoint}: {response.json().get('detail')}")
            return []
    except Exception as e:
        st.error(f"No se pudo conectar al Backend. ¿Está corriendo uvicorn? {e}")
        return []

# --- CARGA DE DATOS ---
kpi_data = fetch_api("kpis")
trend_data = fetch_api("tendencia")
top_data = fetch_api("top-productos")

# --- VISUALIZACIÓN ---

# 1. KPIs
st.subheader("Resumen General")
col1, col2, col3 = st.columns(3)

# Validamos que kpi_data no esté vacío
if kpi_data:
    ventas = kpi_data.get('TotalVentas') or 0
    pedidos = kpi_data.get('TotalPedidos') or 0
    ticket = kpi_data.get('TicketPromedio') or 0
    
    col1.metric("💰 Ventas Totales", f"${ventas:,.2f}")
    col2.metric("📦 Total Pedidos", f"{pedidos:,}")
    col3.metric("🏷️ Ticket Promedio", f"${ticket:,.2f}")
else:
    st.warning("No hay datos de KPIs disponibles.")

st.markdown("---")

# 2. Gráficos
c1, c2 = st.columns(2)

with c1:
    st.subheader("📅 Tendencia de Ventas")
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        # Convertimos Mes a string para que se ordene bien en el gráfico
        fig = px.line(df_trend, x='Mes', y='Ventas', markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos de tendencia.")

with c2:
    st.subheader("🏆 Top 10 Productos")
    if top_data:
        df_top = pd.DataFrame(top_data)
        fig = px.bar(df_top, x='Ventas', y='Producto', orientation='h', template="plotly_dark")
        # Invertimos el eje Y para que el #1 salga arriba
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos de productos.")