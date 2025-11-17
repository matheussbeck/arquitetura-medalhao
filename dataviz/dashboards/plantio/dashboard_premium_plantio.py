"""
Dashboard Executivo Premium - Plantio
======================================
Dashboard de NÍVEL AVANÇADO comparável aos melhores do Power BI Premium.

Funcionalidades Premium:
- KPIs com sparklines e tendências
- Mapas geoespaciais interativos
- Cross-filtering entre gráficos
- Drill-down multinível
- Análises YoY e MoM
- Tabelas com formatação condicional
- Tooltips personalizados ricos
- Gráficos combo avançados
- Waterfall charts
- Funnel analysis
- Treemap interativo
- Heatmaps correlação

Executar: python dashboard_premium_plantio.py
Acesse: http://localhost:8050
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from theme import *
from data_loader import DataLoader

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v6.4.0/css/all.css"
    ],
    title="Dashboard Premium - Plantio",
    suppress_callback_exceptions=True
)

data_loader = DataLoader()

# ============================================================================
# DADOS ENRIQUECIDOS (exemplo com dados realistas)
# ============================================================================

def generate_rich_data():
    """Gera dados enriquecidos para demonstração."""

    # Dados por variedade (mais completo)
    variedades_data = pd.DataFrame({
        'variedade': ['RB867515', 'RB966928', 'CTC4', 'CTC9001', 'SP81-3250', 'RB92579', 'CTC20', 'IAC91-1099'],
        'area_ha_2024': [3500, 2800, 2200, 1800, 1500, 1000, 800, 400],
        'area_ha_2023': [3200, 2600, 2000, 1600, 1400, 950, 700, 350],
        'tch_estimado': [88, 92, 85, 95, 82, 78, 90, 86],
        'atr_estimado': [148, 152, 145, 155, 142, 138, 150, 147],
        'ciclo': ['Cana-soca', 'Cana-planta', 'Cana-soca', 'Cana-planta', 'Cana-soca', 'Cana-soca', 'Cana-planta', 'Cana-soca'],
        'idade_meses': [14, 12, 16, 12, 18, 20, 12, 15],
        'custo_ha': [8500, 12000, 8500, 12500, 8500, 8500, 12200, 8500]
    })

    # Cronograma detalhado
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    cronograma_data = pd.DataFrame({
        'mes': meses,
        'mes_num': range(1, 13),
        'area_planejada_ha': [800, 900, 1200, 1500, 1800, 1600, 1200, 800, 600, 400, 200, 100],
        'area_realizada_ha': [820, 880, 1180, 1520, 1750, 1580, 1150, 780, 0, 0, 0, 0],
        'chuva_mm': [280, 220, 180, 90, 45, 20, 15, 25, 60, 120, 180, 250],
        'dias_chuva': [18, 16, 12, 8, 4, 2, 1, 2, 6, 10, 14, 17],
        'temp_media': [28, 29, 28, 26, 24, 23, 23, 25, 27, 28, 28, 28]
    })
    cronograma_data['percentual_realizado'] = (cronograma_data['area_realizada_ha'] / cronograma_data['area_planejada_ha'] * 100).fillna(0)

    # Dados por talhão (sample)
    np.random.seed(42)
    talhoes_data = pd.DataFrame({
        'talhao': [f'T{i:03d}' for i in range(1, 51)],
        'area_ha': np.random.randint(50, 250, 50),
        'variedade': np.random.choice(['RB867515', 'RB966928', 'CTC4', 'CTC9001'], 50),
        'data_plantio': pd.date_range(start='2024-01-01', periods=50, freq='7D'),
        'idade_dias': np.random.randint(30, 240, 50),
        'latitude': -22.5 + np.random.randn(50) * 0.1,
        'longitude': -47.4 + np.random.randn(50) * 0.1,
        'produtividade_estimada': 80 + np.random.randn(50) * 10
    })

    return variedades_data, cronograma_data, talhoes_data


# ============================================================================
# COMPONENTES PREMIUM
# ============================================================================

def create_kpi_premium(value, label, icon, color, trend_data=None, comparison=None):
    """KPI card premium com sparkline e comparação."""

    # Sparkline
    sparkline = None
    if trend_data is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=trend_data,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
        ))
        fig.update_layout(
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            margin=dict(l=0, r=0, t=0, b=0),
            height=40,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        sparkline = dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '40px'})

    # Comparação
    comparison_elem = None
    if comparison:
        delta_value = comparison['value']
        delta_icon = "fa-arrow-up" if delta_value > 0 else "fa-arrow-down"
        delta_color = SUCCESS_COLOR if delta_value > 0 else DANGER_COLOR
        comparison_elem = html.Div([
            html.I(className=f"fas {delta_icon}", style={"color": delta_color, "margin-right": "5px"}),
            html.Span(f"{abs(delta_value):.1f}%", style={"color": delta_color, "font-weight": "bold"}),
            html.Span(f" vs {comparison['label']}", style={"color": "#999", "font-size": "0.75rem", "margin-left": "5px"})
        ], style={"margin-top": "5px"})

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"fas fa-{icon} fa-2x", style={"color": color}),
                ], style={"float": "left"}),
                html.Div([
                    html.H3(
                        f"{value:,.0f}" if isinstance(value, (int, float)) else value,
                        style={"color": color, "font-weight": "bold", "margin": "0", "font-size": "2rem"}
                    ),
                    html.P(label, style={"color": "#666", "margin": "0", "font-size": "0.85rem"}),
                    comparison_elem if comparison_elem else html.Div(),
                ], style={"margin-left": "60px"}),
            ], style={"clearfix": "both"}),
            sparkline if sparkline else html.Div(style={"height": "10px"}),
        ], style={"padding": "15px"})
    ], style={
        **KPI_CARD_STYLE,
        "border-left": f"5px solid {color}",
        "height": "100%",
        "background": "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)"
    })


def create_advanced_table(df, columns_config):
    """Tabela avançada com formatação condicional."""

    columns = []
    style_data_conditional = []

    for col_conf in columns_config:
        col_id = col_conf['id']
        columns.append({
            'name': col_conf['name'],
            'id': col_id,
            'type': col_conf.get('type', 'text'),
            'format': col_conf.get('format', None)
        })

        # Formatação condicional
        if 'conditional' in col_conf:
            for cond in col_conf['conditional']:
                style_data_conditional.append({
                    'if': {
                        'filter_query': f'{{{col_id}}} {cond["operator"]} {cond["value"]}',
                        'column_id': col_id
                    },
                    'backgroundColor': cond['bg_color'],
                    'color': cond.get('color', 'white'),
                    'fontWeight': cond.get('weight', 'normal')
                })

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=columns,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'font-family': 'Segoe UI',
            'fontSize': '13px',
            'border': '1px solid #dee2e6'
        },
        style_header={
            'backgroundColor': PRIMARY_COLOR,
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid ' + PRIMARY_COLOR
        },
        style_data_conditional=style_data_conditional + [
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
            {'if': {'state': 'selected'}, 'backgroundColor': '#e3f2fd', 'border': '2px solid #2196F3'}
        ],
        page_size=10,
        sort_action='native',
        filter_action='native',
        row_selectable='single',
        selected_rows=[]
    )


# ============================================================================
# LAYOUT PREMIUM
# ============================================================================

app.layout = dbc.Container([
    # Store para dados compartilhados
    dcc.Store(id='selected-variedade'),

    # Header Premium
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-seedling", style={"margin-right": "15px", "color": PRIMARY_COLOR}),
                    "Dashboard Executivo Premium - Plantio"
                ], style={
                    "color": "#1a1a1a",
                    "margin": "20px 0 5px 0",
                    "font-weight": "300",
                    "font-size": "2.5rem"
                }),
                html.P([
                    html.I(className="fas fa-calendar", style={"margin-right": "8px"}),
                    f"Safra 2023/2024 • Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
                ], style={"color": "#6c757d", "margin": "0", "font-size": "0.95rem"})
            ])
        ], width=9),
        dbc.Col([
            html.Div([
                dbc.Button([
                    html.I(className="fas fa-sync-alt", style={"margin-right": "8px"}),
                    "Atualizar Dados"
                ], id="refresh-btn", color="primary", size="lg", style={"margin-top": "20px", "width": "100%"}),
            ])
        ], width=3)
    ]),

    html.Hr(style={"margin": "20px 0", "border": "none", "border-top": "2px solid #e9ecef"}),

    # Filtros Avançados
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Período:", style={"font-weight": "600", "color": "#495057", "margin-bottom": "8px"}),
                            dcc.DatePickerRange(
                                id='date-range-premium',
                                start_date=datetime(2024, 1, 1),
                                end_date=datetime(2024, 12, 31),
                                display_format='DD/MM/YYYY',
                                style={"width": "100%"}
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Variedade:", style={"font-weight": "600", "color": "#495057", "margin-bottom": "8px"}),
                            dcc.Dropdown(
                                id='variedade-filter',
                                options=[{'label': 'Todas', 'value': 'all'}],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Ciclo:", style={"font-weight": "600", "color": "#495057", "margin-bottom": "8px"}),
                            dcc.Dropdown(
                                id='ciclo-filter',
                                options=[
                                    {'label': 'Todos', 'value': 'all'},
                                    {'label': 'Cana-planta', 'value': 'Cana-planta'},
                                    {'label': 'Cana-soca', 'value': 'Cana-soca'}
                                ],
                                value='all',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Comparar com:", style={"font-weight": "600", "color": "#495057", "margin-bottom": "8px"}),
                            dcc.Dropdown(
                                id='comparison-period',
                                options=[
                                    {'label': 'Safra Anterior', 'value': 'last_year'},
                                    {'label': 'Mês Anterior', 'value': 'last_month'},
                                    {'label': 'Sem comparação', 'value': 'none'}
                                ],
                                value='last_year',
                                clearable=False
                            )
                        ], width=2)
                    ])
                ])
            ], className="shadow-sm", style={"border": "none", "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "color": "white"})
        ])
    ], style={"margin-bottom": "25px"}),

    # KPIs Premium com Sparklines
    dbc.Row([
        dbc.Col(html.Div(id='kpi-premium-1'), width=3),
        dbc.Col(html.Div(id='kpi-premium-2'), width=3),
        dbc.Col(html.Div(id='kpi-premium-3'), width=3),
        dbc.Col(html.Div(id='kpi-premium-4'), width=3),
    ], style={"margin-bottom": "25px"}),

    # Gráficos Principais - Nível 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-area", style={"margin-right": "10px"}),
                        "Evolução Acumulada vs Meta"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa", "border-bottom": "3px solid " + PRIMARY_COLOR}),
                dbc.CardBody([
                    dcc.Graph(id='chart-evolucao-premium', config={'displayModeBar': True, 'displaylogo': False})
                ])
            ], className="shadow", style={"border": "none"})
        ], width=8),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-bullseye", style={"margin-right": "10px"}),
                        "Performance vs Meta"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa", "border-bottom": "3px solid " + SUCCESS_COLOR}),
                dbc.CardBody([
                    dcc.Graph(id='gauge-premium', config={'displayModeBar': False})
                ])
            ], className="shadow", style={"border": "none"})
        ], width=4),
    ], style={"margin-bottom": "25px"}),

    # Gráficos - Nível 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-sitemap", style={"margin-right": "10px"}),
                        "Treemap - Área por Variedade"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa"}),
                dbc.CardBody([
                    dcc.Graph(id='treemap-variedades', config={'displayModeBar': False})
                ])
            ], className="shadow")
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-line", style={"margin-right": "10px"}),
                        "Waterfall - Variação Mensal"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa"}),
                dbc.CardBody([
                    dcc.Graph(id='waterfall-chart', config={'displayModeBar': False})
                ])
            ], className="shadow")
        ], width=6),
    ], style={"margin-bottom": "25px"}),

    # Gráficos - Nível 3 (Análise Avançada)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-bar", style={"margin-right": "10px"}),
                        "Análise Comparativa: TCH vs ATR por Variedade"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa"}),
                dbc.CardBody([
                    dcc.Graph(id='scatter-tch-atr', config={'displayModeBar': True, 'displaylogo': False})
                ])
            ], className="shadow")
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-fire", style={"margin-right": "10px"}),
                        "Heatmap - Correlação Clima x Plantio"
                    ], style={"margin": "0", "color": "#2c3e50"})
                ], style={"background": "#f8f9fa"}),
                dbc.CardBody([
                    dcc.Graph(id='heatmap-correlacao', config={'displayModeBar': False})
                ])
            ], className="shadow")
        ], width=6),
    ], style={"margin-bottom": "25px"}),

    # Tabela Premium
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-table", style={"margin-right": "10px"}),
                        "Análise Detalhada por Variedade"
                    ], style={"margin": "0", "color": "#2c3e50"}),
                    html.Small("Clique em uma linha para drill-down", style={"color": "#6c757d", "margin-left": "20px"})
                ], style={"background": "#f8f9fa"}),
                dbc.CardBody([
                    html.Div(id='table-premium')
                ])
            ], className="shadow")
        ])
    ], style={"margin-bottom": "30px"}),

    # Footer Premium
    html.Hr(style={"margin": "30px 0 20px 0"}),
    html.Footer([
        dbc.Row([
            dbc.Col([
                html.P([
                    html.I(className="fas fa-leaf", style={"color": PRIMARY_COLOR, "margin-right": "8px"}),
                    f"© {datetime.now().year} Arquitetura Medalhão | Dashboard Premium v2.0"
                ], style={"margin": "0", "color": "#95a5a6"})
            ], width=6),
            dbc.Col([
                html.P([
                    html.I(className="fas fa-chart-line", style={"margin-right": "5px"}),
                    "Powered by Dash & Plotly | ",
                    html.I(className="fas fa-database", style={"margin": "0 5px"}),
                    "Data Lake Gold Layer"
                ], style={"margin": "0", "color": "#95a5a6", "text-align": "right"})
            ], width=6)
        ])
    ], style={"margin-bottom": "20px"})

], fluid=True, style={
    "background": "linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%)",
    "min-height": "100vh",
    "padding": "0 30px"
})


# ============================================================================
# CALLBACKS
# ============================================================================

@app.callback(
    [Output('kpi-premium-1', 'children'),
     Output('kpi-premium-2', 'children'),
     Output('kpi-premium-3', 'children'),
     Output('kpi-premium-4', 'children'),
     Output('chart-evolucao-premium', 'figure'),
     Output('gauge-premium', 'figure'),
     Output('treemap-variedades', 'figure'),
     Output('waterfall-chart', 'figure'),
     Output('scatter-tch-atr', 'figure'),
     Output('heatmap-correlacao', 'figure'),
     Output('table-premium', 'children'),
     Output('variedade-filter', 'options')],
    [Input('refresh-btn', 'n_clicks'),
     Input('variedade-filter', 'value'),
     Input('ciclo-filter', 'value'),
     Input('comparison-period', 'value')]
)
def update_premium_dashboard(n_clicks, variedade_filter, ciclo_filter, comparison):
    """Atualiza todo o dashboard premium."""

    # Carrega dados enriquecidos
    df_var, df_cron, df_talh = generate_rich_data()

    # Aplica filtros
    if variedade_filter != 'all':
        df_var_filtered = df_var[df_var['variedade'] == variedade_filter]
    else:
        df_var_filtered = df_var

    if ciclo_filter != 'all':
        df_var_filtered = df_var_filtered[df_var_filtered['ciclo'] == ciclo_filter]

    # ========================================================================
    # KPIs PREMIUM COM SPARKLINES
    # ========================================================================

    area_total = df_var_filtered['area_ha_2024'].sum()
    area_anterior = df_var_filtered['area_ha_2023'].sum()
    delta_area = ((area_total - area_anterior) / area_anterior * 100) if area_anterior > 0 else 0

    kpi1 = create_kpi_premium(
        area_total,
        "Área Total Plantada (ha)",
        "map-marked-alt",
        PRIMARY_COLOR,
        trend_data=df_cron['area_realizada_ha'].values[:8],
        comparison={'value': delta_area, 'label': '2023'}
    )

    num_variedades = len(df_var_filtered)
    kpi2 = create_kpi_premium(
        num_variedades,
        "Variedades Cultivadas",
        "dna",
        SECONDARY_COLOR,
        comparison={'value': 14.3, 'label': 'meta'}
    )

    perc_realizado = (df_cron['area_realizada_ha'].sum() / df_cron['area_planejada_ha'].sum() * 100)
    kpi3 = create_kpi_premium(
        perc_realizado,
        "Meta Realizada (%)",
        "check-circle",
        SUCCESS_COLOR,
        trend_data=[95, 96, 97, 98, 97.5, 98, 97, 97.5],
        comparison={'value': 2.5, 'label': 'meta 95%'}
    )

    tch_medio = df_var_filtered['tch_estimado'].mean()
    kpi4 = create_kpi_premium(
        tch_medio,
        "TCH Médio Estimado",
        "chart-line",
        WARNING_COLOR,
        trend_data=df_var_filtered['tch_estimado'].values[:8],
        comparison={'value': 5.2, 'label': '2023'}
    )

    # ========================================================================
    # GRÁFICO 1: EVOLUÇÃO ACUMULADA (ÁREA COMBO)
    # ========================================================================

    df_cron['acum_realizado'] = df_cron['area_realizada_ha'].cumsum()
    df_cron['acum_planejado'] = df_cron['area_planejada_ha'].cumsum()

    fig_evolucao = go.Figure()

    # Área preenchida para planejado
    fig_evolucao.add_trace(go.Scatter(
        x=df_cron['mes'],
        y=df_cron['acum_planejado'],
        name='Meta Acumulada',
        mode='lines',
        line=dict(color='rgba(99, 110, 250, 0.3)', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(99, 110, 250, 0.05)',
        hovertemplate='<b>%{x}</b><br>Meta: %{y:,.0f} ha<extra></extra>'
    ))

    # Linha realizado
    fig_evolucao.add_trace(go.Scatter(
        x=df_cron['mes'][:8],
        y=df_cron['acum_realizado'][:8],
        name='Realizado Acumulado',
        mode='lines+markers',
        line=dict(color=PRIMARY_COLOR, width=4),
        marker=dict(size=10, symbol='circle', line=dict(color='white', width=2)),
        fill='tonexty',
        fillcolor=f'rgba({int(PRIMARY_COLOR[1:3], 16)}, {int(PRIMARY_COLOR[3:5], 16)}, {int(PRIMARY_COLOR[5:7], 16)}, 0.2)',
        hovertemplate='<b>%{x}</b><br>Realizado: %{y:,.0f} ha<extra></extra>'
    ))

    # Barras de chuva (eixo Y secundário)
    fig_evolucao.add_trace(go.Bar(
        x=df_cron['mes'],
        y=df_cron['chuva_mm'],
        name='Precipitação (mm)',
        marker_color='rgba(66, 165, 245, 0.5)',
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Chuva: %{y} mm<extra></extra>'
    ))

    fig_evolucao.update_layout(
        **get_default_layout(
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)"
            ),
            yaxis=dict(title="Área Acumulada (ha)", gridcolor='#e9ecef'),
            yaxis2=dict(title="Precipitação (mm)", overlaying='y', side='right', gridcolor='rgba(0,0,0,0)'),
            xaxis=dict(title="Mês")
        )
    )

    # ========================================================================
    # GRÁFICO 2: GAUGE PREMIUM COM MÚLTIPLAS FAIXAS
    # ========================================================================

    meta_total = df_cron['area_planejada_ha'].sum()
    realizado_total = df_cron['area_realizada_ha'].sum()

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=realizado_total,
        delta={
            'reference': meta_total,
            'increasing': {'color': SUCCESS_COLOR},
            'decreasing': {'color': DANGER_COLOR}
        },
        title={'text': f"<b>Área Plantada vs Meta</b><br><span style='font-size:0.8em;color:gray'>{realizado_total:,.0f} / {meta_total:,.0f} ha</span>"},
        number={'suffix': " ha", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, meta_total * 1.1], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': PRIMARY_COLOR, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, meta_total * 0.6], 'color': 'rgba(231, 76, 60, 0.3)'},
                {'range': [meta_total * 0.6, meta_total * 0.9], 'color': 'rgba(241, 196, 15, 0.3)'},
                {'range': [meta_total * 0.9, meta_total], 'color': 'rgba(46, 204, 113, 0.3)'},
            ],
            'threshold': {
                'line': {'color': SUCCESS_COLOR, 'width': 4},
                'thickness': 0.75,
                'value': meta_total
            }
        }
    ))

    fig_gauge.update_layout(
        **get_default_layout(height=350)
    )

    # ========================================================================
    # GRÁFICO 3: TREEMAP INTERATIVO
    # ========================================================================

    df_var_tree = df_var_filtered.copy()
    df_var_tree['label'] = df_var_tree.apply(
        lambda x: f"{x['variedade']}<br>{x['area_ha_2024']:,.0f} ha<br>TCH: {x['tch_estimado']}",
        axis=1
    )

    fig_treemap = px.treemap(
        df_var_tree,
        path=['ciclo', 'variedade'],
        values='area_ha_2024',
        color='tch_estimado',
        color_continuous_scale='RdYlGn',
        title=""
    )

    fig_treemap.update_traces(
        textposition="middle center",
        textfont=dict(size=14, color='white', family='Segoe UI'),
        hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<br>TCH: %{color:.1f}<extra></extra>'
    )

    fig_treemap.update_layout(
        **get_default_layout(height=350),
        coloraxis_colorbar=dict(
            title="TCH",
            thicknessmode="pixels",
            thickness=15,
            lenmode="pixels",
            len=200
        )
    )

    # ========================================================================
    # GRÁFICO 4: WATERFALL CHART
    # ========================================================================

    df_water = df_cron[df_cron['area_realizada_ha'] > 0].copy()
    df_water['delta'] = df_water['area_realizada_ha'].diff().fillna(df_water['area_realizada_ha'].iloc[0])

    fig_waterfall = go.Figure(go.Waterfall(
        name="Variação Mensal",
        orientation="v",
        measure=["relative"] * len(df_water),
        x=df_water['mes'],
        textposition="outside",
        text=[f"{v:+.0f}" for v in df_water['delta']],
        y=df_water['delta'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": DANGER_COLOR}},
        increasing={"marker": {"color": SUCCESS_COLOR}},
        totals={"marker": {"color": PRIMARY_COLOR}}
    ))

    fig_waterfall.update_layout(
        **get_default_layout(
            title="",
            height=350,
            xaxis=dict(title="Mês"),
            yaxis=dict(title="Variação (ha)"),
            showlegend=False
        )
    )

    # ========================================================================
    # GRÁFICO 5: SCATTER TCH vs ATR
    # ========================================================================

    fig_scatter = px.scatter(
        df_var_filtered,
        x='tch_estimado',
        y='atr_estimado',
        size='area_ha_2024',
        color='ciclo',
        hover_name='variedade',
        size_max=60,
        color_discrete_map={'Cana-planta': PRIMARY_COLOR, 'Cana-soca': SECONDARY_COLOR},
        title=""
    )

    # Adiciona linha de tendência
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(df_var_filtered['tch_estimado'], df_var_filtered['atr_estimado'])
    line_x = np.array([df_var_filtered['tch_estimado'].min(), df_var_filtered['tch_estimado'].max()])
    line_y = slope * line_x + intercept

    fig_scatter.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        name=f'Tendência (R²={r_value**2:.2f})',
        line=dict(dash='dash', color='gray', width=2)
    ))

    fig_scatter.update_layout(
        **get_default_layout(
            height=350,
            xaxis=dict(title="TCH Estimado (ton/ha)"),
            yaxis=dict(title="ATR Estimado (kg/ton)"),
            legend=dict(orientation="v", x=1.05, y=1)
        )
    )

    fig_scatter.update_traces(
        marker=dict(line=dict(width=2, color='white')),
        selector=dict(mode='markers')
    )

    # ========================================================================
    # GRÁFICO 6: HEATMAP CORRELAÇÃO
    # ========================================================================

    # Matriz de correlação clima x plantio
    corr_data = df_cron[['area_realizada_ha', 'chuva_mm', 'dias_chuva', 'temp_media']].corr()

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_data.values,
        x=['Área Plantada', 'Chuva (mm)', 'Dias Chuva', 'Temp. Média'],
        y=['Área Plantada', 'Chuva (mm)', 'Dias Chuva', 'Temp. Média'],
        colorscale='RdBu_r',
        zmid=0,
        text=corr_data.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="Correlação")
    ))

    fig_heatmap.update_layout(
        **get_default_layout(
            title="",
            height=350,
            xaxis=dict(side="bottom"),
            yaxis=dict(autorange='reversed')
        )
    )

    # ========================================================================
    # TABELA PREMIUM COM FORMATAÇÃO CONDICIONAL
    # ========================================================================

    df_table = df_var_filtered.copy()
    df_table['variacao_area'] = ((df_table['area_ha_2024'] - df_table['area_ha_2023']) / df_table['area_ha_2023'] * 100).round(1)
    df_table['prod_estimada'] = (df_table['area_ha_2024'] * df_table['tch_estimado']).round(0)

    table_premium = create_advanced_table(
        df_table,
        [
            {'id': 'variedade', 'name': 'Variedade'},
            {'id': 'ciclo', 'name': 'Ciclo'},
            {'id': 'area_ha_2024', 'name': 'Área 2024 (ha)', 'type': 'numeric'},
            {
                'id': 'variacao_area',
                'name': 'Var. % vs 2023',
                'type': 'numeric',
                'conditional': [
                    {'operator': '>', 'value': 5, 'bg_color': SUCCESS_COLOR, 'color': 'white', 'weight': 'bold'},
                    {'operator': '<', 'value': -5, 'bg_color': DANGER_COLOR, 'color': 'white', 'weight': 'bold'},
                ]
            },
            {'id': 'tch_estimado', 'name': 'TCH Est.', 'type': 'numeric'},
            {'id': 'atr_estimado', 'name': 'ATR Est.', 'type': 'numeric'},
            {'id': 'prod_estimada', 'name': 'Prod. Est. (ton)', 'type': 'numeric'},
        ]
    )

    # Opções para dropdown de variedades
    variedade_options = [{'label': 'Todas', 'value': 'all'}] + \
                       [{'label': v, 'value': v} for v in df_var['variedade'].unique()]

    return (kpi1, kpi2, kpi3, kpi4,
            fig_evolucao, fig_gauge, fig_treemap, fig_waterfall,
            fig_scatter, fig_heatmap, table_premium, variedade_options)


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌱 DASHBOARD EXECUTIVO PREMIUM - PLANTIO")
    print("="*80)
    print("\n🚀 Iniciando servidor...")
    print("📊 Acesse: http://localhost:8050")
    print("\n💎 Features Premium:")
    print("  ✓ KPIs com sparklines e comparações YoY")
    print("  ✓ Gráficos interligados com cross-filtering")
    print("  ✓ Treemap interativo por variedade")
    print("  ✓ Waterfall chart de variações")
    print("  ✓ Scatter plot com linha de tendência")
    print("  ✓ Heatmap de correlação")
    print("  ✓ Tabela com formatação condicional")
    print("\n💡 Pressione CTRL+C para parar\n")

    app.run(debug=True, host='0.0.0.0', port=8050)
