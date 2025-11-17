"""
Logger - Sistema de Logging e Auditoria
========================================
Sistema de logging para rastreamento de execuções e auditoria.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType


class PipelineLogger:
    """Logger para pipelines de dados com auditoria."""

    def __init__(
        self,
        pipeline_name: str,
        spark: SparkSession = None,
        config: Dict[str, Any] = None
    ):
        """
        Inicializa o logger.

        Args:
            pipeline_name: Nome do pipeline
            spark: Sessão Spark (para logs em tabela)
            config: Configurações do projeto
        """
        self.pipeline_name = pipeline_name
        self.spark = spark
        self.config = config or {}
        self.log_config = self.config.get('logging', {})

        # Configura logger Python
        self.logger = self._setup_python_logger()

        # Variáveis de controle de execução
        self.execution_id = self._generate_execution_id()
        self.start_time = None
        self.end_time = None
        self.status = "initialized"
        self.records_processed = 0
        self.errors = []

    def _setup_python_logger(self) -> logging.Logger:
        """
        Configura logger Python padrão.

        Returns:
            Logger configurado
        """
        logger = logging.getLogger(self.pipeline_name)

        log_level = self.log_config.get('log_level', 'INFO')
        logger.setLevel(getattr(logging, log_level))

        # Handler para console
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level))

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def _generate_execution_id(self) -> str:
        """
        Gera ID único para execução.

        Returns:
            ID de execução
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{self.pipeline_name}_{timestamp}"

    def start(self, **kwargs):
        """
        Marca início da execução.

        Args:
            **kwargs: Parâmetros adicionais da execução
        """
        self.start_time = datetime.now()
        self.status = "running"

        msg = f"🚀 Iniciando pipeline: {self.pipeline_name}"
        if kwargs:
            msg += f" | Parâmetros: {kwargs}"

        self.logger.info(msg)
        print("\n" + "="*80)
        print(msg)
        print("="*80 + "\n")

    def end(self, status: str = "success"):
        """
        Marca fim da execução.

        Args:
            status: Status final (success, failed, partial)
        """
        self.end_time = datetime.now()
        self.status = status

        duration = (self.end_time - self.start_time).total_seconds()

        msg = (f"{'✅' if status == 'success' else '❌'} "
               f"Pipeline finalizado: {self.pipeline_name} | "
               f"Status: {status} | "
               f"Duração: {duration:.2f}s | "
               f"Registros: {self.records_processed}")

        self.logger.info(msg)
        print("\n" + "="*80)
        print(msg)
        print("="*80 + "\n")

        # Salva auditoria se configurado
        if self.log_config.get('enable_audit_log') and self.spark:
            self._save_audit_log()

    def info(self, message: str, **kwargs):
        """
        Log de informação.

        Args:
            message: Mensagem
            **kwargs: Campos adicionais
        """
        self.logger.info(message)
        if kwargs:
            self.logger.debug(f"Detalhes: {kwargs}")

    def warning(self, message: str, **kwargs):
        """
        Log de aviso.

        Args:
            message: Mensagem
            **kwargs: Campos adicionais
        """
        self.logger.warning(f"⚠️ {message}")
        if kwargs:
            self.logger.debug(f"Detalhes: {kwargs}")

    def error(self, message: str, exception: Exception = None, **kwargs):
        """
        Log de erro.

        Args:
            message: Mensagem
            exception: Exceção capturada
            **kwargs: Campos adicionais
        """
        error_info = {
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        if exception:
            error_info['exception'] = str(exception)
            error_info['exception_type'] = type(exception).__name__

        error_info.update(kwargs)
        self.errors.append(error_info)

        self.logger.error(f"❌ {message}")
        if exception:
            self.logger.error(f"   Exceção: {exception}")

    def log_dataframe_info(self, df: DataFrame, step_name: str):
        """
        Loga informações sobre um DataFrame.

        Args:
            df: DataFrame a analisar
            step_name: Nome da etapa
        """
        count = df.count()
        self.records_processed = count

        msg = (f"📊 {step_name} | "
               f"Registros: {count:,} | "
               f"Colunas: {len(df.columns)}")

        self.logger.info(msg)
        print(f"\n{msg}")

        # Mostra schema
        print("\n🔍 Schema:")
        df.printSchema()

    def log_transformation(
        self,
        step_name: str,
        input_count: int,
        output_count: int,
        description: str = ""
    ):
        """
        Loga transformação de dados.

        Args:
            step_name: Nome da etapa
            input_count: Registros de entrada
            output_count: Registros de saída
            description: Descrição da transformação
        """
        delta = output_count - input_count
        percentage = (delta / input_count * 100) if input_count > 0 else 0

        msg = (f"🔄 {step_name} | "
               f"Entrada: {input_count:,} | "
               f"Saída: {output_count:,} | "
               f"Delta: {delta:+,} ({percentage:+.2f}%)")

        if description:
            msg += f" | {description}"

        self.logger.info(msg)
        print(f"\n{msg}")

    def log_quality_check(
        self,
        check_name: str,
        passed: bool,
        details: Dict[str, Any] = None
    ):
        """
        Loga verificação de qualidade.

        Args:
            check_name: Nome da verificação
            passed: Se passou ou não
            details: Detalhes adicionais
        """
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        msg = f"🔍 Qualidade - {check_name}: {status}"

        if details:
            msg += f" | {details}"

        if passed:
            self.logger.info(msg)
        else:
            self.logger.warning(msg)

        print(f"\n{msg}")

    def _save_audit_log(self):
        """Salva log de auditoria em tabela."""
        if not self.spark:
            return

        audit_table = self.log_config.get('audit_table', 'auditoria_execucoes')

        try:
            # Prepara dados de auditoria
            audit_data = [(
                self.execution_id,
                self.pipeline_name,
                self.start_time,
                self.end_time,
                self.status,
                self.records_processed,
                (self.end_time - self.start_time).total_seconds() if self.end_time else None,
                len(self.errors),
                str(self.errors) if self.errors else None
            )]

            schema = StructType([
                StructField("execution_id", StringType(), False),
                StructField("pipeline_name", StringType(), False),
                StructField("start_time", TimestampType(), False),
                StructField("end_time", TimestampType(), True),
                StructField("status", StringType(), False),
                StructField("records_processed", IntegerType(), True),
                StructField("duration_seconds", IntegerType(), True),
                StructField("error_count", IntegerType(), True),
                StructField("error_details", StringType(), True)
            ])

            audit_df = self.spark.createDataFrame(audit_data, schema)

            # Salva em tabela (ajuste o caminho conforme necessário)
            audit_df.write.mode("append").saveAsTable(audit_table)

            self.logger.info(f"📝 Log de auditoria salvo: {audit_table}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar auditoria: {e}")

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo da execução.

        Returns:
            Dicionário com resumo
        """
        return {
            'execution_id': self.execution_id,
            'pipeline_name': self.pipeline_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'records_processed': self.records_processed,
            'duration_seconds': (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time else None
            ),
            'error_count': len(self.errors),
            'errors': self.errors
        }


# Decorador para logging automático de funções
def log_execution(logger: PipelineLogger):
    """
    Decorador para logar execução de funções.

    Args:
        logger: PipelineLogger a usar

    Example:
        >>> @log_execution(logger)
        >>> def minha_transformacao(df):
        >>>     return df.filter(...)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.info(f"Iniciando: {func_name}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"Concluído: {func_name}")
                return result
            except Exception as e:
                logger.error(f"Erro em {func_name}", exception=e)
                raise

        return wrapper
    return decorator


# Exemplo de uso
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    print("\n=== TESTE DE PIPELINE LOGGER ===\n")

    # Cria sessão Spark
    spark = SparkSession.builder.appName("TesteLogger").getOrCreate()

    # Cria logger
    logger = PipelineLogger("teste_pipeline", spark=spark)

    # Inicia execução
    logger.start(parametro1="valor1", parametro2="valor2")

    # Logs durante execução
    logger.info("Lendo dados de origem")

    # Cria DataFrame de teste
    df = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")], ["id", "nome"])
    logger.log_dataframe_info(df, "Dados de entrada")

    # Log de transformação
    logger.log_transformation(
        "Filtro aplicado",
        input_count=3,
        output_count=2,
        description="Removidos registros inválidos"
    )

    # Log de qualidade
    logger.log_quality_check(
        "Validação de schema",
        passed=True,
        details={"colunas_validadas": 2}
    )

    # Warning
    logger.warning("Alguns registros com valores nulos", count=5)

    # Finaliza
    logger.end(status="success")

    # Obtém resumo
    summary = logger.get_execution_summary()
    print(f"\n📋 Resumo: {summary}")

    spark.stop()
