# Databricks notebook source
# MAGIC %md
# MAGIC # 🥉 TEMPLATE BRONZE - INGESTÃO DE DADOS
# MAGIC
# MAGIC ## 📋 Objetivo
# MAGIC Este notebook realiza a ingestão de dados brutos (raw) para a camada Bronze.
# MAGIC A camada Bronze armazena dados exatamente como vieram da origem, sem transformações.
# MAGIC
# MAGIC ## 📝 Instruções de Uso
# MAGIC 1. **Copie este template** para a pasta da sua área de negócio
# MAGIC 2. **Renomeie** o arquivo para refletir a fonte de dados (ex: bronze_vendas.py)
# MAGIC 3. **Configure** os parâmetros na seção "CONFIGURAÇÕES"
# MAGIC 4. **Execute** célula por célula ou rode tudo com "Run All"
# MAGIC
# MAGIC ## 🎯 O que este notebook faz:
# MAGIC - Conecta na fonte de dados (Synapse, Data Lake, SharePoint, etc.)
# MAGIC - Lê os dados brutos
# MAGIC - Adiciona colunas de auditoria (data de ingestão, fonte, etc.)
# MAGIC - Salva na camada Bronze no formato Parquet
# MAGIC - Gera log de execução
# MAGIC
# MAGIC ## ⚠️ IMPORTANTE
# MAGIC - NÃO faça transformações nos dados nesta camada!
# MAGIC - Mantenha os dados exatamente como vieram da origem
# MAGIC - Use apenas tipo de carga FULL ou INCREMENTAL

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1️⃣ CONFIGURAÇÕES
# MAGIC
# MAGIC **Configure estas variáveis antes de executar o notebook**

# COMMAND ----------

# ============================================================================
# CONFIGURAÇÕES DO PIPELINE
# ============================================================================

# Nome da fonte de dados (usado para logs e nomeação de arquivos)
# Exemplo: "vendas", "equipamentos", "clientes"
FONTE_DADOS = "nome_da_fonte"  # ⬅️ ALTERE AQUI

# Área de negócio (cct, producao, manutencao, apoio, etc.)
AREA_NEGOCIO = "producao"  # ⬅️ ALTERE AQUI

# Tipo de fonte (synapse, datalake, sql_dw, sharepoint, local)
TIPO_FONTE = "synapse"  # ⬅️ ALTERE AQUI

# Tipo de carga (full ou incremental)
TIPO_CARGA = "incremental"  # ⬅️ ALTERE AQUI (full ou incremental)

# Se incremental, informe a coluna de controle e o último valor processado
COLUNA_INCREMENTAL = "data_atualizacao"  # ⬅️ ALTERE AQUI (se incremental)
ULTIMO_VALOR_PROCESSADO = "2024-01-01"  # ⬅️ ALTERE AQUI (se incremental)

# ============================================================================
# CONFIGURAÇÕES ESPECÍFICAS POR TIPO DE FONTE
# ============================================================================

# Para fonte SYNAPSE:
SYNAPSE_DATABASE = "DW_Vendas"  # ⬅️ ALTERE AQUI
SYNAPSE_SCHEMA = "dbo"  # ⬅️ ALTERE AQUI
SYNAPSE_TABLE = "fato_vendas"  # ⬅️ ALTERE AQUI

# Para fonte DATALAKE:
DATALAKE_PATH = "raw/vendas/2024/"  # ⬅️ ALTERE AQUI
DATALAKE_FORMAT = "parquet"  # ⬅️ ALTERE AQUI (parquet, csv, json)

# Para fonte SHAREPOINT:
SHAREPOINT_LIBRARY = "Documentos"  # ⬅️ ALTERE AQUI
SHAREPOINT_FOLDER = "Relatorios/Vendas"  # ⬅️ ALTERE AQUI
SHAREPOINT_FILENAME = "vendas_2024.xlsx"  # ⬅️ ALTERE AQUI
SHAREPOINT_SHEET = "Dados"  # ⬅️ ALTERE AQUI (se Excel)

# Para fonte LOCAL:
LOCAL_PATH = "data/input/vendas.csv"  # ⬅️ ALTERE AQUI
LOCAL_FORMAT = "csv"  # ⬅️ ALTERE AQUI
LOCAL_DELIMITER = ","  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE SAÍDA
# ============================================================================

# Caminho de saída na camada Bronze
OUTPUT_PATH = f"bronze/{AREA_NEGOCIO}/{FONTE_DADOS}/"

# Colunas para particionamento (deixe vazio [] se não quiser particionar)
PARTITION_COLUMNS = ["ano", "mes", "dia"]  # ⬅️ ALTERE AQUI

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2️⃣ IMPORTAÇÕES E SETUP
# MAGIC
# MAGIC **NÃO ALTERE ESTA SEÇÃO - Apenas execute**

# COMMAND ----------

# Importações necessárias
import sys
from datetime import datetime
from pyspark.sql import functions as F

# Adiciona utils ao path (ajuste o caminho se necessário)
sys.path.append('/Workspace/utils')  # Para Databricks
# sys.path.append('../utils')  # Para execução local

# Importa utilitários do projeto
from config_loader import get_config_loader
from spark_session import get_spark_session
from connectors.azure_connector import AzureDataLakeConnector
from connectors.synapse_connector import SynapseConnector
from connectors.sharepoint_connector import SharePointConnector
from logger import PipelineLogger
from data_quality import DataQualityChecker

# Carrega configurações
config = get_config_loader()

# Cria sessão Spark (se não existir)
try:
    spark
    print("✅ Usando sessão Spark existente")
except NameError:
    spark = get_spark_session(f"Bronze_{AREA_NEGOCIO}_{FONTE_DADOS}", config.config)
    print("✅ Nova sessão Spark criada")

# Inicializa logger
logger = PipelineLogger(
    pipeline_name=f"bronze_{AREA_NEGOCIO}_{FONTE_DADOS}",
    spark=spark,
    config=config.config
)

# Inicializa checker de qualidade
quality_checker = DataQualityChecker(config.config)

print("\n" + "="*80)
print(f"🥉 PIPELINE BRONZE - {FONTE_DADOS.upper()}")
print(f"   Área: {AREA_NEGOCIO}")
print(f"   Tipo de Fonte: {TIPO_FONTE}")
print(f"   Tipo de Carga: {TIPO_CARGA}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3️⃣ LEITURA DA FONTE DE DADOS
# MAGIC
# MAGIC **Esta seção lê os dados da fonte configurada**

# COMMAND ----------

# Inicia execução
logger.start(
    fonte=FONTE_DADOS,
    area=AREA_NEGOCIO,
    tipo_carga=TIPO_CARGA
)

# Variável para armazenar o DataFrame
df_raw = None

try:
    # ========================================================================
    # LEITURA DE DADOS BASEADA NO TIPO DE FONTE
    # ========================================================================

    if TIPO_FONTE == "synapse":
        logger.info(f"📖 Lendo dados do Synapse: {SYNAPSE_DATABASE}.{SYNAPSE_SCHEMA}.{SYNAPSE_TABLE}")

        # Cria conector Synapse
        synapse = SynapseConnector(spark, config.config)

        if TIPO_CARGA == "incremental":
            # Leitura incremental
            df_raw = synapse.read_incremental(
                database=SYNAPSE_DATABASE,
                schema=SYNAPSE_SCHEMA,
                table=SYNAPSE_TABLE,
                incremental_column=COLUNA_INCREMENTAL,
                last_value=ULTIMO_VALOR_PROCESSADO
            )
        else:
            # Leitura full
            df_raw = synapse.read_synapse_table(
                database=SYNAPSE_DATABASE,
                schema=SYNAPSE_SCHEMA,
                table=SYNAPSE_TABLE
            )

    elif TIPO_FONTE == "datalake":
        logger.info(f"📖 Lendo dados do Data Lake: {DATALAKE_PATH}")

        # Cria conector Data Lake
        adls = AzureDataLakeConnector(spark, config.config)

        if TIPO_CARGA == "incremental" and COLUNA_INCREMENTAL:
            # Leitura incremental
            df_raw = adls.read_incremental(
                path=DATALAKE_PATH,
                date_column=COLUNA_INCREMENTAL,
                start_date=ULTIMO_VALOR_PROCESSADO,
                format=DATALAKE_FORMAT
            )
        else:
            # Leitura full
            df_raw = adls.read(
                path=DATALAKE_PATH,
                format=DATALAKE_FORMAT
            )

    elif TIPO_FONTE == "sharepoint":
        logger.info(f"📖 Lendo dados do SharePoint: {SHAREPOINT_FILENAME}")

        # Cria conector SharePoint
        sp = SharePointConnector(spark, config.config)
        sp.authenticate()

        if SHAREPOINT_FILENAME.endswith('.xlsx'):
            df_raw = sp.read_excel(
                file_name=SHAREPOINT_FILENAME,
                library=SHAREPOINT_LIBRARY,
                folder=SHAREPOINT_FOLDER,
                sheet_name=SHAREPOINT_SHEET
            )
        else:
            df_raw = sp.read_csv(
                file_name=SHAREPOINT_FILENAME,
                library=SHAREPOINT_LIBRARY,
                folder=SHAREPOINT_FOLDER
            )

    elif TIPO_FONTE == "local":
        logger.info(f"📖 Lendo dados local: {LOCAL_PATH}")

        if LOCAL_FORMAT == "csv":
            df_raw = spark.read.format("csv") \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .option("delimiter", LOCAL_DELIMITER) \
                .load(LOCAL_PATH)
        elif LOCAL_FORMAT == "excel":
            # Requer biblioteca pandas
            import pandas as pd
            pdf = pd.read_excel(LOCAL_PATH)
            df_raw = spark.createDataFrame(pdf)
        else:
            df_raw = spark.read.format(LOCAL_FORMAT).load(LOCAL_PATH)

    else:
        raise ValueError(f"Tipo de fonte não suportado: {TIPO_FONTE}")

    # Loga informações do DataFrame
    logger.log_dataframe_info(df_raw, "Dados lidos da origem")

except Exception as e:
    logger.error("Erro ao ler dados da fonte", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4️⃣ ADIÇÃO DE COLUNAS DE AUDITORIA
# MAGIC
# MAGIC **Adiciona metadados de controle**

# COMMAND ----------

try:
    # ========================================================================
    # ADICIONA COLUNAS DE AUDITORIA
    # ========================================================================

    logger.info("📝 Adicionando colunas de auditoria")

    # Data e hora da ingestão
    df_bronze = df_raw.withColumn(
        "bronze_ingestion_date",
        F.current_timestamp()
    )

    # Nome da fonte
    df_bronze = df_bronze.withColumn(
        "bronze_source",
        F.lit(FONTE_DADOS)
    )

    # Tipo de carga
    df_bronze = df_bronze.withColumn(
        "bronze_load_type",
        F.lit(TIPO_CARGA)
    )

    # Se particionamento por data for necessário e não existir
    if "ano" in PARTITION_COLUMNS or "mes" in PARTITION_COLUMNS or "dia" in PARTITION_COLUMNS:
        # Tenta usar coluna de data existente ou usa data de ingestão
        date_column = COLUNA_INCREMENTAL if COLUNA_INCREMENTAL in df_bronze.columns else "bronze_ingestion_date"

        if "ano" in PARTITION_COLUMNS:
            df_bronze = df_bronze.withColumn("ano", F.year(F.col(date_column)))

        if "mes" in PARTITION_COLUMNS:
            df_bronze = df_bronze.withColumn("mes", F.month(F.col(date_column)))

        if "dia" in PARTITION_COLUMNS:
            df_bronze = df_bronze.withColumn("dia", F.dayofmonth(F.col(date_column)))

    logger.log_dataframe_info(df_bronze, "Dados com colunas de auditoria")

except Exception as e:
    logger.error("Erro ao adicionar colunas de auditoria", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5️⃣ VERIFICAÇÃO DE QUALIDADE BÁSICA
# MAGIC
# MAGIC **Verifica problemas óbvios nos dados**

# COMMAND ----------

try:
    # ========================================================================
    # VERIFICAÇÕES DE QUALIDADE
    # ========================================================================

    logger.info("🔍 Executando verificações de qualidade")

    # Verifica se há dados
    record_count = df_bronze.count()
    if record_count == 0:
        logger.warning("⚠️ Nenhum registro encontrado!")
    else:
        logger.info(f"✅ {record_count:,} registros encontrados")

    # Verifica valores nulos (apenas alerta, não bloqueia)
    null_report = quality_checker.check_null_values(df_bronze)

    # Mostra amostra dos dados
    print("\n📊 AMOSTRA DOS DADOS (5 primeiras linhas):")
    print("="*80)
    df_bronze.show(5, truncate=False)

except Exception as e:
    logger.error("Erro na verificação de qualidade", exception=e)
    # Não levanta exceção - qualidade é informativa na camada Bronze

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6️⃣ ESCRITA NA CAMADA BRONZE
# MAGIC
# MAGIC **Salva os dados no Data Lake (camada Bronze)**

# COMMAND ----------

try:
    # ========================================================================
    # ESCRITA NO DATA LAKE
    # ========================================================================

    logger.info(f"💾 Salvando dados na camada Bronze: {OUTPUT_PATH}")

    # Cria conector para escrita
    adls = AzureDataLakeConnector(spark, config.config)

    # Define modo de escrita
    write_mode = "overwrite" if TIPO_CARGA == "full" else "append"

    # Escreve os dados
    adls.write(
        df=df_bronze,
        path=OUTPUT_PATH,
        format="parquet",
        mode=write_mode,
        partition_by=PARTITION_COLUMNS if PARTITION_COLUMNS else None
    )

    logger.info("✅ Dados salvos com sucesso!")

    # Atualiza contador de registros processados
    logger.records_processed = record_count

except Exception as e:
    logger.error("Erro ao escrever dados na camada Bronze", exception=e)
    logger.end(status="failed")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7️⃣ FINALIZAÇÃO
# MAGIC
# MAGIC **Encerra o pipeline e gera logs**

# COMMAND ----------

# Finaliza execução com sucesso
logger.end(status="success")

# Mostra resumo
summary = logger.get_execution_summary()

print("\n" + "="*80)
print("📊 RESUMO DA EXECUÇÃO")
print("="*80)
print(f"Pipeline: {summary['pipeline_name']}")
print(f"Status: {summary['status']}")
print(f"Registros Processados: {summary['records_processed']:,}")
print(f"Duração: {summary['duration_seconds']:.2f} segundos")
print(f"Início: {summary['start_time']}")
print(f"Fim: {summary['end_time']}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ FIM DO NOTEBOOK
# MAGIC
# MAGIC ### Próximos Passos:
# MAGIC 1. Os dados agora estão disponíveis na camada Bronze
# MAGIC 2. Execute o notebook Silver correspondente para transformar os dados
# MAGIC 3. Verifique os logs de auditoria para acompanhar a execução
# MAGIC
# MAGIC ### 💡 Dicas:
# MAGIC - Se encontrar erros, verifique primeiro as configurações na seção 1
# MAGIC - Para depuração, execute célula por célula
# MAGIC - Mantenha um histórico do ULTIMO_VALOR_PROCESSADO para cargas incrementais
