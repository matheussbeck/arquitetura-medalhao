"""
Conectores de Fontes de Dados
==============================
Módulos para conexão com diferentes fontes de dados.
"""

from .azure_connector import AzureDataLakeConnector
from .synapse_connector import SynapseConnector
from .sharepoint_connector import SharePointConnector

__all__ = [
    'AzureDataLakeConnector',
    'SynapseConnector',
    'SharePointConnector'
]
