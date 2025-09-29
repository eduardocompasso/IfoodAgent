## AgentIfood

Pequeno agente para gerar relatório de restaurante usando Gemini.

### Pré‑requisitos
- Python 3.10+
- Chave da API Gemini em `GEMINI_API_KEY`

### Clonar o projeto
```bash
git clone https://github.com/eduardocompasso/AgentIfood
cd AgentIfood
```

### Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz com:
```bash
GEMINI_API_KEY=SEU_TOKEN_AQUI
```

### Instalar dependências com venv

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

macOS/Linux (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

### Rodar o projeto
```bash
python main.py
```

Comandos no chat:
- `/metrics`: atualiza métricas
- `/anomalies`: detecta anomalias
- `/report`: gera relatório
- `/exit`: sair

### Estrutura do projeto
```text
config.py              # Configuração do Gemini e variáveis de ambiente
agent.py               # Orquestração: run_agent e chat_loop
connectors/
  gemini_connector    # Conecta o Agente ao Gemini
plugins/
  metrics_plugin.py   # Apresenta métricas sobre o restaurante
  anomaly_plugin.py   # Detecta anomalias nas vendas e preparo dos pratos
utils/
  prompt_utils.py      # template e renderização de prompt
main.py                
requirements.txt
.env
```

### Uso com Semantic Kernel (Gemini)
Este projeto foi adaptado para um estilo de orquestração com Semantic Kernel (SK) mantendo o backend Gemini.

1) Instale SK:
```bash
pip install semantic-kernel
```

2) Plugins/Conectores:
- `connectors/gemini_connector.py`: wrapper simples para chamadas ao Gemini
- `plugins/metrics_plugin.py`: funções nativas (métricas e anomalias)
- `plugins/report_plugin.py`: função assíncrona que gera relatório via Gemini

3) Execução: o `agent.py` utiliza os plugins para `/metrics`, `/anomalies`, `/report`.



