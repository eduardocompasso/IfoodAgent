import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
from plugins.metrics_plugin import MetricsPlugin
from plugins.report_plugin import ReportPlugin

st.set_page_config(
    page_title="iFood Analytics Agent",
    page_icon="👤",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "alerts" not in st.session_state:
    st.session_state.alerts = None

st.title("👤 iFood Analytics Agent")
st.markdown("""
Converse com o assistente de IA sobre as métricas do seu restaurante. 
Faça perguntas sobre vendas, produtos, tempos de preparo e muito mais!
""")

st.sidebar.title("📊 Painel Rápido")
st.sidebar.markdown("### Comandos Disponíveis")
st.sidebar.markdown("""
- `/metrics` - Atualizar métricas
- `/anomalies` - Detectar anomalias
- `/report` - Gerar relatório completo
- `/clear` - Limpar conversa
""")

try:
    with open('data/pedidos.json', 'r', encoding='utf-8') as f:
        PEDIDOS_JSON_STR = f.read()
    pedidos = json.loads(PEDIDOS_JSON_STR)
    
    metrics_plugin = MetricsPlugin()
    report_plugin = ReportPlugin()
    
    if st.session_state.metrics is None:
        st.session_state.metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
    
    if st.session_state.metrics:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Métricas Rápidas")
        m = st.session_state.metrics
        st.sidebar.metric("Restaurante", m.get('restaurant_name', 'N/A'))
        if m.get('avg_prep_seconds'):
            avg_min = round(m['avg_prep_seconds'] / 60, 1)
            st.sidebar.metric("Tempo Médio Preparo", f"{avg_min} min")
        if m.get('top_products'):
            st.sidebar.markdown(f"**Mais vendido:** {m['top_products'][0]['name']}")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Digite sua mensagem ou comando..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = ""
                
                if prompt.strip().lower() == "/clear":
                    st.session_state.messages = []
                    response = "✅ Conversa limpa!"
                    st.rerun()
                
                elif prompt.strip().lower() == "/metrics":
                    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    st.session_state.metrics = metrics
                    
                    response = f"""📊 **Métricas Atualizadas**
                                        
                    **Restaurante:** {metrics.get('restaurant_name', 'N/A')}
                    **Tempo Médio de Preparo:** {round(metrics.get('avg_prep_seconds', 0) / 60, 1)} minutos
                    **Tempo Médio (30 dias):** {round(metrics.get('avg_prep_30d_seconds', 0) / 60, 1)} minutos

                    **Top 3 Produtos Mais Vendidos:**
                    """
                    for i, prod in enumerate(metrics.get('top_products', [])[:3], 1):
                        response += f"\n{i}. {prod['name']} - {prod['sold']} vendas"
                
                elif prompt.strip().lower() == "/anomalies":
                    if not st.session_state.metrics:
                        st.session_state.metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    
                    alerts = metrics_plugin.detect_anomalies(st.session_state.metrics)
                    st.session_state.alerts = alerts
                    
                    if alerts:
                        response = "🔔 **Alertas Detectados:**\n\n"
                        for alert in alerts:
                            response += f"⚠️ {alert}\n\n"
                    else:
                        response = "✅ Nenhuma anomalia detectada. Tudo funcionando perfeitamente!"
                
                elif prompt.strip().lower() == "/report":
                    if not st.session_state.metrics:
                        st.session_state.metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    if not st.session_state.alerts:
                        st.session_state.alerts = metrics_plugin.detect_anomalies(st.session_state.metrics)
                    
                    m = st.session_state.metrics
                    report_json = asyncio.run(
                        report_plugin.generate_report(
                            restaurant_name=m.get("restaurant_name", "Seu Restaurante"),
                            top_products=m.get("top_products", []),
                            avg_prep_seconds=m.get("avg_prep_seconds", 0),
                            avg_prep_30d_seconds=m.get("avg_prep_30d_seconds", 0),
                            alerts=st.session_state.alerts,
                        )
                    )
                    
                    try:
                        report_data = json.loads(report_json)
                        response = f"""📄 **{report_data.get('title', 'Relatório Completo')}**

                        **Resumo:**
                        {report_data.get('summary', 'N/A')}

                        **Produtos Principais:**
                        """
                        for i, prod in enumerate(report_data.get('top_products', []), 1):
                            response += f"{i}. {prod}\n"
                        
                        response += f"""
                        **Tempo de Preparo:**
                        - Atual: {report_data.get('avg_prep', 0)} segundos ({round(report_data.get('avg_prep', 0) / 60, 1)} min)
                        - Média 30 dias: {report_data.get('avg_prep_30d', 0)} segundos ({round(report_data.get('avg_prep_30d', 0) / 60, 1)} min)

                        **Alertas:**
                        """
                        alerts_list = report_data.get('alerts', [])
                        if alerts_list:
                            for alert in alerts_list:
                                response += f"⚠️ {alert}\n"
                        else:
                            response += "✅ Nenhum alerta\n"
                        
                        response += "\n**Recomendações:**\n"
                        for i, rec in enumerate(report_data.get('recommendations', []), 1):
                            response += f"{i}. {rec}\n"
                    except json.JSONDecodeError:
                        response = f"📄 **Relatório Completo**\n\n{report_json}"
                
                else:
                    context_prompt = prompt
                    if st.session_state.metrics:
                        m = st.session_state.metrics
                        top_prods = ", ".join([f"{p['name']} ({p['sold']} vendas)" for p in m.get('top_products', [])[:3]])
                        context_info = f"""
                        Contexto das métricas do restaurante:
                        - Nome: {m.get('restaurant_name', 'N/A')}
                        - Tempo médio de preparo: {round(m.get('avg_prep_seconds', 0) / 60, 1)} minutos
                        - Tempo médio (30 dias): {round(m.get('avg_prep_30d_seconds', 0) / 60, 1)} minutos
                        - Top 3 produtos: {top_prods}

                        Pergunta do usuário: {prompt}
                        """
                        context_prompt = context_info
                    
                    response = asyncio.run(report_plugin._chat.complete(context_prompt))
                
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

except FileNotFoundError:
    st.error("❌ Arquivo 'data/pedidos.json' não encontrado. Por favor, verifique o caminho do arquivo.")
except json.JSONDecodeError:
    st.error("❌ Erro ao ler o arquivo de pedidos. Verifique se o formato JSON está correto.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro inesperado: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.text("by:\nEduardo Domingues\nTiago Soares")
