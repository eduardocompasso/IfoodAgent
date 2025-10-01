## 🍽️ AgentIfood

Agente inteligente para análise de métricas de restaurantes no iFood com interface web interativa.

### ✨ Funcionalidades

- 💬 **Agente Inteligente**: Converse naturalmente com IA sobre suas métricas
- 📊 **Análise em Tempo Real**: Métricas atualizadas instantaneamente
- 📈 **Insights Automáticos**: Produtos mais vendidos e faturamento
- ⏱️ **Monitoramento de Tempo**: Acompanhe tempos de preparo
- 🔔 **Detecção de Anomalias**: Alertas automáticos de problemas
- 📄 **Relatórios IA**: Relatórios completos gerados por Gemini AI
- 🎯 **Comandos Rápidos**: Acesso direto a funcionalidades via comandos

### 🛠️ Pré‑requisitos
- Python 3.10+
- Chave da API Gemini em `GEMINI_API_KEY`

### 📦 Instalação

1. **Clone o projeto**
```bash
git clone https://github.com/eduardocompasso/AgentIfood
cd AgentIfood
```

2. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz com:
```bash
GEMINI_API_KEY=SEU_TOKEN_AQUI
```

3. **Instale as dependências**

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

**macOS/Linux (bash/zsh):**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### 🚀 Rodar o projeto

#### Opção 1: Agent Web (Recomendado) 💬
```bash
streamlit run app.py
```
A interface web será aberta automaticamente no navegador em `http://localhost:8501`

**Como usar o Agent:**
1. Digite perguntas naturais como:
   - "Quais são os produtos mais vendidos?"
   - "Como está o tempo de preparo?"
   - "Há algum problema nas vendas?"
   
2. Use comandos rápidos:
   - `/metrics` - Atualizar e visualizar métricas
   - `/anomalies` - Detectar anomalias
   - `/report` - Gerar relatório completo com IA
   - `/clear` - Limpar conversa

3. A IA responde com contexto das métricas do restaurante

#### Opção 2: Interface de Linha de Comando 💻
```bash
python main.py
```

**Comandos CLI:**
- `/metrics`: atualiza métricas
- `/anomalies`: detecta anomalias
- `/report`: gera relatório
- `/exit`: sair

### 📁 Estrutura do projeto
```text
config.py              # Configuração do Gemini e variáveis de ambiente
agent.py               # Orquestração: run_agent e chat_loop
app.py                 # Interface web com Streamlit
connectors/
  gemini_connector.py  # Conecta o Agente ao Gemini
plugins/
  metrics_plugin.py    # Apresenta métricas sobre o restaurante
  report_plugin.py     # Gera relatórios com IA
data/
  pedidos.json         # Dados dos pedidos
utils/
  prompt_utils.py      # Template e renderização de prompt
main.py                # Entrada CLI
requirements.txt
.env
```