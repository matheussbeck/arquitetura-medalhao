# 📊 Tutorial Completo: Visualização de Dados - Do Básico ao Avançado

## 🎯 Objetivo

Este tutorial ensina como criar visualizações profissionais usando Plotly, desde gráficos básicos até visualizações avançadas de nível executivo.

---

## 📚 Índice

1. [Fundamentos](#1-fundamentos)
2. [Gráficos Básicos](#2-gráficos-básicos)
3. [Gráficos Intermediários](#3-gráficos-intermediários)
4. [Gráficos Avançados](#4-gráficos-avançados)
5. [Boas Práticas](#5-boas-práticas)
6. [Exemplos do Agronegócio](#6-exemplos-do-agronegócio)

---

## 1. Fundamentos

### 1.1 Instalação

```bash
pip install plotly pandas numpy scipy
```

### 1.2 Imports Necessários

```python
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
```

### 1.3 Anatomia de um Gráfico Plotly

```python
fig = go.Figure()  # Cria figura vazia

# Adiciona dados
fig.add_trace(go.Scatter(
    x=[1, 2, 3],
    y=[4, 5, 6],
    mode='lines+markers',
    name='Serie 1'
))

# Personaliza layout
fig.update_layout(
    title="Título do Gráfico",
    xaxis_title="Eixo X",
    yaxis_title="Eixo Y",
    template="plotly_white"
)

# Exibe
fig.show()
```

### 1.4 Cores e Paletas

```python
# Cores individuais
PRIMARY_COLOR = '#2c5f2d'
SUCCESS_COLOR = '#28a745'
WARNING_COLOR = '#ffc107'
DANGER_COLOR = '#dc3545'

# Paletas (sequencial)
SEQUENTIAL_COLORS = ['#f7fbff', '#6baed6', '#2171b5', '#08306b']

# Paletas (divergente)
DIVERGENT_COLORS = ['#d73027', '#fee090', '#e0f3f8', '#4575b4']

# Uso
fig.update_traces(marker_color=PRIMARY_COLOR)
fig.update_layout(colorway=[SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR])
```

---

## 2. Gráficos Básicos

### 2.1 Gráfico de Linhas (Line Chart)

**Quando usar**: Tendências ao longo do tempo, séries temporais.

```python
import pandas as pd
import plotly.graph_objects as go

# Dados de exemplo
df = pd.DataFrame({
    'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'area_plantada': [120, 150, 180, 200, 190, 170]
})

# Cria gráfico
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['mes'],
    y=df['area_plantada'],
    mode='lines+markers',
    name='Área Plantada',
    line=dict(color='#28a745', width=3),
    marker=dict(size=8)
))

fig.update_layout(
    title="Evolução da Área Plantada",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    hovermode='x unified',
    template='plotly_white'
)

fig.show()
```

**Dica**: Use `mode='lines+markers'` para séries curtas, apenas `'lines'` para séries longas.

---

### 2.2 Gráfico de Barras (Bar Chart)

**Quando usar**: Comparação entre categorias.

```python
# Dados
variedades = ['RB867515', 'RB966928', 'CTC4', 'SP81-3250']
areas = [3500, 2800, 2200, 1500]

# Gráfico vertical
fig = go.Figure(go.Bar(
    x=variedades,
    y=areas,
    marker_color='#2c5f2d',
    text=areas,
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Área: %{y:,} ha<extra></extra>'
))

fig.update_layout(
    title="Área por Variedade de Cana",
    xaxis_title="Variedade",
    yaxis_title="Área (ha)",
    template='plotly_white'
)

fig.show()

# Gráfico horizontal (para muitas categorias)
fig_h = go.Figure(go.Bar(
    y=variedades,
    x=areas,
    orientation='h',
    marker_color='#2c5f2d'
))

fig_h.update_layout(
    title="Área por Variedade",
    yaxis=dict(categoryorder='total ascending')  # Ordena por valor
)

fig_h.show()
```

**Dica**: Use horizontal para > 6 categorias ou nomes longos.

---

### 2.3 Gráfico de Pizza (Pie Chart)

**Quando usar**: Proporções de um todo (use com moderação!).

```python
# Dados
variedades = ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'Outras']
percentuais = [31.8, 25.5, 20.0, 13.6, 9.1]

fig = go.Figure(go.Pie(
    labels=variedades,
    values=percentuais,
    hole=0.4,  # Cria donut chart
    marker=dict(
        colors=['#2c5f2d', '#28a745', '#6baed6', '#ffc107', '#dc3545']
    ),
    textinfo='label+percent',
    hovertemplate='<b>%{label}</b><br>%{value}%<br>%{percent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição de Variedades",
    showlegend=True,
    template='plotly_white'
)

fig.show()
```

**⚠️ Atenção**: Evite pizza com > 5 categorias. Prefira barras horizontais.

---

### 2.4 Gráfico de Área (Area Chart)

**Quando usar**: Magnitude ao longo do tempo, acumulados.

```python
# Dados
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
area_acumulada = [120, 270, 450, 650, 840, 1010]

fig = go.Figure(go.Scatter(
    x=meses,
    y=area_acumulada,
    mode='lines',
    fill='tozeroy',  # Preenche até y=0
    fillcolor='rgba(44, 95, 45, 0.3)',
    line=dict(color='#2c5f2d', width=2),
    name='Área Acumulada'
))

fig.update_layout(
    title="Área Plantada Acumulada",
    xaxis_title="Mês",
    yaxis_title="Área Acumulada (ha)",
    template='plotly_white'
)

fig.show()
```

---

## 3. Gráficos Intermediários

### 3.1 Gráfico de Dispersão (Scatter Plot)

**Quando usar**: Relação entre duas variáveis numéricas.

```python
# Dados
df = pd.DataFrame({
    'tch': [85, 90, 78, 95, 88, 92, 85, 89, 91, 87],
    'atr': [142, 148, 138, 152, 145, 150, 143, 147, 149, 144],
    'variedade': ['RB867515']*5 + ['RB966928']*5
})

fig = px.scatter(
    df,
    x='atr',
    y='tch',
    color='variedade',
    size=[10]*len(df),  # Tamanho uniforme
    hover_data=['atr', 'tch'],
    title="TCH vs ATR por Variedade"
)

fig.update_layout(
    xaxis_title="ATR (kg/t)",
    yaxis_title="TCH (t/ha)",
    template='plotly_white'
)

fig.show()
```

**Com linha de tendência**:

```python
from scipy import stats

# Calcula regressão linear
slope, intercept, r_value, p_value, std_err = stats.linregress(df['atr'], df['tch'])

# Linha de tendência
x_trend = np.linspace(df['atr'].min(), df['atr'].max(), 100)
y_trend = slope * x_trend + intercept

fig.add_trace(go.Scatter(
    x=x_trend,
    y=y_trend,
    mode='lines',
    name=f'Tendência (R²={r_value**2:.3f})',
    line=dict(color='red', dash='dash')
))

fig.show()
```

---

### 3.2 Gráfico de Caixas (Box Plot)

**Quando usar**: Distribuição, mediana, quartis, outliers.

```python
# Dados
df = pd.DataFrame({
    'variedade': ['RB867515']*20 + ['RB966928']*20 + ['CTC4']*20,
    'tch': np.random.normal(85, 5, 20).tolist() +
           np.random.normal(90, 4, 20).tolist() +
           np.random.normal(88, 6, 20).tolist()
})

fig = go.Figure()

for variedade in df['variedade'].unique():
    df_var = df[df['variedade'] == variedade]

    fig.add_trace(go.Box(
        y=df_var['tch'],
        name=variedade,
        boxmean='sd',  # Mostra média e desvio padrão
        marker_color='#28a745'
    ))

fig.update_layout(
    title="Distribuição de TCH por Variedade",
    yaxis_title="TCH (t/ha)",
    template='plotly_white',
    showlegend=True
)

fig.show()
```

---

### 3.3 Histograma

**Quando usar**: Distribuição de frequências.

```python
# Dados
tch_values = np.random.normal(85, 10, 200)

fig = go.Figure(go.Histogram(
    x=tch_values,
    nbinsx=20,  # Número de bins
    marker_color='#2c5f2d',
    opacity=0.7,
    name='TCH'
))

# Adiciona linha de média
mean_tch = np.mean(tch_values)
fig.add_vline(
    x=mean_tch,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Média: {mean_tch:.1f}",
    annotation_position="top right"
)

fig.update_layout(
    title="Distribuição de TCH",
    xaxis_title="TCH (t/ha)",
    yaxis_title="Frequência",
    template='plotly_white'
)

fig.show()
```

---

### 3.4 Heatmap

**Quando usar**: Matriz de valores, correlações.

```python
# Dados de correlação
df = pd.DataFrame({
    'TCH': [85, 90, 78, 95, 88],
    'ATR': [142, 148, 138, 152, 145],
    'Idade': [2, 3, 1, 2, 4],
    'Chuva': [1200, 1400, 1100, 1500, 1300]
})

# Calcula correlação
corr = df.corr()

fig = go.Figure(go.Heatmap(
    z=corr.values,
    x=corr.columns,
    y=corr.columns,
    colorscale='RdBu',
    zmid=0,
    text=corr.values,
    texttemplate='%{text:.2f}',
    textfont={"size": 12},
    colorbar=dict(title="Correlação")
))

fig.update_layout(
    title="Matriz de Correlação",
    template='plotly_white',
    height=500
)

fig.show()
```

---

### 3.5 Gráfico de Barras Empilhadas

**Quando usar**: Comparação de partes que formam um todo.

```python
# Dados
meses = ['Jan', 'Fev', 'Mar', 'Abr']
cana_planta = [80, 95, 110, 100]
cana_soca = [40, 55, 70, 100]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=meses,
    y=cana_planta,
    name='Cana Planta',
    marker_color='#28a745'
))

fig.add_trace(go.Bar(
    x=meses,
    y=cana_soca,
    name='Cana Soca',
    marker_color='#ffc107'
))

fig.update_layout(
    barmode='stack',  # 'stack' ou 'group'
    title="Plantio por Tipo de Cana",
    xaxis_title="Mês",
    yaxis_title="Área (ha)",
    template='plotly_white'
)

fig.show()
```

---

## 4. Gráficos Avançados

### 4.1 Gráfico Combo (Dual-Axis)

**Quando usar**: Duas métricas com escalas diferentes.

```python
from plotly.subplots import make_subplots

# Dados
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
area_plantada = [120, 150, 180, 200, 190, 170]
precipitacao = [250, 180, 200, 100, 50, 30]

# Cria figura com eixo secundário
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Área plantada (eixo principal)
fig.add_trace(
    go.Scatter(
        x=meses,
        y=area_plantada,
        name="Área Plantada",
        mode='lines+markers',
        line=dict(color='#28a745', width=3),
        fill='tozeroy',
        fillcolor='rgba(40, 167, 69, 0.2)'
    ),
    secondary_y=False
)

# Precipitação (eixo secundário)
fig.add_trace(
    go.Bar(
        x=meses,
        y=precipitacao,
        name="Precipitação",
        marker_color='#17a2b8',
        opacity=0.6
    ),
    secondary_y=True
)

# Atualiza eixos
fig.update_xaxes(title_text="Mês")
fig.update_yaxes(title_text="Área (ha)", secondary_y=False)
fig.update_yaxes(title_text="Precipitação (mm)", secondary_y=True)

fig.update_layout(
    title="Área Plantada vs Precipitação",
    hovermode='x unified',
    template='plotly_white'
)

fig.show()
```

---

### 4.2 Waterfall Chart (Cascata)

**Quando usar**: Análise de variação sequencial.

```python
# Dados
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Total']
valores = [120, 30, 40, -20, 15, -10, None]
measure = ["relative"] * 6 + ["total"]

fig = go.Figure(go.Waterfall(
    x=meses,
    y=valores,
    measure=measure,
    text=[f"{v:+.0f}" if v else "185" for v in valores],
    textposition="outside",
    decreasing={"marker": {"color": "#dc3545"}},
    increasing={"marker": {"color": "#28a745"}},
    totals={"marker": {"color": "#2c5f2d"}},
    connector={"line": {"color": "#6c757d", "dash": "dot"}}
))

fig.update_layout(
    title="Variação Mensal de Área Plantada",
    yaxis_title="Área (ha)",
    template='plotly_white',
    showlegend=False
)

fig.show()
```

---

### 4.3 Treemap

**Quando usar**: Hierarquias, proporções aninhadas.

```python
# Dados hierárquicos
df = pd.DataFrame({
    'labels': ['Total', 'Safra 23/24', 'Safra 22/23',
               'RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579'],
    'parents': ['', 'Total', 'Total',
                'Safra 23/24', 'Safra 23/24', 'Safra 22/23', 'Safra 22/23', 'Safra 22/23'],
    'values': [11000, 6000, 5000,
               3500, 2500, 2200, 1800, 1000]
})

fig = go.Figure(go.Treemap(
    labels=df['labels'],
    parents=df['parents'],
    values=df['values'],
    branchvalues="total",
    marker=dict(
        colorscale='Greens',
        cmid=df['values'].median()
    ),
    textinfo='label+value+percent parent',
    hovertemplate='<b>%{label}</b><br>Área: %{value:,} ha<br>%{percentParent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição Hierárquica de Área",
    template='plotly_white'
)

fig.show()
```

---

### 4.4 Sunburst Chart

**Quando usar**: Hierarquias radiais, drill-down.

```python
# Mesmo dataframe do treemap
fig = go.Figure(go.Sunburst(
    labels=df['labels'],
    parents=df['parents'],
    values=df['values'],
    branchvalues="total",
    marker=dict(colorscale='Greens'),
    hovertemplate='<b>%{label}</b><br>Área: %{value:,} ha<br>%{percentParent}<extra></extra>'
))

fig.update_layout(
    title="Distribuição Radial de Área",
    template='plotly_white',
    height=600
)

fig.show()
```

---

### 4.5 Gauge Chart (Velocímetro)

**Quando usar**: Progresso vs meta, performance.

```python
# KPI: 75% da meta de plantio atingida
percentual_meta = 75

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=percentual_meta,
    domain={'x': [0, 1], 'y': [0, 1]},
    delta={'reference': 100, 'increasing': {'color': "green"}},
    gauge={
        'axis': {'range': [None, 100], 'ticksuffix': '%'},
        'bar': {'color': "#2c5f2d"},
        'steps': [
            {'range': [0, 50], 'color': "#dc3545"},
            {'range': [50, 75], 'color': "#ffc107"},
            {'range': [75, 100], 'color': "#28a745"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 90
        }
    },
    title={'text': "Progresso de Plantio"}
))

fig.update_layout(
    height=400,
    template='plotly_white'
)

fig.show()
```

---

### 4.6 Violin Plot

**Quando usar**: Distribuição completa (densidade + quartis).

```python
# Dados
df = pd.DataFrame({
    'variedade': ['RB867515']*50 + ['RB966928']*50 + ['CTC4']*50,
    'tch': np.concatenate([
        np.random.normal(85, 5, 50),
        np.random.normal(90, 4, 50),
        np.random.normal(88, 6, 50)
    ])
})

fig = go.Figure()

for variedade in df['variedade'].unique():
    df_var = df[df['variedade'] == variedade]

    fig.add_trace(go.Violin(
        y=df_var['tch'],
        name=variedade,
        box_visible=True,
        meanline_visible=True,
        fillcolor='#28a745',
        opacity=0.6,
        line_color='#2c5f2d'
    ))

fig.update_layout(
    title="Distribuição de TCH por Variedade (Violin Plot)",
    yaxis_title="TCH (t/ha)",
    template='plotly_white'
)

fig.show()
```

---

### 4.7 Radar Chart (Spider)

**Quando usar**: Comparação multidimensional.

```python
# Dados
categorias = ['TCH', 'ATR', 'Eficiência', 'Qualidade', 'Sustentabilidade']
valores_atual = [85, 92, 78, 88, 95]
valores_benchmark = [90, 90, 90, 90, 90]

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=valores_atual,
    theta=categorias,
    fill='toself',
    name='Atual',
    line=dict(color='#28a745', width=2),
    fillcolor='rgba(40, 167, 69, 0.3)'
))

fig.add_trace(go.Scatterpolar(
    r=valores_benchmark,
    theta=categorias,
    fill='toself',
    name='Benchmark',
    line=dict(color='#ffc107', width=2, dash='dash'),
    fillcolor='rgba(255, 193, 7, 0.2)'
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100])
    ),
    title="Performance vs Benchmark",
    template='plotly_white'
)

fig.show()
```

---

### 4.8 Gráfico 3D de Superfície

**Quando usar**: Relação entre 3 variáveis numéricas.

```python
# Cria grid
idade = np.linspace(1, 6, 30)
atr = np.linspace(130, 160, 30)
X, Y = np.meshgrid(idade, atr)

# Modelo: TCH = f(idade, ATR)
Z = 100 - (X - 2.5)**2 * 3 + (Y - 145) * 0.3

fig = go.Figure(data=[go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale='Viridis',
    colorbar=dict(title="TCH")
)])

fig.update_layout(
    title="TCH = f(Idade, ATR)",
    scene=dict(
        xaxis_title='Idade (anos)',
        yaxis_title='ATR',
        zaxis_title='TCH (t/ha)',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
    ),
    template='plotly_white'
)

fig.show()
```

---

### 4.9 Funil (Funnel Chart)

**Quando usar**: Conversão, etapas sequenciais.

```python
# Dados
stages = ['Área Total', 'Área Plantável', 'Área Plantada', 'Área Colhida', 'Produção']
values = [11000, 10000, 9500, 9200, 9000]

fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textposition="inside",
    textinfo="value+percent initial",
    marker=dict(
        color=["#17a2b8", "#28a745", "#2c5f2d", "#ffc107", "#dc3545"]
    ),
    connector={"line": {"color": "#6c757d"}}
))

fig.update_layout(
    title="Funil de Conversão - Área para Produção",
    template='plotly_white'
)

fig.show()
```

---

### 4.10 Análise de Pareto

**Quando usar**: Identificar os "poucos vitais" (regra 80/20).

```python
from plotly.subplots import make_subplots

# Dados
variedades = ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579', 'Outras']
areas = [3500, 2800, 2200, 1500, 800, 200]

# Ordena
df = pd.DataFrame({'variedade': variedades, 'area': areas})
df = df.sort_values('area', ascending=False).reset_index(drop=True)

# Calcula acumulado
df['area_acum'] = df['area'].cumsum()
df['pct_acum'] = (df['area_acum'] / df['area'].sum()) * 100

# Cria gráfico
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Barras
fig.add_trace(
    go.Bar(
        x=df['variedade'],
        y=df['area'],
        name='Área (ha)',
        marker_color='#28a745'
    ),
    secondary_y=False
)

# Linha acumulada
fig.add_trace(
    go.Scatter(
        x=df['variedade'],
        y=df['pct_acum'],
        name='% Acumulado',
        mode='lines+markers',
        line=dict(color='#dc3545', width=3),
        marker=dict(size=8)
    ),
    secondary_y=True
)

# Linha 80%
fig.add_hline(
    y=80,
    line_dash="dash",
    line_color="gray",
    annotation_text="80% (Pareto)",
    secondary_y=True
)

fig.update_xaxes(title_text="Variedade")
fig.update_yaxes(title_text="Área (ha)", secondary_y=False)
fig.update_yaxes(title_text="% Acumulado", range=[0, 105], secondary_y=True)

fig.update_layout(
    title="Análise de Pareto - Variedades",
    template='plotly_white'
)

fig.show()
```

---

## 5. Boas Práticas

### 5.1 Escolha do Gráfico Certo

| Objetivo | Gráfico Recomendado |
|----------|---------------------|
| Tendência temporal | Linha, Área |
| Comparação de categorias | Barras (vertical/horizontal) |
| Proporção do todo | Pizza (≤5 categorias), Barras |
| Distribuição | Histograma, Box Plot, Violin |
| Relação entre variáveis | Scatter, Heatmap |
| Hierarquia | Treemap, Sunburst |
| Variação sequencial | Waterfall |
| Performance vs meta | Gauge, Radar |
| Conversão/funil | Funnel |
| Ranking/priorização | Pareto |

### 5.2 Cores

✅ **Faça**:
- Use cores consistentes (paleta corporativa)
- Verde para positivo, vermelho para negativo
- Use cores acessíveis (contraste adequado)
- Limite a 5-7 cores por gráfico

❌ **Evite**:
- Arco-íris sem significado
- Vermelho/verde para daltônicos (use também símbolos)
- Cores muito saturadas

### 5.3 Títulos e Rótulos

✅ **Faça**:
- Título descritivo e claro
- Eixos sempre com unidades
- Legendas explicativas
- Tooltips informativos

```python
fig.update_layout(
    title="Evolução da Produtividade (TCH) - Safra 2023/2024",
    xaxis_title="Mês de Plantio",
    yaxis_title="TCH (toneladas/hectare)",
    hovermode='x unified'
)
```

### 5.4 Simplicidade

✅ **Faça**:
- Um gráfico = uma mensagem
- Remova elementos desnecessários (gridlines excessivos, borders)
- Use espaço em branco

❌ **Evite**:
- Gráficos 3D sem necessidade
- Muitos dados em um único gráfico
- Efeitos desnecessários (sombras, gradientes excessivos)

### 5.5 Templates

Use templates consistentes:

```python
# Template padrão
TEMPLATE_CONFIG = {
    'template': 'plotly_white',
    'font': {'family': 'Segoe UI, sans-serif', 'size': 12},
    'title': {'font': {'size': 18, 'color': '#2c3e50'}},
    'margin': {'l': 60, 'r': 40, 't': 80, 'b': 60}
}

fig.update_layout(**TEMPLATE_CONFIG)
```

### 5.6 Responsividade

```python
# Configuração responsiva
fig.update_layout(
    autosize=True,
    height=400,  # Altura fixa
    # width não definido = responsivo
)
```

### 5.7 Tooltips Informativos

```python
# Bom tooltip
hovertemplate='<b>%{x}</b><br>' +
              'TCH: %{y:.1f} t/ha<br>' +
              'Variedade: %{customdata[0]}<br>' +
              '<extra></extra>'  # Remove box secundário
```

---

## 6. Exemplos do Agronegócio

### 6.1 Dashboard de Plantio

```python
from plotly.subplots import make_subplots

# Dados
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
planejado = [800, 1700, 2900, 4400, 6200, 7800]
realizado = [820, 1700, 2880, 5400, 7150, 8730]
chuva = [250, 180, 200, 100, 50, 30]

# Cria subplots
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Planejado vs Realizado', 'Precipitação',
                    'Desvio (%)', 'Status Mensal'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"type": "indicator"}]]
)

# 1. Área acumulada
fig.add_trace(
    go.Scatter(x=meses, y=planejado, name='Planejado',
               line=dict(color='#ffc107', dash='dash')),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=meses, y=realizado, name='Realizado',
               fill='tozeroy', line=dict(color='#28a745')),
    row=1, col=1
)

# 2. Precipitação
fig.add_trace(
    go.Bar(x=meses, y=chuva, name='Chuva (mm)',
           marker_color='#17a2b8'),
    row=1, col=2
)

# 3. Desvio
desvio = [(r-p)/p*100 for r, p in zip(realizado, planejado)]
fig.add_trace(
    go.Bar(x=meses, y=desvio, name='Desvio (%)',
           marker_color=['#28a745' if d >= 0 else '#dc3545' for d in desvio]),
    row=2, col=1
)

# 4. KPI Gauge
percentual = (realizado[-1] / planejado[-1]) * 100
fig.add_trace(
    go.Indicator(
        mode="gauge+number+delta",
        value=percentual,
        delta={'reference': 100},
        title={'text': "% da Meta"},
        gauge={'axis': {'range': [0, 120]},
               'steps': [
                   {'range': [0, 80], 'color': "#dc3545"},
                   {'range': [80, 100], 'color': "#ffc107"},
                   {'range': [100, 120], 'color': "#28a745"}
               ]}
    ),
    row=2, col=2
)

fig.update_layout(
    height=800,
    showlegend=True,
    title_text="Dashboard de Plantio - Safra 2023/2024",
    template='plotly_white'
)

fig.show()
```

### 6.2 Análise de Qualidade da Vinhaça

```python
# Gráfico de controle de qualidade
dates = pd.date_range('2024-01-01', periods=90, freq='D')
ph = 7.5 + np.random.randn(90) * 0.5
k2o = 3.5 + np.random.randn(90) * 0.3

df = pd.DataFrame({'data': dates, 'ph': ph, 'k2o': k2o})

# Limites
PH_MIN, PH_MAX, PH_IDEAL = 6.5, 8.5, 7.5

fig = go.Figure()

# Valores reais
fig.add_trace(go.Scatter(
    x=df['data'],
    y=df['ph'],
    mode='lines+markers',
    name='pH',
    line=dict(color='#28a745', width=2),
    marker=dict(size=4)
))

# Linha ideal
fig.add_hline(y=PH_IDEAL, line_dash="dash", line_color="blue",
              annotation_text="Ideal")

# Limites
fig.add_hrect(y0=PH_MIN, y1=PH_MAX, fillcolor="green", opacity=0.1,
              annotation_text="Faixa Aceitável", annotation_position="top left")

fig.update_layout(
    title="Controle de Qualidade - pH da Vinhaça",
    xaxis_title="Data",
    yaxis_title="pH",
    template='plotly_white',
    hovermode='x unified'
)

fig.show()
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Plotly Python](https://plotly.com/python/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Dash Documentation](https://dash.plotly.com/)

### Exemplos
- [Plotly Chart Examples](https://plotly.com/python/)
- [Figure Reference](https://plotly.com/python/reference/)

### Tutoriais
- [Plotly Fundamentals](https://plotly.com/python/plotly-fundamentals/)
- [Statistical Charts](https://plotly.com/python/statistical-charts/)

---

## ✅ Checklist Final

Antes de publicar um gráfico:

- [ ] Título claro e descritivo
- [ ] Eixos com rótulos e unidades
- [ ] Cores acessíveis e consistentes
- [ ] Tooltips informativos
- [ ] Legenda quando necessário
- [ ] Fonte legível (≥ 10pt)
- [ ] Gráfico correto para o objetivo
- [ ] Dados precisos e atualizados
- [ ] Performance otimizada (< 1000 pontos se possível)
- [ ] Responsivo

---

**Versão**: 1.0
**Última Atualização**: 2024
**Nível**: Básico → Avançado
