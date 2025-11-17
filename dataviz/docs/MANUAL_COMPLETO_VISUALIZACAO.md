# 📊 Manual Completo de Visualização de Dados
## Do Básico ao Avançado - Guia Prático com Exemplos Prontos

---

## 🎯 Sobre Este Manual

Este é um **guia prático e completo** com exemplos de código prontos para **copiar e colar**.

**Objetivo**: Capacitar toda a equipe a criar visualizações profissionais, mesmo sem experiência prévia em programação.

**Como usar**:
1. Encontre o tipo de gráfico que você precisa
2. Copie o código completo
3. Adapte os dados para seu cenário
4. Execute e veja o resultado!

---

# 📑 ÍNDICE

## Parte 1: Fundamentos
- [1.1 Configuração Inicial](#11-configuração-inicial)
- [1.2 Estrutura Básica de um Gráfico](#12-estrutura-básica-de-um-gráfico)
- [1.3 Paleta de Cores](#13-paleta-de-cores)

## Parte 2: Gráficos Básicos
- [2.1 Gráfico de Linhas](#21-gráfico-de-linhas)
- [2.2 Gráfico de Barras](#22-gráfico-de-barras)
- [2.3 Gráfico de Pizza](#23-gráfico-de-pizza)
- [2.4 Gráfico de Área](#24-gráfico-de-área)

## Parte 3: Gráficos Intermediários
- [3.1 Scatter Plot (Dispersão)](#31-scatter-plot-dispersão)
- [3.2 Box Plot](#32-box-plot)
- [3.3 Histograma](#33-histograma)
- [3.4 Heatmap](#34-heatmap)
- [3.5 Barras Empilhadas](#35-barras-empilhadas)

## Parte 4: Gráficos Avançados
- [4.1 Gráfico Combo (Dual-Axis)](#41-gráfico-combo-dual-axis)
- [4.2 Waterfall Chart](#42-waterfall-chart)
- [4.3 Treemap](#43-treemap)
- [4.4 Sunburst](#44-sunburst)
- [4.5 Gauge (Velocímetro)](#45-gauge-velocímetro)
- [4.6 Violin Plot](#46-violin-plot)
- [4.7 Radar Chart](#47-radar-chart)
- [4.8 Gráfico 3D](#48-gráfico-3d)
- [4.9 Funil](#49-funil)
- [4.10 Análise de Pareto](#410-análise-de-pareto)

## Parte 5: Templates Reutilizáveis
- [5.1 Template de Dashboard Completo](#51-template-de-dashboard-completo)
- [5.2 Template de KPI Cards](#52-template-de-kpi-cards)
- [5.3 Template de Tabelas](#53-template-de-tabelas)

## Parte 6: Boas Práticas
- [6.1 Escolha do Gráfico Certo](#61-escolha-do-gráfico-certo)
- [6.2 Cores e Acessibilidade](#62-cores-e-acessibilidade)
- [6.3 Títulos e Legendas](#63-títulos-e-legendas)

---

# PARTE 1: FUNDAMENTOS

## 1.1 Configuração Inicial

### Instalação de Pacotes

```bash
# Instala todos os pacotes necessários
pip install plotly pandas numpy scipy dash
```

### Imports Padrão

**Copie este bloco no início de todos os seus scripts:**

```python
# ============================================================================
# IMPORTS NECESSÁRIOS
# ============================================================================

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Para análises estatísticas
from scipy import stats

# Para dashboards (opcional)
import dash
from dash import dcc, html, dash_table
```

### Configuração de Cores Corporativas

**Defina suas cores no início do arquivo:**

```python
# ============================================================================
# PALETA DE CORES CORPORATIVA
# ============================================================================

# Cores principais (ajuste para sua empresa)
PRIMARY_COLOR = '#2E7D32'      # Verde escuro (cana)
SUCCESS_COLOR = '#43A047'      # Verde claro (sucesso)
WARNING_COLOR = '#FFA726'      # Laranja (atenção)
DANGER_COLOR = '#E53935'       # Vermelho (perigo)
INFO_COLOR = '#29B6F6'         # Azul (informação)

# Cores de fundo
BACKGROUND = '#F5F5F5'         # Cinza claro
CARD_BG = '#FFFFFF'            # Branco

# Cores de texto
TEXT_DARK = '#212121'          # Texto principal
TEXT_LIGHT = '#757575'         # Texto secundário
```

---

## 1.2 Estrutura Básica de um Gráfico

**Todo gráfico Plotly segue esta estrutura:**

```python
# ============================================================================
# ESTRUTURA BÁSICA DE UM GRÁFICO
# ============================================================================

# 1. Preparar os dados
dados = {
    'categorias': ['A', 'B', 'C', 'D'],
    'valores': [10, 25, 15, 30]
}
df = pd.DataFrame(dados)

# 2. Criar a figura
fig = go.Figure()

# 3. Adicionar os dados (trace)
fig.add_trace(go.Bar(
    x=df['categorias'],
    y=df['valores'],
    marker_color=PRIMARY_COLOR
))

# 4. Personalizar o layout
fig.update_layout(
    title="Título do Gráfico",
    xaxis_title="Eixo X",
    yaxis_title="Eixo Y",
    plot_bgcolor='white',      # Fundo do gráfico
    paper_bgcolor='white',     # Fundo da área toda
    font=dict(
        family="Segoe UI",
        size=12,
        color=TEXT_DARK
    )
)

# 5. Exibir
fig.show()
```

**💡 Explicação linha por linha:**

- **Linha 4-7**: Criamos um dicionário com nossos dados
- **Linha 8**: Convertemos para DataFrame (facilita manipulação)
- **Linha 11**: Criamos uma figura vazia
- **Linha 14-17**: Adicionamos um gráfico de barras à figura
- **Linha 20-29**: Personalizamos títulos, cores e fontes
- **Linha 32**: Mostramos o gráfico

---

## 1.3 Paleta de Cores

### Quando Usar Cada Cor

```python
# ============================================================================
# GUIA DE USO DE CORES
# ============================================================================

# ✅ VERDE (SUCCESS) - Use para:
# - Valores positivos
# - Metas atingidas
# - Status "OK"
# - Crescimento
cor_positivo = SUCCESS_COLOR

# ⚠️ AMARELO/LARANJA (WARNING) - Use para:
# - Valores próximos ao limite
# - Atenção necessária
# - Médio desempenho
cor_atencao = WARNING_COLOR

# ❌ VERMELHO (DANGER) - Use para:
# - Valores negativos
# - Metas não atingidas
# - Problemas/erros
# - Queda
cor_negativo = DANGER_COLOR

# ℹ️ AZUL (INFO) - Use para:
# - Informações neutras
# - Dados de contexto
# - Valores de referência
cor_neutro = INFO_COLOR

# 🎨 VERDE ESCURO (PRIMARY) - Use para:
# - Destaque principal
# - Títulos importantes
# - Elementos da marca
cor_principal = PRIMARY_COLOR
```

### Exemplo: Colorindo por Condição

```python
# ============================================================================
# EXEMPLO: CORES CONDICIONAIS
# ============================================================================

# Dados de TCH por talhão
df = pd.DataFrame({
    'talhao': ['T001', 'T002', 'T003', 'T004', 'T005'],
    'tch': [92, 75, 88, 65, 95]  # Toneladas por hectare
})

# Define cor baseada no desempenho
def definir_cor(tch):
    """
    Retorna cor baseada no valor de TCH.

    Regra:
    - TCH >= 90: Verde (excelente)
    - TCH >= 80: Amarelo (bom)
    - TCH < 80: Vermelho (ruim)
    """
    if tch >= 90:
        return SUCCESS_COLOR
    elif tch >= 80:
        return WARNING_COLOR
    else:
        return DANGER_COLOR

# Aplica a função
df['cor'] = df['tch'].apply(definir_cor)

# Cria gráfico com cores condicionais
fig = go.Figure(go.Bar(
    x=df['talhao'],
    y=df['tch'],
    marker_color=df['cor'],  # ← Usa as cores definidas
    text=df['tch'],
    textposition='outside'
))

fig.update_layout(
    title="TCH por Talhão (Colorido por Performance)",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**🎯 Resultado**: Barras verdes para valores excelentes (≥90), amarelas para bons (80-89), vermelhas para ruins (<80).

---

# PARTE 2: GRÁFICOS BÁSICOS

## 2.1 Gráfico de Linhas

### Exemplo 1: Linha Simples

**Use para**: Mostrar tendência ao longo do tempo

```python
# ============================================================================
# GRÁFICO DE LINHAS SIMPLES
# ============================================================================

# Dados: Área plantada por mês
dados = {
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'area_ha': [120, 150, 180, 200, 190, 170]
}
df = pd.DataFrame(dados)

# Cria gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['area_ha'],
    mode='lines+markers',      # Linha + pontos
    name='Área Plantada',
    line=dict(
        color=SUCCESS_COLOR,    # Cor da linha
        width=3                 # Espessura da linha
    ),
    marker=dict(
        size=8,                 # Tamanho dos pontos
        color=SUCCESS_COLOR,
        line=dict(width=2, color='white')  # Borda branca nos pontos
    )
))

fig.update_layout(
    title={
        'text': "Evolução da Área Plantada",
        'font': {'size': 20, 'color': TEXT_DARK}
    },
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    hovermode='x unified',      # Tooltip unificado
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI", size=12)
)

fig.show()
```

**💡 Explicação**:
- `mode='lines+markers'`: Mostra linha E pontos (use só `'lines'` para linha sem pontos)
- `width=3`: Linha mais grossa (padrão é 2)
- `size=8`: Pontos maiores (padrão é 6)
- `hovermode='x unified'`: Ao passar mouse, mostra todos valores daquele X

---

### Exemplo 2: Múltiplas Linhas

**Use para**: Comparar várias séries temporais

```python
# ============================================================================
# MÚLTIPLAS LINHAS (COMPARAÇÃO)
# ============================================================================

# Dados: Área planejada vs realizada
df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'planejado': [150, 160, 170, 180, 175, 165],
    'realizado': [145, 162, 168, 185, 172, 170]
})

fig = go.Figure()

# Linha 1: Planejado
fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['planejado'],
    mode='lines',
    name='Planejado',
    line=dict(
        color=WARNING_COLOR,
        width=2,
        dash='dash'            # Linha tracejada
    )
))

# Linha 2: Realizado
fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['realizado'],
    mode='lines+markers',
    name='Realizado',
    line=dict(
        color=SUCCESS_COLOR,
        width=3
    ),
    marker=dict(size=6)
))

fig.update_layout(
    title="Planejado vs Realizado",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(
        orientation="h",        # Legenda horizontal
        yanchor="bottom",
        y=-0.2,                # Abaixo do gráfico
        xanchor="center",
        x=0.5
    )
)

fig.show()
```

**💡 Dicas**:
- `dash='dash'`: Linha tracejada (outras opções: `'dot'`, `'dashdot'`)
- Use tracejado para valores de referência/meta
- Use linha sólida para valores reais

---

### Exemplo 3: Linha com Área Preenchida

**Use para**: Destacar magnitude de valores

```python
# ============================================================================
# LINHA COM ÁREA PREENCHIDA
# ============================================================================

df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'area_acumulada': [120, 270, 450, 650, 840, 1010]
})

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['area_acumulada'],
    mode='lines',
    fill='tozeroy',            # Preenche até o zero
    fillcolor='rgba(67, 160, 71, 0.3)',  # Verde transparente
    line=dict(
        color=SUCCESS_COLOR,
        width=2
    ),
    name='Área Acumulada'
))

fig.update_layout(
    title="Área Plantada Acumulada",
    xaxis_title="Mês",
    yaxis_title="Área Acumulada (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Explicação**:
- `fill='tozeroy'`: Preenche área entre a linha e o eixo Y=0
- `rgba(67, 160, 71, 0.3)`: Cor RGB com transparência (0.3 = 30% opaco)
- Outras opções de fill: `'tonexty'` (preenche até próxima linha), `'toself'` (fecha forma)

---

## 2.2 Gráfico de Barras

### Exemplo 1: Barras Verticais Simples

**Use para**: Comparar valores entre categorias

```python
# ============================================================================
# BARRAS VERTICAIS SIMPLES
# ============================================================================

# Dados: Área por variedade de cana
df = pd.DataFrame({
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250'],
    'area_ha': [3500, 2800, 2200, 1500]
})

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['variedade'],
    y=df['area_ha'],
    marker_color=PRIMARY_COLOR,
    text=df['area_ha'],       # Mostra valores
    textposition='outside',   # Posição do texto (outside = acima)
    texttemplate='%{text:,.0f} ha',  # Formato: número com separador de milhar
    hovertemplate='<b>%{x}</b><br>Área: %{y:,.0f} ha<extra></extra>'
))

fig.update_layout(
    title="Área por Variedade de Cana",
    xaxis_title="Variedade",
    yaxis_title="Área (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    showlegend=False           # Não mostra legenda (só 1 série)
)

fig.show()
```

**💡 Explicação**:
- `text=df['area_ha']`: Usa valores da coluna como rótulo
- `textposition='outside'`: Outras opções: `'inside'`, `'auto'`
- `texttemplate='%{text:,.0f} ha'`: Formata número (`,` = separador de milhar, `.0f` = 0 casas decimais)
- `<extra></extra>`: Remove box secundário do tooltip

---

### Exemplo 2: Barras Horizontais

**Use para**: Categorias com nomes longos ou muitas categorias

```python
# ============================================================================
# BARRAS HORIZONTAIS
# ============================================================================

df = pd.DataFrame({
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579',
                  'CTC20', 'RB975935', 'IACSP95-5000'],
    'area_ha': [3500, 2800, 2200, 1500, 1000, 800, 600, 400]
})

# Ordena do maior para o menor
df = df.sort_values('area_ha', ascending=True)  # True = crescente (para horizontal)

fig = go.Figure()

fig.add_trace(go.Bar(
    y=df['variedade'],        # Y em horizontal!
    x=df['area_ha'],          # X em horizontal!
    orientation='h',          # Horizontal
    marker_color=SUCCESS_COLOR,
    text=df['area_ha'],
    textposition='outside',
    texttemplate='%{text:,.0f}'
))

fig.update_layout(
    title="Área por Variedade (Ranking)",
    yaxis_title="Variedade",
    xaxis_title="Área (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400                # Altura em pixels
)

fig.show()
```

**💡 Dicas**:
- Barras horizontais são melhores para > 6 categorias
- Use `ascending=True` para ordem crescente (maior no topo)
- Ajuste `height` baseado no número de categorias (50-60px por barra)

---

### Exemplo 3: Barras com Cores Condicionais

**Use para**: Destacar valores bom/médio/ruim

```python
# ============================================================================
# BARRAS COM CORES CONDICIONAIS
# ============================================================================

df = pd.DataFrame({
    'talhao': ['T001', 'T002', 'T003', 'T004', 'T005', 'T006'],
    'tch': [92, 75, 88, 65, 95, 82]
})

# Define cores baseadas no TCH
cores = []
for tch in df['tch']:
    if tch >= 90:
        cores.append(SUCCESS_COLOR)    # Verde
    elif tch >= 80:
        cores.append(WARNING_COLOR)    # Amarelo
    else:
        cores.append(DANGER_COLOR)     # Vermelho

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['talhao'],
    y=df['tch'],
    marker_color=cores,        # Lista de cores
    text=df['tch'],
    textposition='outside',
    texttemplate='%{text:.0f}',
    hovertemplate='<b>%{x}</b><br>TCH: %{y:.1f} t/ha<br>' +
                  '<i>Meta: 90 t/ha</i><extra></extra>'
))

# Adiciona linha de meta
fig.add_hline(
    y=90,                      # Valor da linha horizontal
    line_dash="dash",
    line_color="black",
    annotation_text="Meta",
    annotation_position="right"
)

fig.update_layout(
    title="TCH por Talhão (Colorido por Performance)",
    xaxis_title="Talhão",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Recursos avançados**:
- `add_hline()`: Adiciona linha horizontal (meta/referência)
- `add_vline()`: Adiciona linha vertical
- HTML em tooltip: `<b>` (negrito), `<i>` (itálico), `<br>` (quebra linha)

---

## 2.3 Gráfico de Pizza

### Exemplo 1: Pizza Básica

**Use para**: Mostrar proporções de um todo (máximo 5-6 categorias)

```python
# ============================================================================
# GRÁFICO DE PIZZA BÁSICO
# ============================================================================

df = pd.DataFrame({
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'Outras'],
    'area_ha': [3500, 2800, 2200, 1500, 1000]
})

fig = go.Figure()

fig.add_trace(go.Pie(
    labels=df['variedade'],
    values=df['area_ha'],
    marker=dict(
        colors=[PRIMARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, INFO_COLOR, '#999']
    ),
    textinfo='label+percent',  # Mostra nome e percentual
    textposition='auto',       # Posição automática
    hovertemplate='<b>%{label}</b><br>' +
                  'Área: %{value:,.0f} ha<br>' +
                  'Percentual: %{percent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição de Área por Variedade",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

### Exemplo 2: Donut Chart (Mais Moderno)

**Use para**: Mesma função da pizza, porém mais elegante

```python
# ============================================================================
# DONUT CHART (PIZZA COM BURACO)
# ============================================================================

df = pd.DataFrame({
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'Outras'],
    'percentual': [31.8, 25.5, 20.0, 13.6, 9.1]
})

fig = go.Figure()

fig.add_trace(go.Pie(
    labels=df['variedade'],
    values=df['percentual'],
    hole=0.4,                  # Tamanho do buraco (0-1, onde 0=pizza, 1=anel)
    marker=dict(
        colors=[PRIMARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, INFO_COLOR, '#999'],
        line=dict(color='white', width=2)  # Borda branca entre fatias
    ),
    textinfo='label+percent',
    textfont=dict(size=12),
    pull=[0.1, 0, 0, 0, 0]    # "Puxa" primeira fatia para fora
))

fig.update_layout(
    title="Distribuição de Variedades (%)",
    showlegend=True,
    legend=dict(
        orientation="v",       # Vertical
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.1                 # À direita do gráfico
    ),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Dicas**:
- `hole=0.4`: Buraco de 40% (experimente valores entre 0.3 e 0.5)
- `pull=[0.1, ...]`: Lista com valores para "puxar" cada fatia (0 = normal, 0.1 = 10% para fora)
- Donut é preferível à pizza tradicional (mais moderno)

---

### ⚠️ IMPORTANTE: Quando NÃO Usar Pizza

**Evite pizza/donut quando:**
- Mais de 6 categorias → Use barras horizontais
- Comparar valores precisos → Use barras
- Mostrar tendência → Use linhas

```python
# ============================================================================
# ALTERNATIVA À PIZZA: BARRAS HORIZONTAIS
# ============================================================================
# Use isto ao invés de pizza quando tiver muitas categorias!

df = pd.DataFrame({
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579',
                  'CTC20', 'RB975935', 'IACSP95'],
    'percentual': [31.8, 25.5, 20.0, 13.6, 9.1, 5.2, 3.8, 1.0]
})

df = df.sort_values('percentual', ascending=True)

fig = go.Figure()

fig.add_trace(go.Bar(
    y=df['variedade'],
    x=df['percentual'],
    orientation='h',
    marker_color=SUCCESS_COLOR,
    text=df['percentual'],
    texttemplate='%{text:.1f}%',
    textposition='outside'
))

fig.update_layout(
    title="Distribuição de Variedades (%) - Formato Correto",
    xaxis_title="Percentual (%)",
    yaxis_title="Variedade",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

## 2.4 Gráfico de Área

### Exemplo 1: Área Simples

**Use para**: Mostrar magnitude acumulada ao longo do tempo

```python
# ============================================================================
# GRÁFICO DE ÁREA SIMPLES
# ============================================================================

df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'area_acumulada': [120, 270, 450, 650, 840, 1010]
})

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['area_acumulada'],
    mode='lines',
    fill='tozeroy',           # Preenche até zero
    fillcolor='rgba(46, 125, 50, 0.2)',  # Verde transparente
    line=dict(
        color=PRIMARY_COLOR,
        width=2
    ),
    name='Área Acumulada',
    hovertemplate='<b>%{x}</b><br>Acumulado: %{y:,.0f} ha<extra></extra>'
))

fig.update_layout(
    title="Área Plantada Acumulada",
    xaxis_title="Mês",
    yaxis_title="Área Acumulada (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

### Exemplo 2: Áreas Empilhadas

**Use para**: Mostrar composição ao longo do tempo

```python
# ============================================================================
# ÁREAS EMPILHADAS
# ============================================================================

df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'cana_planta': [80, 95, 110, 120, 115, 100],
    'cana_soca': [40, 55, 70, 80, 75, 70]
})

fig = go.Figure()

# Área 1: Cana Planta
fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['cana_planta'],
    mode='lines',
    name='Cana Planta',
    fill='tozeroy',
    fillcolor='rgba(67, 160, 71, 0.6)',
    line=dict(color=SUCCESS_COLOR, width=0)
))

# Área 2: Cana Soca (empilhada)
fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['cana_soca'],
    mode='lines',
    name='Cana Soca',
    fill='tonexty',           # Preenche até a linha anterior
    fillcolor='rgba(255, 167, 38, 0.6)',
    line=dict(color=WARNING_COLOR, width=0)
))

fig.update_layout(
    title="Área Plantada por Tipo de Cana",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center')
)

fig.show()
```

**💡 Explicação**:
- `fill='tonexty'`: Preenche até a linha de baixo (empilha)
- Ordem importa: adicione da base para o topo
- `width=0`: Esconde a linha de contorno

---

# PARTE 3: GRÁFICOS INTERMEDIÁRIOS

## 3.1 Scatter Plot (Dispersão)

### Exemplo 1: Scatter Básico

**Use para**: Analisar relação entre duas variáveis numéricas

```python
# ============================================================================
# SCATTER PLOT BÁSICO
# ============================================================================

# Dados: TCH vs ATR
df = pd.DataFrame({
    'tch': [85, 90, 78, 95, 88, 92, 85, 89, 91, 87, 93, 82],
    'atr': [142, 148, 138, 152, 145, 150, 143, 147, 149, 144, 151, 140]
})

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['atr'],
    y=df['tch'],
    mode='markers',
    marker=dict(
        size=10,
        color=PRIMARY_COLOR,
        line=dict(width=2, color='white')
    ),
    hovertemplate='<b>Ponto</b><br>ATR: %{x:.1f}<br>TCH: %{y:.1f}<extra></extra>'
))

fig.update_layout(
    title="Relação entre TCH e ATR",
    xaxis_title="ATR (kg/t)",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

### Exemplo 2: Scatter com Cores por Categoria

**Use para**: Comparar grupos diferentes

```python
# ============================================================================
# SCATTER COM GRUPOS
# ============================================================================

df = pd.DataFrame({
    'tch': [85, 90, 78, 95, 88, 92, 85, 89, 91, 87],
    'atr': [142, 148, 138, 152, 145, 150, 143, 147, 149, 144],
    'variedade': ['RB867515']*5 + ['RB966928']*5
})

# Cria scatter colorido por variedade
fig = px.scatter(
    df,
    x='atr',
    y='tch',
    color='variedade',
    color_discrete_sequence=[SUCCESS_COLOR, WARNING_COLOR],
    title="TCH vs ATR por Variedade",
    labels={'atr': 'ATR (kg/t)', 'tch': 'TCH (t/ha)'}
)

fig.update_traces(marker=dict(size=12, line=dict(width=2, color='white')))

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI")
)

fig.show()
```

**💡 Nota**: `px.scatter()` é mais rápido para scatter com grupos!

---

### Exemplo 3: Scatter com Linha de Tendência

**Use para**: Mostrar correlação e fazer previsões

```python
# ============================================================================
# SCATTER COM LINHA DE REGRESSÃO
# ============================================================================

from scipy import stats

df = pd.DataFrame({
    'atr': [142, 148, 138, 152, 145, 150, 143, 147, 149, 144, 151, 140],
    'tch': [85, 90, 78, 95, 88, 92, 85, 89, 91, 87, 93, 82]
})

# Calcula regressão linear
slope, intercept, r_value, p_value, std_err = stats.linregress(df['atr'], df['tch'])

# Gera pontos para a linha
x_trend = np.linspace(df['atr'].min(), df['atr'].max(), 100)
y_trend = slope * x_trend + intercept

fig = go.Figure()

# Pontos
fig.add_trace(go.Scatter(
    x=df['atr'],
    y=df['tch'],
    mode='markers',
    name='Dados Reais',
    marker=dict(
        size=12,
        color=PRIMARY_COLOR,
        line=dict(width=2, color='white')
    ),
    hovertemplate='<b>Talhão</b><br>ATR: %{x:.1f}<br>TCH: %{y:.1f}<extra></extra>'
))

# Linha de tendência
fig.add_trace(go.Scatter(
    x=x_trend,
    y=y_trend,
    mode='lines',
    name=f'Tendência (R²={r_value**2:.3f})',
    line=dict(
        color=DANGER_COLOR,
        width=3,
        dash='dash'
    ),
    hovertemplate='Previsão: %{y:.1f}<extra></extra>'
))

# Adiciona equação no gráfico
fig.add_annotation(
    x=145,
    y=95,
    text=f'y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_value**2:.3f}',
    showarrow=False,
    bgcolor='white',
    bordercolor=TEXT_DARK,
    borderwidth=1,
    font=dict(size=12)
)

fig.update_layout(
    title="TCH vs ATR com Linha de Tendência",
    xaxis_title="ATR (kg/t)",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Explicação**:
- `stats.linregress()`: Calcula regressão linear (precisa de scipy)
- `slope`: Inclinação da reta
- `intercept`: Ponto de corte com eixo Y
- `r_value**2`: R² (quanto mais próximo de 1, melhor o ajuste)
- `add_annotation()`: Adiciona texto no gráfico

---

### Exemplo 4: Bubble Chart (Bolhas)

**Use para**: Mostrar 3 dimensões (X, Y, tamanho)

```python
# ============================================================================
# BUBBLE CHART (SCATTER COM TAMANHOS)
# ============================================================================

df = pd.DataFrame({
    'talhao': ['T001', 'T002', 'T003', 'T004', 'T005'],
    'tch': [92, 75, 88, 65, 95],
    'atr': [148, 142, 146, 140, 152],
    'area_ha': [45, 28, 38, 22, 50]  # Tamanho da bolha
})

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['atr'],
    y=df['tch'],
    mode='markers',
    marker=dict(
        size=df['area_ha'],   # Tamanho proporcional à área
        sizemode='diameter',  # 'diameter' ou 'area'
        sizeref=2,            # Ajusta escala (experimente valores)
        color=df['tch'],      # Cor também baseada em TCH
        colorscale='Greens',  # Escala de verde
        showscale=True,       # Mostra barra de cores
        colorbar=dict(title="TCH (t/ha)"),
        line=dict(width=2, color='white')
    ),
    text=df['talhao'],
    hovertemplate='<b>%{text}</b><br>' +
                  'ATR: %{x:.1f}<br>' +
                  'TCH: %{y:.1f}<br>' +
                  'Área: %{marker.size:.0f} ha<extra></extra>'
))

fig.update_layout(
    title="Análise Multivariada: TCH vs ATR (Tamanho = Área)",
    xaxis_title="ATR (kg/t)",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Recursos**:
- `size=df['area_ha']`: Tamanho baseado em coluna
- `color=df['tch']`: Cor baseada em coluna
- `colorscale='Greens'`: Outras opções: `'Blues'`, `'Reds'`, `'Viridis'`
- `sizeref`: Ajusta escala (se bolhas muito grandes/pequenas, mude este valor)

---

## 3.2 Box Plot

### Exemplo 1: Box Plot Simples

**Use para**: Entender distribuição, mediana, quartis, outliers

```python
# ============================================================================
# BOX PLOT SIMPLES
# ============================================================================

# Dados: TCH de vários talhões
np.random.seed(42)
tch_values = np.random.normal(85, 8, 50)  # 50 valores, média 85, desvio 8

fig = go.Figure()

fig.add_trace(go.Box(
    y=tch_values,
    name='TCH',
    marker_color=SUCCESS_COLOR,
    boxmean='sd',            # Mostra média e desvio padrão
    boxpoints='outliers'     # Mostra apenas outliers ('all' = todos pontos)
))

fig.update_layout(
    title="Distribuição de TCH",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    showlegend=False
)

fig.show()
```

**💡 Lendo o Box Plot**:
- Linha do meio: Mediana (50% dos dados)
- Caixa: Q1 (25%) até Q3 (75%)
- Bigodes: Valores mín/máx (dentro de 1.5×IQR)
- Pontos: Outliers (valores atípicos)

---

### Exemplo 2: Box Plot por Grupo

**Use para**: Comparar distribuições entre grupos

```python
# ============================================================================
# BOX PLOT POR GRUPO
# ============================================================================

# Dados: TCH de 3 variedades
np.random.seed(42)
df = pd.DataFrame({
    'variedade': ['RB867515']*20 + ['RB966928']*20 + ['CTC4']*20,
    'tch': np.concatenate([
        np.random.normal(85, 5, 20),   # RB867515: média 85
        np.random.normal(90, 4, 20),   # RB966928: média 90
        np.random.normal(88, 6, 20)    # CTC4: média 88
    ])
})

fig = go.Figure()

# Cria um box plot para cada variedade
cores = [PRIMARY_COLOR, SUCCESS_COLOR, WARNING_COLOR]
for i, variedade in enumerate(['RB867515', 'RB966928', 'CTC4']):
    df_var = df[df['variedade'] == variedade]

    fig.add_trace(go.Box(
        y=df_var['tch'],
        name=variedade,
        marker_color=cores[i],
        boxmean='sd',
        boxpoints='outliers'
    ))

fig.update_layout(
    title="Distribuição de TCH por Variedade",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

## 3.3 Histograma

### Exemplo 1: Histograma Básico

**Use para**: Ver distribuição de frequências

```python
# ============================================================================
# HISTOGRAMA BÁSICO
# ============================================================================

# Dados: TCH de 200 talhões
np.random.seed(42)
tch_values = np.random.normal(85, 10, 200)

fig = go.Figure()

fig.add_trace(go.Histogram(
    x=tch_values,
    nbinsx=20,              # Número de bins (barras)
    marker_color=PRIMARY_COLOR,
    opacity=0.7,
    name='TCH'
))

# Adiciona linha de média
media = np.mean(tch_values)
fig.add_vline(
    x=media,
    line_dash="dash",
    line_color=DANGER_COLOR,
    line_width=2,
    annotation_text=f"Média: {media:.1f}",
    annotation_position="top"
)

fig.update_layout(
    title="Distribuição de TCH (Histograma)",
    xaxis_title="TCH (t/ha)",
    yaxis_title="Frequência",
    plot_bgcolor='white',
    paper_bgcolor='white',
    bargap=0.1             # Espaço entre barras (0-1)
)

fig.show()
```

**💡 Dicas**:
- `nbinsx`: Mais bins = mais detalhado (experimente 10, 20, 30)
- Use `bargap=0.1` para pequeno espaço entre barras
- Adicione linha de média/meta para referência

---

### Exemplo 2: Histograma com Curva de Distribuição

**Use para**: Ver se dados seguem distribuição normal

```python
# ============================================================================
# HISTOGRAMA COM CURVA DE DISTRIBUIÇÃO NORMAL
# ============================================================================

from scipy.stats import norm

# Dados
np.random.seed(42)
tch_values = np.random.normal(85, 10, 200)

# Calcula curva normal
media = np.mean(tch_values)
desvio = np.std(tch_values)
x_curve = np.linspace(tch_values.min(), tch_values.max(), 100)
y_curve = norm.pdf(x_curve, media, desvio)

# Normaliza para escala do histograma
y_curve = y_curve * len(tch_values) * (tch_values.max() - tch_values.min()) / 20

fig = go.Figure()

# Histograma
fig.add_trace(go.Histogram(
    x=tch_values,
    nbinsx=20,
    marker_color=PRIMARY_COLOR,
    opacity=0.7,
    name='Frequência'
))

# Curva normal
fig.add_trace(go.Scatter(
    x=x_curve,
    y=y_curve,
    mode='lines',
    name='Distribuição Normal',
    line=dict(color=DANGER_COLOR, width=3)
))

fig.update_layout(
    title=f"Distribuição de TCH (μ={media:.1f}, σ={desvio:.1f})",
    xaxis_title="TCH (t/ha)",
    yaxis_title="Frequência",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

---

## 3.4 Heatmap

### Exemplo 1: Heatmap de Correlação

**Use para**: Identificar relações entre variáveis

```python
# ============================================================================
# HEATMAP DE CORRELAÇÃO
# ============================================================================

# Dados: Múltiplas variáveis
np.random.seed(42)
df = pd.DataFrame({
    'TCH': np.random.normal(85, 10, 50),
    'ATR': np.random.normal(148, 5, 50),
    'Idade': np.random.randint(1, 6, 50),
    'Chuva': np.random.normal(1200, 300, 50),
    'Temperatura': np.random.normal(26, 3, 50)
})

# Calcula matriz de correlação
corr_matrix = df.corr()

fig = go.Figure()

fig.add_trace(go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    colorscale='RdBu',       # Vermelho-Azul (divergente)
    zmid=0,                  # Centro em zero
    text=corr_matrix.values,
    texttemplate='%{text:.2f}',  # 2 casas decimais
    textfont={"size": 12},
    colorbar=dict(title="Correlação"),
    hovertemplate='%{y} vs %{x}<br>Correlação: %{z:.3f}<extra></extra>'
))

fig.update_layout(
    title="Matriz de Correlação - Fatores Agronômicos",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500,
    width=600
)

fig.show()
```

**💡 Interpretação**:
- Cor azul escuro: Correlação positiva forte (+1)
- Cor branca: Sem correlação (0)
- Cor vermelha: Correlação negativa forte (-1)
- Diagonal sempre = 1 (variável com ela mesma)

---

### Exemplo 2: Heatmap de Valores

**Use para**: Visualizar matriz de dados

```python
# ============================================================================
# HEATMAP DE VALORES (EXEMPLO: TCH POR TALHÃO E MÊS)
# ============================================================================

# Dados: TCH de 10 talhões ao longo de 6 meses
talhoes = [f'T{i:03d}' for i in range(1, 11)]
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']

# Gera dados aleatórios
np.random.seed(42)
data = np.random.randint(70, 100, (10, 6))

fig = go.Figure()

fig.add_trace(go.Heatmap(
    z=data,
    x=meses,
    y=talhoes,
    colorscale='Greens',     # Verde (sequencial)
    text=data,
    texttemplate='%{text}',
    textfont={"size": 10},
    colorbar=dict(title="TCH (t/ha)"),
    hovertemplate='<b>%{y}</b> - %{x}<br>TCH: %{z} t/ha<extra></extra>'
))

fig.update_layout(
    title="TCH por Talhão e Mês",
    xaxis_title="Mês",
    yaxis_title="Talhão",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500
)

fig.show()
```

**💡 Escalas de Cores**:
- `'Greens'`: Verde (use para valores "quanto mais, melhor")
- `'Reds'`: Vermelho (use para problemas)
- `'RdBu'`: Vermelho-Azul (use para correlações)
- `'Viridis'`: Multicolorido (neutro)

---

## 3.5 Barras Empilhadas

### Exemplo 1: Barras Empilhadas Verticais

**Use para**: Mostrar composição e total de cada categoria

```python
# ============================================================================
# BARRAS EMPILHADAS VERTICAIS
# ============================================================================

# Dados: Área por tipo de cana em cada mês
df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'cana_planta': [80, 95, 110, 120, 115, 100],
    'cana_soca': [40, 55, 70, 80, 75, 70]
})

fig = go.Figure()

# Barra 1: Cana Planta
fig.add_trace(go.Bar(
    x=df['mes'],
    y=df['cana_planta'],
    name='Cana Planta',
    marker_color=SUCCESS_COLOR,
    text=df['cana_planta'],
    textposition='inside',
    hovertemplate='<b>%{x}</b><br>Cana Planta: %{y} ha<extra></extra>'
))

# Barra 2: Cana Soca (empilhada em cima)
fig.add_trace(go.Bar(
    x=df['mes'],
    y=df['cana_soca'],
    name='Cana Soca',
    marker_color=WARNING_COLOR,
    text=df['cana_soca'],
    textposition='inside',
    hovertemplate='<b>%{x}</b><br>Cana Soca: %{y} ha<extra></extra>'
))

fig.update_layout(
    barmode='stack',         # 'stack' = empilhado, 'group' = agrupado
    title="Área Plantada por Tipo de Cana",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center')
)

fig.show()
```

---

### Exemplo 2: Barras Agrupadas (Comparação)

**Use para**: Comparar categorias lado a lado

```python
# ============================================================================
# BARRAS AGRUPADAS (NÃO EMPILHADAS)
# ============================================================================

df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'planejado': [150, 160, 170, 180, 175, 165],
    'realizado': [145, 162, 168, 185, 172, 170]
})

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['mes'],
    y=df['planejado'],
    name='Planejado',
    marker_color=WARNING_COLOR
))

fig.add_trace(go.Bar(
    x=df['mes'],
    y=df['realizado'],
    name='Realizado',
    marker_color=SUCCESS_COLOR
))

fig.update_layout(
    barmode='group',         # Lado a lado
    title="Planejado vs Realizado",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig.show()
```

**💡 Diferença**:
- `barmode='stack'`: Empilhado (mostra total)
- `barmode='group'`: Agrupado (compara valores)

---

# PARTE 4: GRÁFICOS AVANÇADOS

## 4.1 Gráfico Combo (Dual-Axis)

### Exemplo Completo: Área + Precipitação

**Use para**: Mostrar duas métricas com escalas diferentes

```python
# ============================================================================
# GRÁFICO COMBO - DUAL AXIS
# ============================================================================

from plotly.subplots import make_subplots

# Dados
df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'area_plantada': [120, 150, 180, 200, 190, 170],
    'precipitacao_mm': [250, 180, 200, 100, 50, 30]
})

# Cria figura com eixo secundário
fig = make_subplots(specs=[[{"secondary_y": True}]])

# EIXO PRINCIPAL (esquerda): Área Plantada
fig.add_trace(
    go.Scatter(
        x=df['mes'],
        y=df['area_plantada'],
        name="Área Plantada",
        mode='lines+markers',
        line=dict(color=SUCCESS_COLOR, width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(67, 160, 71, 0.2)'
    ),
    secondary_y=False      # Eixo principal
)

# EIXO SECUNDÁRIO (direita): Precipitação
fig.add_trace(
    go.Bar(
        x=df['mes'],
        y=df['precipitacao_mm'],
        name="Precipitação",
        marker_color=INFO_COLOR,
        opacity=0.6
    ),
    secondary_y=True       # Eixo secundário
)

# Configurar eixos
fig.update_xaxes(title_text="Mês")
fig.update_yaxes(title_text="Área Plantada (ha)", secondary_y=False)
fig.update_yaxes(title_text="Precipitação (mm)", secondary_y=True)

fig.update_layout(
    title="Área Plantada vs Precipitação",
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center')
)

fig.show()
```

**💡 Passo a passo**:
1. `make_subplots(specs=[[{"secondary_y": True}]])`: Cria figura com 2 eixos Y
2. `secondary_y=False`: Primeiro trace vai no eixo esquerdo
3. `secondary_y=True`: Segundo trace vai no eixo direito
4. `update_yaxes(..., secondary_y=...)`: Configura cada eixo separadamente

---

## 4.2 Waterfall Chart

### Exemplo Completo: Análise de Variação

**Use para**: Mostrar acúmulo/redução passo a passo

```python
# ============================================================================
# WATERFALL CHART (CASCATA)
# ============================================================================

# Dados: Variação mensal de área
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Total']
valores = [120, 30, 40, -20, 15, -10, None]  # None para total
measure = ["relative"] * 6 + ["total"]        # relative ou total

fig = go.Figure()

fig.add_trace(go.Waterfall(
    x=meses,
    y=valores,
    measure=measure,
    text=[f"{v:+.0f}" if v else "185" for v in valores],  # Formato +/-
    textposition="outside",
    decreasing={"marker": {"color": DANGER_COLOR}},      # Valores negativos
    increasing={"marker": {"color": SUCCESS_COLOR}},     # Valores positivos
    totals={"marker": {"color": PRIMARY_COLOR}},         # Total
    connector={"line": {"color": "#888", "dash": "dot"}} # Linha conectora
))

fig.update_layout(
    title="Variação Mensal de Área Plantada",
    yaxis_title="Área (ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    showlegend=False
)

fig.show()
```

**💡 Explicação**:
- `measure=["relative", ..., "total"]`: Tipo de cada barra
  - `"relative"`: Variação (+ ou -)
  - `"total"`: Soma total
- `text=[...]`: Rótulo customizado em cada barra
- Cores diferentes para aumento (verde) e queda (vermelho)

---

## 4.3 Treemap

### Exemplo Completo: Hierarquia de Áreas

**Use para**: Mostrar hierarquia e proporções

```python
# ============================================================================
# TREEMAP
# ============================================================================

# Dados hierárquicos: Total > Safra > Variedade
import plotly.express as px

df = pd.DataFrame({
    'area_ha': [3500, 2800, 2200, 1800, 1000],
    'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579'],
    'safra': ['2023/24', '2023/24', '2022/23', '2022/23', '2022/23']
})

# Adiciona nível "Total"
# Plotly precisa de estrutura: labels, parents, values

labels = ['Total']  # Raiz
parents = ['']      # Raiz não tem pai
values = [df['area_ha'].sum()]

# Adiciona safras
for safra in df['safra'].unique():
    labels.append(safra)
    parents.append('Total')
    values.append(df[df['safra'] == safra]['area_ha'].sum())

# Adiciona variedades
for _, row in df.iterrows():
    labels.append(row['variedade'])
    parents.append(row['safra'])
    values.append(row['area_ha'])

fig = go.Figure()

fig.add_trace(go.Treemap(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",    # "total" ou "remainder"
    marker=dict(
        colorscale='Greens',
        cmid=np.median(values),
        colorbar=dict(title="Área (ha)")
    ),
    textinfo='label+value+percent parent',
    hovertemplate='<b>%{label}</b><br>' +
                  'Área: %{value:,.0f} ha<br>' +
                  '%{percentParent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição Hierárquica de Área",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=500
)

fig.show()
```

**💡 Estrutura hierárquica**:
- `labels`: Nome de cada bloco
- `parents`: Pai de cada bloco ('' = raiz)
- `values`: Tamanho de cada bloco
- Exemplo:
  ```
  Total
  ├── 2023/24
  │   ├── RB867515
  │   └── RB966928
  └── 2022/23
      ├── CTC4
      ├── SP81-3250
      └── RB92579
  ```

---

## 4.4 Sunburst

### Exemplo Completo: Hierarquia Radial

**Use para**: Mesma função do treemap, formato radial

```python
# ============================================================================
# SUNBURST (HIERARQUIA RADIAL)
# ============================================================================

# Usa mesmos dados do treemap
labels = ['Total', '2023/24', '2022/23',
          'RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579']
parents = ['', 'Total', 'Total',
           '2023/24', '2023/24', '2022/23', '2022/23', '2022/23']
values = [11000, 6300, 4700,
          3500, 2800, 2200, 1800, 1000]

fig = go.Figure()

fig.add_trace(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    marker=dict(colorscale='Greens'),
    hovertemplate='<b>%{label}</b><br>' +
                  'Área: %{value:,.0f} ha<br>' +
                  '%{percentParent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição Radial de Área",
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=600
)

fig.show()
```

**💡 Diferença Treemap vs Sunburst**:
- **Treemap**: Retangular, melhor para muitos itens
- **Sunburst**: Radial, mais bonito, melhor para apresentações

---

## 4.5 Gauge (Velocímetro)

### Exemplo Completo: Progresso de Meta

**Use para**: Mostrar progresso vs meta

```python
# ============================================================================
# GAUGE CHART (VELOCÍMETRO)
# ============================================================================

# Dados
percentual_meta = 75  # 75% da meta atingida
meta = 100

fig = go.Figure()

fig.add_trace(go.Indicator(
    mode="gauge+number+delta",
    value=percentual_meta,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Progresso de Plantio", 'font': {'size': 20}},
    delta={
        'reference': meta,
        'increasing': {'color': SUCCESS_COLOR},
        'decreasing': {'color': DANGER_COLOR}
    },
    gauge={
        'axis': {
            'range': [None, 100],
            'ticksuffix': '%',
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 10
        },
        'bar': {'color': PRIMARY_COLOR, 'thickness': 0.75},
        'steps': [
            {'range': [0, 50], 'color': '#ffebee'},      # Vermelho claro
            {'range': [50, 75], 'color': '#fff9c4'},     # Amarelo claro
            {'range': [75, 100], 'color': '#e8f5e9'}     # Verde claro
        ],
        'threshold': {
            'line': {'color': DANGER_COLOR, 'width': 4},
            'thickness': 0.75,
            'value': 90                                   # Linha de meta
        }
    }
))

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400,
    font=dict(family="Segoe UI")
)

fig.show()
```

**💡 Componentes**:
- `mode="gauge+number+delta"`: Mostra velocímetro + número + variação
- `steps`: Faixas de cores (ruim/médio/bom)
- `threshold`: Linha de meta/objetivo
- `delta.reference`: Valor de comparação

---

Vou continuar o manual na próxima parte com os gráficos restantes. Você quer que eu continue agora com:
- 4.6 Violin Plot
- 4.7 Radar Chart
- 4.8 Gráfico 3D
- 4.9 Funil
- 4.10 Análise de Pareto
- Parte 5: Templates Reutilizáveis
- Parte 6: Boas Práticas

Ou prefere que eu commit isso e continue depois?