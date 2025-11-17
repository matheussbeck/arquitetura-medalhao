"""
Config Loader - Carregador de Configurações
============================================
Módulo responsável por carregar configurações do projeto.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
import re
from dotenv import load_dotenv


class ConfigLoader:
    """Classe para carregar e gerenciar configurações do projeto."""

    def __init__(self, config_dir: str = None):
        """
        Inicializa o carregador de configurações.

        Args:
            config_dir: Diretório com arquivos de configuração
        """
        if config_dir is None:
            # Detecta automaticamente o diretório config
            current_dir = Path(__file__).parent.parent
            config_dir = current_dir / "config"

        self.config_dir = Path(config_dir)

        # Carrega variáveis de ambiente
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        self.config = {}
        self.sources = {}

    def load_config(self, filename: str = "config.yaml") -> Dict[str, Any]:
        """
        Carrega arquivo de configuração principal.

        Args:
            filename: Nome do arquivo de configuração

        Returns:
            Dicionário com configurações
        """
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_raw = yaml.safe_load(f)

        # Substitui variáveis de ambiente
        self.config = self._replace_env_variables(config_raw)
        return self.config

    def load_sources(self, filename: str = "sources.yaml") -> Dict[str, Any]:
        """
        Carrega arquivo de configuração de fontes de dados.

        Args:
            filename: Nome do arquivo de fontes

        Returns:
            Dicionário com configurações de fontes
        """
        sources_path = self.config_dir / filename

        if not sources_path.exists():
            raise FileNotFoundError(f"Arquivo de fontes não encontrado: {sources_path}")

        with open(sources_path, 'r', encoding='utf-8') as f:
            sources_raw = yaml.safe_load(f)

        # Substitui variáveis de ambiente
        self.sources = self._replace_env_variables(sources_raw)
        return self.sources

    def _replace_env_variables(self, obj: Any) -> Any:
        """
        Substitui variáveis de ambiente recursivamente.

        Args:
            obj: Objeto para processar (dict, list, str, etc.)

        Returns:
            Objeto com variáveis substituídas
        """
        if isinstance(obj, dict):
            return {k: self._replace_env_variables(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_variables(item) for item in obj]
        elif isinstance(obj, str):
            # Procura por padrão ${VAR_NAME}
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, obj)

            result = obj
            for var_name in matches:
                env_value = os.getenv(var_name, f"${{{var_name}}}")
                result = result.replace(f"${{{var_name}}}", env_value)

            return result
        else:
            return obj

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração usando caminho com pontos.

        Args:
            key_path: Caminho da chave (ex: "azure_data_lake.account_name")
            default: Valor padrão se não encontrado

        Returns:
            Valor da configuração

        Example:
            >>> config = ConfigLoader()
            >>> config.load_config()
            >>> account = config.get("azure_data_lake.account_name")
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_source(self, source_name: str) -> Dict[str, Any]:
        """
        Obtém configuração de uma fonte de dados específica.

        Args:
            source_name: Nome da fonte de dados

        Returns:
            Dicionário com configuração da fonte
        """
        # Procura em todas as categorias de fontes
        for category in self.sources.values():
            if isinstance(category, dict) and source_name in category:
                return category[source_name]

        raise ValueError(f"Fonte de dados não encontrada: {source_name}")

    def get_sources_by_business_area(self, business_area: str) -> Dict[str, Any]:
        """
        Obtém todas as fontes de uma área de negócio.

        Args:
            business_area: Nome da área de negócio

        Returns:
            Dicionário com fontes da área
        """
        result = {}

        for category_name, category in self.sources.items():
            if isinstance(category, dict):
                for source_name, source_config in category.items():
                    if isinstance(source_config, dict):
                        if source_config.get('business_area') == business_area:
                            result[source_name] = source_config

        return result

    def validate_config(self) -> bool:
        """
        Valida se configurações obrigatórias estão presentes.

        Returns:
            True se válido, False caso contrário
        """
        required_keys = [
            "environment.name",
            "azure_data_lake.account_name",
            "layers.bronze.path",
            "layers.silver.path",
            "layers.gold.path"
        ]

        for key in required_keys:
            value = self.get(key)
            if value is None or (isinstance(value, str) and value.startswith("${")):
                print(f"❌ Configuração obrigatória ausente ou não definida: {key}")
                return False

        print("✅ Configurações validadas com sucesso!")
        return True


# Singleton para uso global
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """
    Obtém instância singleton do ConfigLoader.

    Returns:
        Instância do ConfigLoader
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
        _config_loader.load_config()
        _config_loader.load_sources()
    return _config_loader


# Exemplo de uso
if __name__ == "__main__":
    # Testa o carregador de configurações
    config = ConfigLoader()
    config.load_config()
    config.load_sources()

    print("\n=== TESTE DE CONFIGURAÇÕES ===\n")
    print(f"Ambiente: {config.get('environment.name')}")
    print(f"Storage Account: {config.get('azure_data_lake.account_name')}")
    print(f"Caminho Bronze: {config.get('layers.bronze.path')}")

    print("\n=== VALIDAÇÃO ===\n")
    config.validate_config()

    print("\n=== FONTES DA ÁREA DE PRODUÇÃO ===\n")
    producao_sources = config.get_sources_by_business_area("producao")
    for source_name, source_config in producao_sources.items():
        print(f"  - {source_name}: {source_config.get('type')}")
