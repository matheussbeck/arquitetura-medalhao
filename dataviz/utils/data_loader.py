"""
Data Loader - Carregador de Dados para Dashboards
==================================================
Carrega dados das camadas Gold do Data Lake para os dashboards.
"""

import pandas as pd
from typing import Optional, List
from datetime import datetime, timedelta


class DataLoader:
    """Carregador de dados otimizado com cache."""

    def __init__(self, spark=None, cache_timeout=300):
        """
        Inicializa o data loader.

        Args:
            spark: SparkSession (opcional, usa global se não fornecido)
            cache_timeout: Tempo de cache em segundos (padrão: 5 minutos)
        """
        self.spark = spark
        self.cache_timeout = cache_timeout
        self._cache = {}
        self._cache_time = {}

    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se cache é válido."""
        if key not in self._cache_time:
            return False

        elapsed = (datetime.now() - self._cache_time[key]).total_seconds()
        return elapsed < self.cache_timeout

    def load_from_gold(
        self,
        table_path: str,
        filters: Optional[dict] = None,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Carrega dados da camada Gold.

        Args:
            table_path: Caminho da tabela Gold (ex: "gold/plantio/area_por_variedade/")
            filters: Filtros para aplicar (ex: {"safra": "2023/2024"})
            columns: Colunas para selecionar (None = todas)

        Returns:
            pandas.DataFrame

        Example:
            >>> loader = DataLoader(spark)
            >>> df = loader.load_from_gold("gold/plantio/area_por_variedade/")
        """
        cache_key = f"{table_path}_{filters}_{columns}"

        # Verifica cache
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key].copy()

        # Carrega dados
        if self.spark:
            # Lê com Spark
            df_spark = self.spark.read.format("delta").load(table_path)

            # Aplica filtros
            if filters:
                for col, value in filters.items():
                    if isinstance(value, list):
                        df_spark = df_spark.filter(df_spark[col].isin(value))
                    else:
                        df_spark = df_spark.filter(df_spark[col] == value)

            # Seleciona colunas
            if columns:
                df_spark = df_spark.select(*columns)

            # Converte para Pandas
            df = df_spark.toPandas()
        else:
            # Lê com Pandas (desenvolvimento local)
            import glob
            files = glob.glob(f"{table_path}/**/*.parquet", recursive=True)

            if files:
                df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

                # Aplica filtros
                if filters:
                    for col, value in filters.items():
                        if isinstance(value, list):
                            df = df[df[col].isin(value)]
                        else:
                            df = df[df[col] == value]

                # Seleciona colunas
                if columns:
                    df = df[columns]
            else:
                # Dados de exemplo se arquivo não existe
                df = pd.DataFrame()

        # Atualiza cache
        self._cache[cache_key] = df.copy()
        self._cache_time[cache_key] = datetime.now()

        return df

    def get_plantio_area_por_variedade(self, safra: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega dados de área plantada por variedade.

        Args:
            safra: Safra específica (None = todas)

        Returns:
            DataFrame com colunas: safra, variedade, area_ha, percentual
        """
        filters = {"safra": safra} if safra else None
        df = self.load_from_gold("gold/plantio/area_por_variedade/", filters=filters)

        # Se não tem dados, cria exemplo
        if df.empty:
            df = pd.DataFrame({
                'safra': ['2023/2024'] * 5,
                'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579'],
                'area_ha': [3500, 2800, 2200, 1500, 1000],
                'percentual': [31.8, 25.5, 20.0, 13.6, 9.1]
            })

        return df

    def get_plantio_cronograma(self, safra: Optional[str] = None) -> pd.DataFrame:
        """
        Carrega cronograma de plantio.

        Args:
            safra: Safra específica

        Returns:
            DataFrame com cronograma mensal
        """
        filters = {"safra": safra} if safra else None
        df = self.load_from_gold("gold/plantio/cronograma/", filters=filters)

        if df.empty:
            # Dados de exemplo
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            df = pd.DataFrame({
                'mes': meses,
                'area_planejada_ha': [800, 900, 1200, 1500, 1800, 1600, 1200, 800, 600, 400, 200, 100],
                'area_realizada_ha': [820, 880, 1180, 1520, 1750, 1580, 1150, 0, 0, 0, 0, 0],
                'percentual_realizado': [102.5, 97.8, 98.3, 101.3, 97.2, 98.8, 95.8, 0, 0, 0, 0, 0]
            })

        return df

    def get_vinhaca_aplicacao(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Carrega dados de aplicação de vinhaça.

        Args:
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)

        Returns:
            DataFrame com aplicações
        """
        # Por simplicidade, cria dados de exemplo
        # Em produção, carregaria de gold/vinhaca/aplicacao/

        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        df = pd.DataFrame({
            'data': dates,
            'talhao': [f'T{i%50:03d}' for i in range(len(dates))],
            'volume_m3': (100 + pd.Series(range(len(dates))) % 200).values,
            'volume_m3_ha': (80 + pd.Series(range(len(dates))) % 50).values,
            'ph': (7.0 + (pd.Series(range(len(dates))) % 20) / 10).values,
            'potassio_kg_m3': (3 + (pd.Series(range(len(dates))) % 15) / 10).values
        })

        if data_inicio:
            df = df[df['data'] >= pd.to_datetime(data_inicio)]
        if data_fim:
            df = df[df['data'] <= pd.to_datetime(data_fim)]

        return df

    def get_kpis_agronomicos(self, safra: Optional[str] = None) -> dict:
        """
        Carrega KPIs agronômicos principais.

        Args:
            safra: Safra específica

        Returns:
            Dicionário com KPIs
        """
        # Em produção, carregaria de gold/agronomico/kpis/

        return {
            'area_total_ha': 11000,
            'area_plantada_safra_ha': 9500,
            'tch_medio': 85.5,
            'atr_medio': 145.2,
            'produtividade_toneladas': 812250,
            'numero_talhoes': 245,
            'numero_variedades': 8,
            'idade_media_canavial_anos': 2.3
        }

    def get_dados_climaticos(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Carrega dados climáticos.

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            DataFrame com dados meteorológicos
        """
        # Dados de exemplo
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')

        df = pd.DataFrame({
            'data': dates,
            'precipitacao_mm': (pd.Series(range(len(dates))) % 50).values,
            'temperatura_max_c': (25 + (pd.Series(range(len(dates))) % 15)).values,
            'temperatura_min_c': (15 + (pd.Series(range(len(dates))) % 10)).values,
            'umidade_relativa_pct': (60 + (pd.Series(range(len(dates))) % 30)).values
        })

        if data_inicio:
            df = df[df['data'] >= pd.to_datetime(data_inicio)]
        if data_fim:
            df = df[df['data'] <= pd.to_datetime(data_fim)]

        return df

    def clear_cache(self):
        """Limpa todo o cache."""
        self._cache = {}
        self._cache_time = {}
