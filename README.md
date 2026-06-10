# 📈 Painel Operacional - LMG 19

Dashboard operacional desenvolvido em Python com Streamlit para acompanhamento de produtividade e auditoria de conferência em tempo real.

---

## 🚀 Funcionalidades

### 📦 Aba — Produção hora a hora
- Upload de CSV de produtividade
- Tabela com produção consolidada por operador e hora
- Mapa de calor por faixa de produção (meta: 1100 unidades/hora)
- Linha de subtotal por hora
- Pódio Top 3 operadores com maior produção

### 🔍 Aba — Auditoria por Operador
- Upload de CSV de Gestão Audit
- Cartões com Média Geral por Rota, Média de Ociosidade e Total de Reconferências
- Rankings Top 3: Mais Pacotes e Melhor Média de conferência
- Mapa de calor por tempo médio de conferência (meta: abaixo de 06:00)
- Tabela detalhada de performance da equipe

### 🎨 Visual
- Legenda de cores no sidebar para Produção/Hora e Média por Rota
- Cabeçalho com data e hora de atualização
- Layout wide para melhor aproveitamento da tela

---

## 📁 Estrutura do Projeto

```
Projeto_Dash_Operacional/
├── venv/                   # Ambiente virtual Python
├── appdash.py              # Aplicação principal
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação
```

---

## 🗂️ Formato dos Arquivos CSV

### CSV de Produção
Exportado do sistema de produtividade. Colunas esperadas:
- `User Email` — identificação do operador (ex: `[ops12345]NOME OPERADOR`)
- `Total` — total de unidades no período
- Colunas de hora no formato `YYYY-MM-DD HH:MM` (ex: `2026-06-09 08:00`)

### CSV de Auditoria (Gestão Audit)
Exportado do LMHub Audit. Colunas esperadas:
- `AT/TO` — identificação da rota
- `Total Scanned Orders` — total de pacotes conferidos
- `Validation Operator` — operador responsável
- `Validation Start Time` — início da conferência
- `Validation End Time` — fim da conferência
- `Revalidated Count` — quantidade de reconferências

---

## ⚙️ Instalação e Execução

### Pré-requisitos
- Python 3.11 ou superior
- pip

### Passo a passo

**1. Clone ou baixe o projeto**
```bash
cd C:\Projeto_Dash_Operacional
```

**2. Crie o ambiente virtual**
```bash
python -m venv venv
```

**3. Ative o ambiente virtual**

Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
venv\Scripts\activate
```

**4. Instale as dependências**
```bash
pip install -r requirements.txt
```

**5. Execute o app**
```bash
streamlit run appdash.py
```

O app abrirá automaticamente em `http://localhost:8501`

---

## 🎨 Legenda de Cores

### Produção por Hora
| Cor | Faixa | Significado |
|-----|-------|-------------|
| 🟢 Verde | ≥ 1100 | Meta atingida |
| 🟡 Amarelo | 700–1099 | Próximo da meta |
| 🟠 Laranja | 300–699 | Abaixo da meta |
| 🔴 Vermelho | 1–299 | Muito abaixo |
| ⬛ Cinza | 0 | Sem produção |

### Média de Conferência
| Cor | Tempo | Significado |
|-----|-------|-------------|
| 🟢 Verde | < 06:00 | Ótimo |
| 🟡 Amarelo | 06:00–07:00 | Moderado |
| 🔴 Vermelho | > 07:00 | Abaixo da meta |

---

## 🛠️ Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) — interface web
- [Pandas](https://pandas.pydata.org/) — tratamento de dados
- [Plotly](https://plotly.com/) — visualizações gráficas

---

## 📌 Observações

- Os arquivos CSV são processados localmente, nenhum dado é enviado para servidores externos
- O horário de atualização exibido no cabeçalho reflete o momento do upload do arquivo
- Operadores com IDs duplicados (diferença de maiúsculas/minúsculas) são consolidados automaticamente