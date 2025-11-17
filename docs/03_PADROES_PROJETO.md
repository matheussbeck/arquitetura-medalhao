# 📋 Padrões e Convenções do Projeto

## Índice
1. [Nomenclatura](#nomenclatura)
2. [Estrutura de Pastas](#estrutura-de-pastas)
3. [Padrões de Código](#padrões-de-código)
4. [Configuração](#configuração)
5. [Logs e Auditoria](#logs-e-auditoria)
6. [Versionamento](#versionamento)

---

## Nomenclatura

### Arquivos e Diretórios

#### Notebooks
```
bronze_<area>_<fonte>.py
silver_<area>_<fonte>.py
gold_<area>_<metrica>.py

Exemplos:
✅ bronze_producao_vendas.py
✅ silver_producao_vendas.py
✅ gold_producao_vendas_mensais.py
✅ gold_diretoria_kpis_executivos.py
```

#### Pastas de Dados
```
<camada>/<area>/<fonte>/
<camada>/<area>/<assunto>/

Exemplos:
✅ bronze/producao/vendas/
✅ silver/producao/vendas/
✅ gold/diretoria/kpis_executivos/
```

### Tabelas e Colunas

#### Nomes de Tabelas
- Minúsculas com underscores
- Prefixo da camada (opcional mas recomendado)

```
Fatos:      fato_<assunto>
Dimensões:  dim_<assunto>
Agregações: agg_<assunto>

Exemplos:
✅ fato_vendas_diarias
✅ dim_clientes
✅ dim_tempo
✅ agg_vendas_mensais
```

#### Nomes de Colunas

**Regras**:
- Minúsculas com underscores
- Descritivo mas conciso
- Sem caracteres especiais ou acentos

```
✅ id_cliente
✅ data_venda
✅ valor_total
✅ quantidade_vendida

❌ IdCliente  (CamelCase)
❌ Data Venda  (espaço)
❌ ValorTotal  (sem underscore)
❌ qtd  (abreviação obscura)
```

#### Prefixos Especiais
```
id_*           : Identificadores
num_*          : Números/Quantidades
data_*         : Datas
is_*           : Booleanos (true/false)
valor_*        : Valores monetários
percentual_*   : Percentuais
qtd_*          : Quantidades (use apenas se contextualmente claro)

Exemplos:
✅ id_venda
✅ num_pedidos
✅ data_criacao
✅ is_ativo
✅ valor_total
✅ percentual_desconto
```

#### Colunas de Auditoria

Padrão obrigatório para todas as camadas:

```python
# Bronze
bronze_ingestion_date     # Timestamp da ingestão
bronze_source            # Nome da fonte
bronze_load_type         # "full" ou "incremental"

# Silver
silver_processing_date   # Timestamp do processamento
silver_pipeline_version  # Versão do pipeline

# Gold
gold_processing_date     # Timestamp do processamento
gold_table_name         # Nome da tabela Gold
```

---

## Estrutura de Pastas

### Organização Padrão

```
arquitetura-medalhao/
├── config/                    # Configurações
│   ├── config.yaml           # Config principal
│   ├── sources.yaml          # Definição de fontes
│   └── .env                  # Variáveis de ambiente (não commitado)
│
├── data/                      # Dados locais (não commitados)
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── notebooks/                 # Notebooks organizados
│   ├── templates/            # Templates reutilizáveis
│   │   ├── bronze_template.py
│   │   ├── silver_template.py
│   │   └── gold_template.py
│   ├── bronze/               # Notebooks Bronze
│   ├── silver/               # Notebooks Silver
│   └── gold/                 # Notebooks Gold
│
├── pipelines/                # Orquestradores por área
│   ├── cct/
│   ├── producao/
│   ├── manutencao/
│   ├── apoio/
│   ├── ssma/
│   ├── agronomico/
│   ├── planejamento/
│   ├── diretoria/
│   ├── governanca_operacional/
│   └── outros/
│
├── utils/                    # Utilitários Python
│   ├── config_loader.py
│   ├── spark_session.py
│   ├── data_quality.py
│   ├── logger.py
│   └── connectors/
│       ├── azure_connector.py
│       ├── synapse_connector.py
│       └── sharepoint_connector.py
│
├── docs/                     # Documentação
│   ├── 01_BOAS_PRATICAS_ARQUITETURA_MEDALHAO.md
│   ├── 02_GUIA_INICIANTES_PYSPARK.md
│   ├── 03_PADROES_PROJETO.md
│   └── 04_DEBUGGING.md
│
├── tests/                    # Testes
│
├── .gitignore               # Arquivos a ignorar
├── .env.example             # Exemplo de variáveis
└── README.md                # Documentação principal
```

---

## Padrões de Código

### Estrutura de Notebook

Todos os notebooks devem seguir esta estrutura:

```python
# 1. DOCUMENTAÇÃO (Markdown)
# MAGIC %md
# MAGIC # Título do Notebook
# MAGIC Descrição do objetivo

# 2. CONFIGURAÇÕES
FONTE_DADOS = "nome_fonte"
AREA_NEGOCIO = "producao"
# ... outras configs

# 3. IMPORTAÇÕES
import sys
from pyspark.sql import functions as F
sys.path.append('/Workspace/utils')
from config_loader import get_config_loader
# ... outras importações

# 4. SETUP
config = get_config_loader()
spark = get_spark_session(...)
logger = PipelineLogger(...)

# 5. LÓGICA PRINCIPAL
logger.start()
try:
    # Leitura
    df = ...

    # Transformações
    df = df.filter(...)

    # Escrita
    df.write.save(...)

    logger.end(status="success")
except Exception as e:
    logger.error("Erro", exception=e)
    logger.end(status="failed")
    raise

# 6. RESUMO
print("Resumo da execução...")
```

### Importações

**Ordem padrão**:
```python
# 1. Bibliotecas Python padrão
import sys
import os
from datetime import datetime

# 2. PySpark
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import *

# 3. Utils do projeto
sys.path.append('/Workspace/utils')
from config_loader import get_config_loader
from spark_session import get_spark_session
from logger import PipelineLogger
from data_quality import DataQualityChecker

# 4. Conectores
from connectors.azure_connector import AzureDataLakeConnector
from connectors.synapse_connector import SynapseConnector
```

### Comentários

```python
# ============================================================================
# SEÇÃO PRINCIPAL
# ============================================================================

# Subseção
# --------

# Comentário de uma linha para operação simples
df = df.filter(col("valor") > 0)

# Comentário de múltiplas linhas para lógica complexa
# Regra de Negócio: Clientes VIP são aqueles que:
# 1. Compraram mais de R$ 10.000 nos últimos 12 meses
# 2. Possuem mais de 5 pedidos no período
# 3. Não possuem débitos em aberto
df_vip = df.filter(...)
```

### Logging

**Use logging em todos os passos importantes**:

```python
logger.start(param1="valor1")

logger.info("📖 Lendo dados da fonte X")
df = read_data()

logger.log_dataframe_info(df, "Dados lidos")

logger.info("🔄 Aplicando transformações")
df_transformed = transform(df)

logger.log_transformation(
    "Limpeza de dados",
    input_count=1000,
    output_count=950
)

logger.end(status="success")
```

---

## Configuração

### Variáveis de Ambiente

**Sempre use variáveis de ambiente para credenciais**:

```python
# ✅ CORRETO
username = os.getenv('SYNAPSE_USERNAME')
password = os.getenv('SYNAPSE_PASSWORD')

# ❌ ERRADO - Nunca faça isso!
username = "meu_usuario"
password = "minha_senha"
```

### Config.yaml

Organize configurações por contexto:

```yaml
# Agrupamento lógico
azure_data_lake:
  account_name: "${AZURE_STORAGE_ACCOUNT}"
  container_bronze: "bronze"
  # ...

# Use variáveis de ambiente
synapse:
  database: "${SYNAPSE_DATABASE}"
  # ...

# Valores padrão quando aplicável
performance:
  shuffle_partitions: 200
  executor_memory: "4g"
```

---

## Logs e Auditoria

### Logs Obrigatórios

Todo pipeline DEVE registrar:

```python
# Início
logger.start(
    fonte="vendas",
    area="producao",
    tipo_carga="incremental"
)

# Durante processamento
logger.info("Mensagem informativa")
logger.warning("Alerta sobre algo")
logger.error("Erro encontrado", exception=e)

# Fim
logger.end(status="success")  # ou "failed", "partial"
```

### Tabela de Auditoria

Todos os pipelines salvam automaticamente em:
```
gold.auditoria_execucoes
```

Campos registrados:
- execution_id
- pipeline_name
- start_time
- end_time
- status
- records_processed
- duration_seconds
- error_count

---

## Versionamento

### Git - O que Commitar

**✅ Sempre commitar**:
- Notebooks (.py, .ipynb)
- Configurações (.yaml)
- Documentação (.md)
- Utilitários Python (.py)
- .gitignore
- .env.example

**❌ Nunca commitar**:
- .env (credenciais)
- Dados (bronze/, silver/, gold/)
- Logs
- Checkpoints
- .ipynb_checkpoints

### Mensagens de Commit

**Formato**:
```
<tipo>(<escopo>): <mensagem>

Tipos:
- feat: Nova funcionalidade
- fix: Correção de bug
- docs: Documentação
- refactor: Refatoração
- test: Testes
- chore: Manutenção

Exemplos:
✅ feat(bronze): adiciona notebook vendas
✅ fix(silver): corrige remoção de duplicatas
✅ docs: atualiza guia de iniciantes
✅ refactor(utils): melhora performance do connector
```

### Branches

```
main              : Produção
develop           : Desenvolvimento
feature/nome      : Nova funcionalidade
fix/nome          : Correção
hotfix/nome       : Correção urgente
```

---

## Boas Práticas de Código

### 1. DRY (Don't Repeat Yourself)

```python
# ❌ RUIM: Código repetido
df1 = df1.withColumn("ano", F.year("data"))
df1 = df1.withColumn("mes", F.month("data"))

df2 = df2.withColumn("ano", F.year("data"))
df2 = df2.withColumn("mes", F.month("data"))

# ✅ BOM: Função reutilizável
def adicionar_colunas_tempo(df, coluna_data="data"):
    return df \
        .withColumn("ano", F.year(coluna_data)) \
        .withColumn("mes", F.month(coluna_data))

df1 = adicionar_colunas_tempo(df1)
df2 = adicionar_colunas_tempo(df2)
```

### 2. Configurações Externalizadas

```python
# ❌ RUIM: Valores hardcoded
df = df.filter(col("valor") > 1000)

# ✅ BOM: Configurável
VALOR_MINIMO = config.get('regras_negocio.valor_minimo', 1000)
df = df.filter(col("valor") > VALOR_MINIMO)
```

### 3. Tratamento de Erros

```python
# ✅ BOM: Trata erros apropriadamente
try:
    df = spark.read.parquet(path)
    logger.info(f"✅ Leitura concluída: {df.count()} registros")
except FileNotFoundError:
    logger.error(f"Arquivo não encontrado: {path}")
    raise
except Exception as e:
    logger.error("Erro inesperado", exception=e)
    raise
```

### 4. Validações

```python
# ✅ BOM: Valida inputs
def processar_vendas(df, data_inicio):
    # Valida DataFrame
    if df is None:
        raise ValueError("DataFrame não pode ser None")

    # Valida colunas necessárias
    required_cols = ["id_venda", "valor", "data"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes: {missing}")

    # Valida data
    if not data_inicio:
        raise ValueError("data_inicio é obrigatória")

    # Processa...
    return df.filter(...)
```

---

## Checklist de Qualidade

Antes de commitar código, verifique:

- [ ] Código segue padrões de nomenclatura
- [ ] Logging implementado
- [ ] Tratamento de erros presente
- [ ] Sem credenciais hardcoded
- [ ] Comentários em lógica complexa
- [ ] Testado com dados reais
- [ ] Documentação atualizada
- [ ] .gitignore configurado
- [ ] Sem warnings do Spark

---

## Recursos

- Templates: `notebooks/templates/`
- Exemplos: `notebooks/bronze/`, `silver/`, `gold/`
- Utilitários: `utils/`
- Documentação: `docs/`

---

**Última atualização**: 2024
**Versão**: 1.0
