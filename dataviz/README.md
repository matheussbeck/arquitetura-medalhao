# 📊 DataViz - Dashboards Profissionais com Dash Plotly

## 🎯 Objetivo

Substituir dashboards do Power BI por dashboards web profissionais usando **Dash + Plotly**, reduzindo custos Microsoft mantendo o **mesmo nível de qualidade e profissionalismo**.

---

## 🌟 Dashboards Disponíveis

### 1. 🌱 Dashboard Executivo - Plantio
**Arquivo**: `dashboards/plantio/dashboard_executivo_plantio.py`
**Porta**: 8050

**Funcionalidades**:
- 4 KPIs principais (Área Total, Variedades, Meta, Talhões)
- Distribuição de área por variedade (Donut Chart)
- Cronograma planejado vs realizado (Barras comparativas)
- Evolução mensal acumulada
- Gauge de cumprimento de meta
- Tabela drill-down por variedade
- Filtros interativos (Safra, Período)

**Executar**:
```bash
cd dataviz/dashboards/plantio
python dashboard_executivo_plantio.py
# Acesse: http://localhost:8050
```

---

### 2. 💧 Dashboard - Vinhaça
**Arquivo**: `dashboards/vinhaca/dashboard_vinhaca.py`
**Porta**: 8051

**Funcionalidades**:
- KPIs de volume, pH e potássio
- Volume aplicado por dia (gráfico de linha)
- Distribuição de pH (histograma)
- Mapa de calor Volume x Potássio
- Análise de qualidade

**Executar**:
```bash
cd dataviz/dashboards/vinhaca
python dashboard_vinhaca.py
# Acesse: http://localhost:8051
```

---

### 3. 🌾 Dashboard Agronômico
**Arquivo**: `dashboards/agronomico/dashboard_agronomico.py`
**Porta**: 8052

**Funcionalidades**:
- KPIs agronômicos (TCH, ATR, Produtividade)
- KPIs climáticos (Precipitação, Temperatura)
- Evolução TCH ao longo do tempo
- Precipitação mensal
- Correlação Temperatura x Produtividade
- Gauge de ATR médio

**Executar**:
```bash
cd dataviz/dashboards/agronomico
python dashboard_agronomico.py
# Acesse: http://localhost:8052
```

---

## 🚀 Como Começar

### 1. Instalar Dependências

```bash
# Instale as dependências DataViz
pip install -r dataviz/requirements_dataviz.txt
```

### 2. Executar um Dashboard

```bash
# Escolha um dashboard
cd dataviz/dashboards/plantio

# Execute
python dashboard_executivo_plantio.py

# Acesse no navegador
http://localhost:8050
```

### 3. Executar Múltiplos Dashboards

```bash
# Terminal 1
python dashboards/plantio/dashboard_executivo_plantio.py

# Terminal 2
python dashboards/vinhaca/dashboard_vinhaca.py

# Terminal 3
python dashboards/agronomico/dashboard_agronomico.py
```

---

## 🎨 Personalização

### Cores e Tema

Edite `utils/theme.py`:

```python
# Ajuste para as cores da sua empresa
PRIMARY_COLOR = "#2E7D32"  # Verde principal
SECONDARY_COLOR = "#1565C0"  # Azul
ACCENT_COLOR = "#F57C00"  # Laranja
```

### Dados

Os dashboards lêem dados da camada **Gold** automaticamente via `utils/data_loader.py`.

Para conectar aos seus dados reais, edite `data_loader.py`:

```python
def load_from_gold(self, table_path):
    # Conecta ao seu Data Lake
    df = self.spark.read.format("delta").load(table_path)
    return df.toPandas()
```

---

## 📂 Estrutura

```
dataviz/
├── dashboards/              # Dashboards por área
│   ├── plantio/
│   │   └── dashboard_executivo_plantio.py
│   ├── vinhaca/
│   │   └── dashboard_vinhaca.py
│   └── agronomico/
│       └── dashboard_agronomico.py
│
├── utils/                   # Utilitários compartilhados
│   ├── theme.py            # Tema e cores corporativas
│   └── data_loader.py      # Carregamento de dados
│
├── assets/                  # CSS/JS/Imagens customizadas
├── components/              # Componentes reutilizáveis
│
├── requirements_dataviz.txt # Dependências
└── README.md                # Este arquivo
```

---

## 🔥 Recursos Avançados

### 1. Deploy em Produção

**Opção A - Azure App Service**:
```bash
# Crie app.py na raiz de dataviz
# Deploy via Azure CLI
az webapp up --name seu-dashboard --resource-group seu-rg
```

**Opção B - Docker**:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements_dataviz.txt .
RUN pip install -r requirements_dataviz.txt
COPY . .
CMD ["python", "dashboards/plantio/dashboard_executivo_plantio.py"]
```

**Opção C - Databricks**:
- Suba os arquivos para Workspace
- Execute via Databricks Jobs
- Acesse via proxy reverso

---

### 2. Autenticação

Para adicionar autenticação, use `dash-auth`:

```python
import dash_auth

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'senha123',
    'usuario': 'senha456'
}

dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)
```

---

### 3. Cache Redis

Para melhor performance:

```python
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.memoize(timeout=300)  # 5 minutos
def load_data():
    return data_loader.get_plantio_area_por_variedade()
```

---

## 💡 Boas Práticas

### ✅ Faça:
- Use cores consistentes (theme.py)
- Adicione tooltips explicativos
- Implemente filtros para diferentes visões
- Otimize queries (carreg

ue apenas dados necessários)
- Use cache para dados que mudam pouco
- Teste responsividade (mobile/desktop)

### ❌ Evite:
- Muitos gráficos em uma tela (max 6-8)
- Cores muito vibrantes que cansam
- Gráficos sem título ou eixos
- Carregar milhões de linhas no frontend
- Executar queries lentas a cada refresh

---

## 📊 Comparação: Power BI vs Dash

| Aspecto | Power BI | Dash Plotly |
|---------|----------|-------------|
| **Custo** | $10-20/usuário/mês | Grátis (apenas hospedagem) |
| **Customização** | Limitada | Total |
| **Integração** | Microsoft ecosystem | Qualquer stack Python |
| **Performance** | Boa | Excelente (otimizável) |
| **Learning Curve** | Baixa | Média |
| **Controle** | Limitado | Total |

**Economia estimada**: R$ 50.000 - 100.000/ano dependendo do número de usuários!

---

## 🆘 Precisa de Ajuda?

1. **Documentação Dash**: https://dash.plotly.com/
2. **Galeria de Exemplos**: https://dash-gallery.plotly.host/
3. **Guias do Projeto**: `docs/`

---

## 📝 Próximos Passos

1. ✅ Executar dashboards localmente
2. ✅ Conectar aos dados reais (Gold layer)
3. ✅ Customizar cores para sua marca
4. ✅ Adicionar mais visualizações conforme necessário
5. ✅ Deploy em produção (Azure/AWS/GCP)
6. ✅ Configurar autenticação
7. ✅ Treinar equipe no uso

---

**Última atualização**: 2024
**Versão**: 1.0
**Status**: ✅ Produção
