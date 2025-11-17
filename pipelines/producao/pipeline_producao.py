# Databricks notebook source
# MAGIC %md
# MAGIC # 🏭 PIPELINE ORQUESTRADOR - PRODUÇÃO
# MAGIC
# MAGIC ## 📋 Objetivo
# MAGIC Este notebook orquestra a execução completa do pipeline de Produção:
# MAGIC - Bronze: Ingestão de dados
# MAGIC - Silver: Transformação e limpeza
# MAGIC - Gold: Agregações e métricas
# MAGIC
# MAGIC ## 📝 Como Usar
# MAGIC 1. Configure as fontes de dados que deseja processar
# MAGIC 2. Execute o notebook completo ou etapa por etapa
# MAGIC 3. Monitore os logs de execução
# MAGIC
# MAGIC ## ⚙️ Configuração de Agendamento
# MAGIC - **Frequência recomendada**: Diária
# MAGIC - **Horário**: 06:00 (conforme config.yaml)
# MAGIC - **Dependências**: Nenhuma

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1️⃣ CONFIGURAÇÕES

# COMMAND ----------

# ============================================================================
# CONFIGURAÇÕES DO PIPELINE
# ============================================================================

AREA_NEGOCIO = "producao"

# Fontes de dados a processar
# Adicione ou remova fontes conforme necessário
FONTES = [
    {
        "nome": "vendas",
        "bronze_notebook": "/Workspace/notebooks/bronze/bronze_vendas",
        "silver_notebook": "/Workspace/notebooks/silver/silver_vendas",
        "gold_notebooks": [
            "/Workspace/notebooks/gold/gold_vendas_mensais",
            "/Workspace/notebooks/gold/gold_vendas_por_produto"
        ]
    },
    {
        "nome": "producao",
        "bronze_notebook": "/Workspace/notebooks/bronze/bronze_producao",
        "silver_notebook": "/Workspace/notebooks/silver/silver_producao",
        "gold_notebooks": [
            "/Workspace/notebooks/gold/gold_producao_diaria"
        ]
    }
    # Adicione mais fontes aqui
]

# Modo de execução
# - "serial": Executa uma fonte por vez
# - "parallel": Executa todas as fontes em paralelo (requer configuração adequada)
MODO_EXECUCAO = "serial"

# Se True, continua pipeline mesmo se uma etapa falhar
CONTINUAR_EM_ERRO = False

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2️⃣ SETUP E IMPORTAÇÕES

# COMMAND ----------

import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('/Workspace/utils')

from config_loader import get_config_loader
from logger import PipelineLogger
from spark_session import get_spark_session

# Carrega configurações
config = get_config_loader()

# Cria sessão Spark
try:
    spark
except NameError:
    spark = get_spark_session(f"Pipeline_{AREA_NEGOCIO}", config.config)

# Inicializa logger principal
main_logger = PipelineLogger(
    pipeline_name=f"pipeline_orquestrador_{AREA_NEGOCIO}",
    spark=spark,
    config=config.config
)

print("\n" + "="*80)
print(f"🏭 PIPELINE ORQUESTRADOR - {AREA_NEGOCIO.upper()}")
print(f"   Fontes: {len(FONTES)}")
print(f"   Modo: {MODO_EXECUCAO}")
print("="*80 + "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3️⃣ FUNÇÕES AUXILIARES

# COMMAND ----------

def executar_notebook(caminho, timeout_segundos=3600, parametros=None):
    """
    Executa um notebook e retorna o resultado.

    Args:
        caminho: Caminho do notebook
        timeout_segundos: Timeout em segundos
        parametros: Dicionário de parâmetros

    Returns:
        Resultado da execução
    """
    try:
        main_logger.info(f"▶️ Executando: {caminho}")

        # Em Databricks, use dbutils.notebook.run
        # Em ambiente local ou outro, adapte conforme necessário
        try:
            resultado = dbutils.notebook.run(
                caminho,
                timeout_segundos,
                parametros or {}
            )
            main_logger.info(f"✅ Sucesso: {caminho}")
            return {"status": "success", "notebook": caminho, "resultado": resultado}

        except NameError:
            # dbutils não disponível (ambiente local/teste)
            main_logger.warning(f"⚠️ dbutils não disponível - simulando execução: {caminho}")
            return {"status": "simulated", "notebook": caminho}

    except Exception as e:
        main_logger.error(f"❌ Erro ao executar {caminho}", exception=e)
        return {"status": "failed", "notebook": caminho, "erro": str(e)}


def processar_fonte(fonte_config):
    """
    Processa uma fonte de dados completa (Bronze -> Silver -> Gold).

    Args:
        fonte_config: Configuração da fonte

    Returns:
        Dicionário com resultados
    """
    nome_fonte = fonte_config["nome"]
    resultados = {
        "fonte": nome_fonte,
        "inicio": datetime.now(),
        "etapas": {}
    }

    try:
        main_logger.info(f"\n{'='*80}")
        main_logger.info(f"🔄 Processando fonte: {nome_fonte.upper()}")
        main_logger.info(f"{'='*80}\n")

        # ====================================================================
        # BRONZE - Ingestão
        # ====================================================================
        main_logger.info(f"🥉 Etapa BRONZE: {nome_fonte}")

        bronze_result = executar_notebook(fonte_config["bronze_notebook"])
        resultados["etapas"]["bronze"] = bronze_result

        if bronze_result["status"] == "failed" and not CONTINUAR_EM_ERRO:
            raise Exception(f"Bronze falhou para {nome_fonte}")

        # ====================================================================
        # SILVER - Transformação
        # ====================================================================
        main_logger.info(f"🥈 Etapa SILVER: {nome_fonte}")

        silver_result = executar_notebook(fonte_config["silver_notebook"])
        resultados["etapas"]["silver"] = silver_result

        if silver_result["status"] == "failed" and not CONTINUAR_EM_ERRO:
            raise Exception(f"Silver falhou para {nome_fonte}")

        # ====================================================================
        # GOLD - Agregações
        # ====================================================================
        main_logger.info(f"🥇 Etapa GOLD: {nome_fonte}")

        resultados["etapas"]["gold"] = []

        for gold_notebook in fonte_config["gold_notebooks"]:
            gold_result = executar_notebook(gold_notebook)
            resultados["etapas"]["gold"].append(gold_result)

            if gold_result["status"] == "failed" and not CONTINUAR_EM_ERRO:
                raise Exception(f"Gold falhou para {nome_fonte}: {gold_notebook}")

        resultados["status"] = "success"
        main_logger.info(f"✅ Fonte {nome_fonte} processada com sucesso!")

    except Exception as e:
        resultados["status"] = "failed"
        resultados["erro"] = str(e)
        main_logger.error(f"❌ Erro ao processar fonte {nome_fonte}", exception=e)

    finally:
        resultados["fim"] = datetime.now()
        resultados["duracao_segundos"] = (resultados["fim"] - resultados["inicio"]).total_seconds()

    return resultados

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4️⃣ EXECUÇÃO DO PIPELINE

# COMMAND ----------

# Inicia pipeline
main_logger.start(area=AREA_NEGOCIO, fontes=len(FONTES), modo=MODO_EXECUCAO)

resultados_pipeline = []

try:
    if MODO_EXECUCAO == "serial":
        # ====================================================================
        # EXECUÇÃO SERIAL (uma fonte por vez)
        # ====================================================================
        main_logger.info("📊 Modo SERIAL: Processando fontes sequencialmente")

        for fonte in FONTES:
            resultado = processar_fonte(fonte)
            resultados_pipeline.append(resultado)

    else:
        # ====================================================================
        # EXECUÇÃO PARALELA (múltiplas fontes simultâneas)
        # ====================================================================
        main_logger.info("⚡ Modo PARALELO: Processando fontes em paralelo")

        max_workers = min(len(FONTES), 5)  # Máximo 5 threads paralelas

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(processar_fonte, fonte): fonte
                for fonte in FONTES
            }

            for future in as_completed(futures):
                fonte = futures[future]
                try:
                    resultado = future.result()
                    resultados_pipeline.append(resultado)
                except Exception as e:
                    main_logger.error(f"Erro no processamento paralelo de {fonte['nome']}", exception=e)
                    resultados_pipeline.append({
                        "fonte": fonte["nome"],
                        "status": "failed",
                        "erro": str(e)
                    })

    # ========================================================================
    # ANÁLISE DE RESULTADOS
    # ========================================================================
    main_logger.info("\n" + "="*80)
    main_logger.info("📊 ANÁLISE DE RESULTADOS")
    main_logger.info("="*80 + "\n")

    total_fontes = len(resultados_pipeline)
    fontes_sucesso = sum(1 for r in resultados_pipeline if r.get("status") == "success")
    fontes_falha = sum(1 for r in resultados_pipeline if r.get("status") == "failed")

    print(f"Total de fontes: {total_fontes}")
    print(f"✅ Sucesso: {fontes_sucesso}")
    print(f"❌ Falhas: {fontes_falha}")
    print("\n" + "-"*80 + "\n")

    # Detalhamento por fonte
    for resultado in resultados_pipeline:
        status_icon = "✅" if resultado.get("status") == "success" else "❌"
        duracao = resultado.get("duracao_segundos", 0)

        print(f"{status_icon} {resultado['fonte']}: {resultado.get('status')} ({duracao:.2f}s)")

        if resultado.get("status") == "failed":
            print(f"   Erro: {resultado.get('erro', 'Desconhecido')}")

    # Determina status geral
    status_geral = "success" if fontes_falha == 0 else "partial" if fontes_sucesso > 0 else "failed"

    main_logger.records_processed = fontes_sucesso

except Exception as e:
    main_logger.error("Erro crítico no pipeline", exception=e)
    status_geral = "failed"
    raise

finally:
    main_logger.end(status=status_geral)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5️⃣ RELATÓRIO FINAL

# COMMAND ----------

# Gera resumo
summary = main_logger.get_execution_summary()

print("\n" + "="*80)
print("📊 RESUMO DO PIPELINE")
print("="*80)
print(f"Área de Negócio: {AREA_NEGOCIO}")
print(f"Status Geral: {summary['status']}")
print(f"Fontes Processadas: {len(resultados_pipeline)}")
print(f"Sucessos: {fontes_sucesso}")
print(f"Falhas: {fontes_falha}")
print(f"Duração Total: {summary['duration_seconds']:.2f} segundos")
print(f"Início: {summary['start_time']}")
print(f"Fim: {summary['end_time']}")
print("="*80 + "\n")

# Salva resultados em variável para possível consulta
dbutils.jobs.taskValues.set(key="pipeline_status", value=status_geral)
dbutils.jobs.taskValues.set(key="fontes_sucesso", value=fontes_sucesso)
dbutils.jobs.taskValues.set(key="fontes_falha", value=fontes_falha)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ FIM DO PIPELINE
# MAGIC
# MAGIC ### Próximos Passos:
# MAGIC 1. Verifique os logs de auditoria
# MAGIC 2. Confirme que os dados estão disponíveis nas camadas Gold
# MAGIC 3. Atualize os dashboards do Power BI
# MAGIC
# MAGIC ### 📅 Agendamento:
# MAGIC Configure este notebook para executar diariamente usando:
# MAGIC - **Databricks Jobs/Workflows**
# MAGIC - **Azure Data Factory**
# MAGIC - **Azure Synapse Pipelines**
