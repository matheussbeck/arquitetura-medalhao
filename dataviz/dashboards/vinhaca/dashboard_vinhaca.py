"""
Dashboard Profissional - Análise de Vinhaça
============================================
Dashboard para monitoramento de aplicação de vinhaça e qualidade.

Executar: python dashboard_vinhaca.py
Acesse: http://localhost:8051
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

from theme import *
from data_loader import DataLoader

# Init
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                title="Dashboard Vinhaça")
data_loader = DataLoader()

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([dbc.Col([
        html.H1([html.I(className="fas fa-tint"), " Dashboard - Vinhaça"],
                style={"color": "#2c3e50", "margin": "20px 0"}),
    ])]),

    html.Hr(),

    # Filtros
    dbc.Row([dbc.Col([
        dbc.Card([dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Período:", style={"font-weight": "bold"}),
                    dcc.DatePickerRange(
                        id='date-range-vinhaca',
                        start_date=datetime.now() - timedelta(days=30),
                        end_date=datetime.now(),
                        display_format='DD/MM/YYYY'
                    )
                ], width=6),
                dbc.Col([
                    html.Br(),
                    dbc.Button("Atualizar", id="refresh-vinhaca", color="primary")
                ], width=3)
            ])
        ])])
    ])], style={"margin-bottom": "20px"}),

    # KPIs
    dbc.Row([
        dbc.Col(html.Div(id='kpi-volume-total'), width=3),
        dbc.Col(html.Div(id='kpi-volume-medio'), width=3),
        dbc.Col(html.Div(id='kpi-ph-medio'), width=3),
        dbc.Col(html.Div(id='kpi-potassio-medio'), width=3),
    ], style={"margin-bottom": "20px"}),

    # Gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Volume Aplicado por Dia")),
                dbc.CardBody([dcc.Graph(id='chart-volume-dia')])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Distribuição de pH")),
                dbc.CardBody([dcc.Graph(id='chart-ph-dist')])
            ])
        ], width=4),
    ], style={"margin-bottom": "20px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Mapa de Calor - Volume x Potássio")),
                dbc.CardBody([dcc.Graph(id='chart-heatmap')])
            ])
        ])
    ])

], fluid=True, style={"background": "#ecf0f1", "min-height": "100vh", "padding": "20px"})


@app.callback(
    [Output('kpi-volume-total', 'children'),
     Output('kpi-volume-medio', 'children'),
     Output('kpi-ph-medio', 'children'),
     Output('kpi-potassio-medio', 'children'),
     Output('chart-volume-dia', 'figure'),
     Output('chart-ph-dist', 'figure'),
     Output('chart-heatmap', 'figure')],
    [Input('refresh-vinhaca', 'n_clicks')]
)
def update_dashboard(n_clicks):
    df = data_loader.get_vinhaca_aplicacao()

    # KPIs
    kpi1 = dbc.Card([dbc.CardBody([
        html.H3(f"{df['volume_m3'].sum():,.0f}", style={"color": PRIMARY_COLOR}),
        html.P("Volume Total (m³)")
    ])], style=KPI_CARD_STYLE)

    kpi2 = dbc.Card([dbc.CardBody([
        html.H3(f"{df['volume_m3_ha'].mean():.1f}", style={"color": SECONDARY_COLOR}),
        html.P("Volume Médio (m³/ha)")
    ])], style=KPI_CARD_STYLE)

    kpi3 = dbc.Card([dbc.CardBody([
        html.H3(f"{df['ph'].mean():.2f}", style={"color": SUCCESS_COLOR}),
        html.P("pH Médio")
    ])], style=KPI_CARD_STYLE)

    kpi4 = dbc.Card([dbc.CardBody([
        html.H3(f"{df['potassio_kg_m3'].mean():.2f}", style={"color": ACCENT_COLOR}),
        html.P("Potássio Médio (kg/m³)")
    ])], style=KPI_CARD_STYLE)

    # Gráfico 1: Volume por dia
    df_daily = df.groupby('data')['volume_m3'].sum().reset_index()
    fig1 = create_line_chart(df_daily, 'data', 'volume_m3', 'Volume Diário de Vinhaça', markers=True)

    # Gráfico 2: Distribuição pH
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(x=df['ph'], nbinsx=20, marker_color=SUCCESS_COLOR))
    fig2.update_layout(**get_default_layout(title="Distribuição de pH",
                                           xaxis_title="pH", yaxis_title="Frequência"))

    # Gráfico 3: Heatmap
    df_sample = df.sample(min(100, len(df)))
    fig3 = px.scatter(df_sample, x='volume_m3_ha', y='potassio_kg_m3',
                      color='ph', size='volume_m3',
                      title="Volume x Potássio (colorido por pH)",
                      color_continuous_scale=SEQUENTIAL_COLORS)
    fig3.update_layout(**get_default_layout())

    return kpi1, kpi2, kpi3, kpi4, fig1, fig2, fig3


if __name__ == '__main__':
    print("\n🚀 Dashboard Vinhaça - http://localhost:8051\n")
    app.run_server(debug=True, host='0.0.0.0', port=8051)
