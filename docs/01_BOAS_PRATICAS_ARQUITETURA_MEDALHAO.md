# 🏅 Boas Práticas - Arquitetura Medalhão

## 📚 Índice
1. [O que é Arquitetura Medalhão](#o-que-é-arquitetura-medalhão)
2. [As Três Camadas](#as-três-camadas)
3. [Princípios Fundamentais](#princípios-fundamentais)
4. [Boas Práticas por Camada](#boas-práticas-por-camada)
5. [Qualidade de Dados](#qualidade-de-dados)
6. [Performance e Otimização](#performance-e-otimização)
7. [Governança e Auditoria](#governança-e-auditoria)
8. [O que Fazer e O que Não Fazer](#o-que-fazer-e-o-que-não-fazer)

---

## O que é Arquitetura Medalhão

A **Arquitetura Medalhão** (Medallion Architecture) é um padrão de design de data lakehouse que organiza dados em três camadas progressivas de qualidade:

```
📥 BRONZE    ➡️    🔧 SILVER    ➡️    💎 GOLD    ➡️    📊 POWER BI
(Bruto)           (Refinado)         (Curado)         (Visualização)
```

### Por que usar?

✅ **Organização clara**: Dados organizados por nível de qualidade
✅ **Rastreabilidade**: Histórico completo desde a origem
✅ **Flexibilidade**: Permite reprocessamento a qualquer momento
✅ **Performance**: Otimizações progressivas
✅ **Qualidade**: Validações em cada etapa

---

## As Três Camadas

### 🥉 Bronze - Dados Brutos

**Objetivo**: Armazenar dados exatamente como vieram da origem

**Características**:
- Dados sem transformações
- Todos os registros são mantidos (inclusive duplicados)
- Formato: geralmente Parquet
- Serve como backup dos dados originais

**Exemplo**:
```
bronze/producao/vendas/
  ├── ano=2024/
  │   ├── mes=01/
  │   │   └── parte-00001.parquet
  │   └── mes=02/
  │       └── parte-00001.parquet
```

### 🥈 Silver - Dados Refinados

**Objetivo**: Dados limpos, validados e padronizados

**Características**:
- Duplicatas removidas
- Dados validados e limpos
- Formato padronizado (datas, textos, etc.)
- Formato: Delta Lake (para ACID transactions)
- Pronto para análises e transformações

**Exemplo**:
```
silver/producao/vendas/
  ├── ano=2024/
  │   └── mes=01/
  │       └── delta files
```

### 🥇 Gold - Dados Curados

**Objetivo**: Agregações e métricas prontas para consumo

**Características**:
- Dados agregados por dimensões de negócio
- KPIs e métricas calculadas
- Modelos dimensionais (fato e dimensão)
- Formato: Delta Lake otimizado
- Otimizado para consultas do Power BI

**Exemplo**:
```
gold/producao/fato_vendas_mensais/
  ├── ano=2024/
  │   └── delta files (otimizados com Z-ORDER)
```

---

## Princípios Fundamentais

### 1. Idempotência
**O QUE É**: Executar o mesmo processo múltiplas vezes produz o mesmo resultado

**POR QUE IMPORTA**: Permite reprocessamento seguro dos dados

**COMO APLICAR**:
```python
# ✅ BOM: Usa overwrite com mesmo resultado
df.write.mode("overwrite").save(path)

# ❌ RUIM: Append sem controle de duplicatas
df.write.mode("append").save(path)
```

### 2. Imutabilidade do Bronze
**O QUE É**: Dados na camada Bronze nunca são modificados

**POR QUE IMPORTA**: Garante rastreabilidade e permite reprocessamento

**COMO APLICAR**:
- Bronze sempre em `append` ou `overwrite` completo
- Nunca deleta ou modifica registros Bronze
- Mantém histórico completo

### 3. Separação de Responsabilidades
**O QUE É**: Cada camada tem uma função específica

**POR QUE IMPORTA**: Facilita manutenção e debugging

**COMO APLICAR**:
- Bronze: apenas ingestão
- Silver: apenas limpeza e padronização
- Gold: apenas agregações e métricas

### 4. Schema Evolution
**O QUE É**: Capacidade de evoluir o schema dos dados

**POR QUE IMPORTA**: Adapta-se a mudanças nas fontes de dados

**COMO APLICAR**:
```python
# Delta Lake permite evolução de schema
df.write \
  .format("delta") \
  .option("mergeSchema", "true") \
  .mode("append") \
  .save(path)
```

---

## Boas Práticas por Camada

### 🥉 Bronze - Boas Práticas

#### ✅ O QUE FAZER

1. **Mantenha dados originais intactos**
   ```python
   # Salve exatamente como veio da fonte
   df_raw.write.mode("append").parquet(bronze_path)
   ```

2. **Adicione metadados de auditoria**
   ```python
   df_bronze = df_raw \
       .withColumn("bronze_ingestion_date", F.current_timestamp()) \
       .withColumn("bronze_source", F.lit("nome_fonte"))
   ```

3. **Use particionamento por data**
   ```python
   df_bronze.write \
       .partitionBy("ano", "mes", "dia") \
       .parquet(bronze_path)
   ```

4. **Implemente carga incremental quando possível**
   ```python
   # Apenas dados novos
   df_new = df.filter(f"data_atualizacao > '{ultimo_processamento}'")
   ```

#### ❌ O QUE NÃO FAZER

1. ❌ Transformar ou limpar dados
2. ❌ Remover duplicatas
3. ❌ Modificar tipos de dados
4. ❌ Deletar dados históricos
5. ❌ Aplicar regras de negócio

---

### 🥈 Silver - Boas Práticas

#### ✅ O QUE FAZER

1. **Use Delta Lake**
   ```python
   df.write \
       .format("delta") \
       .mode("overwrite") \
       .save(silver_path)
   ```

2. **Remova duplicatas de forma determinística**
   ```python
   # Mantém registro mais recente
   window = Window.partitionBy("id").orderBy(F.desc("data_atualizacao"))
   df_dedup = df.withColumn("rn", F.row_number().over(window)) \
                .filter(F.col("rn") == 1) \
                .drop("rn")
   ```

3. **Padronize formatos**
   ```python
   df_clean = df \
       .withColumn("data", F.to_timestamp("data", "yyyy-MM-dd")) \
       .withColumn("nome", F.upper(F.trim("nome")))
   ```

4. **Valide qualidade**
   ```python
   # Remove registros inválidos
   df_valid = df.filter(
       F.col("id").isNotNull() &
       F.col("valor") >= 0
   )
   ```

5. **Documente transformações**
   ```python
   # Comente cada transformação importante
   # Regra de Negócio: Valores negativos são inválidos
   df = df.filter(F.col("valor") >= 0)
   ```

#### ❌ O QUE NÃO FAZER

1. ❌ Fazer agregações (isso é para Gold)
2. ❌ Criar métricas calculadas complexas
3. ❌ Remover colunas originais importantes
4. ❌ Modificar dados Bronze

---

### 🥇 Gold - Boas Práticas

#### ✅ O QUE FAZER

1. **Crie agregações com granularidade adequada**
   ```python
   df_gold = df_silver.groupBy("ano", "mes", "produto") \
       .agg(
           F.sum("valor").alias("total_vendas"),
           F.avg("quantidade").alias("media_quantidade"),
           F.count("id").alias("numero_vendas")
       )
   ```

2. **Otimize para consultas do Power BI**
   ```python
   # Z-ORDER nas colunas mais filtradas
   spark.sql(f"""
       OPTIMIZE delta.`{gold_path}`
       ZORDER BY (ano, mes, id_cliente)
   """)
   ```

3. **Crie modelos estrela (Star Schema)**
   ```
   Tabela Fato: fato_vendas
   ├── id_cliente (FK)
   ├── id_produto (FK)
   ├── id_tempo (FK)
   ├── valor_venda
   └── quantidade

   Dimensões:
   ├── dim_clientes
   ├── dim_produtos
   └── dim_tempo
   ```

4. **Calcule métricas de negócio**
   ```python
   df_gold = df_gold \
       .withColumn("ticket_medio", F.col("total_vendas") / F.col("numero_vendas")) \
       .withColumn("variacao_mes_anterior",
           (F.col("total_vendas") - F.col("total_vendas_mes_anterior")) /
           F.col("total_vendas_mes_anterior") * 100
       )
   ```

5. **Mantenha granularidade apropriada**
   - Dados mensais para análises executivas
   - Dados diários para análises operacionais
   - Dados horários apenas se necessário

#### ❌ O QUE NÃO FAZER

1. ❌ Criar granularidade muito fina desnecessariamente
2. ❌ Duplicar dados de Silver sem agregação
3. ❌ Criar tabelas Gold sem otimização
4. ❌ Misturar múltiplos assuntos em uma tabela

---

## Qualidade de Dados

### Validações Essenciais

#### 1. Completude
```python
# Verifica % de nulos
total = df.count()
nulos = df.filter(F.col("campo_importante").isNull()).count()
percentual_nulo = (nulos / total) * 100

if percentual_nulo > 5:  # Threshold de 5%
    print(f"⚠️ ALERTA: {percentual_nulo}% de nulos!")
```

#### 2. Unicidade
```python
# Verifica duplicatas
total = df.count()
unicos = df.dropDuplicates(["id"]).count()

if total != unicos:
    print(f"⚠️ {total - unicos} duplicatas encontradas!")
```

#### 3. Validade
```python
# Verifica ranges válidos
invalidos = df.filter(
    (F.col("idade") < 0) |
    (F.col("idade") > 120)
).count()

if invalidos > 0:
    print(f"⚠️ {invalidos} valores inválidos!")
```

#### 4. Consistência
```python
# Verifica relacionamentos
clientes_sem_vendas = df_clientes \
    .join(df_vendas, on="id_cliente", how="left_anti")

if clientes_sem_vendas.count() > 0:
    print("⚠️ Clientes sem vendas encontrados")
```

---

## Performance e Otimização

### 1. Particionamento

**Bronze e Silver**: Particione por data de ingestão
```python
df.write \
    .partitionBy("ano", "mes") \
    .parquet(path)
```

**Gold**: Particione por dimensão de tempo
```python
df.write \
    .partitionBy("ano") \
    .format("delta") \
    .save(path)
```

**Regras**:
- ✅ Use 50-1000 partições
- ❌ Evite too many small files (<128MB)
- ❌ Evite too many partitions (>10.000)

### 2. Formato de Arquivo

| Camada | Formato Recomendado | Por quê? |
|--------|-------------------|----------|
| Bronze | Parquet | Compressão eficiente, schema preservado |
| Silver | Delta Lake | ACID, time travel, schema evolution |
| Gold | Delta Lake | Otimizações, Z-ORDER, melhor performance |

### 3. Otimizações Delta

```python
# OPTIMIZE: Compacta arquivos pequenos
spark.sql(f"OPTIMIZE delta.`{path}`")

# Z-ORDER: Otimiza para filtros específicos
spark.sql(f"OPTIMIZE delta.`{path}` ZORDER BY (ano, mes, cliente_id)")

# VACUUM: Remove arquivos antigos (CUIDADO!)
spark.sql(f"VACUUM delta.`{path}` RETAIN 168 HOURS")  # 7 dias
```

### 4. Caching

```python
# Cache dataframes usados múltiplas vezes
df_clientes.cache()

# Use depois
result1 = df_clientes.filter(...)
result2 = df_clientes.join(...)

# Libere quando terminar
df_clientes.unpersist()
```

---

## Governança e Auditoria

### 1. Logging Obrigatório

Sempre registre:
- ✅ Data/hora de execução
- ✅ Número de registros processados
- ✅ Erros e warnings
- ✅ Duração da execução
- ✅ Usuário/job que executou

```python
logger.start(fonte="vendas", tipo_carga="incremental")
# ... processamento ...
logger.end(status="success")
```

### 2. Nomenclatura Padronizada

**Tabelas**:
- Bronze: `bronze_<area>_<fonte>`
- Silver: `silver_<area>_<fonte>`
- Gold: `gold_<area>_<assunto>` ou `fato_<assunto>`, `dim_<assunto>`

**Colunas**:
- Lowercase com underscores: `id_cliente`, `data_venda`
- Prefixo de camada: `bronze_ingestion_date`, `silver_processing_date`

### 3. Documentação

Cada fonte de dados deve ter:
```yaml
# Exemplo em sources.yaml
vendas:
  descricao: "Dados de vendas do ERP"
  origem: "Synapse - DW_Vendas.dbo.fato_vendas"
  responsavel: "equipe.dados@empresa.com"
  sla_atualizacao: "Diário - 06:00"
  colunas_chave: ["id_venda"]
  carga: "incremental"
  coluna_incremental: "data_atualizacao"
```

---

## O que Fazer e O que Não Fazer

### ✅ SEMPRE FAÇA

1. ✅ **Use controle de versão** (Git) para todos os notebooks
2. ✅ **Teste com dados pequenos** antes de rodar em produção
3. ✅ **Documente transformações** e regras de negócio
4. ✅ **Valide qualidade** em cada camada
5. ✅ **Monitore execuções** através de logs
6. ✅ **Use nomenclatura padronizada**
7. ✅ **Particione adequadamente**
8. ✅ **Otimize tabelas Gold** com OPTIMIZE e Z-ORDER
9. ✅ **Implemente tratamento de erros**
10. ✅ **Mantenha Bronze imutável**

### ❌ NUNCA FAÇA

1. ❌ **Transformar dados na camada Bronze**
2. ❌ **Deletar dados Bronze**
3. ❌ **Fazer agregações na camada Silver**
4. ❌ **Commitar credenciais no Git**
5. ❌ **Rodar VACUUM com retention menor que 7 dias**
6. ❌ **Criar tabelas Gold sem otimização**
7. ❌ **Ignorar erros de qualidade**
8. ❌ **Processar dados em produção sem testar**
9. ❌ **Usar `mode("append")` sem controle de duplicatas**
10. ❌ **Criar partições demais (>10.000)**

---

## 📚 Recursos Adicionais

- Databricks: [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- Delta Lake: [Documentação Oficial](https://docs.delta.io/)
- Guia de Iniciantes deste projeto: `docs/02_GUIA_INICIANTES.md`
- Padrões do Projeto: `docs/03_PADROES_PROJETO.md`

---

## 🆘 Precisa de Ajuda?

1. Consulte os templates em `notebooks/templates/`
2. Veja exemplos em `notebooks/bronze/`, `silver/`, `gold/`
3. Leia o guia de debugging: `docs/04_DEBUGGING.md`
4. Entre em contato com a equipe de dados

---

**Última atualização**: 2024
**Versão**: 1.0
