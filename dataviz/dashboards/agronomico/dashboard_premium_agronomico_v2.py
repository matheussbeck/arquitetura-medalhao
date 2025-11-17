"""
🌾 Dashboard Premium - Visão Agronômica 360° (Versão 2.0)
===========================================================
Dashboard EXECUTIVO com análises multidimensionais avançadas.
Todos os dados são mockados para demonstração visual impressionante.

Executar: python dashboard_premium_agronomico_v2.py
Acesse: http://localhost:8052
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Cores
PRIMARY = '#2E7D32'
SUCCESS = '#43A047'
WARNING = '#FFA726'
DANGER = '#E53935'
INFO = '#29B6F6'

# Benchmarks
BENCHMARK_TCH = 90.0
BENCHMARK_ATR = 150.0
BENCHMARK_EFIC = 95.0

# ============================================================================
# DADOS MOCKADOS
# ============================================================================

def gerar_dados_agronomicos():
    """Gera dados mockados completos."""
    np.random.seed(42)

    # Variedades
    df_var = pd.DataFrame({
        'variedade': ['RB867515', 'RB966928', 'CTC4', 'SP81-3250', 'RB92579'],
        'area_ha': [3500, 2800, 2200, 1500, 1000],
        'tch': [88, 92, 85, 78, 82],
        'atr': [148, 152, 145, 142, 146],
        'safra': ['2023/24']*5
    })

    # Análise temporal (12 meses)
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    df_temporal = pd.DataFrame({
        'mes': meses,
        'tch': [85, 86, 87, 88, 89, 90, 88, 87, 86, 85, 84, 85],
        'atr': [145, 146, 147, 148, 149, 150, 148, 147, 146, 145, 144, 145],
        'chuva': [250, 180, 200, 100, 50, 30, 20, 25, 80, 120, 180, 220],
        'temp': [28, 29, 27, 26, 24, 23, 22, 24, 26, 27, 28, 29]
    })

    # Performance vs Benchmark
    performance = {
        'TCH': 87.5 / BENCHMARK_TCH * 100,
        'ATR': 147.6 / BENCHMARK_ATR * 100,
        'Eficiência': 92.0,
        'Qualidade': 94.0,
        'Sustentabilidade': 88.0
    }

    # Dados 3D (Idade x ATR x TCH)
    idade = np.linspace(1, 5, 20)
    atr_vals = np.linspace(135, 155, 20)
    X, Y = np.meshgrid(idade, atr_vals)
    Z = 100 - (X - 2.5)**2 * 4 + (Y - 145) * 0.4 + np.random.randn(20, 20) * 2

    # Funil de conversão
    funil = pd.DataFrame({
        'etapa': ['Área Total', 'Área Plantável', 'Área Plantada', 'Área em Produção', 'Produção Efetiva'],
        'valor': [11000, 10000, 9500, 9000, 8500]
    })

    return df_var, df_temporal, performance, (X, Y, Z), funil


df_var, df_temp, perf, dados_3d, df_funil = gerar_dados_agronomicos()

# KPIs
tch_medio = (df_var['tch'] * df_var['area_ha']).sum() / df_var['area_ha'].sum()
atr_medio = (df_var['atr'] * df_var['area_ha']).sum() / df_var['area_ha'].sum()
area_total = df_var['area_ha'].sum()
producao_total = (df_var['tch'] * df_var['area_ha']).sum()

# ============================================================================
# FUNÇÕES
# ============================================================================

def criar_kpi_executivo(valor, titulo, icone, cor, benchmark=None, unidade=""):
    """KPI executivo com benchmark."""
    bench_div = html.Div()
    if benchmark:
        diff_pct = ((valor - benchmark) / benchmark * 100)
        arrow = "▲" if diff_pct > 0 else "▼"
        cor_diff = SUCCESS if diff_pct > 0 else DANGER
        bench_div = html.Div([
            html.Div([
                html.Span(arrow, style={'color': cor_diff, 'marginRight': '5px'}),
                html.Span(f"{abs(diff_pct):.1f}%", style={'color': cor_diff, 'fontWeight': 'bold'}),
                html.Span(" vs benchmark", style={'color': '#666', 'fontSize': '11px', 'marginLeft': '5px'})
            ]),
            html.Div(f"Benchmark: {benchmark:.1f} {unidade}",
                     style={'fontSize': '11px', 'color': '#999', 'marginTop': '5px'})
        ], style={'marginTop': '10px'})

    return html.Div([
        html.I(className=f"fas {icone}", style={'fontSize': '34px', 'color': cor, 'marginBottom': '12px'}),
        html.Div(titulo, style={'fontSize': '12px', 'color': '#666', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
        html.Div(f"{valor:,.1f} {unidade}",
                 style={'fontSize': '30px', 'fontWeight': 'bold', 'color': '#2c3e50', 'margin': '10px 0'}),
        bench_div
    ], style={
        'background': 'white',
        'padding': '25px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.1)',
        'border': f'2px solid {cor}30',
        'textAlign': 'center',
        'height': '100%'
    })


# ============================================================================
# GRÁFICOS
# ============================================================================

# 1. GRÁFICO 3D
X, Y, Z = dados_3d

fig_3d = go.Figure(data=[go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale='Viridis',
    colorbar=dict(title="TCH (t/ha)")
)])

fig_3d.update_layout(
    title={'text': "Superfície 3D: TCH = f(Idade, ATR)", 'font': {'size': 18}},
    scene=dict(
        xaxis_title='Idade (anos)',
        yaxis_title='ATR (kg/t)',
        zaxis_title='TCH (t/ha)',
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.3))
    ),
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    height=500
)

# 2. RADAR CHART
categorias = list(perf.keys())
valores_atual = list(perf.values())
valores_bench = [100] * len(categorias)

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=valores_atual,
    theta=categorias,
    fill='toself',
    name='Atual',
    line=dict(color=SUCCESS, width=2),
    fillcolor=f'rgba(67, 160, 71, 0.3)'
))

fig_radar.add_trace(go.Scatterpolar(
    r=valores_bench,
    theta=categorias,
    fill='toself',
    name='Benchmark',
    line=dict(color=WARNING, width=2, dash='dash'),
    fillcolor=f'rgba(255, 167, 38, 0.2)'
))

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 110])),
    title={'text': "Performance vs Benchmark", 'font': {'size': 18}},
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    height=450
)

# 3. SUNBURST
# Prepara dados hierárquicos
labels = ['Total'] + df_var['variedade'].tolist()
parents = [''] + ['Total']*len(df_var)
values = [df_var['area_ha'].sum()] + df_var['area_ha'].tolist()

fig_sunburst = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    marker=dict(colorscale='Greens'),
    hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<extra></extra>'
))

fig_sunburst.update_layout(
    title={'text': "Distribuição Hierárquica de Área", 'font': {'size': 18}},
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    height=450
)

# 4. ANÁLISE DE PARETO
df_pareto = df_var.sort_values('area_ha', ascending=False).reset_index(drop=True)
df_pareto['area_acum'] = df_pareto['area_ha'].cumsum()
df_pareto['pct_acum'] = (df_pareto['area_acum'] / df_pareto['area_ha'].sum() * 100)

fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])

fig_pareto.add_trace(
    go.Bar(
        x=df_pareto['variedade'],
        y=df_pareto['area_ha'],
        name='Área (ha)',
        marker_color=SUCCESS
    ),
    secondary_y=False
)

fig_pareto.add_trace(
    go.Scatter(
        x=df_pareto['variedade'],
        y=df_pareto['pct_acum'],
        name='% Acumulado',
        mode='lines+markers',
        line=dict(color=DANGER, width=3),
        marker=dict(size=10)
    ),
    secondary_y=True
)

fig_pareto.add_hline(y=80, line_dash="dash", line_color="gray",
                     annotation_text="80% (Regra de Pareto)",
                     secondary_y=True, annotation_position="right")

fig_pareto.update_xaxes(title_text="Variedade")
fig_pareto.update_yaxes(title_text="Área (ha)", secondary_y=False)
fig_pareto.update_yaxes(title_text="% Acumulado", range=[0, 105], secondary_y=True)

fig_pareto.update_layout(
    title={'text': "Análise de Pareto - Variedades por Área", 'font': {'size': 18}},
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    plot_bgcolor='white',
    height=400,
    hovermode='x'
)

# 5. FUNIL DE CONVERSÃO
fig_funil = go.Figure(go.Funnel(
    y=df_funil['etapa'],
    x=df_funil['valor'],
    textposition="inside",
    textinfo="value+percent initial",
    marker=dict(color=[INFO, SUCCESS, PRIMARY, WARNING, DANGER]),
    connector={"line": {"color": "#888"}}
))

fig_funil.update_layout(
    title={'text': "Funil: Área Total → Produção Efetiva", 'font': {'size': 18}},
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    height=400
)

# 6. TIMELINE DE EVENTOS
eventos = pd.DataFrame({
    'Evento': ['Plantio Safra 23/24', 'Aplicação Vinhaça', 'Colheita Safra 22/23', 'Preparo de Solo', 'Controle de Pragas'],
    'Inicio': ['2023-03-01', '2023-06-01', '2023-04-01', '2023-01-15', '2023-05-01'],
    'Fim': ['2023-08-31', '2023-12-31', '2023-11-30', '2023-03-15', '2023-06-30'],
    'Tipo': ['Plantio', 'Fertirrigação', 'Colheita', 'Preparo', 'Defensivo']
})

eventos['Inicio'] = pd.to_datetime(eventos['Inicio'])
eventos['Fim'] = pd.to_datetime(eventos['Fim'])

color_map = {
    'Plantio': SUCCESS,
    'Fertirrigação': INFO,
    'Colheita': WARNING,
    'Preparo': PRIMARY,
    'Defensivo': DANGER
}

fig_timeline = px.timeline(
    eventos,
    x_start='Inicio',
    x_end='Fim',
    y='Evento',
    color='Tipo',
    color_discrete_map=color_map
)

fig_timeline.update_layout(
    title={'text': "Timeline de Eventos Agronômicos - 2023", 'font': {'size': 18}},
    xaxis_title="Período",
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    height=350
)

# 7. EVOLUÇÃO TEMPORAL
fig_temporal = make_subplots(
    rows=2, cols=2,
    subplot_titles=("TCH Médio Mensal", "ATR Médio Mensal", "Precipitação", "Temperatura"),
    vertical_spacing=0.15,
    horizontal_spacing=0.12
)

fig_temporal.add_trace(
    go.Scatter(x=df_temp['mes'], y=df_temp['tch'], mode='lines+markers',
               line=dict(color=SUCCESS, width=2), name='TCH'),
    row=1, col=1
)

fig_temporal.add_trace(
    go.Scatter(x=df_temp['mes'], y=df_temp['atr'], mode='lines+markers',
               line=dict(color=WARNING, width=2), name='ATR'),
    row=1, col=2
)

fig_temporal.add_trace(
    go.Bar(x=df_temp['mes'], y=df_temp['chuva'], marker_color=INFO, name='Chuva'),
    row=2, col=1
)

fig_temporal.add_trace(
    go.Scatter(x=df_temp['mes'], y=df_temp['temp'], mode='lines+markers',
               fill='tozeroy', line=dict(color=DANGER, width=2), name='Temp'),
    row=2, col=2
)

fig_temporal.update_layout(
    title_text="Análise Temporal Multivariada",
    showlegend=False,
    font=dict(family="Segoe UI"),
    paper_bgcolor='white',
    plot_bgcolor='white',
    height=500
)

# ============================================================================
# LAYOUT
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css']
)

app.layout = html.Div([
    # Header
    html.Div([
        html.H1([
            html.I(className="fas fa-chart-line", style={'marginRight': '15px'}),
            "Dashboard Executivo - Visão Agronômica 360°"
        ], style={'color': 'white', 'margin': '0', 'fontSize': '36px'}),
        html.P(
            f"Análise Estratégica Integrada | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            style={'color': 'rgba(255,255,255,0.9)', 'margin': '10px 0 0 0'}
        )
    ], style={
        'background': f'linear-gradient(135deg, {PRIMARY} 0%, {SUCCESS} 100%)',
        'padding': '40px',
        'borderRadius': '15px',
        'marginBottom': '30px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.2)'
    }),

    # KPIs Executivos
    html.Div([
        html.Div([criar_kpi_executivo(tch_medio, "TCH Médio", "fa-seedling", SUCCESS, BENCHMARK_TCH, "t/ha")],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_executivo(atr_medio, "ATR Médio", "fa-flask", WARNING, BENCHMARK_ATR, "kg/t")],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_executivo(area_total, "Área Total", "fa-map", PRIMARY, None, "ha")],
                 style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi_executivo(producao_total/1000, "Produção", "fa-industry", INFO, None, "mil t")],
                 style={'width': '24%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Linha 1: 3D e Radar
    html.Div([
        html.Div([dcc.Graph(figure=fig_3d)],
                 style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_radar)],
                 style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Linha 2: Sunburst e Funil
    html.Div([
        html.Div([dcc.Graph(figure=fig_sunburst)],
                 style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_funil)],
                 style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Linha 3: Pareto
    html.Div([
        dcc.Graph(figure=fig_pareto)
    ], style={'marginBottom': '30px'}),

    # Linha 4: Timeline
    html.Div([
        dcc.Graph(figure=fig_timeline)
    ], style={'marginBottom': '30px'}),

    # Linha 5: Temporal
    html.Div([
        dcc.Graph(figure=fig_temporal)
    ])

], style={
    'fontFamily': 'Segoe UI',
    'padding': '30px',
    'background': '#f0f2f5'
})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌾 DASHBOARD EXECUTIVO AGRONÔMICO V2.0")
    print("="*80)
    print("\n🚀 Servidor iniciado com sucesso!")
    print("📊 Acesse: http://localhost:8052")
    print("\n💡 Dados mockados com análises multidimensionais")
    print("✨ 7 tipos de visualizações executivas avançadas:")
    print("   • Superfície 3D")
    print("   • Radar Chart comparativo")
    print("   • Sunburst hierárquico")
    print("   • Análise de Pareto")
    print("   • Funil de conversão")
    print("   • Timeline de eventos")
    print("   • Análise temporal multivariada")
    print("\n⌨️  CTRL+C para parar\n")

    app.run(debug=True, host='0.0.0.0', port=8052)
