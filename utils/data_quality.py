"""
Data Quality - Validação e Qualidade de Dados
==============================================
Módulo para validação e verificação de qualidade de dados.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan, isnull, sum as spark_sum
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataQualityChecker:
    """Verificador de qualidade de dados."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o verificador.

        Args:
            config: Configurações de qualidade
        """
        self.config = config or {}
        self.quality_config = self.config.get('quality', {})
        self.null_threshold = self.quality_config.get('null_threshold', 0.05)
        self.duplicate_threshold = self.quality_config.get('duplicate_threshold', 0.01)
        self.quality_report = {}

    def validate_schema(
        self,
        df: DataFrame,
        expected_schema: Dict[str, str],
        strict: bool = True
    ) -> bool:
        """
        Valida schema do DataFrame.

        Args:
            df: DataFrame a validar
            expected_schema: Schema esperado (dict com nome_coluna: tipo)
            strict: Se True, todas as colunas devem existir

        Returns:
            True se válido, False caso contrário

        Example:
            >>> expected = {"id": "long", "nome": "string", "valor": "double"}
            >>> is_valid = checker.validate_schema(df, expected)
        """
        actual_schema = {field.name: field.dataType.simpleString() for field in df.schema.fields}

        is_valid = True
        missing_columns = []
        type_mismatches = []

        # Verifica colunas esperadas
        for col_name, expected_type in expected_schema.items():
            if col_name not in actual_schema:
                missing_columns.append(col_name)
                is_valid = False
            elif actual_schema[col_name] != expected_type:
                type_mismatches.append({
                    'column': col_name,
                    'expected': expected_type,
                    'actual': actual_schema[col_name]
                })
                if strict:
                    is_valid = False

        # Reporta resultados
        if missing_columns:
            print(f"❌ Colunas ausentes: {missing_columns}")

        if type_mismatches:
            print(f"⚠️ Tipos incompatíveis:")
            for mismatch in type_mismatches:
                print(f"   - {mismatch['column']}: esperado {mismatch['expected']}, "
                      f"encontrado {mismatch['actual']}")

        if is_valid:
            print(f"✅ Schema validado com sucesso")

        return is_valid

    def check_null_values(
        self,
        df: DataFrame,
        columns: List[str] = None
    ) -> Dict[str, float]:
        """
        Verifica percentual de valores nulos por coluna.

        Args:
            df: DataFrame a verificar
            columns: Lista de colunas (None para todas)

        Returns:
            Dicionário com percentual de nulos por coluna

        Example:
            >>> null_report = checker.check_null_values(df)
        """
        if columns is None:
            columns = df.columns

        total_count = df.count()
        null_counts = {}

        for column in columns:
            null_count = df.filter(
                col(column).isNull() | isnan(column)
            ).count()
            null_percentage = (null_count / total_count) if total_count > 0 else 0
            null_counts[column] = null_percentage

            # Alerta se acima do threshold
            if null_percentage > self.null_threshold:
                print(f"⚠️ {column}: {null_percentage:.2%} de valores nulos "
                      f"(threshold: {self.null_threshold:.2%})")

        return null_counts

    def check_duplicates(
        self,
        df: DataFrame,
        key_columns: List[str] = None
    ) -> Dict[str, Any]:
        """
        Verifica registros duplicados.

        Args:
            df: DataFrame a verificar
            key_columns: Colunas que formam a chave (None para todas)

        Returns:
            Dicionário com estatísticas de duplicatas

        Example:
            >>> dup_report = checker.check_duplicates(df, ["id"])
        """
        total_count = df.count()

        if key_columns is None:
            key_columns = df.columns

        # Conta duplicatas
        duplicates_df = df.groupBy(key_columns).count().filter(col("count") > 1)
        duplicate_count = duplicates_df.count()
        duplicate_percentage = (duplicate_count / total_count) if total_count > 0 else 0

        result = {
            'total_records': total_count,
            'duplicate_keys': duplicate_count,
            'duplicate_percentage': duplicate_percentage,
            'unique_percentage': 1 - duplicate_percentage
        }

        # Alerta se acima do threshold
        if duplicate_percentage > self.duplicate_threshold:
            print(f"⚠️ {duplicate_percentage:.2%} de duplicatas encontradas "
                  f"(threshold: {self.duplicate_threshold:.2%})")
        else:
            print(f"✅ Duplicatas dentro do aceitável: {duplicate_percentage:.2%}")

        return result

    def check_data_types(
        self,
        df: DataFrame,
        columns: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Verifica tipos de dados inconsistentes.

        Args:
            df: DataFrame a verificar
            columns: Colunas a verificar

        Returns:
            Dicionário com issues encontrados
        """
        if columns is None:
            columns = df.columns

        issues = {}

        for column in columns:
            col_type = dict(df.dtypes)[column]

            # Verifica se tipo numérico tem strings
            if col_type in ['int', 'bigint', 'double', 'float']:
                # Tenta converter e conta falhas
                try:
                    invalid_count = df.filter(
                        col(column).isNotNull() &
                        col(column).cast('double').isNull()
                    ).count()

                    if invalid_count > 0:
                        issues[column] = f"{invalid_count} valores não numéricos"
                except:
                    pass

        return issues

    def check_value_ranges(
        self,
        df: DataFrame,
        range_rules: Dict[str, Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Verifica se valores estão dentro de ranges esperados.

        Args:
            df: DataFrame a verificar
            range_rules: Regras de range por coluna
                         Ex: {"idade": {"min": 0, "max": 120}}

        Returns:
            Dicionário com contagem de valores fora do range

        Example:
            >>> rules = {"valor": {"min": 0, "max": 10000}}
            >>> violations = checker.check_value_ranges(df, rules)
        """
        violations = {}

        for column, rules in range_rules.items():
            if column not in df.columns:
                continue

            condition = col(column).isNotNull()

            if 'min' in rules:
                condition = condition & (col(column) >= rules['min'])
            if 'max' in rules:
                condition = condition & (col(column) <= rules['max'])

            # Conta violações (valores que NÃO atendem a condição)
            violation_count = df.filter(~condition).count()
            violations[column] = violation_count

            if violation_count > 0:
                print(f"⚠️ {column}: {violation_count} valores fora do range esperado")

        return violations

    def generate_quality_report(
        self,
        df: DataFrame,
        key_columns: List[str] = None,
        schema: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório completo de qualidade.

        Args:
            df: DataFrame a analisar
            key_columns: Colunas chave para verificar duplicatas
            schema: Schema esperado para validação

        Returns:
            Dicionário com relatório completo

        Example:
            >>> report = checker.generate_quality_report(df, ["id"])
        """
        print("\n" + "="*60)
        print("RELATÓRIO DE QUALIDADE DE DADOS")
        print("="*60 + "\n")

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': df.count(),
            'total_columns': len(df.columns),
            'columns': df.columns
        }

        # Validação de schema
        if schema:
            print("\n📋 VALIDAÇÃO DE SCHEMA")
            print("-" * 60)
            report['schema_valid'] = self.validate_schema(df, schema, strict=False)

        # Valores nulos
        print("\n🔍 VALORES NULOS")
        print("-" * 60)
        report['null_analysis'] = self.check_null_values(df)

        # Duplicatas
        if key_columns:
            print("\n🔄 ANÁLISE DE DUPLICATAS")
            print("-" * 60)
            report['duplicate_analysis'] = self.check_duplicates(df, key_columns)

        # Estatísticas básicas
        print("\n📊 ESTATÍSTICAS BÁSICAS")
        print("-" * 60)
        numeric_cols = [f.name for f in df.schema.fields
                       if f.dataType.simpleString() in ['int', 'bigint', 'double', 'float']]

        if numeric_cols:
            stats = df.select(numeric_cols).describe()
            report['statistics'] = stats.toPandas().to_dict()
            stats.show()

        print("\n" + "="*60)
        print("FIM DO RELATÓRIO")
        print("="*60 + "\n")

        self.quality_report = report
        return report

    def apply_quality_filters(
        self,
        df: DataFrame,
        remove_nulls: bool = True,
        remove_duplicates: bool = True,
        key_columns: List[str] = None
    ) -> DataFrame:
        """
        Aplica filtros de qualidade no DataFrame.

        Args:
            df: DataFrame a filtrar
            remove_nulls: Remove registros com valores nulos
            remove_duplicates: Remove duplicatas
            key_columns: Colunas para identificar duplicatas

        Returns:
            DataFrame filtrado

        Example:
            >>> df_clean = checker.apply_quality_filters(df, key_columns=["id"])
        """
        df_clean = df
        initial_count = df.count()

        # Remove nulos
        if remove_nulls:
            df_clean = df_clean.dropna()
            print(f"🧹 Removidos {initial_count - df_clean.count()} registros com nulos")

        # Remove duplicatas
        if remove_duplicates:
            if key_columns:
                df_clean = df_clean.dropDuplicates(key_columns)
            else:
                df_clean = df_clean.dropDuplicates()

            final_count = df_clean.count()
            print(f"🧹 Removidas {initial_count - final_count} duplicatas")

        return df_clean


# Exemplo de uso
if __name__ == "__main__":
    from pyspark.sql import SparkSession

    print("\n=== TESTE DE DATA QUALITY CHECKER ===\n")

    # Cria sessão Spark
    spark = SparkSession.builder.appName("TesteDataQuality").getOrCreate()

    # Cria DataFrame de teste
    data = [
        (1, "João", 25, 5000.0),
        (2, "Maria", 30, 6000.0),
        (3, "Pedro", None, 5500.0),  # Null
        (1, "João", 25, 5000.0),  # Duplicata
        (4, "Ana", 28, None),  # Null
    ]

    df = spark.createDataFrame(data, ["id", "nome", "idade", "salario"])

    # Cria checker
    checker = DataQualityChecker()

    # Gera relatório
    report = checker.generate_quality_report(
        df,
        key_columns=["id"],
        schema={"id": "bigint", "nome": "string", "idade": "bigint", "salario": "double"}
    )

    # Aplica filtros de qualidade
    df_clean = checker.apply_quality_filters(df, key_columns=["id"])
    print(f"\n✅ DataFrame limpo: {df_clean.count()} registros")

    spark.stop()
