"""
Azure Data Lake Connector
==========================
Conector para leitura e escrita no Azure Data Lake Storage Gen2.
"""

from pyspark.sql import DataFrame, SparkSession
from typing import Dict, Any, Optional, List
from datetime import datetime
import os


class AzureDataLakeConnector:
    """Conector para Azure Data Lake Storage Gen2."""

    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        """
        Inicializa o conector.

        Args:
            spark: Sessão Spark
            config: Configurações do projeto
        """
        self.spark = spark
        self.config = config
        self.account_name = config.get('azure_data_lake', {}).get('account_name')

        if not self.account_name:
            raise ValueError("Azure Storage Account não configurado")

    def read(
        self,
        path: str,
        format: str = "parquet",
        options: Dict[str, str] = None,
        schema: Any = None
    ) -> DataFrame:
        """
        Lê dados do Azure Data Lake.

        Args:
            path: Caminho do arquivo/diretório (pode ser relativo ou absoluto)
            format: Formato dos dados (parquet, delta, csv, json, etc.)
            options: Opções específicas do formato
            schema: Schema para aplicar na leitura

        Returns:
            DataFrame com os dados

        Example:
            >>> df = connector.read("bronze/vendas/2024/01/", format="parquet")
        """
        # Converte para caminho ABFSS se necessário
        full_path = self._build_abfss_path(path)

        reader = self.spark.read.format(format)

        # Aplica schema se fornecido
        if schema:
            reader = reader.schema(schema)

        # Aplica opções
        if options:
            for key, value in options.items():
                reader = reader.option(key, value)

        try:
            df = reader.load(full_path)
            print(f"✅ Leitura concluída: {full_path}")
            print(f"   Registros: {df.count()}, Colunas: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler dados de {full_path}: {str(e)}")
            raise

    def write(
        self,
        df: DataFrame,
        path: str,
        format: str = "parquet",
        mode: str = "append",
        partition_by: List[str] = None,
        options: Dict[str, str] = None
    ):
        """
        Escreve dados no Azure Data Lake.

        Args:
            df: DataFrame a ser escrito
            path: Caminho de destino
            format: Formato de saída (parquet, delta, csv, json, etc.)
            mode: Modo de escrita (append, overwrite, ignore, error)
            partition_by: Colunas para particionar
            options: Opções específicas do formato

        Example:
            >>> connector.write(df, "silver/vendas/",
            ...                 partition_by=["ano", "mes"])
        """
        # Converte para caminho ABFSS se necessário
        full_path = self._build_abfss_path(path)

        writer = df.write.format(format).mode(mode)

        # Particiona se especificado
        if partition_by:
            writer = writer.partitionBy(*partition_by)

        # Aplica opções
        if options:
            for key, value in options.items():
                writer = writer.option(key, value)

        try:
            writer.save(full_path)
            print(f"✅ Escrita concluída: {full_path}")
            print(f"   Registros escritos: {df.count()}")
        except Exception as e:
            print(f"❌ Erro ao escrever dados em {full_path}: {str(e)}")
            raise

    def read_incremental(
        self,
        path: str,
        date_column: str,
        start_date: str = None,
        end_date: str = None,
        format: str = "parquet"
    ) -> DataFrame:
        """
        Lê dados incrementalmente baseado em coluna de data.

        Args:
            path: Caminho dos dados
            date_column: Nome da coluna de data para filtrar
            start_date: Data inicial (formato: YYYY-MM-DD)
            end_date: Data final (formato: YYYY-MM-DD)
            format: Formato dos dados

        Returns:
            DataFrame filtrado

        Example:
            >>> df = connector.read_incremental(
            ...     "bronze/vendas/",
            ...     date_column="data_venda",
            ...     start_date="2024-01-01"
            ... )
        """
        # Lê todos os dados
        df = self.read(path, format=format)

        # Aplica filtros de data
        if start_date:
            df = df.filter(f"{date_column} >= '{start_date}'")
        if end_date:
            df = df.filter(f"{date_column} <= '{end_date}'")

        print(f"📅 Filtro incremental aplicado: {start_date} a {end_date}")
        return df

    def list_files(self, path: str) -> List[str]:
        """
        Lista arquivos em um diretório do Data Lake.

        Args:
            path: Caminho do diretório

        Returns:
            Lista de caminhos de arquivos

        Example:
            >>> files = connector.list_files("bronze/vendas/")
        """
        full_path = self._build_abfss_path(path)

        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
                self.spark._jvm.java.net.URI(full_path),
                hadoop_conf
            )

            path_obj = self.spark._jvm.org.apache.hadoop.fs.Path(full_path)
            files = []

            if fs.exists(path_obj):
                file_status = fs.listStatus(path_obj)
                for status in file_status:
                    files.append(str(status.getPath()))

            return files
        except Exception as e:
            print(f"❌ Erro ao listar arquivos em {full_path}: {str(e)}")
            return []

    def path_exists(self, path: str) -> bool:
        """
        Verifica se um caminho existe no Data Lake.

        Args:
            path: Caminho a verificar

        Returns:
            True se existe, False caso contrário
        """
        full_path = self._build_abfss_path(path)

        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
                self.spark._jvm.java.net.URI(full_path),
                hadoop_conf
            )
            path_obj = self.spark._jvm.org.apache.hadoop.fs.Path(full_path)
            return fs.exists(path_obj)
        except Exception as e:
            print(f"⚠️ Erro ao verificar existência de {full_path}: {str(e)}")
            return False

    def delete_path(self, path: str, recursive: bool = False):
        """
        Deleta um caminho no Data Lake.

        Args:
            path: Caminho a deletar
            recursive: Se True, deleta recursivamente

        ⚠️ ATENÇÃO: Esta operação é destrutiva!
        """
        full_path = self._build_abfss_path(path)

        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
                self.spark._jvm.java.net.URI(full_path),
                hadoop_conf
            )
            path_obj = self.spark._jvm.org.apache.hadoop.fs.Path(full_path)

            if fs.exists(path_obj):
                fs.delete(path_obj, recursive)
                print(f"🗑️ Caminho deletado: {full_path}")
            else:
                print(f"⚠️ Caminho não existe: {full_path}")
        except Exception as e:
            print(f"❌ Erro ao deletar {full_path}: {str(e)}")
            raise

    def _build_abfss_path(self, path: str) -> str:
        """
        Constrói caminho ABFSS completo.

        Args:
            path: Caminho relativo ou absoluto

        Returns:
            Caminho ABFSS completo
        """
        # Se já é um caminho completo, retorna como está
        if path.startswith("abfss://") or path.startswith("abfs://"):
            return path

        # Se tem container especificado
        if path.startswith("bronze/") or path.startswith("silver/") or path.startswith("gold/"):
            container = path.split("/")[0]
            relative_path = "/".join(path.split("/")[1:])
            return f"abfss://{container}@{self.account_name}.dfs.core.windows.net/{relative_path}"

        # Caso contrário, usa o caminho como está
        return path

    def get_layer_path(self, layer: str, relative_path: str = "") -> str:
        """
        Obtém caminho completo para uma camada específica.

        Args:
            layer: Nome da camada (bronze, silver, gold)
            relative_path: Caminho relativo dentro da camada

        Returns:
            Caminho completo

        Example:
            >>> path = connector.get_layer_path("bronze", "vendas/2024/")
        """
        layer_config = self.config.get('layers', {}).get(layer, {})
        base_path = layer_config.get('path', '')

        if base_path and not base_path.endswith('/'):
            base_path += '/'

        return base_path + relative_path


# Exemplo de uso
if __name__ == "__main__":
    print("\n=== EXEMPLO DE USO DO AZURE CONNECTOR ===\n")

    # Nota: Este exemplo requer uma sessão Spark configurada
    print("""
    # Exemplo de uso:
    from utils.spark_session import get_spark_session
    from utils.config_loader import get_config_loader

    # Carrega configurações
    config = get_config_loader()

    # Cria sessão Spark
    spark = get_spark_session("ExemploAzure", config.config)

    # Cria conector
    connector = AzureDataLakeConnector(spark, config.config)

    # Lê dados
    df = connector.read("bronze/vendas/2024/01/", format="parquet")

    # Escreve dados
    connector.write(df, "silver/vendas/", partition_by=["ano", "mes"])

    # Leitura incremental
    df_incremental = connector.read_incremental(
        "bronze/vendas/",
        date_column="data_venda",
        start_date="2024-01-01"
    )
    """)
