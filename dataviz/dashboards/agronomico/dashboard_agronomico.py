"""
Dashboard Agronômico Completo
==============================
Análise integrada: Produtividade + Clima + Análises de Solo

Executar: python dashboard_agronomico.py
Acesse: http://localhost:8052
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta

from theme import *
from data_loader import DataLoader

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                title="Dashboard Agronômico")
data_loader = DataLoader()

app.layout = dbc.Container([
    # Header
    dbc.Row([dbc.Col([
        html.H1([html.I(className="fas fa-chart-area"), " Dashboard Agronômico"],
                style={"color": "#2c3e50", "margin": "20px 0"}),
    ])]),

    # KPIs Agronômicos
    dbc.Row([
        dbc.Col(html.Div(id='kpi-tch'), width=2),
        dbc.Col(html.Div(id='kpi-atr'), width=2),
        dbc.Col(html.Div(id='kpi-produtividade'), width=2),
        dbc.Col(html.Div(id='kpi-precipitacao'), width=3),
        dbc.Col(html.Div(id='kpi-temperatura'), width=3),
    ], style={"margin": "20px 0"}),

    # Gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([html.I(className="fas fa-chart-line"), " Evolução TCH"])),
                dbc.CardBody([dcc.Graph(id='chart-tch-evolucao')])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([html.I(className="fas fa-cloud-rain"), " Precipitação Mensal"])),
                dbc.CardBody([dcc.Graph(id='chart-precipitacao')])
            ])
        ], width=6),
    ], style={"margin-bottom": "20px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([html.I(className="fas fa-temperature-high"), " Temperatura x Produtividade"])),
                dbc.CardBody([dcc.Graph(id='chart-temp-prod')])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5([html.I(className="fas fa-tachometer-alt"), " ATR Médio"])),
                dbc.CardBody([dcc.Graph(id='gauge-atr')])
            ])
        ], width=4),
    ])

], fluid=True, style={"background": "#ecf0f1", "min-height": "100vh", "padding": "20px"})


@app.callback(
    [Output('kpi-tch', 'children'),
     Output('kpi-atr', 'children'),
     Output('kpi-produtividade', 'children'),
     Output('kpi-precipitacao', 'children'),
     Output('kpi-temperatura', 'children'),
     Output('chart-tch-evolucao', 'figure'),
     Output('chart-precipitacao', 'figure'),
     Output('chart-temp-prod', 'figure'),
     Output('gauge-atr', 'figure')],
    [Input('url', 'pathname')]
)
def update_dashboard(_):
    kpis = data_loader.get_kpis_agronomicos()
    df_clima = data_loader.get_dados_climaticos()

    # KPIs
    kpi1 = dbc.Card([dbc.CardBody([
        html.H3(f"{kpis['tch_medio']:.1f}", style={"color": PRIMARY_COLOR}),
        html.P("TCH Médio (ton/ha)")
    ])], style={**KPI_CARD_STYLE, "border-left": f"4px solid {PRIMARY_COLOR}"})

    kpi2 = dbc.Card([dbc.CardBody([
        html.H3(f"{kpis['atr_medio']:.1f}", style={"color": SECONDARY_COLOR}),
        html.P("ATR Médio (kg/ton)")
    ])], style={**KPI_CARD_STYLE, "border-left": f"4px solid {SECONDARY_COLOR}"})

    kpi3 = dbc.Card([dbc.CardBody([
        html.H3(f"{kpis['produtividade_toneladas']/1000:.0f}k", style={"color": SUCCESS_COLOR}),
        html.P("Produtividade (ton)")
    ])], style={**KPI_CARD_STYLE, "border-left": f"4px solid {SUCCESS_COLOR}"})

    precip_total = df_clima['precipitacao_mm'].sum()
    kpi4 = dbc.Card([dbc.CardBody([
        html.H3(f"{precip_total:,.0f}", style={"color": INFO_COLOR}),
        html.P("Precipitação Acumulada (mm)")
    ])], style={**KPI_CARD_STYLE, "border-left": f"4px solid {INFO_COLOR}"})

    temp_media = df_clima['temperatura_max_c'].mean()
    kpi5 = dbc.Card([dbc.CardBody([
        html.H3(f"{temp_media:.1f}°C", style={"color": WARNING_COLOR}),
        html.P("Temperatura Média Máxima")
    ])], style={**KPI_CARD_STYLE, "border-left": f"4px solid {WARNING_COLOR}"})

    # Gráfico 1: Evolução TCH (exemplo)
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago']
    tch_valores = [82, 84, 86, 85, 87, 88, 86, 85]
    fig1 = create_line_chart(
        pd.DataFrame({'mes': meses, 'tch': tch_valores}),
        'mes', 'tch', '', markers=True
    )

    # Gráfico 2: Precipitação
    df_clima_monthly = df_clima.groupby(df_clima['data'].dt.month)['precipitacao_mm'].sum().reset_index()
    df_clima_monthly['mes'] = df_clima_monthly['data'].apply(lambda x: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][x-1])
    fig2 = create_bar_chart(df_clima_monthly, 'mes', 'precipitacao_mm', '')

    # Gráfico 3: Scatter Temp x Produtividade
    df_scatter = pd.DataFrame({
        'temperatura': df_clima['temperatura_max_c'].sample(50).values,
        'tch': 70 + (pd.Series(range(50)) % 30).values
    })
    fig3 = create_scatter_plot(df_scatter, 'temperatura', 'tch', '', trendline='ols')

    # Gauge ATR
    fig4 = create_gauge_chart(kpis['atr_medio'], "ATR Médio", 160)

    return kpi1, kpi2, kpi3, kpi4, kpi5, fig1, fig2, fig3, fig4


app.layout.children.insert(0, dcc.Location(id='url', refresh=False))

if __name__ == '__main__':
    print("\n🚀 Dashboard Agronômico - http://localhost:8052\n")
    app.run_server(debug=True, host='0.0.0.0', port=8052)
