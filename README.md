# 🏅 Arquitetura Medalhão - Data Lakehouse Agronegócio

Projeto completo de migração de ETL do Power BI para arquitetura medalhão usando PySpark, com **Dashboards Profissionais** em Dash Plotly, focado em **Agronegócio** e integração com Azure.

---

## 📋 Visão Geral

Este projeto implementa uma **Arquitetura Medalhão** (Medallion Architecture) para processar dados de múltiplas fontes e disponibilizá-los para o Power BI de forma otimizada.

### O que é Arquitetura Medalhão?

```
📥 BRONZE          🔧 SILVER           💎 GOLD            📊 POWER BI
(Dados Brutos) ➡️  (Dados Limpos)  ➡️  (Agregações)  ➡️  (Relatórios)
```

- **Bronze**: Dados brutos da origem, sem transformações
- **Silver**: Dados limpos, validados e padronizados
- **Gold**: Agregações, métricas e modelos prontos para análise

### Áreas de Negócio Agronegócio

- 🌱 **PLANTIO** - Dados de plantio, talhões, variedades, cronograma
- 💧 **VINHAÇA** - Aplicação de vinhaça, análises químicas, fertirrigação
- 🚜 **PREPARO DE SOLO** - Operações de preparo (aração, gradagem, subsolagem)
- 🌾 **AGRONÔMICO** - Produtividade, TCH, ATR, análises de solo, clima
- 🏭 **CCT** - Centro de Controle de Tráfego
- 🔧 **MANUTENÇÃO** - Equipamentos agrícolas e manutenção
- 🤝 **APOIO** - Áreas de apoio operacional
- 💼 **SSMA** - Sistema de Gestão
- 📊 **PLANEJAMENTO** - Planejamento de safras
- 👔 **DIRETORIA** - Indicadores executivos agrícolas
- ⚖️ **GOVERNANÇA OPERACIONAL** - Compliance e governança
- 📂 **OUTROS** - Outras áreas

---

## 🚀 Quick Start

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd arquitetura-medalhao
```

### 2. Configure Variáveis de Ambiente

```bash
# Copie o exemplo
cp .env.example .env

# Edite com suas credenciais
nano .env
```

### 3. Configure suas Fontes de Dados

Edite `config/sources.yaml` e adicione suas fontes:

```yaml
synapse_sources:
  minha_fonte:
    type: "synapse"
    database: "MeuDatabase"
    schema: "dbo"
    table: "MinhaTabela"
    load_type: "incremental"
    business_area: "producao"
```

### 4. Crie seu Primeiro Pipeline

```bash
# 1. Copie os templates
cp notebooks/templates/bronze_template.py notebooks/bronze/bronze_minha_fonte.py
cp notebooks/templates/silver_template.py notebooks/silver/silver_minha_fonte.py
cp notebooks/templates/gold_template.py notebooks/gold/gold_minha_metrica.py

# 2. Edite os notebooks e configure os parâmetros
# 3. Execute no Databricks ou Synapse
```

---

## 📁 Estrutura do Projeto

```
arquitetura-medalhao/
│
├── 📂 config/                   # Configurações centralizadas
│   ├── config.yaml             # Configuração principal
│   ├── sources.yaml            # Definição de fontes de dados
│   └── .env                    # Credenciais (não commitado)
│
├── 📂 notebooks/               # Notebooks organizados por camada
│   ├── templates/              # 🎯 COMECE AQUI - Templates reutilizáveis
│   │   ├── bronze_template.py  #    Template ingestão (Bronze)
│   │   ├── silver_template.py  #    Template limpeza (Silver)
│   │   └── gold_template.py    #    Template agregação (Gold)
│   ├── bronze/                 # Notebooks Bronze (ingestão)
│   ├── silver/                 # Notebooks Silver (transformação)
│   └── gold/                   # Notebooks Gold (agregações)
│
├── 📂 pipelines/               # Orquestradores por área
│   ├── producao/
│   │   ├── pipeline_producao.py
│   │   └── README.md
│   ├── manutencao/
│   ├── planejamento/
│   └── ...
│
├── 📂 utils/                   # Utilitários Python reutilizáveis
│   ├── config_loader.py        # Carregador de configurações
│   ├── spark_session.py        # Gerenciador de sessão Spark
│   ├── data_quality.py         # Validação de qualidade
│   ├── logger.py               # Sistema de logging
│   └── connectors/             # Conectores para fontes
│       ├── azure_connector.py
│       ├── synapse_connector.py
│       └── sharepoint_connector.py
│
├── 📂 docs/                    # 📚 DOCUMENTAÇÃO COMPLETA
│   ├── 01_BOAS_PRATICAS_ARQUITETURA_MEDALHAO.md
│   ├── 02_GUIA_INICIANTES_PYSPARK.md
│   ├── 03_PADROES_PROJETO.md
│   └── 04_DEBUGGING_E_DEPLOY.md
│
├── 📂 data/                    # Dados locais (desenvolvimento)
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
└── 📂 tests/                   # Testes automatizados
```

---

## 📚 Documentação

### Para Iniciantes

Se você **não programa** ou está começando, leia nesta ordem:

1. 📘 [**Guia de Iniciantes PySpark**](docs/02_GUIA_INICIANTES_PYSPARK.md)
   - Conceitos básicos de PySpark
   - Operações comuns (filtrar, agrupar, etc.)
   - Exemplos práticos passo a passo

2. 🏅 [**Boas Práticas Arquitetura Medalhão**](docs/01_BOAS_PRATICAS_ARQUITETURA_MEDALHAO.md)
   - O que é cada camada (Bronze, Silver, Gold)
   - O que fazer e não fazer em cada camada
   - Princípios fundamentais

3. 📋 [**Padrões do Projeto**](docs/03_PADROES_PROJETO.md)
   - Como nomear arquivos e variáveis
   - Estrutura de código padrão
   - Convenções do projeto

4. 🔧 [**Debugging e Deploy**](docs/04_DEBUGGING_E_DEPLOY.md)
   - Como resolver problemas comuns
   - Como fazer deploy no Databricks/Synapse
   - Monitoramento e alertas

### Templates Prontos

Os templates são arquivos prontos que você pode copiar e adaptar:

- **Bronze Template**: [notebooks/templates/bronze_template.py](notebooks/templates/bronze_template.py)
  - Ingestão de dados de Synapse, Data Lake, SharePoint
  - Comentários linha por linha explicando o que fazer

- **Silver Template**: [notebooks/templates/silver_template.py](notebooks/templates/silver_template.py)
  - Limpeza e padronização de dados
  - Remoção de duplicatas, validação de qualidade

- **Gold Template**: [notebooks/templates/gold_template.py](notebooks/templates/gold_template.py)
  - Agregações e cálculo de métricas
  - Otimização para Power BI

---

## 🎯 Como Usar os Templates

### Passo 1: Copie o Template

```bash
# Copie o template Bronze
cp notebooks/templates/bronze_template.py notebooks/bronze/bronze_vendas.py
```

### Passo 2: Configure os Parâmetros

Abra o arquivo e edite a seção de configurações:

```python
# ============================================================================
# CONFIGURAÇÕES DO PIPELINE
# ============================================================================

FONTE_DADOS = "vendas"           # ⬅️ ALTERE para nome da sua fonte
AREA_NEGOCIO = "producao"        # ⬅️ ALTERE para sua área
TIPO_FONTE = "synapse"           # ⬅️ synapse, datalake, sharepoint, local
TIPO_CARGA = "incremental"       # ⬅️ full ou incremental

# Se Synapse:
SYNAPSE_DATABASE = "DW_Vendas"   # ⬅️ ALTERE aqui
SYNAPSE_SCHEMA = "dbo"           # ⬅️ ALTERE aqui
SYNAPSE_TABLE = "fato_vendas"    # ⬅️ ALTERE aqui
```

### Passo 3: Execute

Execute o notebook célula por célula no Databricks ou Synapse Analytics.

---

## 🔌 Fontes de Dados Suportadas

| Fonte | Status | Conector |
|-------|--------|----------|
| Azure Synapse Analytics | ✅ | `SynapseConnector` |
| Azure Data Lake Gen2 | ✅ | `AzureDataLakeConnector` |
| Azure SQL Data Warehouse | ✅ | `SynapseConnector` |
| SharePoint Online | ✅ | `SharePointConnector` |
| Arquivos Locais (CSV, Excel) | ✅ | Spark nativo |
| SQL Server (via JDBC) | 🔄 | Em desenvolvimento |

---

## ⚙️ Configuração

### Variáveis de Ambiente Obrigatórias

No arquivo `.env`, configure:

```bash
# Azure Data Lake
AZURE_STORAGE_ACCOUNT=seu-storage-account
AZURE_STORAGE_CONNECTION_STRING=...

# Azure Synapse
SYNAPSE_WORKSPACE_NAME=seu-workspace
SYNAPSE_DEDICATED_ENDPOINT=seu-endpoint.sql.azuresynapse.net
SYNAPSE_DATABASE=seu-database
SYNAPSE_USERNAME=usuario
SYNAPSE_PASSWORD=senha

# SharePoint (se usar)
SHAREPOINT_SITE_URL=https://empresa.sharepoint.com/sites/site
SHAREPOINT_CLIENT_ID=...
SHAREPOINT_CLIENT_SECRET=...
SHAREPOINT_TENANT_ID=...
```

### Config.yaml

Personalize comportamentos em `config/config.yaml`:

```yaml
# Performance
performance:
  shuffle_partitions: 200
  executor_memory: "4g"
  max_executors: 10

# Qualidade
quality:
  null_threshold: 0.05      # 5% de nulos aceitável
  duplicate_threshold: 0.01 # 1% de duplicatas aceitável

# Agendamento por área
business_areas:
  producao:
    enabled: true
    schedule: "0 6 * * *"    # Diário às 06:00
    priority: "high"
```

---

## 🔄 Fluxo de Dados Completo

```
┌─────────────────┐
│  Fontes de      │
│  Dados          │
│  - Synapse      │
│  - Data Lake    │
│  - SharePoint   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  🥉 BRONZE      │
│  - Ingestão     │
│  - Sem mudanças │
│  - Formato:     │
│    Parquet      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  🥈 SILVER      │
│  - Limpeza      │
│  - Validação    │
│  - Formato:     │
│    Delta Lake   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  🥇 GOLD        │
│  - Agregações   │
│  - Métricas     │
│  - Formato:     │
│    Delta Lake   │
│    (otimizado)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  📊 POWER BI    │
│  Dashboards e   │
│  Relatórios     │
└─────────────────┘
```

---

## 🎓 Treinamento da Equipe

### Roteiro de Aprendizado

#### Semana 1: Fundamentos
- [ ] Ler [Guia de Iniciantes PySpark](docs/02_GUIA_INICIANTES_PYSPARK.md)
- [ ] Ler [Boas Práticas](docs/01_BOAS_PRATICAS_ARQUITETURA_MEDALHAO.md)
- [ ] Executar exemplos do Guia de Iniciantes

#### Semana 2: Prática
- [ ] Copiar template Bronze
- [ ] Configurar uma fonte simples
- [ ] Executar pipeline Bronze completo
- [ ] Validar dados na camada Bronze

#### Semana 3: Transformações
- [ ] Copiar template Silver
- [ ] Aplicar limpezas básicas
- [ ] Validar qualidade dos dados
- [ ] Executar pipeline Silver

#### Semana 4: Agregações
- [ ] Copiar template Gold
- [ ] Criar agregações mensais
- [ ] Conectar Power BI na camada Gold
- [ ] Criar primeiro dashboard

---

## 📊 Monitoramento

### Logs de Auditoria

Todos os pipelines registram execuções em:

```
gold/auditoria_execucoes/
```

Para consultar:

```python
df_logs = spark.read.format("delta").load("gold/auditoria_execucoes/")

# Execuções de hoje
df_logs.filter(F.col("start_time") >= F.current_date()) \
    .orderBy(F.col("start_time").desc()) \
    .show()

# Pipelines com falha
df_logs.filter(F.col("status") == "failed").show()
```

### Métricas de Execução

Cada pipeline registra:
- ⏱️ Tempo de execução
- 📊 Registros processados
- ✅ Status (success/failed/partial)
- ❌ Erros (se houver)

---

## 🔒 Segurança

### Credenciais

⚠️ **NUNCA commite credenciais no Git!**

✅ **Sempre use**:
- Variáveis de ambiente (`.env`)
- Databricks Secrets
- Azure Key Vault

```python
# ✅ CORRETO
username = os.getenv('SYNAPSE_USERNAME')

# ❌ ERRADO
username = "meu_usuario"  # NUNCA!
```

### Controle de Acesso

Configure RBAC (Role-Based Access Control) no Azure:
- **Desenvolvedores**: Leitura/Escrita em camadas Bronze e Silver
- **Analistas**: Leitura em todas as camadas
- **Power BI**: Leitura apenas em Gold

---

## 🆘 Precisa de Ajuda?

### Problemas Comuns

1. **"Erro ao ler dados"**
   - ➡️ Consulte [Debugging](docs/04_DEBUGGING_E_DEPLOY.md#debugging---problemas-comuns)

2. **"Pipeline muito lento"**
   - ➡️ Veja [Performance](docs/04_DEBUGGING_E_DEPLOY.md#4-pipeline-muito-lento)

3. **"Não sei qual fonte usar"**
   - ➡️ Veja [Fontes de Dados](#-fontes-de-dados-suportadas)

### Recursos

- 📚 **Documentação**: [`docs/`](docs/)
- 🎯 **Templates**: [`notebooks/templates/`](notebooks/templates/)
- 💬 **Suporte**: Entre em contato com a equipe de dados

---

## 🤝 Contribuindo

### Como Contribuir

1. Crie uma branch para sua feature
   ```bash
   git checkout -b feature/minha-feature
   ```

2. Faça suas alterações seguindo os [Padrões do Projeto](docs/03_PADROES_PROJETO.md)

3. Commit com mensagem descritiva
   ```bash
   git commit -m "feat(bronze): adiciona notebook vendas"
   ```

4. Envie para o repositório
   ```bash
   git push origin feature/minha-feature
   ```

5. Abra um Pull Request

### Padrões de Commit

```
feat: Nova funcionalidade
fix: Correção de bug
docs: Documentação
refactor: Refatoração
test: Testes
```

---

## 📈 Roadmap

### Versão Atual: 1.0
- ✅ Estrutura de projeto completa
- ✅ Templates para Bronze, Silver, Gold
- ✅ Conectores Azure (Synapse, Data Lake, SharePoint)
- ✅ Documentação completa
- ✅ Sistema de logging e auditoria

### Próximas Versões

#### v1.1 (Planejado)
- [ ] Testes automatizados
- [ ] CI/CD com GitHub Actions
- [ ] Mais conectores (SQL Server, API REST)

#### v1.2 (Futuro)
- [ ] Interface web para configuração
- [ ] Monitoramento em tempo real
- [ ] Machine Learning integrado

---

## 📄 Licença

Este projeto é de uso interno da empresa.

---

## 👥 Equipe

Desenvolvido pela equipe de Engenharia de Dados com foco em democratização de dados e empowerment das áreas de negócio.

---

## 📞 Contato

Para dúvidas, sugestões ou suporte:
- 📧 Email: equipe.dados@empresa.com
- 💬 Teams: Canal Engenharia de Dados
- 📝 Issues: Use o GitHub Issues deste repositório

---

**Versão**: 1.0
**Última atualização**: 2024
**Status**: ✅ Produção

---

## ⭐ Início Rápido - Checklist

Para começar hoje mesmo:

- [ ] Clone o repositório
- [ ] Configure `.env` com suas credenciais
- [ ] Leia o [Guia de Iniciantes](docs/02_GUIA_INICIANTES_PYSPARK.md)
- [ ] Copie um template Bronze
- [ ] Configure para uma fonte simples
- [ ] Execute seu primeiro pipeline!

**Boa sorte e bons dados! 🚀📊**
