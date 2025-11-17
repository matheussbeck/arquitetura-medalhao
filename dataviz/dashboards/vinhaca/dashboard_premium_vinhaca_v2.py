"""
💧 Dashboard Premium - Vinhaça (Versão 2.0)
============================================
Dashboard de CONTROLE DE QUALIDADE com visualizações avançadas.
Todos os dados são mockados para demonstração.

Executar: python dashboard_premium_vinhaca_v2.py
Acesse: http://localhost:8051
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

# Limites de controle
PH_MIN, PH_MAX, PH_IDEAL = 6.5, 8.5, 7.5
K2O_MIN, K2O_MAX, K2O_IDEAL = 2.0, 5.0, 3.5
VOL_MIN, VOL_MAX, VOL_IDEAL = 60, 150, 100

# ============================================================================
# DADOS MOCKADOS
# ============================================================================

def gerar_dados_vinhaca():
    """Gera dados mockados de vinhaça."""
    np.random.seed(42)

    # Dados diários (90 dias)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    df_diario = pd.DataFrame({
        'data': dates,
        'ph': 7.5 + np.random.randn(90) * 0.4,
        'k2o': 3.5 + np.random.randn(90) * 0.6,
        'volume_m3': np.random.uniform(5000, 15000, 90),
        'volume_m3_ha': np.random.uniform(80, 120, 90)
    })

    # Adiciona alguns outliers
    df_diario.loc[10:12, 'ph'] = 9.0
    df_diario.loc[45:47, 'k2o'] = 1.8
    df_diario.loc[70:72, 'volume_m3_ha'] = 160

    # Dados por talhão
    df_talhoes = pd.DataFrame({
        'talhao': [f'T{i:03d}' for i in range(1, 51)],
        'volume_total_m3': np.random.uniform(2000, 8000, 50),
        'volume_m3_ha': np.random.uniform(70, 130, 50),
        'ph_medio': 7.5 + np.random.randn(50) * 0.5,
        'k2o_medio': 3.5 + np.random.randn(50) * 0.7,
        'lat': -22.5 + np.random.randn(50) * 0.05,
        'lon': -47.4 + np.random.randn(50) * 0.05
    })

    # Status de conformidade
    df_talhoes['conforme_ph'] = df_talhoes['ph_medio'].between(PH_MIN, PH_MAX)
    df_talhoes['conforme_k2o'] = df_talhoes['k2o_medio'].between(K2O_MIN, K2O_MAX)
    df_talhoes['conforme_vol'] = df_talhoes['volume_m3_ha'].between(VOL_MIN, VOL_MAX)
    df_talhoes['status'] = (df_talhoes['conforme_ph'] &
                            df_talhoes['conforme_k2o'] &
                            df_talhoes['conforme_vol']).map({True: 'Conforme', False: 'Não Conforme'})

    return df_diario, df_talhoes


df_dia, df_tal = gerar_dados_vinhaca()

# KPIs
volume_total = df_dia['volume_m3'].sum()
volume_medio_ha = df_dia['volume_m3_ha'].mean()
ph_medio = df_dia['ph'].mean()
k2o_medio = df_dia['k2o'].mean()
taxa_conformidade = (df_tal['status'] == 'Conforme').mean() * 100

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def criar_kpi(valor, titulo, icone, cor, unidade="", comparacao=None):
    """KPI card simplificado."""
    comp = html.Div()
    if comparacao:
        arrow = "▲" if comparacao > 0 else "▼"
        cor_comp = SUCCESS if comparacao > 0 else DANGER
        comp = html.Div([
            html.Span(arrow, style={'color': cor_comp}),
            html.Span(f" {abs(comparacao):.1f}% vs período anterior",
                     style={'fontSize': '12px', 'color': '#666'})
        ], style={'marginTop': '8px'})

    return html.Div([
        html.I(className=f"fas {icone}", style={'fontSize': '32px', 'color': cor, 'marginBottom': '10px'}),
        html.Div(titulo, style={'fontSize': '12px', 'color': '#666', 'textTransform': 'uppercase'}),
        html.Div(f"{valor:,.1f} {unidade}", style={'fontSize': '28px', 'fontWeight': 'bold', 'color': '#2c3e50', 'margin': '8px 0'}),
        comp
    ], style={
        'background': 'white',
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
        'border': f'2px solid {cor}30',
        'textAlign': 'center'
    })


# ============================================================================
# GRÁFICOS
# ============================================================================

# 1. CONTROLE DE pH
fig_ph = go.Figure()

fig_ph.add_trace(go.Scatter(
    x=df_dia['data'],
    y=df_dia['ph'],
    mode='lines+markers',
    name='pH',
    line=dict(color=WARNING, width=2),
    marker=dict(size=5)
))

# Linhas de controle
fig_ph.add_hline(y=PH_IDEAL, line_dash="dash", line_color=SUCCESS,
                 annotation_text="Ideal", annotation_position="right")
fig_ph.add_hrect(y0=PH_MIN, y1=PH_MAX, fillcolor="green", opacity=0.1,
                 annotation_text="Faixa Aceitável", annotation_position="top left")

fig_ph.update_layout(
    title={'text': "Controle de Qualidade - pH", 'font': {'size': 18}},
    xaxis_title="Data",
    yaxis_title="pH",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=350,
    hovermode='x unified'
)

# 2. CONTROLE DE K2O
fig_k2o = go.Figure()

fig_k2o.add_trace(go.Scatter(
    x=df_dia['data'],
    y=df_dia['k2o'],
    mode='lines+markers',
    name='K₂O',
    line=dict(color=DANGER, width=2),
    marker=dict(size=5)
))

fig_k2o.add_hline(y=K2O_IDEAL, line_dash="dash", line_color=SUCCESS,
                  annotation_text="Ideal", annotation_position="right")
fig_k2o.add_hrect(y0=K2O_MIN, y1=K2O_MAX, fillcolor="green", opacity=0.1,
                  annotation_text="Faixa Aceitável", annotation_position="top left")

fig_k2o.update_layout(
    title={'text': "Controle de Qualidade - K₂O", 'font': {'size': 18}},
    xaxis_title="Data",
    yaxis_title="K₂O (kg/m³)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=350,
    hovermode='x unified'
)

# 3. VIOLIN PLOTS
fig_violin = make_subplots(rows=1, cols=3,
                           subplot_titles=("pH", "K₂O (kg/m³)", "Volume (m³/ha)"))

fig_violin.add_trace(
    go.Violin(y=df_dia['ph'], name='pH', box_visible=True,
              meanline_visible=True, fillcolor=WARNING, opacity=0.6),
    row=1, col=1
)

fig_violin.add_trace(
    go.Violin(y=df_dia['k2o'], name='K₂O', box_visible=True,
              meanline_visible=True, fillcolor=DANGER, opacity=0.6),
    row=1, col=2
)

fig_violin.add_trace(
    go.Violin(y=df_dia['volume_m3_ha'], name='Volume', box_visible=True,
              meanline_visible=True, fillcolor=INFO, opacity=0.6),
    row=1, col=3
)

fig_violin.update_layout(
    title_text="Análise de Distribuição dos Parâmetros",
    showlegend=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Segoe UI"),
    height=400
)

# 4. MAPA DE APLICAÇÃO
fig_mapa = px.scatter_mapbox(
    df_tal,
    lat='lat',
    lon='lon',
    color='status',
    size='volume_total_m3',
    hover_name='talhao',
    hover_data={
        'volume_m3_ha': ':.1f',
        'ph_medio': ':.2f',
        'k2o_medio': ':.2f',
        'lat': False,
        'lon': False
    },
    color_discrete_map={'Conforme': SUCCESS, 'Não Conforme': DANGER},
    zoom=10,
    height=500,
    title="Mapa de Aplicação por Talhão"
)

fig_mapa.update_layout(
    mapbox_style="open-street-map",
    font=dict(family="Segoe UI"),
    title={'font': {'size': 18}}
)

# 5. HEATMAP CORRELAÇÃO
corr_data = df_dia[['ph', 'k2o', 'volume_m3_ha']].corr()

fig_corr = go.Figure(go.Heatmap(
    z=corr_data.values,
    x=['pH', 'K₂O', 'Volume/ha'],
    y=['pH', 'K₂O', 'Volume/ha'],
    colorscale='RdBu',
    zmid=0,
    text=corr_data.values,
    texttemplate='%{text:.2f}',
    textfont={"size": 16},
    colorbar=dict(title="Correlação")
))

fig_corr.update_layout(
    title={'text': "Matriz de Correlação", 'font': {'size': 18}},
    height=400,
    font=dict(family="Segoe UI"),
    paper_bgcolor='white'
)

# 6. TABELA DE CONFORMIDADE
df_table = df_tal[['talhao', 'volume_m3_ha', 'ph_medio', 'k2o_medio', 'status']].head(20).copy()
df_table.columns = ['Talhão', 'Volume (m³/ha)', 'pH Médio', 'K₂O Médio', 'Status']

table = dash_table.DataTable(
    data=df_table.to_dict('records'),
    columns=[
        {'name': 'Talhão', 'id': 'Talhão'},
        {'name': 'Volume (m³/ha)', 'id': 'Volume (m³/ha)', 'type': 'numeric', 'format': {'specifier': '.1f'}},
        {'name': 'pH Médio', 'id': 'pH Médio', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'K₂O Médio', 'id': 'K₂O Médio', 'type': 'numeric', 'format': {'specifier': '.2f'}},
        {'name': 'Status', 'id': 'Status'}
    ],
    style_header={
        'backgroundColor': PRIMARY,
        'color': 'white',
        'fontWeight': 'bold',
        'textAlign': 'center',
        'padding': '12px'
    },
    style_cell={
        'textAlign': 'center',
        'padding': '12px',
        'fontFamily': 'Segoe UI'
    },
    style_data_conditional=[
        {
            'if': {
                'filter_query': '{pH Médio} < ' + str(PH_MIN),
                'column_id': 'pH Médio'
            },
            'backgroundColor': '#ffebee',
            'color': DANGER,
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{K₂O Médio} < ' + str(K2O_MIN),
                'column_id': 'K₂O Médio'
            },
            'backgroundColor': '#ffebee',
            'color': DANGER,
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
            html.I(className="fas fa-tint", style={'marginRight': '15px'}),
            "Dashboard Premium - Controle de Vinhaça"
        ], style={'color': 'white', 'margin': '0', 'fontSize': '36px'}),
        html.P(
            f"Monitoramento de Qualidade | {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            style={'color': 'rgba(255,255,255,0.9)', 'margin': '10px 0 0 0'}
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
        html.Div([criar_kpi(volume_total/1000, "Volume Total", "fa-tint", INFO, "mil m³", 8.2)],
                 style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi(volume_medio_ha, "Volume/ha", "fa-flask", SUCCESS, "m³/ha", -2.1)],
                 style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi(ph_medio, "pH Médio", "fa-vial", WARNING, "", 0.5)],
                 style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi(k2o_medio, "K₂O Médio", "fa-atom", DANGER, "kg/m³", 3.2)],
                 style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
        html.Div([criar_kpi(taxa_conformidade, "Taxa Conformidade", "fa-check-circle", PRIMARY, "%", 5.0)],
                 style={'width': '19%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Gráficos de Controle
    html.Div([
        html.Div([dcc.Graph(figure=fig_ph)],
                 style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_k2o)],
                 style={'width': '49%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Violin Plots
    html.Div([
        dcc.Graph(figure=fig_violin)
    ], style={'marginBottom': '30px'}),

    # Mapa e Correlação
    html.Div([
        html.Div([dcc.Graph(figure=fig_mapa)],
                 style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),
        html.Div([dcc.Graph(figure=fig_corr)],
                 style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Tabela
    html.Div([
        html.H3("Resumo de Conformidade por Talhão", style={'color': '#2c3e50', 'marginBottom': '20px'}),
        table
    ], style={
        'background': 'white',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
    })

], style={
    'fontFamily': 'Segoe UI',
    'padding': '30px',
    'background': '#f0f2f5'
})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("💧 DASHBOARD PREMIUM - VINHAÇA V2.0")
    print("="*80)
    print("\n🚀 Servidor iniciado!")
    print("📊 Acesse: http://localhost:8051")
    print("\n💡 Dados mockados com controle de qualidade SPC")
    print("✨ 6 tipos de visualizações avançadas")
    print("\n⌨️  CTRL+C para parar\n")

    app.run(debug=True, host='0.0.0.0', port=8051)
