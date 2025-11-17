# Databricks notebook source
# MAGIC %md
# MAGIC # 🥇 TEMPLATE GOLD - AGREGAÇÕES E MODELOS DIMENSIONAIS
# MAGIC
# MAGIC ## 📋 Objetivo
# MAGIC Este notebook cria agregações e modelos dimensionais para consumo pelo Power BI.
# MAGIC A camada Gold contém dados otimizados para análise e relatórios.
# MAGIC
# MAGIC ## 📝 Instruções de Uso
# MAGIC 1. **Copie este template** para a pasta da sua área de negócio
# MAGIC 2. **Renomeie** o arquivo (ex: gold_vendas_mensais.py)
# MAGIC 3. **Configure** os parâmetros
# MAGIC 4. **Defina** as agregações e métricas de negócio
# MAGIC 5. **Execute** o notebook
# MAGIC
# MAGIC ## 🎯 O que este notebook faz:
# MAGIC - Lê dados da camada Silver
# MAGIC - Cria agregações (somas, médias, contagens, etc.)
# MAGIC - Constrói tabelas fato e dimensões
# MAGIC - Calcula KPIs e métricas de negócio
# MAGIC - Otimiza para consultas do Power BI
# MAGIC - Salva em formato Delta Lake com otimizações
# MAGIC
# MAGIC ## 📊 Tipos de Tabelas Gold:
# MAGIC - **Fatos**: Métricas agregadas (vendas, produção, etc.)
# MAGIC - **Dimensões**: Tabelas de referência (clientes, produtos, tempo)
# MAGIC - **Data Marts**: Conjuntos prontos para análises específicas

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1️⃣ CONFIGURAÇÕES
# MAGIC
# MAGIC **Configure estas variáveis antes de executar o notebook**

# COMMAND ----------

# ============================================================================
# CONFIGURAÇÕES DO PIPELINE
# ============================================================================

# Nome do data mart / tabela Gold
GOLD_TABLE_NAME = "fato_vendas_mensais"  # ⬅️ ALTERE AQUI

# Tipo de tabela (fato ou dimensao)
TIPO_TABELA = "fato"  # ⬅️ ALTERE AQUI (fato ou dimensao)

# Área de negócio
AREA_NEGOCIO = "producao"  # ⬅️ ALTERE AQUI

# Fonte de dados Silver
FONTE_DADOS_SILVER = "vendas"  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE ENTRADA (SILVER)
# ============================================================================

# Caminho dos dados Silver
SILVER_PATH = f"silver/{AREA_NEGOCIO}/{FONTE_DADOS_SILVER}/"

# Tabelas Silver adicionais para joins (se necessário)
ADDITIONAL_SILVER_TABLES = {
    # "clientes": "silver/dimensoes/clientes/",
    # "produtos": "silver/dimensoes/produtos/"
}  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE SAÍDA (GOLD)
# ============================================================================

# Caminho de saída na camada Gold
GOLD_PATH = f"gold/{AREA_NEGOCIO}/{GOLD_TABLE_NAME}/"

# Colunas para particionar (geralmente por tempo para tabelas fato)
PARTITION_COLUMNS = ["ano"]  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE AGREGAÇÃO (Para tabelas FATO)
# ============================================================================

# Nível de granularidade da agregação
# Exemplo: ["ano", "mes", "id_produto", "id_cliente"]
GRANULARIDADE = ["ano", "mes", "id_cliente"]  # ⬅️ ALTERE AQUI

# Métricas a calcular
# Formato: {"nome_metrica": ("coluna_origem", "funcao_agregacao")}
METRICAS = {
    "total_vendas": ("valor_venda", "sum"),
    "quantidade_vendas": ("id_venda", "count"),
    "ticket_medio": ("valor_venda", "avg"),
    "maior_venda": ("valor_venda", "max"),
    "menor_venda": ("valor_venda", "min")
}  # ⬅️ ALTERE AQUI

# ============================================================================
# CONFIGURAÇÕES DE OTIMIZAÇÃO
# ============================================================================

# Colunas para otimizar consultas (Z-Order)
# Colunas mais usadas em filtros do Power BI
Z_ORDER_COLUMNS = ["ano", "mes", "id_cliente"]  # ⬅️ ALTERE AQUI

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2️⃣ IMPORTAÇÕES E SETUP
# MAGIC
# MAGIC **NÃO ALTERE ESTA SEÇÃO - Apenas execute**

# COMMAND ----------

import sys
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql import Window
from pyspark.sql.types import *

# Adiciona utils ao path
sys.path.append('/Workspace/utils')

# Importa utilitários
from config_loader import get_config_loader
from spark_session import get_spark_session
from connectors.azure_connector import AzureDataLakeConnector
from logger import PipelineLogger

# Carrega configurações
config = get_config_loader()

# Cria/obtém sessão Spark
try:
    spark
    print("✅ Usando sessão Spark existente")
except NameError:
    spark = get_spark_session(f"Gold_{AREA_NEGOCIO}_{GOLD_TABLE_NAME}", config.config)
    print("✅ Nova sessão Spark criada")

# Inicializa logger
logger = PipelineLogger(
    pipeline_name=f"gold_{AREA_NEGOCIO}_{GOLD_TABLE_NAME}",
    spark=spark,
    config=config.config
)

# Inicializa conector
adls = AzureDataLakeConnector(spark, config.config)

print("\n" + "="*80)
print(f"🥇 PIPELINE GOLD - {GOLD_TABLE_NAME.upper()}")
print(f"   Tipo: {TIPO_TABELA}")
print(f"   Área: {AREA_NEGOCIO}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3️⃣ LEITURA DA CAMADA SILVER
# MAGIC
# MAGIC **Lê os dados transformados da camada Silver**

# COMMAND ----------

# Inicia execução
logger.start(
    gold_table=GOLD_TABLE_NAME,
    tipo=TIPO_TABELA,
    area=AREA_NEGOCIO
)

try:
    logger.info(f"📖 Lendo dados da camada Silver: {SILVER_PATH}")

    # Lê dados Silver principal
    df_silver = adls.read(
        path=SILVER_PATH,
        format="delta"
    )

    input_count = df_silver.count()
    logger.log_dataframe_info(df_silver, "Dados Silver lidos")

    # Lê tabelas Silver adicionais se configuradas
    silver_tables = {}
    for table_name, table_path in ADDITIONAL_SILVER_TABLES.items():
        logger.info(f"📖 Lendo tabela adicional: {table_name}")
        silver_tables[table_name] = adls.read(path=table_path, format="delta")

except Exception as e:
    logger.error("Erro ao ler dados da camada Silver", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4️⃣ CONSTRUÇÃO DA TABELA GOLD
# MAGIC
# MAGIC **Cria agregações e modelos dimensionais**

# COMMAND ----------

try:
    if TIPO_TABELA == "fato":
        # ====================================================================
        # CRIAÇÃO DE TABELA FATO
        # ====================================================================
        logger.info("📊 Criando tabela FATO com agregações")

        # Prepara DataFrame base
        df_base = df_silver

        # Aplica joins com tabelas dimensionais se necessário
        for table_name, table_df in silver_tables.items():
            logger.info(f"🔗 Aplicando join com {table_name}")
            # Ajuste a lógica de join conforme necessário
            # Exemplo:
            # df_base = df_base.join(table_df, on="id_campo", how="left")

        # ================================================================
        # AGREGAÇÕES
        # ================================================================
        logger.info(f"⚙️ Agregando por: {GRANULARIDADE}")

        # Constrói expressões de agregação
        agg_expressions = []

        for metrica_nome, (coluna, funcao) in METRICAS.items():
            if funcao == "sum":
                agg_expressions.append(F.sum(coluna).alias(metrica_nome))
            elif funcao == "count":
                agg_expressions.append(F.count(coluna).alias(metrica_nome))
            elif funcao == "avg":
                agg_expressions.append(F.avg(coluna).alias(metrica_nome))
            elif funcao == "max":
                agg_expressions.append(F.max(coluna).alias(metrica_nome))
            elif funcao == "min":
                agg_expressions.append(F.min(coluna).alias(metrica_nome))
            elif funcao == "countDistinct":
                agg_expressions.append(F.countDistinct(coluna).alias(metrica_nome))

        # Executa agregação
        df_gold = df_base.groupBy(*GRANULARIDADE).agg(*agg_expressions)

        # ================================================================
        # MÉTRICAS CALCULADAS (KPIs)
        # ================================================================
        logger.info("💡 Calculando métricas derivadas")

        # Adicione cálculos de KPIs específicos aqui
        # Exemplo:
        # df_gold = df_gold.withColumn(
        #     "variacao_mes_anterior",
        #     # Lógica para calcular variação
        # )

        # Adicione colunas de particionamento se necessário
        if "ano" in PARTITION_COLUMNS and "ano" not in df_gold.columns:
            # Tenta extrair de coluna de data existente em GRANULARIDADE
            date_cols = [c for c in GRANULARIDADE if "ano" in c.lower() or "data" in c.lower()]
            if date_cols:
                df_gold = df_gold.withColumn("ano", F.year(date_cols[0]))

        if "mes" in PARTITION_COLUMNS and "mes" not in df_gold.columns:
            date_cols = [c for c in GRANULARIDADE if "mes" in c.lower() or "data" in c.lower()]
            if date_cols:
                df_gold = df_gold.withColumn("mes", F.month(date_cols[0]))

    else:
        # ====================================================================
        # CRIAÇÃO DE TABELA DIMENSÃO
        # ====================================================================
        logger.info("📋 Criando tabela DIMENSÃO")

        # Para dimensões, geralmente apenas selecionamos e transformamos colunas
        df_gold = df_silver

        # ⬇️ CUSTOMIZE SUAS DIMENSÕES AQUI ⬇️
        #
        # Exemplo para dimensão de clientes:
        # df_gold = df_gold.select(
        #     "id_cliente",
        #     "nome_cliente",
        #     "segmento",
        #     "regiao",
        #     "data_cadastro"
        # ).distinct()
        #
        # Exemplo para dimensão de tempo:
        # df_gold = df_silver.select("data").distinct()
        # df_gold = df_gold.withColumn("ano", F.year("data"))
        # df_gold = df_gold.withColumn("mes", F.month("data"))
        # df_gold = df_gold.withColumn("trimestre", F.quarter("data"))
        # df_gold = df_gold.withColumn("nome_mes", F.date_format("data", "MMMM"))
        # df_gold = df_gold.withColumn("dia_semana", F.dayofweek("data"))

        # Remove duplicatas para garantir unicidade
        if GRANULARIDADE:
            df_gold = df_gold.dropDuplicates(GRANULARIDADE)

    logger.log_dataframe_info(df_gold, "Tabela Gold construída")

except Exception as e:
    logger.error("Erro ao construir tabela Gold", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5️⃣ TRANSFORMAÇÕES CUSTOMIZADAS
# MAGIC
# MAGIC **⬇️ ADICIONE TRANSFORMAÇÕES ESPECÍFICAS DE NEGÓCIO AQUI ⬇️**

# COMMAND ----------

try:
    logger.info("⚙️ Aplicando transformações customizadas Gold")

    df_gold_final = df_gold

    # ========================================================================
    # EXEMPLO 1: CÁLCULO DE VARIAÇÃO PERCENTUAL
    # ========================================================================
    # from pyspark.sql.window import Window
    #
    # # Window para calcular valores do mês anterior
    # window_spec = Window.partitionBy("id_cliente").orderBy("ano", "mes")
    #
    # df_gold_final = df_gold_final.withColumn(
    #     "total_vendas_mes_anterior",
    #     F.lag("total_vendas", 1).over(window_spec)
    # )
    #
    # df_gold_final = df_gold_final.withColumn(
    #     "variacao_percentual",
    #     ((F.col("total_vendas") - F.col("total_vendas_mes_anterior")) /
    #      F.col("total_vendas_mes_anterior") * 100)
    # )

    # ========================================================================
    # EXEMPLO 2: CLASSIFICAÇÃO/RANKING
    # ========================================================================
    # window_ranking = Window.partitionBy("ano", "mes").orderBy(F.desc("total_vendas"))
    #
    # df_gold_final = df_gold_final.withColumn(
    #     "ranking_cliente",
    #     F.rank().over(window_ranking)
    # )

    # ========================================================================
    # EXEMPLO 3: CÁLCULO DE ACUMULADO (YTD, MTD)
    # ========================================================================
    # window_ytd = Window.partitionBy("id_cliente", "ano").orderBy("mes") \
    #                    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    #
    # df_gold_final = df_gold_final.withColumn(
    #     "total_vendas_ytd",
    #     F.sum("total_vendas").over(window_ytd)
    # )

    # ========================================================================
    # EXEMPLO 4: CATEGORIZAÇÃO
    # ========================================================================
    # df_gold_final = df_gold_final.withColumn(
    #     "categoria_performance",
    #     F.when(F.col("total_vendas") >= 100000, "Alto")
    #      .when((F.col("total_vendas") >= 50000) & (F.col("total_vendas") < 100000), "Médio")
    #      .otherwise("Baixo")
    # )

    # ⬇️⬇️⬇️ ADICIONE SUAS TRANSFORMAÇÕES ABAIXO ⬇️⬇️⬇️




    # ⬆️⬆️⬆️ ADICIONE SUAS TRANSFORMAÇÕES ACIMA ⬆️⬆️⬆️

    logger.info("✅ Transformações customizadas concluídas")

except Exception as e:
    logger.error("Erro nas transformações customizadas", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6️⃣ ADIÇÃO DE METADADOS GOLD
# MAGIC
# MAGIC **Adiciona colunas de controle**

# COMMAND ----------

try:
    logger.info("📝 Adicionando metadados Gold")

    # Data de processamento
    df_gold_output = df_gold_final.withColumn(
        "gold_processing_date",
        F.current_timestamp()
    )

    # Adiciona nome da tabela para rastreabilidade
    df_gold_output = df_gold_output.withColumn(
        "gold_table_name",
        F.lit(GOLD_TABLE_NAME)
    )

    final_count = df_gold_output.count()
    logger.log_dataframe_info(df_gold_output, "Dados Gold finais")

    # Mostra amostra
    print("\n📊 AMOSTRA DA TABELA GOLD (10 primeiras linhas):")
    print("="*80)
    df_gold_output.show(10, truncate=False)

except Exception as e:
    logger.error("Erro ao adicionar metadados", exception=e)
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7️⃣ OTIMIZAÇÃO E ESCRITA
# MAGIC
# MAGIC **Otimiza e salva os dados para consultas do Power BI**

# COMMAND ----------

try:
    logger.info(f"💾 Salvando tabela Gold: {GOLD_PATH}")

    # ========================================================================
    # ESCRITA EM DELTA LAKE COM OTIMIZAÇÕES
    # ========================================================================

    writer = df_gold_output.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true")

    # Adiciona particionamento
    if PARTITION_COLUMNS:
        writer = writer.partitionBy(*PARTITION_COLUMNS)

    # Salva
    full_path = adls.get_layer_path("gold", f"{AREA_NEGOCIO}/{GOLD_TABLE_NAME}/")
    writer.save(full_path)

    logger.info("✅ Dados salvos com sucesso!")

    # ========================================================================
    # OTIMIZAÇÕES DELTA LAKE
    # ========================================================================

    # Compacta arquivos pequenos (OPTIMIZE)
    logger.info("⚡ Otimizando arquivos Delta...")

    try:
        # Registra tabela temporariamente para executar comandos Delta
        df_gold_output.createOrReplaceTempView("temp_gold_table")

        # OPTIMIZE: compacta arquivos pequenos
        optimize_cmd = f"OPTIMIZE delta.`{full_path}`"

        # Adiciona Z-ORDER se configurado (melhora performance de consultas)
        if Z_ORDER_COLUMNS:
            z_order_cols = ", ".join(Z_ORDER_COLUMNS)
            optimize_cmd += f" ZORDER BY ({z_order_cols})"

        spark.sql(optimize_cmd)
        logger.info("✅ Otimização concluída!")

    except Exception as e:
        logger.warning(f"Aviso: Otimização falhou (não crítico): {e}")

    # ========================================================================
    # VACUUM (Limpeza de arquivos antigos - CUIDADO!)
    # ========================================================================
    # Descomente apenas se necessário e após confirmar que não há problemas
    # logger.info("🧹 Limpando arquivos antigos...")
    # spark.sql(f"VACUUM delta.`{full_path}` RETAIN 168 HOURS")  # 7 dias

    logger.records_processed = final_count

except Exception as e:
    logger.error("Erro ao escrever dados Gold", exception=e)
    logger.end(status="failed")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8️⃣ ESTATÍSTICAS E ANÁLISE
# MAGIC
# MAGIC **Gera estatísticas sobre os dados Gold**

# COMMAND ----------

try:
    logger.info("📈 Gerando estatísticas")

    # Estatísticas descritivas para colunas numéricas
    numeric_columns = [f.name for f in df_gold_output.schema.fields
                      if f.dataType.typeName() in ['double', 'float', 'integer', 'long']]

    if numeric_columns:
        print("\n📊 ESTATÍSTICAS DESCRITIVAS:")
        print("="*80)
        df_gold_output.select(numeric_columns).describe().show()

    # Distribuição por partições (se houver)
    if PARTITION_COLUMNS:
        print(f"\n📊 DISTRIBUIÇÃO POR {', '.join(PARTITION_COLUMNS)}:")
        print("="*80)
        df_gold_output.groupBy(*PARTITION_COLUMNS).count() \
            .orderBy(*PARTITION_COLUMNS) \
            .show(20)

except Exception as e:
    logger.warning(f"Erro ao gerar estatísticas: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9️⃣ FINALIZAÇÃO
# MAGIC
# MAGIC **Encerra o pipeline**

# COMMAND ----------

# Finaliza execução
logger.end(status="success")

# Mostra resumo
summary = logger.get_execution_summary()

print("\n" + "="*80)
print("📊 RESUMO DA EXECUÇÃO")
print("="*80)
print(f"Tabela Gold: {GOLD_TABLE_NAME}")
print(f"Tipo: {TIPO_TABELA}")
print(f"Status: {summary['status']}")
print(f"Registros Silver (entrada): {input_count:,}")
print(f"Registros Gold (saída): {final_count:,}")
print(f"Taxa de Agregação: {(input_count/final_count if final_count > 0 else 0):.2f}x")
print(f"Duração: {summary['duration_seconds']:.2f} segundos")
print(f"Caminho: {GOLD_PATH}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ FIM DO NOTEBOOK
# MAGIC
# MAGIC ### Próximos Passos:
# MAGIC 1. **Conecte o Power BI** à tabela Gold criada
# MAGIC 2. **Configure refresh** automático no Power BI Service
# MAGIC 3. **Crie visualizações** usando as métricas calculadas
# MAGIC
# MAGIC ### 📊 Conexão com Power BI:
# MAGIC ```
# MAGIC Fonte de Dados: Azure Data Lake Storage Gen2
# MAGIC Caminho: {GOLD_PATH}
# MAGIC Formato: Delta Lake (usar conector Delta no Power BI)
# MAGIC ```
# MAGIC
# MAGIC ### 💡 Dicas de Performance:
# MAGIC - As colunas em Z_ORDER_COLUMNS terão consultas mais rápidas
# MAGIC - Use filtros no Power BI sobre colunas particionadas
# MAGIC - Execute OPTIMIZE regularmente (semanal ou mensal)
# MAGIC - Considere criar índices adicionais se necessário
