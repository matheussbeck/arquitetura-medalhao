"""
SharePoint Connector
====================
Conector para leitura de arquivos do SharePoint Online.
"""

from pyspark.sql import DataFrame, SparkSession
from typing import Dict, Any, List, Optional
import os
import requests
from io import BytesIO
import pandas as pd


class SharePointConnector:
    """Conector para SharePoint Online."""

    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        """
        Inicializa o conector.

        Args:
            spark: Sessão Spark
            config: Configurações do projeto
        """
        self.spark = spark
        self.config = config
        self.sp_config = config.get('sharepoint', {})
        self.access_token = None

    def authenticate(self):
        """
        Autentica no SharePoint usando Azure AD.

        Obtém access token usando Client Credentials Flow.
        """
        tenant_id = self.sp_config.get('tenant_id') or os.getenv('SHAREPOINT_TENANT_ID')
        client_id = self.sp_config.get('client_id') or os.getenv('SHAREPOINT_CLIENT_ID')
        client_secret = self.sp_config.get('client_secret') or os.getenv('SHAREPOINT_CLIENT_SECRET')

        if not all([tenant_id, client_id, client_secret]):
            raise ValueError("Credenciais do SharePoint não configuradas")

        # Endpoint para obter token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        # Dados para requisição
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            self.access_token = response.json()['access_token']
            print("✅ Autenticação no SharePoint concluída")
        except Exception as e:
            print(f"❌ Erro ao autenticar no SharePoint: {str(e)}")
            raise

    def list_files(
        self,
        site_url: str = None,
        library: str = "Documents",
        folder: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Lista arquivos em uma biblioteca do SharePoint.

        Args:
            site_url: URL do site SharePoint
            library: Nome da biblioteca de documentos
            folder: Caminho da pasta (opcional)

        Returns:
            Lista de dicionários com informações dos arquivos

        Example:
            >>> files = connector.list_files(
            ...     library="Documentos Compartilhados",
            ...     folder="Relatorios/2024"
            ... )
        """
        if not self.access_token:
            self.authenticate()

        if site_url is None:
            site_url = self.sp_config.get('site_url')

        # Extrai informações do site
        site_info = self._parse_site_url(site_url)

        # Constrói URL da API Graph
        if folder:
            api_url = (f"https://graph.microsoft.com/v1.0/sites/{site_info['site_id']}/"
                      f"drives/{library}/root:/{folder}:/children")
        else:
            api_url = (f"https://graph.microsoft.com/v1.0/sites/{site_info['site_id']}/"
                      f"drives/{library}/root/children")

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            items = response.json().get('value', [])

            files = []
            for item in items:
                if 'file' in item:  # É um arquivo, não pasta
                    files.append({
                        'name': item['name'],
                        'size': item['size'],
                        'download_url': item['@microsoft.graph.downloadUrl'],
                        'modified': item['lastModifiedDateTime'],
                        'web_url': item['webUrl']
                    })

            print(f"✅ {len(files)} arquivo(s) encontrado(s)")
            return files
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {str(e)}")
            raise

    def read_excel(
        self,
        file_url: str = None,
        file_name: str = None,
        library: str = "Documents",
        folder: str = "",
        sheet_name: str = None,
        header: int = 0
    ) -> DataFrame:
        """
        Lê arquivo Excel do SharePoint.

        Args:
            file_url: URL completa do arquivo (opcional)
            file_name: Nome do arquivo (se file_url não fornecido)
            library: Nome da biblioteca
            folder: Caminho da pasta
            sheet_name: Nome ou índice da aba
            header: Linha do cabeçalho

        Returns:
            DataFrame Spark com os dados

        Example:
            >>> df = connector.read_excel(
            ...     file_name="relatorio.xlsx",
            ...     library="Documentos",
            ...     sheet_name="Dados"
            ... )
        """
        # Baixa arquivo
        file_content = self._download_file(file_url, file_name, library, folder)

        # Lê com pandas
        try:
            if sheet_name:
                pdf = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=header)
            else:
                pdf = pd.read_excel(BytesIO(file_content), header=header)

            # Converte para Spark DataFrame
            df = self.spark.createDataFrame(pdf)

            print(f"✅ Arquivo Excel lido com sucesso")
            print(f"   Registros: {df.count()}, Colunas: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler arquivo Excel: {str(e)}")
            raise

    def read_csv(
        self,
        file_url: str = None,
        file_name: str = None,
        library: str = "Documents",
        folder: str = "",
        delimiter: str = ",",
        encoding: str = "utf-8",
        header: bool = True
    ) -> DataFrame:
        """
        Lê arquivo CSV do SharePoint.

        Args:
            file_url: URL completa do arquivo (opcional)
            file_name: Nome do arquivo
            library: Nome da biblioteca
            folder: Caminho da pasta
            delimiter: Delimitador do CSV
            encoding: Encoding do arquivo
            header: Se tem cabeçalho

        Returns:
            DataFrame Spark com os dados
        """
        # Baixa arquivo
        file_content = self._download_file(file_url, file_name, library, folder)

        # Lê com pandas
        try:
            pdf = pd.read_csv(
                BytesIO(file_content),
                delimiter=delimiter,
                encoding=encoding,
                header=0 if header else None
            )

            # Converte para Spark DataFrame
            df = self.spark.createDataFrame(pdf)

            print(f"✅ Arquivo CSV lido com sucesso")
            print(f"   Registros: {df.count()}, Colunas: {len(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler arquivo CSV: {str(e)}")
            raise

    def download_file_to_local(
        self,
        local_path: str,
        file_url: str = None,
        file_name: str = None,
        library: str = "Documents",
        folder: str = ""
    ):
        """
        Baixa arquivo do SharePoint para disco local.

        Args:
            local_path: Caminho local de destino
            file_url: URL completa do arquivo
            file_name: Nome do arquivo
            library: Nome da biblioteca
            folder: Caminho da pasta
        """
        file_content = self._download_file(file_url, file_name, library, folder)

        try:
            with open(local_path, 'wb') as f:
                f.write(file_content)
            print(f"✅ Arquivo baixado para: {local_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {str(e)}")
            raise

    def _download_file(
        self,
        file_url: str = None,
        file_name: str = None,
        library: str = "Documents",
        folder: str = ""
    ) -> bytes:
        """
        Baixa conteúdo de arquivo do SharePoint.

        Args:
            file_url: URL completa do arquivo
            file_name: Nome do arquivo
            library: Nome da biblioteca
            folder: Caminho da pasta

        Returns:
            Conteúdo do arquivo em bytes
        """
        if not self.access_token:
            self.authenticate()

        # Se URL completa fornecida, usa diretamente
        if file_url and '@microsoft.graph.downloadUrl' not in file_url:
            # Precisa obter download URL
            files = self.list_files(library=library, folder=folder)
            matching_file = next((f for f in files if f['name'] == file_name), None)

            if not matching_file:
                raise FileNotFoundError(f"Arquivo não encontrado: {file_name}")

            download_url = matching_file['download_url']
        else:
            download_url = file_url

        # Baixa arquivo
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"❌ Erro ao baixar arquivo: {str(e)}")
            raise

    def _parse_site_url(self, site_url: str) -> Dict[str, str]:
        """
        Extrai informações do site URL.

        Args:
            site_url: URL do site SharePoint

        Returns:
            Dicionário com informações
        """
        # Exemplo: https://empresa.sharepoint.com/sites/meusite
        # Para simplificar, este método retorna estrutura básica
        # Em produção, seria necessário fazer chamada à API Graph para obter site_id

        parts = site_url.replace('https://', '').split('/')
        tenant = parts[0].split('.')[0]
        site_name = parts[-1] if len(parts) > 1 else ''

        return {
            'tenant': tenant,
            'site_name': site_name,
            'site_id': f"{tenant}.sharepoint.com,sites,{site_name}"  # Aproximação
        }


# Exemplo de uso
if __name__ == "__main__":
    print("\n=== EXEMPLO DE USO DO SHAREPOINT CONNECTOR ===\n")

    print("""
    # Exemplo de uso:
    from utils.spark_session import get_spark_session
    from utils.config_loader import get_config_loader

    # Carrega configurações
    config = get_config_loader()

    # Cria sessão Spark
    spark = get_spark_session("ExemploSharePoint", config.config)

    # Cria conector
    connector = SharePointConnector(spark, config.config)

    # Autentica
    connector.authenticate()

    # Lista arquivos
    files = connector.list_files(
        library="Documentos Compartilhados",
        folder="Relatorios"
    )

    # Lê arquivo Excel
    df = connector.read_excel(
        file_name="relatorio.xlsx",
        library="Documentos",
        folder="Relatorios/2024",
        sheet_name="Dados"
    )

    # Lê arquivo CSV
    df = connector.read_csv(
        file_name="dados.csv",
        library="Documentos",
        delimiter=";"
    )
    """)
