# Pipeline de Produção

## 📋 Visão Geral

Este pipeline processa dados da área de **Produção**, incluindo:
- Ordens de produção
- Vendas
- Indicadores de produtividade
- Outros dados operacionais de produção

## 🗂️ Estrutura

```
pipelines/producao/
├── README.md                       # Este arquivo
├── pipeline_producao.py            # Orquestrador principal
└── notebooks/                      # Notebooks específicos (criar conforme necessário)
    ├── bronze_vendas.py
    ├── silver_vendas.py
    └── gold_vendas_mensais.py
```

## 🚀 Como Usar

### 1. Criar Notebooks para suas Fontes

Para cada fonte de dados:

1. **Copie os templates** da pasta `notebooks/templates/`
2. **Renomeie** adequadamente (ex: `bronze_vendas.py`)
3. **Configure** os parâmetros conforme sua fonte
4. **Salve** na pasta `notebooks/bronze/`, `notebooks/silver/` ou `notebooks/gold/`

### 2. Configurar o Orquestrador

Edite o arquivo `pipeline_producao.py` e adicione suas fontes em `FONTES`:

```python
FONTES = [
    {
        "nome": "vendas",
        "bronze_notebook": "/Workspace/notebooks/bronze/bronze_vendas",
        "silver_notebook": "/Workspace/notebooks/silver/silver_vendas",
        "gold_notebooks": [
            "/Workspace/notebooks/gold/gold_vendas_mensais"
        ]
    },
    # Adicione mais fontes aqui
]
```

### 3. Executar o Pipeline

#### Execução Manual
1. Abra `pipeline_producao.py` no Databricks/Synapse
2. Execute o notebook completo
3. Monitore os logs de execução

#### Execução Agendada
Configure um Job no Databricks ou Azure Data Factory:
- **Notebook**: `pipelines/producao/pipeline_producao.py`
- **Frequência**: Diária
- **Horário**: 06:00 (conforme `config.yaml`)

## ⚙️ Configurações

### Variáveis de Ambiente Necessárias

Certifique-se de que as seguintes variáveis estejam configuradas em `.env`:

```bash
# Azure Synapse (se usado)
SYNAPSE_WORKSPACE_NAME=seu-workspace
SYNAPSE_DATABASE=DW_Producao
SYNAPSE_USERNAME=seu-usuario
SYNAPSE_PASSWORD=sua-senha

# Azure Data Lake
AZURE_STORAGE_ACCOUNT=seu-storage
AZURE_STORAGE_CONNECTION_STRING=...

# SharePoint (se usado)
SHAREPOINT_SITE_URL=...
SHAREPOINT_CLIENT_ID=...
SHAREPOINT_CLIENT_SECRET=...
```

### Configuração de Fontes em `config/sources.yaml`

Adicione suas fontes de produção:

```yaml
synapse_sources:
  vendas:
    type: "synapse"
    database: "DW_Vendas"
    schema: "dbo"
    table: "fato_vendas"
    load_type: "incremental"
    incremental_column: "data_atualizacao"
    primary_key: ["id_venda"]
    business_area: "producao"
```

## 📊 Dados Processados

### Camada Bronze (Dados Brutos)
- Localização: `bronze/producao/`
- Formato: Parquet
- Conteúdo: Dados exatamente como vieram da origem

### Camada Silver (Dados Limpos)
- Localização: `silver/producao/`
- Formato: Delta Lake
- Conteúdo: Dados limpos, validados e padronizados

### Camada Gold (Agregações)
- Localização: `gold/producao/`
- Formato: Delta Lake
- Conteúdo: Agregações, métricas e modelos dimensionais para Power BI

## 🔧 Troubleshooting

### Pipeline Falhou
1. Verifique os logs no próprio notebook
2. Consulte a tabela de auditoria: `gold.auditoria_execucoes`
3. Execute manualmente célula por célula para identificar o problema

### Dados Não Atualizados
1. Verifique se o job está agendado corretamente
2. Confirme que as credenciais estão válidas
3. Verifique se a fonte de dados está acessível

### Performance Ruim
1. Verifique particionamento nas camadas
2. Execute `OPTIMIZE` nas tabelas Delta
3. Considere ajustar `Z_ORDER_COLUMNS` nas tabelas Gold

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `docs/`
2. Veja exemplos nos templates
3. Entre em contato com a equipe de dados
