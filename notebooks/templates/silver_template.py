# Databricks notebook source
# MAGIC %md
# MAGIC # 🥈 TEMPLATE SILVER - TRANSFORMAÇÃO E LIMPEZA
# MAGIC
# MAGIC ## 📋 Objetivo
# MAGIC Este notebook transforma e limpa dados da camada Bronze para a camada Silver.
# MAGIC A camada Silver contém dados limpos, validados e padronizados.
# MAGIC
# MAGIC ## 📝 Instruções de Uso
# MAGIC 1. **Copie este template** para a pasta da sua área de negócio
# MAGIC 2. **Renomeie** o arquivo (ex: silver_vendas.py)
# MAGIC 3. **Configure** os parâmetros na seção "CONFIGURAÇÕES"
# MAGIC 4. **Customize** as transformações na seção "TRANSFORMAÇÕES CUSTOMIZADAS"
# MAGIC 5. **Execute** o notebook
# MAGIC
# MAGIC ## 🎯 O que este notebook faz:
# MAGIC - Lê dados da camada Bronze
# MAGIC - Remove duplicatas
# MAGIC - Limpa valores nulos
# MAGIC - Padroniza formatos (datas, strings, números)
# MAGIC - Valida qualidade dos dados
# MAGIC - Aplica transformações de negócio
# MAGIC - Salva na camada Silver (formato Delta Lake)
# MAGIC
# MAGIC ## ⚠️ IMPORTANTE
# MAGIC - Transformações devem ser idempotentes (mesma entrada = mesma saída)
# MAGIC - Documente todas as regras de negócio aplicadas
# MAGIC - Use Delta Lake para garantir ACID transactions

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1️⃣ CONFIGURAÇÕES
# MAGIC
# MAGIC **Configure estas variáveis antes de executar o notebook**

# COMMAND ----------

# ============================================================================
# CONFIGURAÇÕES DO PIPELINE
# ============================================================================

# Nome da fonte de dados
FONTE_DADOS = "nome_da_fonte"  # ⬅️ ALTERE AQUI

# Área de negócio
AREA_NEGOCIO = "producao"  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE ENTRADA (BRONZE)
# ============================================================================

# Caminho dos dados Bronze
BRONZE_PATH = f"bronze/{AREA_NEGOCIO}/{FONTE_DADOS}/"

# ============================================================================
# CONFIGURAÇÕES DE SAÍDA (SILVER)
# ============================================================================

# Caminho de saída na camada Silver
SILVER_PATH = f"silver/{AREA_NEGOCIO}/{FONTE_DADOS}/"

# Colunas para particionar
PARTITION_COLUMNS = ["ano", "mes"]  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE QUALIDADE
# ============================================================================

# Colunas que formam a chave primária (para remoção de duplicatas)
PRIMARY_KEY_COLUMNS = ["id"]  # ⬅️ ALTERE AQUI

# Colunas obrigatórias (não podem ser nulas)
REQUIRED_COLUMNS = ["id", "data_registro"]  # ⬅️ ALTERE AQUI

# Colunas de data para padronização
DATE_COLUMNS = ["data_registro", "data_atualizacao"]  # ⬅️ ALTERE AQUI

# Colunas de texto para padronização (trim, uppercase, etc.)
TEXT_COLUMNS = ["nome", "descricao"]  # ⬅️ ALTERE AQUI

# Regras de validação de valores
# Formato: {"coluna": {"min": valor_min, "max": valor_max}}
VALUE_RANGES = {
    "quantidade": {"min": 0, "max": 999999},
    "valor": {"min": 0}
}  # ⬅️ ALTERE AQUI

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2️⃣ IMPORTAÇÕES E SETUP
# MAGIC
# MAGIC **NÃO ALTERE ESTA SEÇÃO - Apenas execute**

# COMMAND ----------

import sys
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql import Window

# Adiciona utils ao path
sys.path.append('/Workspace/utils')

# Importa utilitários
from config_loader import get_config_loader
from spark_session import get_spark_session
from connectors.azure_connector import AzureDataLakeConnector
from logger import PipelineLogger
from data_quality import DataQualityChecker

# Carrega configurações
config = get_config_loader()

# Cria/obtém sessão Spark
try:
    spark
    print("✅ Usando sessão Spark existente")
except NameError:
    spark = get_spark_session(f"Silver_{AREA_NEGOCIO}_{FONTE_DADOS}", config.config)
    print("✅ Nova sessão Spark criada")

# Inicializa logger
logger = PipelineLogger(
    pipeline_name=f"silver_{AREA_NEGOCIO}_{FONTE_DADOS}",
    spark=spark,
    config=config.config
)

# Inicializa checker de qualidade
quality_checker = DataQualityChecker(config.config)

print("\n" + "="*80)
print(f"🥈 PIPELINE SILVER - {FONTE_DADOS.upper()}")
print(f"   Área: {AREA_NEGOCIO}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3️⃣ LEITURA DA CAMADA BRONZE
# MAGIC
# MAGIC **Lê os dados brutos da camada Bronze**

# COMMAND ----------

# Inicia execução
logger.start(fonte=FONTE_DADOS, area=AREA_NEGOCIO, layer="silver")

try:
    logger.info(f"📖 Lendo dados da camada Bronze: {BRONZE_PATH}")

    # Cria conector
    adls = AzureDataLakeConnector(spark, config.config)

    # Lê dados Bronze
    df_bronze = adls.read(
        path=BRONZE_PATH,
        format="parquet"
    )

    input_count = df_bronze.count()
    logger.log_dataframe_info(df_bronze, "Dados Bronze lidos")

except Exception as e:
    logger.error("Erro ao ler dados da camada Bronze", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4️⃣ LIMPEZA E PADRONIZAÇÃO
# MAGIC
# MAGIC **Aplica limpezas e padronizações padrão**

# COMMAND ----------

try:
    logger.info("🧹 Iniciando limpeza e padronização")

    df_clean = df_bronze

    # ========================================================================
    # 1. REMOVE DUPLICATAS
    # ========================================================================
    logger.info("🔄 Removendo duplicatas")

    before_dedup = df_clean.count()

    if PRIMARY_KEY_COLUMNS:
        # Remove duplicatas pela chave primária, mantendo o registro mais recente
        window_spec = Window.partitionBy(PRIMARY_KEY_COLUMNS).orderBy(F.col("bronze_ingestion_date").desc())

        df_clean = df_clean.withColumn("row_num", F.row_number().over(window_spec)) \
                           .filter(F.col("row_num") == 1) \
                           .drop("row_num")
    else:
        # Remove duplicatas completas
        df_clean = df_clean.dropDuplicates()

    after_dedup = df_clean.count()
    logger.log_transformation(
        "Remoção de duplicatas",
        input_count=before_dedup,
        output_count=after_dedup
    )

    # ========================================================================
    # 2. PADRONIZA COLUNAS DE DATA
    # ========================================================================
    if DATE_COLUMNS:
        logger.info("📅 Padronizando datas")

        for col_name in DATE_COLUMNS:
            if col_name in df_clean.columns:
                # Converte para timestamp se ainda não for
                df_clean = df_clean.withColumn(
                    col_name,
                    F.to_timestamp(F.col(col_name))
                )

    # ========================================================================
    # 3. PADRONIZA COLUNAS DE TEXTO
    # ========================================================================
    if TEXT_COLUMNS:
        logger.info("📝 Padronizando texto")

        for col_name in TEXT_COLUMNS:
            if col_name in df_clean.columns:
                # Remove espaços em branco extras
                df_clean = df_clean.withColumn(
                    col_name,
                    F.trim(F.col(col_name))
                )

                # Remove valores vazios (converte para null)
                df_clean = df_clean.withColumn(
                    col_name,
                    F.when(F.col(col_name) == "", None).otherwise(F.col(col_name))
                )

    # ========================================================================
    # 4. REMOVE REGISTROS COM COLUNAS OBRIGATÓRIAS NULAS
    # ========================================================================
    if REQUIRED_COLUMNS:
        logger.info("🔍 Validando colunas obrigatórias")

        before_null_filter = df_clean.count()

        for col_name in REQUIRED_COLUMNS:
            if col_name in df_clean.columns:
                df_clean = df_clean.filter(F.col(col_name).isNotNull())

        after_null_filter = df_clean.count()

        if before_null_filter != after_null_filter:
            logger.log_transformation(
                "Remoção de nulos em colunas obrigatórias",
                input_count=before_null_filter,
                output_count=after_null_filter
            )

    logger.info("✅ Limpeza e padronização concluída")

except Exception as e:
    logger.error("Erro na limpeza e padronização", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5️⃣ TRANSFORMAÇÕES CUSTOMIZADAS
# MAGIC
# MAGIC **⬇️ ADICIONE SUAS TRANSFORMAÇÕES ESPECÍFICAS AQUI ⬇️**
# MAGIC
# MAGIC **Exemplos de transformações comuns:**
# MAGIC - Cálculo de colunas derivadas
# MAGIC - Conversão de unidades
# MAGIC - Categorização de valores
# MAGIC - Joins com outras tabelas
# MAGIC - Agregações específicas

# COMMAND ----------

try:
    logger.info("⚙️ Aplicando transformações customizadas")

    df_transformed = df_clean

    # ========================================================================
    # EXEMPLO 1: CALCULAR COLUNA DERIVADA
    # ========================================================================
    # Descomente e adapte conforme necessário:
    #
    # df_transformed = df_transformed.withColumn(
    #     "valor_total",
    #     F.col("quantidade") * F.col("preco_unitario")
    # )

    # ========================================================================
    # EXEMPLO 2: CATEGORIZAR VALORES
    # ========================================================================
    # df_transformed = df_transformed.withColumn(
    #     "categoria_valor",
    #     F.when(F.col("valor") < 1000, "Baixo")
    #      .when((F.col("valor") >= 1000) & (F.col("valor") < 5000), "Médio")
    #      .otherwise("Alto")
    # )

    # ========================================================================
    # EXEMPLO 3: EXTRAIR COMPONENTES DE DATA
    # ========================================================================
    # if "data_registro" in df_transformed.columns:
    #     df_transformed = df_transformed \
    #         .withColumn("ano_registro", F.year("data_registro")) \
    #         .withColumn("mes_registro", F.month("data_registro")) \
    #         .withColumn("dia_semana", F.dayofweek("data_registro"))

    # ========================================================================
    # EXEMPLO 4: PADRONIZAR VALORES
    # ========================================================================
    # df_transformed = df_transformed.withColumn(
    #     "status",
    #     F.upper(F.col("status"))
    # )

    # ========================================================================
    # EXEMPLO 5: JOIN COM OUTRA TABELA (ENRIQUECIMENTO)
    # ========================================================================
    # # Lê tabela de referência
    # df_ref = adls.read("silver/dimensoes/clientes/", format="delta")
    #
    # # Faz join
    # df_transformed = df_transformed.join(
    #     df_ref.select("id_cliente", "nome_cliente", "segmento"),
    #     on="id_cliente",
    #     how="left"
    # )

    # ⬇️⬇️⬇️ ADICIONE SUAS TRANSFORMAÇÕES ABAIXO ⬇️⬇️⬇️




    # ⬆️⬆️⬆️ ADICIONE SUAS TRANSFORMAÇÕES ACIMA ⬆️⬆️⬆️

    logger.info("✅ Transformações customizadas concluídas")

except Exception as e:
    logger.error("Erro nas transformações customizadas", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6️⃣ VALIDAÇÃO DE QUALIDADE
# MAGIC
# MAGIC **Valida a qualidade dos dados transformados**

# COMMAND ----------

try:
    logger.info("🔍 Validando qualidade dos dados")

    # ========================================================================
    # VALIDAÇÃO DE SCHEMA
    # ========================================================================
    # Opcional: Defina schema esperado
    # expected_schema = {
    #     "id": "bigint",
    #     "nome": "string",
    #     "valor": "double",
    #     "data_registro": "timestamp"
    # }
    # is_valid = quality_checker.validate_schema(df_transformed, expected_schema)

    # ========================================================================
    # VERIFICAÇÃO DE NULOS
    # ========================================================================
    null_report = quality_checker.check_null_values(df_transformed)

    # ========================================================================
    # VERIFICAÇÃO DE DUPLICATAS
    # ========================================================================
    if PRIMARY_KEY_COLUMNS:
        dup_report = quality_checker.check_duplicates(df_transformed, PRIMARY_KEY_COLUMNS)
        logger.log_quality_check(
            "Duplicatas",
            passed=dup_report['duplicate_percentage'] < 0.01,
            details=dup_report
        )

    # ========================================================================
    # VALIDAÇÃO DE RANGES
    # ========================================================================
    if VALUE_RANGES:
        violations = quality_checker.check_value_ranges(df_transformed, VALUE_RANGES)
        total_violations = sum(violations.values())

        logger.log_quality_check(
            "Validação de ranges",
            passed=total_violations == 0,
            details=f"{total_violations} violações encontradas"
        )

    # ========================================================================
    # MOSTRA AMOSTRA DOS DADOS
    # ========================================================================
    print("\n📊 AMOSTRA DOS DADOS TRANSFORMADOS (5 primeiras linhas):")
    print("="*80)
    df_transformed.show(5, truncate=False)

    logger.info("✅ Validação de qualidade concluída")

except Exception as e:
    logger.error("Erro na validação de qualidade", exception=e)
    # Não levanta exceção - qualidade é informativa

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7️⃣ ADIÇÃO DE METADADOS SILVER
# MAGIC
# MAGIC **Adiciona colunas de controle da camada Silver**

# COMMAND ----------

try:
    logger.info("📝 Adicionando metadados Silver")

    df_silver = df_transformed

    # Data e hora do processamento Silver
    df_silver = df_silver.withColumn(
        "silver_processing_date",
        F.current_timestamp()
    )

    # Versão do pipeline (opcional - útil para rastreabilidade)
    df_silver = df_silver.withColumn(
        "silver_pipeline_version",
        F.lit("1.0")
    )

    # Adiciona colunas de particionamento se necessário
    if "ano" in PARTITION_COLUMNS or "mes" in PARTITION_COLUMNS:
        # Usa coluna de data existente ou data de processamento
        date_col = DATE_COLUMNS[0] if DATE_COLUMNS and DATE_COLUMNS[0] in df_silver.columns else "silver_processing_date"

        if "ano" in PARTITION_COLUMNS and "ano" not in df_silver.columns:
            df_silver = df_silver.withColumn("ano", F.year(date_col))

        if "mes" in PARTITION_COLUMNS and "mes" not in df_silver.columns:
            df_silver = df_silver.withColumn("mes", F.month(date_col))

    final_count = df_silver.count()
    logger.log_dataframe_info(df_silver, "Dados Silver finais")

except Exception as e:
    logger.error("Erro ao adicionar metadados", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8️⃣ ESCRITA NA CAMADA SILVER
# MAGIC
# MAGIC **Salva os dados no formato Delta Lake**

# COMMAND ----------

try:
    logger.info(f"💾 Salvando dados na camada Silver: {SILVER_PATH}")

    # ========================================================================
    # ESCRITA EM DELTA LAKE
    # ========================================================================

    # Delta Lake permite MERGE (upsert) para dados incrementais
    # Para simplificar, este template usa overwrite por partição

    writer = df_silver.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true")  # Permite evolução de schema

    # Adiciona particionamento se configurado
    if PARTITION_COLUMNS:
        writer = writer.partitionBy(*PARTITION_COLUMNS)

    # Salva os dados
    writer.save(adls.get_layer_path("silver", f"{AREA_NEGOCIO}/{FONTE_DADOS}/"))

    logger.info("✅ Dados salvos com sucesso!")
    logger.records_processed = final_count

except Exception as e:
    logger.error("Erro ao escrever dados na camada Silver", exception=e)
    logger.end(status="failed")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9️⃣ FINALIZAÇÃO
# MAGIC
# MAGIC **Encerra o pipeline e gera logs**

# COMMAND ----------

# Finaliza execução
logger.end(status="success")

# Mostra resumo
summary = logger.get_execution_summary()

print("\n" + "="*80)
print("📊 RESUMO DA EXECUÇÃO")
print("="*80)
print(f"Pipeline: {summary['pipeline_name']}")
print(f"Status: {summary['status']}")
print(f"Registros Entrada (Bronze): {input_count:,}")
print(f"Registros Saída (Silver): {final_count:,}")
print(f"Taxa de Aproveitamento: {(final_count/input_count*100):.2f}%")
print(f"Duração: {summary['duration_seconds']:.2f} segundos")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ FIM DO NOTEBOOK
# MAGIC
# MAGIC ### Próximos Passos:
# MAGIC 1. Os dados transformados estão na camada Silver
# MAGIC 2. Execute o notebook Gold para criar agregações e modelos dimensionais
# MAGIC 3. Configure o Power BI para conectar na camada Silver ou Gold
# MAGIC
# MAGIC ### 💡 Dicas para Troubleshooting:
# MAGIC - Se muitos registros foram removidos, revise as regras de qualidade
# MAGIC - Valide se as transformações estão corretas executando célula por célula
# MAGIC - Use `.show()` para inspecionar dados intermediários
# MAGIC - Verifique os logs de auditoria para histórico de execuções
