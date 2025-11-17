"""
🌱 Dashboard Premium - Plantio (Versão 2.0)
============================================
Dashboard de ALTO NÍVEL com visualizações impressionantes.
Todos os dados são mockados para demonstração visual.

Executar: python dashboard_premium_plantio_v2.py
Acesse: http://localhost:8050
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

# Cores
PRIMARY = '#2E7D32'
SUCCESS = '#43A047'
WARNING = '#FFA726'
DANGER = '#E53935'
INFO = '#29B6F6'

# ============================================================================
# DADOS MOCKADOS COMPLETOS
# ============================================================================

def gerar_dados_mock():
    """Gera todos os dados mockados para o dashboard."""
    np.random.seed(42)

    # Área por variedade
    df_variedades = pd.DataFrame({
        'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579', 'CTC20', 'RB975935', 'IACSP955000'],
        'area_ha': [3500, 2800, 2200, 1500, 1000, 800, 600, 400],
        'tch_medio': [88, 92, 85, 78, 82, 90, 86, 84],
        'atr_medio': [148, 152, 145, 142, 146, 151, 147, 144],
        'ciclo': ['Cana-planta']*4 + ['Cana-soca']*4
    })
    df_variedades['percentual'] = (df_variedades['area_ha'] / df_variedades['area_ha'].sum() * 100).round(1)

    # Cronograma mensal
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    df_cronograma = pd.DataFrame({
        'mes': meses,
        'planejado': [800, 900, 1200, 1500, 1800, 1600, 1200, 800, 600, 400, 200, 100],
        'realizado': [820, 880, 1180, 1520, 1750, 1580, 1150, 780, 0, 0, 0, 0],
        'precipitacao_mm': [250, 180, 200, 100, 50, 30, 20, 25, 80, 120, 180, 220]
    })
    df_cronograma['acum_planejado'] = df_cronograma['planejado'].cumsum()
    df_cronograma['acum_realizado'] = df_cronograma['realizado'].cumsum()
    df_cronograma['desvio_pct'] = ((df_cronograma['realizado'] - df_cronograma['planejado']) / df_cronograma['planejado'] * 100).fillna(0)

    # Dados diários (últimos 90 dias)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    df_diario = pd.DataFrame({
        'data': dates,
        'area_dia': np.random.randint(80, 150, 90),
        'tch': 85 + np.random.randn(90) * 5,
        'atr': 148 + np.random.randn(90) * 4,
        'temp_max': 28 + np.random.randn(90) * 3,
        'chuva': np.random.exponential(10, 90)
    })

    # Dados por talhão
    df_talhoes = pd.DataFrame({
        'talhao': [f'T{i:03d}' for i in range(1, 51)],
        'area_ha': np.random.uniform(15, 50, 50),
        'tch': np.random.normal(85, 8, 50),
        'atr': np.random.normal(148, 5, 50),
        'idade_anos': np.random.randint(1, 6, 50),
        'variedade': np.random.choice(df_variedades['variedade'].values, 50)
    })
    df_talhoes['producao_t'] = df_talhoes['area_ha'] * df_talhoes['tch']
    df_talhoes['status'] = pd.cut(df_talhoes['tch'],
                                   bins=[0, 70, 85, 100],
                                   labels=['Baixo', 'Médio', 'Alto'])

    return df_variedades, df_cronograma, df_diario, df_talhoes


# ============================================================================
# FUNÇÕES DE GRÁFICOS
# ============================================================================

def criar_kpi_card(valor, titulo, icone, cor, tendencia=None, comparacao=None):
    """Cria KPI card visual com sparkline."""

    # Sparkline
    sparkline = html.Div()
    if tendencia is not None:
        fig_spark = go.Figure()
        fig_spark.add_trace(go.Scatter(
            y=tendencia,
            mode='lines',
            line=dict(color=cor, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(cor[1:3], 16)}, {int(cor[3:5], 16)}, {int(cor[5:7], 16)}, 0.2)'
        ))
        fig_spark.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False
        )
        sparkline = dcc.Graph(figure=fig_spark, config={'displayModeBar': False}, style={'height': '60px'})

    # Comparação
    comp_div = html.Div()
    if comparacao:
        arrow = "▲" if comparacao['valor'] > 0 else "▼"
        cor_comp = SUCCESS if comparacao['valor'] > 0 else DANGER
        comp_div = html.Div([
            html.Span(arrow, style={'color': cor_comp, 'marginRight': '5px'}),
            html.Span(f"{abs(comparacao['valor']):.1f}%",
                     style={'color': cor_comp, 'fontWeight': 'bold', 'fontSize': '14px'}),
            html.Span(f" vs {comparacao['periodo']}",
                     style={'fontSize': '12px', 'color': '#666', 'marginLeft': '5px'})
        ], style={'marginTop': '8px'})

    return html.Div([
        html.Div([
            html.I(className=f"fas {icone}", style={'fontSize': '36px', 'color': cor, 'marginBottom': '10px'}),
            html.Div(titulo, style={'fontSize': '13px', 'color': '#666', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
            html.Div(f"{valor:,.0f}", style={'fontSize': '32px', 'fontWeight': 'bold', 'color': '#2c3e50', 'marginTop': '5px'}),
            comp_div,
            sparkline
        ])
    ], style={
        'background': 'linear-gradient(135deg, #fff 0%, #f8f9fa 100%)',
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
        'border': f'2px solid {cor}30',
        'textAlign': 'center',
        'height': '100%'
    })


# ============================================================================
# GERA DADOS
# ============================================================================

df_var, df_cron, df_dia, df_tal = gerar_dados_mock()

# KPIs principais
area_total = df_var['area_ha'].sum()
tch_medio = (df_var['tch_medio'] * df_var['area_ha']).sum() / df_var['area_ha'].sum()
atr_medio = (df_var['atr_medio'] * df_var['area_ha']).sum() / df_var['area_ha'].sum()
producao_total = (df_var['tch_medio'] * df_var['area_ha']).sum()

# Tendências (últimos 30 pontos)
trend_area = df_dia['area_dia'].tail(30).values
trend_tch = df_dia['tch'].tail(30).values
trend_atr = df_dia['atr'].tail(30).values

# ============================================================================
# GRÁFICOS AVANÇADOS
# ============================================================================

# 1. ÁREA COMBO - Acumulado + Precipitação
fig_combo = make_subplots(specs=[[{"secondary_y": True}]])

fig_combo.add_trace(
    go.Scatter(
        x=df_cron['mes'],
        y=df_cron['acum_planejado'],
        name='Planejado',
        mode='lines',
        line=dict(color=WARNING, width=2, dash='dash')
    ),
    secondary_y=False
)

fig_combo.add_trace(
    go.Scatter(
        x=df_cron['mes'],
        y=df_cron['acum_realizado'],
        name='Realizado',
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color=SUCCESS, width=3),
        fillcolor=f'rgba(67, 160, 71, 0.2)'
    ),
    secondary_y=False
)

fig_combo.add_trace(
    go.Bar(
        x=df_cron['mes'],
        y=df_cron['precipitacao_mm'],
        name='Precipitação',
        marker_color=INFO,
        opacity=0.6
    ),
    secondary_y=True
)

fig_combo.update_xaxes(title_text="Mês")
fig_combo.update_yaxes(title_text="Área Acumulada (ha)", secondary_y=False)
fig_combo.update_yaxes(title_text="Precipitação (mm)", secondary_y=True)

fig_combo.update_layout(
    title={'text': "Evolução de Plantio vs Precipitação", 'font': {'size': 18, 'color': '#2c3e50'}},
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=400,
    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor='center')
)

# 2. GAUGE PREMIUM
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=df_cron['acum_realizado'].iloc[6],
    title={'text': "Progresso de Plantio (Jul)", 'font': {'size': 16}},
    delta={'reference': df_cron['acum_planejado'].iloc[6], 'increasing': {'color': SUCCESS}},
    gauge={
        'axis': {'range': [0, 12000], 'ticksuffix': ' ha'},
        'bar': {'color': SUCCESS, 'thickness': 0.8},
        'steps': [
            {'range': [0, 4000], 'color': '#ffebee'},
            {'range': [4000, 8000], 'color': '#fff9c4'},
            {'range': [8000, 12000], 'color': '#e8f5e9'}
        ],
        'threshold': {
            'line': {'color': PRIMARY, 'width': 4},
            'thickness': 0.75,
            'value': df_cron['acum_planejado'].iloc[6]
        }
    }
))

fig_gauge.update_layout(
    height=350,
    font=dict(family="Segoe UI"),
    paper_bgcolor='white'
)

# 3. TREEMAP
df_tree = df_var.copy()
df_tree['label'] = df_tree['variedade'] + '<br>' + df_tree['area_ha'].astype(int).astype(str) + ' ha'

fig_treemap = go.Figure(go.Treemap(
    labels=df_tree['variedade'],
    parents=['Total']*len(df_tree),
    values=df_tree['area_ha'],
    text=df_tree['label'],
    textposition='middle center',
    marker=dict(
        colorscale='Greens',
        cmid=df_tree['area_ha'].median(),
        colorbar=dict(title="Área (ha)")
    ),
    hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<br>TCH: %{customdata[0]:.1f}<extra></extra>',
    customdata=df_tree[['tch_medio']].values
))

fig_treemap.update_layout(
    title={'text': "Distribuição de Área por Variedade", 'font': {'size': 18, 'color': '#2c3e50'}},
    height=400,
    font=dict(family="Segoe UI"),
    paper_bgcolor='white'
)

# 4. WATERFALL
variacoes = df_cron['realizado'].iloc[:7] - df_cron['planejado'].iloc[:7]
fig_waterfall = go.Figure(go.Waterfall(
    x=df_cron['mes'].iloc[:7],
    y=variacoes.values,
    text=[f"{v:+.0f}" for v in variacoes],
    textposition="outside",
    measure=["relative"]*7,
    decreasing={"marker": {"color": DANGER}},
    increasing={"marker": {"color": SUCCESS}},
    connector={"line": {"color": "#888", "dash": "dot"}}
))

fig_waterfall.update_layout(
    title={'text': "Desvio Mensal: Realizado vs Planejado", 'font': {'size': 18, 'color': '#2c3e50'}},
    yaxis_title="Desvio (ha)",
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=400
)

# 5. SCATTER COM REGRESSÃO
slope, intercept, r_value, p_value, std_err = stats.linregress(df_tal['atr'], df_tal['tch'])
x_trend = np.linspace(df_tal['atr'].min(), df_tal['atr'].max(), 100)
y_trend = slope * x_trend + intercept

fig_scatter = go.Figure()

fig_scatter.add_trace(go.Scatter(
    x=df_tal['atr'],
    y=df_tal['tch'],
    mode='markers',
    marker=dict(
        size=df_tal['area_ha'],
        color=df_tal['tch'],
        colorscale='Viridis',
        showscale=True,
        colorbar=dict(title="TCH"),
        line=dict(width=1, color='white')
    ),
    text=df_tal['talhao'],
    hovertemplate='<b>%{text}</b><br>ATR: %{x:.1f}<br>TCH: %{y:.1f}<extra></extra>'
))

fig_scatter.add_trace(go.Scatter(
    x=x_trend,
    y=y_trend,
    mode='lines',
    name=f'Tendência (R²={r_value**2:.3f})',
    line=dict(color=DANGER, width=3, dash='dash')
))

fig_scatter.update_layout(
    title={'text': "Correlação TCH vs ATR", 'font': {'size': 18, 'color': '#2c3e50'}},
    xaxis_title="ATR (kg/t)",
    yaxis_title="TCH (t/ha)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=400,
    showlegend=True
)

# 6. HEATMAP CORRELAÇÃO
corr_data = df_dia[['tch', 'atr', 'temp_max', 'chuva']].corr()

fig_heatmap = go.Figure(go.Heatmap(
    z=corr_data.values,
    x=['TCH', 'ATR', 'Temp. Máx', 'Chuva'],
    y=['TCH', 'ATR', 'Temp. Máx', 'Chuva'],
    colorscale='RdBu',
    zmid=0,
    text=corr_data.values,
    texttemplate='%{text:.2f}',
    textfont={"size": 14},
    colorbar=dict(title="Correlação")
))

fig_heatmap.update_layout(
    title={'text': "Matriz de Correlação - Fatores Agronômicos", 'font': {'size': 18, 'color': '#2c3e50'}},
    height=400,
    font=dict(family="Segoe UI"),
    paper_bgcolor='white'
)

# 7. TABELA COM FORMATAÇÃO CONDICIONAL
df_table = df_var[['variedade', 'area_ha', 'tch_medio', 'atr_medio', 'percentual']].copy()
df_table.columns = ['Variedade', 'Área (ha)', 'TCH Médio', 'ATR Médio', '% Total']

table = dash_table.DataTable(
    data=df_table.to_dict('records'),
    columns=[
        {'name': 'Variedade', 'id': 'Variedade'},
        {'name': 'Área (ha)', 'id': 'Área (ha)', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
        {'name': 'TCH Médio', 'id': 'TCH Médio', 'type': 'numeric', 'format': {'specifier': '.1f'}},
        {'name': 'ATR Médio', 'id': 'ATR Médio', 'type': 'numeric', 'format': {'specifier': '.1f'}},
        {'name': '% Total', 'id': '% Total', 'type': 'numeric', 'format': {'specifier': '.1f'}}
    ],
    style_table={'overflowX': 'auto'},
    style_header={
        'backgroundColor': PRIMARY,
        'color': 'white',
        'fontWeight': 'bold',
        'textAlign': 'center',
        'padding': '12px',
        'fontSize': '14px'
    },
    style_cell={
        'textAlign': 'center',
        'padding': '12px',
        'fontSize': '13px',
        'fontFamily': 'Segoe UI'
    },
    style_data_conditional=[
        {
            'if': {
                'filter_query': '{TCH Médio} < 80',
                'column_id': 'TCH Médio'
            },
            'backgroundColor': '#ffebee',
            'color': DANGER,
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{TCH Médio} >= 90',
                'column_id': 'TCH Médio'
            },
            'backgroundColor': '#e8f5e9',
            'color': SUCCESS,
            'fontWeight': 'bold'
        },
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#f8f9fa'
        }
    ],
    page_size=10
)

# ============================================================================
# LAYOUT DO APP
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css']
)

app.layout = html.Div([
    # Header
    html.Div([
        html.H1([
            html.I(className="fas fa-seedling", style={'marginRight': '15px'}),
            "Dashboard Premium - Plantio"
        ], style={'color': 'white', 'margin': '0', 'fontSize': '36px'}),
        html.P(
            f"Safra 2023/2024 | Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            style={'color': 'rgba(255,255,255,0.9)', 'margin': '10px 0 0 0', 'fontSize': '16px'}
        )
    ], style={
        'background': f'linear-gradient(135deg, {PRIMARY} 0%, {SUCCESS} 100%)',
        'padding': '40px',
        'borderRadius': '15px',
        'marginBottom': '30px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.2)'
    }),

    # KPIs
    html.Div([
        html.Div([criar_kpi_card(area_total, "Área Total Plantada", "fa-map", SUCCESS, trend_area, {'valor': 5.2, 'periodo': 'mês anterior'})],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_card(tch_medio, "TCH Médio", "fa-chart-line", PRIMARY, trend_tch, {'valor': -2.1, 'periodo': 'safra anterior'})],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_card(atr_medio, "ATR Médio", "fa-flask", WARNING, trend_atr, {'valor': 3.8, 'periodo': 'benchmark'})],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_card(producao_total/1000, "Produção Total (mil t)", "fa-industry", INFO, None, {'valor': 8.4, 'periodo': 'meta'})],
                 style={'width': '24%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Linha 1
    html.Div([
        html.Div([dcc.Graph(figure=fig_combo)],
                 style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_gauge)],
                 style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Linha 2
    html.Div([
        html.Div([dcc.Graph(figure=fig_treemap)],
                 style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_waterfall)],
                 style={'width': '49%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Linha 3
    html.Div([
        html.Div([dcc.Graph(figure=fig_scatter)],
                 style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_heatmap)],
                 style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Tabela
    html.Div([
        html.H3("Desempenho por Variedade", style={'color': '#2c3e50', 'marginBottom': '20px'}),
        table
    ], style={
        'background': 'white',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
    })

], style={
    'fontFamily': 'Segoe UI, sans-serif',
    'padding': '30px',
    'background': '#f0f2f5'
})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌱 DASHBOARD PREMIUM - PLANTIO V2.0")
    print("="*80)
    print("\n🚀 Servidor iniciado com sucesso!")
    print("📊 Acesse: http://localhost:8050")
    print("\n💡 Todos os dados são mockados para demonstração visual")
    print("✨ 7 tipos de gráficos avançados incluídos")
    print("\n⌨️  Pressione CTRL+C para parar\n")

    app.run(debug=True, host='0.0.0.0', port=8050)
