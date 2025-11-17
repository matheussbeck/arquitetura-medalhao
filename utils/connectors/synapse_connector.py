"""
Azure Synapse Connector
=======================
Conector para leitura e escrita no Azure Synapse Analytics.
"""

from pyspark.sql import DataFrame, SparkSession
from typing import Dict, Any, Optional
import os


class SynapseConnector:
    """Conector para Azure Synapse Analytics (SQL Pool e Serverless)."""

    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        """
        Inicializa o conector.

        Args:
            spark: Sessão Spark
            config: Configurações do projeto
        """
        self.spark = spark
        self.config = config
        self.synapse_config = config.get('azure_synapse', {})
        self.sql_dw_config = config.get('azure_sql_dw', {})

    def read_synapse_table(
        self,
        database: str,
        schema: str,
        table: str,
        pool_type: str = "dedicated",
        query: str = None
    ) -> DataFrame:
        """
        Lê tabela do Synapse SQL Pool.

        Args:
            database: Nome do database
            schema: Nome do schema
            table: Nome da tabela
            pool_type: Tipo de pool ("dedicated" ou "serverless")
            query: Query SQL customizada (opcional)

        Returns:
            DataFrame com os dados

        Example:
            >>> df = connector.read_synapse_table(
            ...     database="DW_Vendas",
            ...     schema="dbo",
            ...     table="fato_vendas"
            ... )
        """
        # Escolhe endpoint baseado no tipo de pool
        if pool_type == "dedicated":
            endpoint = self.synapse_config.get('dedicated_pool_endpoint')
        else:
            endpoint = self.synapse_config.get('serverless_endpoint')

        if not endpoint:
            raise ValueError(f"Endpoint do Synapse não configurado para pool_type={pool_type}")

        # Constrói JDBC URL
        jdbc_url = self._build_jdbc_url(endpoint, database)

        # Define query ou nome da tabela
        if query:
            query_str = f"({query}) as query_result"
        else:
            query_str = f"{schema}.{table}"

        # Propriedades de conexão
        connection_properties = self._get_connection_properties()

        try:
            df = (self.spark.read
                  .format("jdbc")
                  .option("url", jdbc_url)
                  .option("dbtable", query_str)
                  .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
                  .options(**connection_properties)
                  .load())

            print(f"✅ Leitura concluída: {database}.{schema}.{table}")
            print(f"   Registros: {df.count()}, Colunas: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler tabela {schema}.{table}: {str(e)}")
            raise

    def read_synapse_query(
        self,
        query: str,
        database: str = None,
        pool_type: str = "dedicated"
    ) -> DataFrame:
        """
        Executa query customizada no Synapse.

        Args:
            query: Query SQL a executar
            database: Nome do database (usa padrão se não especificado)
            pool_type: Tipo de pool ("dedicated" ou "serverless")

        Returns:
            DataFrame com resultado da query

        Example:
            >>> df = connector.read_synapse_query(
            ...     "SELECT * FROM dbo.vendas WHERE ano = 2024"
            ... )
        """
        if database is None:
            database = self.synapse_config.get('database')

        # Escolhe endpoint
        if pool_type == "dedicated":
            endpoint = self.synapse_config.get('dedicated_pool_endpoint')
        else:
            endpoint = self.synapse_config.get('serverless_endpoint')

        jdbc_url = self._build_jdbc_url(endpoint, database)
        connection_properties = self._get_connection_properties()

        # Encapsula query em subquery
        query_wrapped = f"({query}) as custom_query"

        try:
            df = (self.spark.read
                  .format("jdbc")
                  .option("url", jdbc_url)
                  .option("dbtable", query_wrapped)
                  .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
                  .options(**connection_properties)
                  .load())

            print(f"✅ Query executada com sucesso")
            print(f"   Registros: {df.count()}")
            return df
        except Exception as e:
            print(f"❌ Erro ao executar query: {str(e)}")
            raise

    def write_synapse_table(
        self,
        df: DataFrame,
        database: str,
        schema: str,
        table: str,
        mode: str = "append",
        pool_type: str = "dedicated"
    ):
        """
        Escreve DataFrame em tabela do Synapse.

        Args:
            df: DataFrame a escrever
            database: Nome do database
            schema: Nome do schema
            table: Nome da tabela
            mode: Modo de escrita (append, overwrite, ignore, error)
            pool_type: Tipo de pool

        Example:
            >>> connector.write_synapse_table(
            ...     df, "DW_Vendas", "dbo", "fato_vendas"
            ... )
        """
        # Escolhe endpoint
        if pool_type == "dedicated":
            endpoint = self.synapse_config.get('dedicated_pool_endpoint')
        else:
            endpoint = self.synapse_config.get('serverless_endpoint')

        jdbc_url = self._build_jdbc_url(endpoint, database)
        connection_properties = self._get_connection_properties()

        table_name = f"{schema}.{table}"

        try:
            (df.write
             .format("jdbc")
             .option("url", jdbc_url)
             .option("dbtable", table_name)
             .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
             .mode(mode)
             .options(**connection_properties)
             .save())

            print(f"✅ Escrita concluída: {database}.{schema}.{table}")
            print(f"   Registros escritos: {df.count()}")
        except Exception as e:
            print(f"❌ Erro ao escrever tabela {schema}.{table}: {str(e)}")
            raise

    def read_sql_dw_table(
        self,
        schema: str,
        table: str,
        query: str = None
    ) -> DataFrame:
        """
        Lê tabela do Azure SQL Data Warehouse.

        Args:
            schema: Nome do schema
            table: Nome da tabela
            query: Query SQL customizada (opcional)

        Returns:
            DataFrame com os dados
        """
        server = self.sql_dw_config.get('server')
        database = self.sql_dw_config.get('database')
        port = self.sql_dw_config.get('port', 1433)

        if not server or not database:
            raise ValueError("Azure SQL DW não configurado")

        # Constrói JDBC URL
        jdbc_url = f"jdbc:sqlserver://{server}:{port};database={database}"

        # Define query ou nome da tabela
        if query:
            query_str = f"({query}) as query_result"
        else:
            query_str = f"{schema}.{table}"

        # Propriedades de conexão
        connection_properties = self._get_sql_dw_connection_properties()

        try:
            df = (self.spark.read
                  .format("jdbc")
                  .option("url", jdbc_url)
                  .option("dbtable", query_str)
                  .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")
                  .options(**connection_properties)
                  .load())

            print(f"✅ Leitura concluída: {database}.{schema}.{table}")
            print(f"   Registros: {df.count()}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler tabela SQL DW {schema}.{table}: {str(e)}")
            raise

    def read_incremental(
        self,
        database: str,
        schema: str,
        table: str,
        incremental_column: str,
        last_value: Any = None,
        pool_type: str = "dedicated"
    ) -> DataFrame:
        """
        Lê dados incrementalmente de uma tabela.

        Args:
            database: Nome do database
            schema: Nome do schema
            table: Nome da tabela
            incremental_column: Coluna para controle incremental
            last_value: Último valor processado
            pool_type: Tipo de pool

        Returns:
            DataFrame com dados novos
        """
        if last_value:
            # Determina tipo de comparação baseado no tipo do valor
            if isinstance(last_value, str):
                condition = f"'{last_value}'"
            else:
                condition = str(last_value)

            query = f"""
                SELECT * FROM {schema}.{table}
                WHERE {incremental_column} > {condition}
                ORDER BY {incremental_column}
            """
        else:
            query = f"SELECT * FROM {schema}.{table} ORDER BY {incremental_column}"

        return self.read_synapse_query(query, database, pool_type)

    def _build_jdbc_url(self, endpoint: str, database: str) -> str:
        """
        Constrói JDBC URL para Synapse.

        Args:
            endpoint: Endpoint do Synapse
            database: Nome do database

        Returns:
            JDBC URL completa
        """
        return f"jdbc:sqlserver://{endpoint};database={database};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.sql.azuresynapse.net;loginTimeout=30;"

    def _get_connection_properties(self) -> Dict[str, str]:
        """
        Obtém propriedades de conexão para Synapse.

        Returns:
            Dicionário com propriedades
        """
        username = os.getenv('SYNAPSE_USERNAME')
        password = os.getenv('SYNAPSE_PASSWORD')

        # Tenta usar autenticação do Azure AD se credenciais não disponíveis
        if not username or not password:
            # Usa autenticação integrada (Managed Identity)
            return {
                "Authentication": "ActiveDirectoryIntegrated"
            }

        return {
            "user": username,
            "password": password
        }

    def _get_sql_dw_connection_properties(self) -> Dict[str, str]:
        """
        Obtém propriedades de conexão para SQL DW.

        Returns:
            Dicionário com propriedades
        """
        username = os.getenv('AZURE_SQL_USERNAME')
        password = os.getenv('AZURE_SQL_PASSWORD')

        if not username or not password:
            return {
                "Authentication": "ActiveDirectoryIntegrated"
            }

        return {
            "user": username,
            "password": password
        }


# Exemplo de uso
if __name__ == "__main__":
    print("\n=== EXEMPLO DE USO DO SYNAPSE CONNECTOR ===\n")

    print("""
    # Exemplo de uso:
    from utils.spark_session import get_spark_session
    from utils.config_loader import get_config_loader

    # Carrega configurações
    config = get_config_loader()

    # Cria sessão Spark
    spark = get_spark_session("ExemploSynapse", config.config)

    # Cria conector
    connector = SynapseConnector(spark, config.config)

    # Lê tabela
    df = connector.read_synapse_table(
        database="DW_Vendas",
        schema="dbo",
        table="fato_vendas"
    )

    # Executa query customizada
    df = connector.read_synapse_query(
        "SELECT * FROM dbo.vendas WHERE ano = 2024"
    )

    # Leitura incremental
    df = connector.read_incremental(
        database="DW_Vendas",
        schema="dbo",
        table="fato_vendas",
        incremental_column="data_atualizacao",
        last_value="2024-01-01"
    )
    """)
