"""
Spark Session Manager
=====================
Gerenciador de sessões Spark com configurações otimizadas para Azure.
"""

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from typing import Optional, Dict, Any
import os


class SparkSessionManager:
    """Gerenciador de sessões Spark."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o gerenciador de sessões Spark.

        Args:
            config: Dicionário de configurações do projeto
        """
        self.config = config or {}
        self.spark: Optional[SparkSession] = None

    def create_session(
        self,
        app_name: str = None,
        enable_hive: bool = True,
        additional_configs: Dict[str, str] = None
    ) -> SparkSession:
        """
        Cria ou obtém uma sessão Spark configurada.

        Args:
            app_name: Nome da aplicação Spark
            enable_hive: Habilita suporte a Hive metastore
            additional_configs: Configurações adicionais

        Returns:
            SparkSession configurada

        Example:
            >>> manager = SparkSessionManager(config)
            >>> spark = manager.create_session("MeuApp")
        """
        if self.spark is not None:
            return self.spark

        # Define nome da aplicação
        if app_name is None:
            app_name = self.config.get('environment', {}).get('spark_app_name', 'ArquiteturaMedalhao')

        # Cria configuração Spark
        conf = self._build_spark_conf(app_name, additional_configs)

        # Cria sessão
        builder = SparkSession.builder.config(conf=conf)

        if enable_hive:
            builder = builder.enableHiveSupport()

        self.spark = builder.getOrCreate()

        # Configura log level
        log_level = self.config.get('environment', {}).get('log_level', 'INFO')
        self.spark.sparkContext.setLogLevel(log_level)

        # Configura Azure Data Lake
        self._configure_azure_storage()

        return self.spark

    def _build_spark_conf(
        self,
        app_name: str,
        additional_configs: Dict[str, str] = None
    ) -> SparkConf:
        """
        Constrói configuração Spark otimizada.

        Args:
            app_name: Nome da aplicação
            additional_configs: Configurações adicionais

        Returns:
            SparkConf configurada
        """
        conf = SparkConf().setAppName(app_name)

        # Configurações de performance
        perf_config = self.config.get('performance', {})

        spark_configs = {
            # Configurações de shuffle
            "spark.sql.shuffle.partitions": str(perf_config.get('shuffle_partitions', 200)),

            # Adaptive Query Execution
            "spark.sql.adaptive.enabled": str(perf_config.get('adaptive_execution', True)).lower(),
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",

            # Dynamic allocation
            "spark.dynamicAllocation.enabled": str(perf_config.get('dynamic_allocation', True)).lower(),
            "spark.dynamicAllocation.minExecutors": "1",
            "spark.dynamicAllocation.maxExecutors": str(perf_config.get('max_executors', 10)),
            "spark.dynamicAllocation.initialExecutors": "2",

            # Memória
            "spark.executor.memory": perf_config.get('executor_memory', '4g'),
            "spark.driver.memory": perf_config.get('driver_memory', '2g'),
            "spark.executor.cores": str(perf_config.get('executor_cores', 2)),

            # Delta Lake (se disponível)
            "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
            "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",

            # Otimizações gerais
            "spark.sql.adaptive.autoBroadcastJoinThreshold": "10MB",
            "spark.sql.files.maxPartitionBytes": "128MB",
            "spark.sql.parquet.compression.codec": "snappy",

            # Configurações Azure
            "spark.hadoop.fs.azure.account.auth.type": "OAuth",
            "spark.hadoop.fs.azure.account.oauth.provider.type":
                "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
        }

        # Aplica configurações
        for key, value in spark_configs.items():
            conf.set(key, value)

        # Aplica configurações adicionais
        if additional_configs:
            for key, value in additional_configs.items():
                conf.set(key, value)

        return conf

    def _configure_azure_storage(self):
        """Configura credenciais do Azure Storage."""
        if not self.spark:
            return

        azure_config = self.config.get('azure_data_lake', {})

        # Obtém credenciais
        account_name = azure_config.get('account_name')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')

        if not account_name:
            print("⚠️ Azure Storage Account não configurado")
            return

        # Configura autenticação
        use_managed_identity = azure_config.get('use_managed_identity', True)

        if use_managed_identity:
            # Usa identidade gerenciada (recomendado para Azure Synapse/Databricks)
            self.spark.conf.set(
                f"fs.azure.account.auth.type.{account_name}.dfs.core.windows.net",
                "OAuth"
            )
            self.spark.conf.set(
                f"fs.azure.account.oauth.provider.type.{account_name}.dfs.core.windows.net",
                "org.apache.hadoop.fs.azurebfs.oauth2.MsiTokenProvider"
            )
        elif client_id and client_secret and tenant_id:
            # Usa Service Principal
            self.spark.conf.set(
                f"fs.azure.account.auth.type.{account_name}.dfs.core.windows.net",
                "OAuth"
            )
            self.spark.conf.set(
                f"fs.azure.account.oauth.provider.type.{account_name}.dfs.core.windows.net",
                "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider"
            )
            self.spark.conf.set(
                f"fs.azure.account.oauth2.client.id.{account_name}.dfs.core.windows.net",
                client_id
            )
            self.spark.conf.set(
                f"fs.azure.account.oauth2.client.secret.{account_name}.dfs.core.windows.net",
                client_secret
            )
            self.spark.conf.set(
                f"fs.azure.account.oauth2.client.endpoint.{account_name}.dfs.core.windows.net",
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
            )
        else:
            # Tenta usar connection string
            connection_string = azure_config.get('connection_string')
            if connection_string and not connection_string.startswith("${"):
                # Extrai a chave de acesso da connection string
                if "AccountKey=" in connection_string:
                    account_key = connection_string.split("AccountKey=")[1].split(";")[0]
                    self.spark.conf.set(
                        f"fs.azure.account.key.{account_name}.dfs.core.windows.net",
                        account_key
                    )

    def stop_session(self):
        """Encerra a sessão Spark."""
        if self.spark:
            self.spark.stop()
            self.spark = None
            print("✅ Sessão Spark encerrada")

    def get_session(self) -> Optional[SparkSession]:
        """
        Retorna a sessão Spark atual.

        Returns:
            SparkSession ou None se não criada
        """
        return self.spark


def get_spark_session(
    app_name: str = None,
    config: Dict[str, Any] = None
) -> SparkSession:
    """
    Função auxiliar para obter uma sessão Spark.

    Args:
        app_name: Nome da aplicação
        config: Configurações do projeto

    Returns:
        SparkSession configurada

    Example:
        >>> spark = get_spark_session("MeuApp")
    """
    manager = SparkSessionManager(config)
    return manager.create_session(app_name)


# Exemplo de uso
if __name__ == "__main__":
    print("\n=== TESTE DE SPARK SESSION ===\n")

    # Cria sessão de teste
    spark = get_spark_session("TesteSparkSession")

    # Testa operação básica
    df = spark.createDataFrame([
        (1, "teste", 100.0),
        (2, "exemplo", 200.0)
    ], ["id", "nome", "valor"])

    print("DataFrame de teste criado:")
    df.show()

    print(f"\nVersão do Spark: {spark.version}")
    print(f"Configuração de shuffle partitions: {spark.conf.get('spark.sql.shuffle.partitions')}")

    # Para a sessão
    spark.stop()
    print("\n✅ Teste concluído!")
