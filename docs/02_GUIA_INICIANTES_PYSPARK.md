# 🚀 Guia de Iniciantes - PySpark

## 📚 Índice
1. [Introdução](#introdução)
2. [Conceitos Básicos](#conceitos-básicos)
3. [DataFrames - Fundamentos](#dataframes---fundamentos)
4. [Operações Comuns](#operações-comuns)
5. [Transformações](#transformações)
6. [Agregações](#agregações)
7. [Joins](#joins)
8. [Funções Úteis](#funções-úteis)
9. [Exemplos Práticos](#exemplos-práticos)
10. [Dicas e Truques](#dicas-e-truques)

---

## Introdução

### O que é PySpark?

PySpark é a interface Python para Apache Spark - uma ferramenta para processar grandes volumes de dados de forma rápida e distribuída.

**Por que usar PySpark?**
- ⚡ Processa milhões de registros rapidamente
- 🔄 Trabalha com dados distribuídos
- 🐍 Usa sintaxe Python familiar
- 📊 Integra com Azure, Databricks, Synapse

### Conceito Chave: DataFrame

Um **DataFrame** é como uma tabela do Excel ou planilha, mas:
- Pode ter milhões (ou bilhões) de linhas
- Operações são executadas em paralelo
- Imutável (não modifica original, cria novo)

```
 DataFrame = Tabela de Dados
  ┌─────┬────────┬───────┐
  │ ID  │ Nome   │ Valor │
  ├─────┼────────┼───────┤
  │ 1   │ João   │ 100   │
  │ 2   │ Maria  │ 200   │
  │ 3   │ Pedro  │ 150   │
  └─────┴────────┴───────┘
```

---

## Conceitos Básicos

### Importações Necessárias

```python
# Sempre comece com estas importações
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql import Window
```

**O que cada uma faz?**
- `functions as F`: Funções prontas (soma, média, etc.)
- `types`: Tipos de dados (string, número, data)
- `Window`: Para cálculos por grupos

### Criando um DataFrame

#### A partir de dados Python
```python
# Lista de tuplas (linha, linha, linha...)
dados = [
    (1, "João", 1000),
    (2, "Maria", 1500),
    (3, "Pedro", 1200)
]

# Cria DataFrame
df = spark.createDataFrame(dados, ["id", "nome", "salario"])

# Mostra resultado
df.show()
```

**Resultado**:
```
+---+-----+-------+
| id| nome|salario|
+---+-----+-------+
|  1| João|   1000|
|  2|Maria|   1500|
|  3|Pedro|   1200|
+---+-----+-------+
```

#### Lendo de arquivos

```python
# CSV
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("caminho/arquivo.csv")

# Parquet
df = spark.read.parquet("caminho/arquivo.parquet")

# Delta Lake
df = spark.read.format("delta").load("caminho/tabela/")

# Excel (usando pandas)
import pandas as pd
pdf = pd.read_excel("arquivo.xlsx")
df = spark.createDataFrame(pdf)
```

---

## DataFrames - Fundamentos

### Ver Estrutura do DataFrame

```python
# Mostra primeiras linhas
df.show()

# Mostra N linhas
df.show(10)

# Mostra sem truncar textos longos
df.show(truncate=False)

# Mostra schema (estrutura)
df.printSchema()

# Conta linhas
total = df.count()
print(f"Total de registros: {total}")

# Lista colunas
colunas = df.columns
print(f"Colunas: {colunas}")

# Informações resumidas
df.describe().show()
```

### Selecionar Colunas

```python
# Seleciona uma coluna
df_nome = df.select("nome")

# Seleciona várias colunas
df_subset = df.select("id", "nome", "salario")

# Usando col()
from pyspark.sql.functions import col
df_subset = df.select(col("id"), col("nome"))

# Seleciona todas MENOS algumas
df_sem_id = df.drop("id")
```

---

## Operações Comuns

### Filtrar Dados (WHERE)

```python
# Filtro simples
df_filtrado = df.filter(df.salario > 1200)

# Usando col()
df_filtrado = df.filter(col("salario") > 1200)

# Usando SQL-like
df_filtrado = df.filter("salario > 1200")

# Múltiplos filtros (E)
df_filtrado = df.filter(
    (col("salario") > 1000) &
    (col("nome") != "João")
)

# Múltiplos filtros (OU)
df_filtrado = df.filter(
    (col("salario") > 1500) |
    (col("nome") == "João")
)

# Filtro NULL
df_sem_nulos = df.filter(col("salario").isNotNull())

# Filtro NOT NULL
df_com_nulos = df.filter(col("salario").isNull())
```

**Importante**: Use `&` para E, `|` para OU, `~` para NÃO

### Adicionar/Modificar Colunas

```python
# Adiciona nova coluna
df_novo = df.withColumn("salario_dobro", col("salario") * 2)

# Modifica coluna existente
df_novo = df.withColumn("salario", col("salario") * 1.1)  # +10%

# Adiciona coluna constante
df_novo = df.withColumn("pais", F.lit("Brasil"))

# Renomeia coluna
df_novo = df.withColumnRenamed("salario", "salario_mensal")
```

### Remover Duplicatas

```python
# Remove linhas totalmente duplicadas
df_unico = df.dropDuplicates()

# Remove duplicatas baseado em colunas específicas
df_unico = df.dropDuplicates(["id"])

# Remove duplicatas e mantém a mais recente
from pyspark.sql import Window

window = Window.partitionBy("id").orderBy(col("data").desc())
df_unico = df.withColumn("rn", F.row_number().over(window)) \
             .filter(col("rn") == 1) \
             .drop("rn")
```

### Ordenar Dados

```python
# Ordem crescente
df_ordenado = df.orderBy("salario")

# Ordem decrescente
df_ordenado = df.orderBy(col("salario").desc())

# Múltiplas colunas
df_ordenado = df.orderBy(
    col("departamento").asc(),
    col("salario").desc()
)
```

---

## Transformações

### Trabalhar com Textos (Strings)

```python
# UPPERCASE (maiúsculas)
df = df.withColumn("nome_upper", F.upper("nome"))

# lowercase (minúsculas)
df = df.withColumn("nome_lower", F.lower("nome"))

# Remover espaços em branco
df = df.withColumn("nome_limpo", F.trim("nome"))

# Concatenar textos
df = df.withColumn(
    "nome_completo",
    F.concat(col("nome"), F.lit(" "), col("sobrenome"))
)

# Substituir texto
df = df.withColumn(
    "nome_novo",
    F.regexp_replace("nome", "João", "John")
)

# Verificar se contém texto
df = df.withColumn(
    "tem_silva",
    col("nome").contains("Silva")
)

# Extrair substring
df = df.withColumn("iniciais", F.substring("nome", 1, 1))
```

### Trabalhar com Números

```python
# Arredondar
df = df.withColumn("valor_arredondado", F.round("valor", 2))

# Valor absoluto
df = df.withColumn("valor_abs", F.abs("valor"))

# Operações matemáticas
df = df.withColumn("valor_10pct", col("valor") * 1.10)
df = df.withColumn("valor_metade", col("valor") / 2)
df = df.withColumn("valor_quadrado", col("valor") ** 2)

# Raiz quadrada
df = df.withColumn("raiz", F.sqrt("valor"))
```

### Trabalhar com Datas

```python
# String para data
df = df.withColumn("data_formatada", F.to_date("data_string", "yyyy-MM-dd"))

# String para timestamp
df = df.withColumn("timestamp", F.to_timestamp("data_string", "yyyy-MM-dd HH:mm:ss"))

# Extrair componentes
df = df.withColumn("ano", F.year("data"))
df = df.withColumn("mes", F.month("data"))
df = df.withColumn("dia", F.dayofmonth("data"))
df = df.withColumn("dia_semana", F.dayofweek("data"))  # 1=Domingo, 7=Sábado

# Data atual
df = df.withColumn("data_hoje", F.current_date())
df = df.withColumn("timestamp_agora", F.current_timestamp())

# Diferença entre datas (dias)
df = df.withColumn("dias_diferenca", F.datediff("data_fim", "data_inicio"))

# Adicionar dias
df = df.withColumn("data_futura", F.date_add("data", 30))  # +30 dias
df = df.withColumn("data_passada", F.date_sub("data", 7))  # -7 dias

# Formatar data como string
df = df.withColumn("data_br", F.date_format("data", "dd/MM/yyyy"))
```

### Condicionais (IF/ELSE)

```python
# IF simples
df = df.withColumn(
    "categoria",
    F.when(col("valor") > 1000, "Alto")
     .otherwise("Baixo")
)

# IF/ELIF/ELSE
df = df.withColumn(
    "categoria",
    F.when(col("valor") > 2000, "Alto")
     .when(col("valor") > 1000, "Médio")
     .otherwise("Baixo")
)

# IF aninhado
df = df.withColumn(
    "status",
    F.when(
        (col("ativo") == True) & (col("valor") > 1000),
        "Premium Ativo"
    ).when(
        col("ativo") == True,
        "Ativo"
    ).otherwise("Inativo")
)

# CASE WHEN (SQL-like)
df = df.selectExpr(
    "*",
    """
    CASE
        WHEN valor > 2000 THEN 'Alto'
        WHEN valor > 1000 THEN 'Médio'
        ELSE 'Baixo'
    END as categoria
    """
)
```

---

## Agregações

### Agregações Básicas

```python
# Soma
total = df.select(F.sum("valor")).collect()[0][0]

# Média
media = df.select(F.avg("valor")).collect()[0][0]

# Máximo e Mínimo
maximo = df.select(F.max("valor")).collect()[0][0]
minimo = df.select(F.min("valor")).collect()[0][0]

# Contagem
total_linhas = df.count()
total_distintos = df.select(F.countDistinct("cliente_id")).collect()[0][0]
```

### GroupBy (Agrupar por)

```python
# Agrupar e somar
df_grupo = df.groupBy("categoria") \
    .agg(F.sum("valor").alias("total_valor"))

# Múltiplas agregações
df_resumo = df.groupBy("categoria") \
    .agg(
        F.sum("valor").alias("total"),
        F.avg("valor").alias("media"),
        F.count("id").alias("quantidade"),
        F.max("valor").alias("maior_valor"),
        F.min("valor").alias("menor_valor")
    )

# Agrupar por múltiplas colunas
df_grupo = df.groupBy("ano", "mes", "categoria") \
    .agg(F.sum("valor").alias("total"))

# Contar por grupo
df_contagem = df.groupBy("categoria").count()
```

---

## Joins

### Tipos de Join

```
INNER JOIN: Apenas registros que existem em ambos
LEFT JOIN: Todos de A + correspondentes de B
RIGHT JOIN: Todos de B + correspondentes de A
FULL JOIN: Todos de A e B
```

### Exemplos

```python
# Dados de exemplo
df_vendas = spark.createDataFrame([
    (1, 100, 1000),
    (2, 101, 2000),
], ["id_venda", "id_cliente", "valor"])

df_clientes = spark.createDataFrame([
    (100, "João"),
    (101, "Maria"),
    (102, "Pedro"),  # Não tem venda
], ["id_cliente", "nome"])

# INNER JOIN (apenas clientes com vendas)
df_inner = df_vendas.join(
    df_clientes,
    on="id_cliente",
    how="inner"
)

# LEFT JOIN (todas vendas + dados de cliente se existir)
df_left = df_vendas.join(
    df_clientes,
    on="id_cliente",
    how="left"
)

# RIGHT JOIN (todos clientes + vendas se existir)
df_right = df_vendas.join(
    df_clientes,
    on="id_cliente",
    how="right"
)

# Join com colunas de nomes diferentes
df_join = df_vendas.join(
    df_clientes,
    df_vendas.id_cliente == df_clientes.cliente_id,
    how="left"
)

# Join com múltiplas colunas
df_join = df_vendas.join(
    df_produtos,
    (df_vendas.id_produto == df_produtos.id) &
    (df_vendas.ano == df_produtos.ano),
    how="left"
)
```

---

## Funções Úteis

### Window Functions (Cálculos por Grupo)

```python
from pyspark.sql import Window

# Ranking dentro de cada grupo
window = Window.partitionBy("categoria").orderBy(col("valor").desc())

df = df.withColumn("rank", F.rank().over(window))
df = df.withColumn("row_number", F.row_number().over(window))

# Valor anterior/próximo
window = Window.partitionBy("cliente_id").orderBy("data")

df = df.withColumn("valor_anterior", F.lag("valor", 1).over(window))
df = df.withColumn("valor_proximo", F.lead("valor", 1).over(window))

# Acumulado
window = Window.partitionBy("ano").orderBy("mes") \
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)

df = df.withColumn("acumulado_ano", F.sum("valor").over(window))

# Média móvel (3 meses)
window = Window.partitionBy("produto").orderBy("mes") \
    .rowsBetween(-2, 0)  # 2 anteriores + atual

df = df.withColumn("media_movel_3m", F.avg("valor").over(window))
```

### Funções de Array/List

```python
# Criar array
df = df.withColumn("tags", F.array(F.lit("tag1"), F.lit("tag2")))

# Tamanho do array
df = df.withColumn("num_tags", F.size("tags"))

# Explodir array (uma linha por elemento)
df_exploded = df.select("id", F.explode("tags").alias("tag"))

# Verificar se contém elemento
df = df.withColumn("tem_vip", F.array_contains("tags", "VIP"))
```

---

## Exemplos Práticos

### Exemplo 1: Relatório de Vendas Mensais

```python
# Dados de vendas
df_vendas = spark.read.parquet("silver/vendas/")

# Calcula resumo mensal
df_mensal = df_vendas \
    .withColumn("ano", F.year("data_venda")) \
    .withColumn("mes", F.month("data_venda")) \
    .groupBy("ano", "mes") \
    .agg(
        F.sum("valor").alias("total_vendas"),
        F.count("id_venda").alias("num_vendas"),
        F.avg("valor").alias("ticket_medio"),
        F.countDistinct("id_cliente").alias("clientes_unicos")
    ) \
    .orderBy("ano", "mes")

# Mostra resultado
df_mensal.show()
```

### Exemplo 2: Identificar Clientes VIP

```python
# Clientes com mais de R$ 10.000 em vendas
df_clientes_vip = df_vendas \
    .groupBy("id_cliente") \
    .agg(
        F.sum("valor").alias("total_compras"),
        F.count("id_venda").alias("num_compras")
    ) \
    .filter(col("total_compras") > 10000) \
    .withColumn("categoria", F.lit("VIP"))

# Junta com dados cadastrais
df_vip_completo = df_clientes_vip.join(
    df_clientes,
    on="id_cliente",
    how="left"
)

# Salva resultado
df_vip_completo.write \
    .format("delta") \
    .mode("overwrite") \
    .save("gold/clientes_vip/")
```

### Exemplo 3: Calcular Variação Mês a Mês

```python
from pyspark.sql import Window

# Ordena por data
window = Window.partitionBy("produto_id").orderBy("ano", "mes")

df_evolucao = df_vendas_mensais \
    .withColumn("vendas_mes_anterior", F.lag("total_vendas").over(window)) \
    .withColumn(
        "variacao_percentual",
        ((col("total_vendas") - col("vendas_mes_anterior")) /
         col("vendas_mes_anterior") * 100)
    ) \
    .withColumn(
        "tendencia",
        F.when(col("variacao_percentual") > 5, "Crescimento")
         .when(col("variacao_percentual") < -5, "Queda")
         .otherwise("Estável")
    )

df_evolucao.show()
```

---

## Dicas e Truques

### 1. Debug: Ver Dados Intermediários

```python
# Mostra sempre após transformações importantes
df = df.filter(col("valor") > 100)
df.show(5)  # ⬅️ Adicione isso para debug

df = df.withColumn("nova_coluna", ...)
print(f"Total de linhas: {df.count()}")  # ⬅️ Verifica contagem
```

### 2. Performance: Cache

```python
# Se vai usar o mesmo DataFrame várias vezes
df_clientes.cache()

resultado1 = df_clientes.filter(...)
resultado2 = df_clientes.join(...)
resultado3 = df_clientes.groupBy(...)

# Libera cache quando terminar
df_clientes.unpersist()
```

### 3. Salvar Resultados

```python
# Parquet (rápido, comprimido)
df.write.mode("overwrite").parquet("caminho/")

# Delta (ACID, versionamento)
df.write.format("delta").mode("overwrite").save("caminho/")

# CSV (para compartilhar)
df.write \
    .option("header", "true") \
    .mode("overwrite") \
    .csv("caminho/")

# Com particionamento
df.write \
    .partitionBy("ano", "mes") \
    .parquet("caminho/")
```

### 4. Tratamento de Erros

```python
try:
    df = spark.read.parquet("caminho/")
    df = df.filter(col("valor") > 0)
    df.write.mode("overwrite").parquet("saida/")
    print("✅ Sucesso!")

except Exception as e:
    print(f"❌ Erro: {e}")
    # Logging, notificação, etc.
```

### 5. SQL vs PySpark

Você pode usar SQL se preferir:

```python
# Registra DataFrame como tabela temporária
df.createOrReplaceTempView("vendas")

# Usa SQL
resultado = spark.sql("""
    SELECT
        ano,
        mes,
        SUM(valor) as total
    FROM vendas
    WHERE valor > 1000
    GROUP BY ano, mes
    ORDER BY ano, mes
""")

resultado.show()
```

---

## 📚 Próximos Passos

1. Pratique com os templates em `notebooks/templates/`
2. Execute os exemplos célula por célula
3. Consulte o guia de debugging: `docs/04_DEBUGGING.md`
4. Leia sobre padrões do projeto: `docs/03_PADROES_PROJETO.md`

---

## 🆘 Mensagens de Erro Comuns

### "AnalysisException: cannot resolve"
**Problema**: Coluna não existe
**Solução**: Verifique nome da coluna com `df.columns` ou `df.printSchema()`

### "Py4JJavaError"
**Problema**: Erro do Spark (Java)
**Solução**: Leia a mensagem completa, geralmente indica problema com tipos ou nulos

### "DataFrame object has no attribute"
**Problema**: Método não existe
**Solução**: Verifique documentação do PySpark ou veja exemplos acima

---

**Última atualização**: 2024
**Versão**: 1.0
