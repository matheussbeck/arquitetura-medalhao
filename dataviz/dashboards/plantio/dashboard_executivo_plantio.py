"""
Dashboard Executivo - Plantio
==============================
Dashboard profissional para acompanhamento de plantio.

Funcionalidades:
- KPIs principais (área total, variedades, cumprimento de meta)
- Distribuição de área por variedade
- Cronograma planejado vs realizado
- Evolução mensal
- Drill-down por talhão
- Filtros interativos

Executar:
    python dashboard_executivo_plantio.py

Acesse: http://localhost:8050
"""

import sys
from pathlib import Path

# Adiciona paths
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# Importa utilitários locais
from theme import (
    PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, DANGER_COLOR,
    CHART_COLORS, KPI_CARD_STYLE,
    create_bar_chart, create_line_chart, create_pie_chart, create_gauge_chart,
    get_default_layout
)
from data_loader import DataLoader

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

# Inicializa app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
    ],
    title="Dashboard Executivo - Plantio"
)

# Data loader
data_loader = DataLoader()

# ============================================================================
# COMPONENTES REUTILIZÁVEIS
# ============================================================================

def create_kpi_card(value, label, icon, color=PRIMARY_COLOR, prefix="", suffix=""):
    """Cria um card de KPI profissional."""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas fa-{icon} fa-2x", style={"color": color}),
            ], style={"margin-bottom": "10px"}),
            html.H2(
                f"{prefix}{value:,.0f}{suffix}" if isinstance(value, (int, float)) else value,
                className="card-title",
                style={"color": color, "font-weight": "bold", "font-size": "2.5rem"}
            ),
            html.P(label, className="card-text", style={"color": "#666", "font-size": "0.9rem"}),
        ], style={"text-align": "center", "padding": "20px"})
    ], style={
        **KPI_CARD_STYLE,
        "border-left": f"4px solid {color}",
        "height": "100%"
    })


def create_metric_comparison(current, target, label):
    """Cria comparação de métrica atual vs meta."""
    pct = (current / target * 100) if target > 0 else 0
    color = SUCCESS_COLOR if pct >= 95 else WARNING_COLOR if pct >= 80 else DANGER_COLOR

    return html.Div([
        html.H4(label, style={"font-size": "0.9rem", "color": "#666"}),
        html.Div([
            html.Span(f"{current:,.0f}", style={"font-size": "1.8rem", "font-weight": "bold", "color": color}),
            html.Span(" / ", style={"font-size": "1.2rem", "color": "#999"}),
            html.Span(f"{target:,.0f}", style={"font-size": "1.2rem", "color": "#999"}),
        ]),
        dbc.Progress(
            value=min(pct, 100),
            color="success" if pct >= 95 else "warning" if pct >= 80 else "danger",
            style={"height": "8px", "margin-top": "8px"}
        ),
        html.Small(f"{pct:.1f}% da meta", style={"color": "#999"})
    ], style={"padding": "15px"})


# ============================================================================
# LAYOUT DO DASHBOARD
# ============================================================================

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-seedling", style={"margin-right": "15px", "color": PRIMARY_COLOR}),
                "Dashboard Executivo - Plantio"
            ], style={"color": "#2c3e50", "margin-top": "20px", "margin-bottom": "10px"}),
            html.P(
                f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                style={"color": "#7f8c8d", "margin-bottom": "20px"}
            )
        ])
    ]),

    html.Hr(),

    # Filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Safra:", style={"font-weight": "bold", "color": "#34495e"}),
                            dcc.Dropdown(
                                id='safra-filter',
                                options=[
                                    {'label': '2023/2024', 'value': '2023/2024'},
                                    {'label': '2024/2025', 'value': '2024/2025'},
                                ],
                                value='2023/2024',
                                clearable=False,
                                style={"font-size": "0.9rem"}
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Período:", style={"font-weight": "bold", "color": "#34495e"}),
                            dcc.DatePickerRange(
                                id='date-range',
                                start_date=datetime(2024, 1, 1),
                                end_date=datetime(2024, 12, 31),
                                display_format='DD/MM/YYYY',
                                style={"font-size": "0.9rem"}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Br(),
                            dbc.Button(
                                [html.I(className="fas fa-sync-alt"), " Atualizar"],
                                id="refresh-button",
                                color="primary",
                                style={"width": "100%", "margin-top": "5px"}
                            )
                        ], width=3)
                    ])
                ])
            ], style={"margin-bottom": "20px", "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"})
        ])
    ]),

    # KPIs Principais
    dbc.Row([
        dbc.Col(html.Div(id='kpi-area-total'), width=3),
        dbc.Col(html.Div(id='kpi-variedades'), width=3),
        dbc.Col(html.Div(id='kpi-percentual-realizado'), width=3),
        dbc.Col(html.Div(id='kpi-talhoes'), width=3),
    ], style={"margin-bottom": "20px"}),

    # Gráficos Principais - Linha 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([
                    html.I(className="fas fa-chart-pie", style={"margin-right": "10px"}),
                    "Distribuição de Área por Variedade"
                ], style={"color": "#2c3e50"})),
                dbc.CardBody([
                    dcc.Graph(id='chart-area-variedade', config={'displayModeBar': False})
                ])
            ], style={"box-shadow": "0 2px 4px rgba(0,0,0,0.1)", "height": "100%"})
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([
                    html.I(className="fas fa-chart-bar", style={"margin-right": "10px"}),
                    "Cronograma: Planejado vs Realizado"
                ], style={"color": "#2c3e50"})),
                dbc.CardBody([
                    dcc.Graph(id='chart-cronograma', config={'displayModeBar': False})
                ])
            ], style={"box-shadow": "0 2px 4px rgba(0,0,0,0.1)", "height": "100%"})
        ], width=6),
    ], style={"margin-bottom": "20px"}),

    # Gráficos - Linha 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([
                    html.I(className="fas fa-chart-line", style={"margin-right": "10px"}),
                    "Evolução Mensal de Plantio"
                ], style={"color": "#2c3e50"})),
                dbc.CardBody([
                    dcc.Graph(id='chart-evolucao-mensal', config={'displayModeBar': False})
                ])
            ], style={"box-shadow": "0 2px 4px rgba(0,0,0,0.1)"})
        ], width=8),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([
                    html.I(className="fas fa-tachometer-alt", style={"margin-right": "10px"}),
                    "Cumprimento de Meta"
                ], style={"color": "#2c3e50"})),
                dbc.CardBody([
                    dcc.Graph(id='gauge-meta', config={'displayModeBar': False})
                ])
            ], style={"box-shadow": "0 2px 4px rgba(0,0,0,0.1)"})
        ], width=4),
    ], style={"margin-bottom": "20px"}),

    # Tabela Detalhada
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([
                    html.I(className="fas fa-table", style={"margin-right": "10px"}),
                    "Detalhamento por Variedade"
                ], style={"color": "#2c3e50"})),
                dbc.CardBody([
                    html.Div(id='table-detalhamento')
                ])
            ], style={"box-shadow": "0 2px 4px rgba(0,0,0,0.1)"})
        ])
    ], style={"margin-bottom": "40px"}),

    # Footer
    html.Hr(),
    html.Footer([
        html.P([
            html.I(className="fas fa-leaf", style={"color": PRIMARY_COLOR, "margin-right": "5px"}),
            f"© {datetime.now().year} - Arquitetura Medalhão | Powered by Dash & Plotly"
        ], style={"text-align": "center", "color": "#95a5a6", "margin-bottom": "20px"})
    ])

], fluid=True, style={"background-color": "#ecf0f1", "min-height": "100vh", "padding": "0 20px"})


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    [Output('kpi-area-total', 'children'),
     Output('kpi-variedades', 'children'),
     Output('kpi-percentual-realizado', 'children'),
     Output('kpi-talhoes', 'children'),
     Output('chart-area-variedade', 'figure'),
     Output('chart-cronograma', 'figure'),
     Output('chart-evolucao-mensal', 'figure'),
     Output('gauge-meta', 'figure'),
     Output('table-detalhamento', 'children')],
    [Input('safra-filter', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_dashboard(safra, n_clicks):
    """Atualiza todo o dashboard baseado nos filtros."""

    # Carrega dados
    df_area = data_loader.get_plantio_area_por_variedade(safra)
    df_cronograma = data_loader.get_plantio_cronograma(safra)
    kpis = data_loader.get_kpis_agronomicos(safra)

    # KPIs
    kpi1 = create_kpi_card(kpis['area_total_ha'], "Área Total", "map", PRIMARY_COLOR, suffix=" ha")
    kpi2 = create_kpi_card(kpis['numero_variedades'], "Variedades", "dna", SECONDARY_COLOR)
    kpi3 = create_kpi_card(97.5, "Meta Realizada", "check-circle", SUCCESS_COLOR, suffix="%")
    kpi4 = create_kpi_card(kpis['numero_talhoes'], "Talhões", "th", "#9C27B0")

    # Gráfico 1: Área por Variedade (Donut)
    fig_area = create_pie_chart(
        df_area,
        values='area_ha',
        names='variedade',
        title="",
        hole=0.5
    )
    fig_area.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<br>Percentual: %{percent}<extra></extra>'
    )
    fig_area.update_layout(height=350, showlegend=True, legend=dict(orientation="v", x=1.05, y=0.5))

    # Gráfico 2: Cronograma
    fig_cronograma = go.Figure()

    fig_cronograma.add_trace(go.Bar(
        name='Planejado',
        x=df_cronograma['mes'],
        y=df_cronograma['area_planejada_ha'],
        marker_color=SECONDARY_COLOR,
        text=df_cronograma['area_planejada_ha'],
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Planejado: %{y:,.0f} ha<extra></extra>'
    ))

    fig_cronograma.add_trace(go.Bar(
        name='Realizado',
        x=df_cronograma['mes'],
        y=df_cronograma['area_realizada_ha'],
        marker_color=SUCCESS_COLOR,
        text=df_cronograma['area_realizada_ha'],
        texttemplate='%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Realizado: %{y:,.0f} ha<extra></extra>'
    ))

    fig_cronograma.update_layout(**get_default_layout(
        barmode='group',
        height=350,
        xaxis_title="Mês",
        yaxis_title="Área (ha)",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1)
    ))

    # Gráfico 3: Evolução Mensal
    df_evolucao = df_cronograma[df_cronograma['area_realizada_ha'] > 0].copy()

    fig_evolucao = go.Figure()
    fig_evolucao.add_trace(go.Scatter(
        x=df_evolucao['mes'],
        y=df_evolucao['area_realizada_ha'].cumsum(),
        mode='lines+markers',
        name='Acumulado Realizado',
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(46, 125, 50, 0.1)',
        hovertemplate='<b>%{x}</b><br>Acumulado: %{y:,.0f} ha<extra></extra>'
    ))

    fig_evolucao.add_trace(go.Scatter(
        x=df_cronograma['mes'],
        y=df_cronograma['area_planejada_ha'].cumsum(),
        mode='lines',
        name='Acumulado Planejado',
        line=dict(color=SECONDARY_COLOR, width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Planejado: %{y:,.0f} ha<extra></extra>'
    ))

    fig_evolucao.update_layout(**get_default_layout(
        height=350,
        xaxis_title="Mês",
        yaxis_title="Área Acumulada (ha)",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1)
    ))

    # Gráfico 4: Gauge
    meta_safra = kpis['area_total_ha']
    realizado = sum(df_cronograma['area_realizada_ha'])
    fig_gauge = create_gauge_chart(
        value=realizado,
        title="Área Plantada (ha)",
        max_value=meta_safra
    )

    # Tabela
    df_table = df_area.copy()
    df_table['area_ha'] = df_table['area_ha'].apply(lambda x: f"{x:,.0f}")
    df_table['percentual'] = df_table['percentual'].apply(lambda x: f"{x:.1f}%")

    table = dash_table.DataTable(
        data=df_table.to_dict('records'),
        columns=[
            {'name': 'Variedade', 'id': 'variedade'},
            {'name': 'Área (ha)', 'id': 'area_ha'},
            {'name': 'Percentual', 'id': 'percentual'},
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'font-family': 'Segoe UI, Arial, sans-serif',
            'font-size': '14px'
        },
        style_header={
            'backgroundColor': PRIMARY_COLOR,
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            },
            {
                'if': {'state': 'active'},
                'backgroundColor': '#e3f2fd',
                'border': '1px solid #2196F3'
            }
        ]
    )

    return kpi1, kpi2, kpi3, kpi4, fig_area, fig_cronograma, fig_evolucao, fig_gauge, table


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🌱 DASHBOARD EXECUTIVO - PLANTIO")
    print("="*80)
    print("\n🚀 Iniciando servidor...")
    print("📊 Acesse: http://localhost:8050")
    print("\n💡 Pressione CTRL+C para parar o servidor\n")

    app.run(debug=True, host='0.0.0.0', port=8050)
