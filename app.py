import streamlit as st
import asyncio
import json
import pandas as pd
import os
from datetime import date, timedelta, datetime
from collections import Counter
from plugins.metrics_plugin import MetricsPlugin
from plugins.report_plugin import ReportPlugin
from plugins.anomalie_plugin import AnomaliePlugin

st.set_page_config(
    page_title="Análise de Restaurante",
    page_icon="👤",
    layout="wide"
)

if "messages" not in st.session_state: st.session_state.messages = []
if "metrics" not in st.session_state: st.session_state.metrics = None

st.title("👤 Agente de Análise de Restaurante")
st.markdown("""
Converse com o assistente de IA sobre as métricas do seu restaurante. 
Faça perguntas sobre vendas, produtos, tempos de preparo e muito mais!
""")

st.sidebar.title("📊 Painel de Controle")
st.sidebar.markdown("### Comandos Disponíveis")
st.sidebar.markdown("""
- `/metrics` - Atualizar métricas gerais
- `/clients_metrics` - Ver métricas de clientes
- `/anomalies` - Detectar anomalias com IA
- `/report` - Gerar relatório completo
- `/clear` - Limpar conversa
""")

try:
    with open('data/pedidos.json', 'r', encoding='utf-8') as f:
        PEDIDOS_JSON_STR = f.read()
    
    metrics_plugin = MetricsPlugin()
    report_plugin = ReportPlugin()
    anomalie_plugin = AnomaliePlugin()
    
    if st.session_state.metrics is None:
        st.session_state.metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
    
    if st.session_state.metrics:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Resumo Rápido")
        m = st.session_state.metrics
        st.sidebar.metric("Restaurante", m.get('restaurant_name', 'N/A'))
        
        if 'avg_prep_30d_seconds' in m:
            avg_min_today = round(m.get('avg_prep_30d_seconds', 0) / 60, 1)
            overall_avg = m.get('avg_prep_seconds', 0)
            delta_vs_overall = m.get('avg_prep_30d_seconds', 0) - overall_avg
            st.sidebar.metric(
                label="Preparo (Ultimos 30 dias)", 
                value=f"{avg_min_today} min",
                delta=f"{round(delta_vs_overall / 60, 1)} min vs Geral",
                delta_color="inverse"
            )
        
        if m.get('top_products'):
            st.sidebar.markdown(f"**Mais vendido:** {m['top_products'][0]['name']}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
    if prompt := st.chat_input("Digite sua mensagem ou comando..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                response = ""
                
                if prompt.strip().lower() == "/clear":
                    st.session_state.messages = []
                    st.rerun()

                elif prompt.strip().lower() == "/metrics":
                    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    st.session_state.metrics = metrics
                    
                    response = f"### 📊 Métricas Gerais Atualizadas\n\n"
                    response += f"**Valor Total Vendido:** R$ {metrics.get('grand_total_sold', 0.0):.2f}\n\n"
                    response += "**Análise de Tempo de Preparo:**\n"
                    
                    avg_today_s = metrics.get('avg_prep_today_seconds', 0)
                    avg_30d_s = metrics.get('avg_prep_30d_seconds', 0)
                    avg_overall_s = metrics.get('avg_prep_seconds', 0)

                    response += f"- **Hoje:** {round(avg_today_s / 60, 1)} min ({avg_today_s}s)\n"
                    response += f"- **Últimos 30 Dias:** {round(avg_30d_s / 60, 1)} min ({avg_30d_s}s)\n"
                    response += f"- **Geral (todo o período):** {round(avg_overall_s / 60, 1)} min ({avg_overall_s}s)\n"
                    
                    st.markdown(response)

                elif prompt.strip().lower() == "/clients_metrics":
                    client_metrics = metrics_plugin.query_clients_metrics(PEDIDOS_JSON_STR)
                    
                    st.markdown("### 👥 Métricas de Clientes")

                    if client_metrics:
                        df = pd.DataFrame.from_dict(client_metrics, orient='index')
                        df.columns = ["Nº de Pedidos", "Total Gasto (R$)"]
                        st.dataframe(df)

                        response_str = "### 👥 Métricas de Clientes\n\n"
                        response_str += "| Cliente | Nº de Pedidos | Total Gasto (R$) |\n| --- | --- | --- |\n"
                        
                        for name, data in client_metrics.items():
                            response_str += f"| {name} | {data['numero_de_pedidos']} | R$ {data['valor_total_gasto']:.2f} |\n"
                        
                        response = response_str
                    else:
                        response = "Nenhuma métrica de cliente encontrada."
                        st.write(response)

                elif prompt.strip().lower() == "/anomalies":
                    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    response = asyncio.run(anomalie_plugin.detect_anomalies_with_ai(metrics=metrics))
                    st.markdown(response)

                elif prompt.strip().lower() == "/report":
                    st.info("Gerando relatório completo...")
                    metrics = metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    st.session_state.metrics = metrics

                    st.info("Detectando anomalias com IA...")
                    alerts_text = asyncio.run(anomalie_plugin.detect_anomalies_with_ai(metrics=metrics))
                    alerts_list = [line.strip("* ") for line in alerts_text.split('\n') if line.strip()]

                    st.info("Compilando o relatório final...")
                    report_json_str = asyncio.run(
                        report_plugin.generate_report(
                            restaurant_name=metrics.get("restaurant_name", "N/A"),
                            top_products=metrics.get("top_products", []),
                            avg_prep_seconds=metrics.get("avg_prep_seconds", 0),
                            avg_prep_today_seconds=metrics.get("avg_prep_today_seconds", 0),
                            avg_prep_30d_seconds=metrics.get("avg_prep_30d_seconds", 0),
                            alerts=alerts_list,
                        )
                    )
                    
                    try:
                        report_data = json.loads(report_json_str)
                        response = f"### 📄 {report_data.get('title', 'Relatório de Performance')}\n\n"
                        response += f"**Resumo:** {report_data.get('summary', 'N/A')}\n\n"
                        response += "**Recomendações da IA:**\n"
                        for rec in report_data.get('recommendations', []):
                            response += f"- {rec}\n"
                    except json.JSONDecodeError:
                        response = f"**Ocorreu um erro ao formatar o relatório. Resposta da IA:**\n\n{report_json_str}"
                    
                    reports_dir = "reports"
                    os.makedirs(reports_dir, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    file_name = f"report_{timestamp}.md"
                    file_path = os.path.join(reports_dir, file_name)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(response)
                    
                    st.success(f"Relatório salvo em: `{file_path}`")
                    
                    st.markdown(response)

                else:
                    m = st.session_state.metrics if st.session_state.metrics else metrics_plugin.query_metrics(PEDIDOS_JSON_STR)
                    context_info = f"""
                    Contexto para responder a pergunta:
                    - Desempenho de hoje (tempo de preparo): {m.get('avg_prep_today_seconds', 0)} segundos.
                    - Desempenho geral (tempo de preparo): {m.get('avg_prep_seconds', 0)} segundos.
                    - Total vendido no geral: R$ {m.get('grand_total_sold', 0.0)}.

                    Pergunta do usuário: {prompt}
                    """
                    response = asyncio.run(report_plugin._chat.complete(context_info))
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

except FileNotFoundError:
    st.error("❌ Arquivo 'data/pedidos.json' não encontrado.")
except Exception as e:
    st.error(f"❌ Ocorreu um erro inesperado: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.text("by:\nEduardo Domingues\nTiago Soares")