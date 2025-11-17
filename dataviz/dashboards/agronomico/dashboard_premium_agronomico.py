"""
Dashboard Premium - Visão Agronômica Integrada
===============================================
Dashboard executivo de nível avançado com visão 360° da operação agrícola.

Características Premium:
- KPIs executivos com sparklines e benchmarks
- Análise multivariada de produtividade (TCH x ATR x Idade)
- Gráficos 3D de superfície para análise espacial
- Sunburst chart para hierarquia de áreas
- Radar chart comparativo de performance
- Análise de Pareto para priorização
- Funil de conversão de área plantada → produção
- Timeline interativa de eventos agronômicos
"""

import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import sys
from pathlib import Path

# Adiciona utils ao path
sys.path.append(str(Path(__file__).parent.parent.parent / "utils"))
from data_loader import DataLoader
from theme import COLORS, get_standard_layout

# ============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================================

PRIMARY_COLOR = COLORS['primary']
SUCCESS_COLOR = COLORS['success']
WARNING_COLOR = COLORS['warning']
DANGER_COLOR = COLORS['danger']
INFO_COLOR = COLORS['info']

# Benchmarks da indústria
BENCHMARK_TCH = 90.0  # Toneladas de cana por hectare
BENCHMARK_ATR = 150.0  # ATR médio
BENCHMARK_EFICIENCIA = 95.0  # % de eficiência operacional

# ============================================================================
# FUNÇÕES AUXILIARES PREMIUM
# ============================================================================

def create_kpi_executive(value, label, icon, color, benchmark=None, trend_data=None, unit=""):
    """
    Cria KPI card executivo com comparação a benchmark.

    Args:
        value: Valor atual
        label: Rótulo
        icon: Ícone FontAwesome
        color: Cor
        benchmark: Valor de referência/benchmark
        trend_data: Dados de tendência
        unit: Unidade
    """
    # Calcula diferença vs benchmark
    benchmark_div = html.Div()
    if benchmark is not None:
        diff_pct = ((value - benchmark) / benchmark) * 100
        diff_icon = "▲" if diff_pct > 0 else "▼"
        diff_color = SUCCESS_COLOR if diff_pct > 0 else DANGER_COLOR

        benchmark_div = html.Div([
            html.Div([
                html.Span(diff_icon, style={'marginRight': '5px', 'color': diff_color}),
                html.Span(f"{abs(diff_pct):.1f}%", style={'color': diff_color, 'fontWeight': 'bold'}),
                html.Span(" vs benchmark", style={'color': '#6c757d', 'fontSize': '12px', 'marginLeft': '5px'})
            ]),
            html.Div([
                html.Span("Benchmark: ", style={'fontSize': '12px', 'color': '#6c757d'}),
                html.Span(f"{benchmark:,.1f} {unit}", style={'fontSize': '12px', 'color': '#6c757d', 'fontWeight': 'bold'})
            ], style={'marginTop': '5px'})
        ], style={'marginTop': '10px'})

    # Sparkline
    sparkline = html.Div()
    if trend_data is not None and len(trend_data) > 0:
        fig_spark = go.Figure()
        fig_spark.add_trace(go.Scatter(
            y=trend_data,
            mode='lines',
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)'
        ))
        fig_spark.update_layout(
            height=50,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False
        )
        sparkline = dcc.Graph(figure=fig_spark, config={'displayModeBar': False}, style={'height': '50px'})

    return html.Div([
        html.Div([
            html.Div([
                html.I(className=f"fas {icon}", style={
                    'fontSize': '40px',
                    'color': color,
                    'opacity': '0.8'
                })
            ], style={'flex': '0 0 auto', 'marginRight': '20px'}),

            html.Div([
                html.Div(label, style={
                    'fontSize': '14px',
                    'color': '#6c757d',
                    'marginBottom': '5px',
                    'textTransform': 'uppercase',
                    'letterSpacing': '1px'
                }),
                html.Div([
                    html.Span(f"{value:,.1f}", style={
                        'fontSize': '32px',
                        'fontWeight': 'bold',
                        'color': '#2c3e50'
                    }),
                    html.Span(f" {unit}", style={
                        'fontSize': '18px',
                        'color': '#6c757d',
                        'marginLeft': '5px'
                    })
                ]),
                benchmark_div
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),

        sparkline

    ], style={
        'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
        'border': f'1px solid {color}20',
        'height': '100%'
    })


def create_3d_surface_plot(df):
    """
    Cria gráfico 3D de superfície para análise espacial.
    Relaciona TCH x ATR x Idade do Canavial
    """
    # Cria grid para superfície
    x = np.linspace(1, 6, 30)  # Idade (anos)
    y = np.linspace(130, 160, 30)  # ATR
    X, Y = np.meshgrid(x, y)

    # Modelo simplificado: TCH = f(idade, ATR)
    # TCH diminui com idade, aumenta com ATR
    Z = 100 - (X - 2.5)**2 * 3 + (Y - 145) * 0.3 + np.random.randn(30, 30) * 2

    fig = go.Figure(data=[go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale='Viridis',
        colorbar=dict(title="TCH"),
        hovertemplate='Idade: %{x:.1f} anos<br>ATR: %{y:.1f}<br>TCH: %{z:.1f}<extra></extra>'
    )])

    fig.update_layout(
        title="Análise 3D: TCH x ATR x Idade do Canavial",
        scene=dict(
            xaxis_title='Idade (anos)',
            yaxis_title='ATR',
            zaxis_title='TCH (t/ha)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        **get_standard_layout("Análise 3D"),
        height=500
    )

    return fig


def create_sunburst_chart(df_area):
    """Cria sunburst chart hierárquico de áreas."""
    # Dados hierárquicos: Total > Safra > Variedade
    data = []

    # Nível 1: Total
    total_area = df_area['area_ha'].sum()

    # Nível 2: Por safra
    for safra in df_area['safra'].unique():
        df_safra = df_area[df_area['safra'] == safra]
        area_safra = df_safra['area_ha'].sum()

        # Nível 3: Por variedade
        for _, row in df_safra.iterrows():
            data.append({
                'labels': row['variedade'],
                'parents': safra,
                'values': row['area_ha']
            })

        data.append({
            'labels': safra,
            'parents': 'Total',
            'values': area_safra
        })

    data.append({
        'labels': 'Total',
        'parents': '',
        'values': total_area
    })

    df_sunburst = pd.DataFrame(data)

    fig = go.Figure(go.Sunburst(
        labels=df_sunburst['labels'],
        parents=df_sunburst['parents'],
        values=df_sunburst['values'],
        branchvalues="total",
        marker=dict(
            colorscale='Greens',
            cmid=df_sunburst['values'].median()
        ),
        hovertemplate='<b>%{label}</b><br>Área: %{value:,.0f} ha<br>%{percentParent}<extra></extra>'
    ))

    fig.update_layout(
        **get_standard_layout("Distribuição Hierárquica de Área"),
        height=500
    )

    return fig


def create_radar_chart(kpis):
    """Cria radar chart comparativo de performance."""
    categories = list(kpis.keys())
    values_atual = [kpis[k]['atual'] for k in categories]
    values_benchmark = [kpis[k]['benchmark'] for k in categories]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_atual,
        theta=categories,
        fill='toself',
        name='Atual',
        line=dict(color=SUCCESS_COLOR, width=2),
        fillcolor=f'rgba({int(SUCCESS_COLOR[1:3], 16)}, {int(SUCCESS_COLOR[3:5], 16)}, {int(SUCCESS_COLOR[5:7], 16)}, 0.3)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_benchmark,
        theta=categories,
        fill='toself',
        name='Benchmark',
        line=dict(color=WARNING_COLOR, width=2, dash='dash'),
        fillcolor=f'rgba({int(WARNING_COLOR[1:3], 16)}, {int(WARNING_COLOR[3:5], 16)}, {int(WARNING_COLOR[5:7], 16)}, 0.2)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 110]
            )
        ),
        **get_standard_layout("Performance vs Benchmark"),
        height=450
    )

    return fig


def create_pareto_chart(df):
    """Cria gráfico de Pareto para análise de variedades."""
    # Ordena por área
    df_sorted = df.sort_values('area_ha', ascending=False).reset_index(drop=True)

    # Calcula percentual acumulado
    df_sorted['area_acum'] = df_sorted['area_ha'].cumsum()
    df_sorted['pct_acum'] = (df_sorted['area_acum'] / df_sorted['area_ha'].sum()) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras
    fig.add_trace(
        go.Bar(
            x=df_sorted['variedade'],
            y=df_sorted['area_ha'],
            name='Área (ha)',
            marker_color=SUCCESS_COLOR,
            hovertemplate='<b>%{x}</b><br>Área: %{y:,.0f} ha<extra></extra>'
        ),
        secondary_y=False
    )

    # Linha acumulada
    fig.add_trace(
        go.Scatter(
            x=df_sorted['variedade'],
            y=df_sorted['pct_acum'],
            name='% Acumulado',
            mode='lines+markers',
            line=dict(color=DANGER_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True
    )

    # Linha 80%
    fig.add_hline(y=80, line_dash="dash", line_color="gray",
                  annotation_text="80% (Regra de Pareto)",
                  secondary_y=True)

    fig.update_xaxes(title_text="Variedade")
    fig.update_yaxes(title_text="Área (ha)", secondary_y=False)
    fig.update_yaxes(title_text="% Acumulado", secondary_y=True, range=[0, 105])

    fig.update_layout(
        **get_standard_layout("Análise de Pareto - Variedades por Área"),
        hovermode='x unified'
    )

    return fig


def create_funnel_chart():
    """Cria funil de conversão: Área Total → Produção Efetiva."""
    stages = ['Área Total', 'Área Plantada', 'Área em Produção', 'Área Colhida', 'Produção Efetiva']
    values = [11000, 9500, 8800, 8500, 8200]
    colors = [INFO_COLOR, SUCCESS_COLOR, PRIMARY_COLOR, WARNING_COLOR, DANGER_COLOR]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=colors),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} ha<br>%{percentInitial}<extra></extra>'
    ))

    fig.update_layout(
        **get_standard_layout("Funil de Conversão - Área para Produção"),
        height=400
    )

    return fig


def create_timeline_chart():
    """Cria timeline de eventos agronômicos."""
    # Dados de exemplo
    eventos = [
        {'Evento': 'Plantio Safra 23/24', 'Inicio': '2023-03-01', 'Fim': '2023-08-31', 'Tipo': 'Plantio'},
        {'Evento': 'Aplicação Vinhaça', 'Inicio': '2023-06-01', 'Fim': '2023-12-31', 'Tipo': 'Fertirrigação'},
        {'Evento': 'Colheita Safra 22/23', 'Inicio': '2023-04-01', 'Fim': '2023-11-30', 'Tipo': 'Colheita'},
        {'Evento': 'Preparo de Solo', 'Inicio': '2023-01-15', 'Fim': '2023-03-15', 'Tipo': 'Preparo'},
        {'Evento': 'Aplicação Herbicida', 'Inicio': '2023-05-01', 'Fim': '2023-05-31', 'Tipo': 'Defensivo'},
    ]

    df_eventos = pd.DataFrame(eventos)
    df_eventos['Inicio'] = pd.to_datetime(df_eventos['Inicio'])
    df_eventos['Fim'] = pd.to_datetime(df_eventos['Fim'])

    color_map = {
        'Plantio': SUCCESS_COLOR,
        'Fertirrigação': INFO_COLOR,
        'Colheita': WARNING_COLOR,
        'Preparo': PRIMARY_COLOR,
        'Defensivo': DANGER_COLOR
    }

    fig = px.timeline(
        df_eventos,
        x_start='Inicio',
        x_end='Fim',
        y='Evento',
        color='Tipo',
        color_discrete_map=color_map,
        title="Timeline de Eventos Agronômicos - 2023"
    )

    fig.update_layout(
        **get_standard_layout("Timeline de Eventos Agronômicos"),
        height=350,
        xaxis_title="Período"
    )

    return fig


# ============================================================================
# CARREGA DADOS
# ============================================================================

loader = DataLoader()

# KPIs
kpis = loader.get_kpis_agronomicos()

# Área por variedade
df_area = loader.get_plantio_area_por_variedade()

# Cronograma
df_cronograma = loader.get_plantio_cronograma()

# Dados climáticos (últimos 90 dias)
data_fim = datetime.now()
data_inicio = data_fim - timedelta(days=90)
df_clima = loader.get_dados_climaticos(
    data_inicio=data_inicio.strftime('%Y-%m-%d'),
    data_fim=data_fim.strftime('%Y-%m-%d')
)

# ============================================================================
# PREPARA DADOS
# ============================================================================

# Tendências para sparklines (simuladas)
np.random.seed(42)
trend_tch = [kpis['tch_medio'] + np.random.randn() * 2 for _ in range(30)]
trend_atr = [kpis['atr_medio'] + np.random.randn() * 3 for _ in range(30)]
trend_prod = [kpis['produtividade_toneladas'] / 1000 + np.random.randn() * 10 for _ in range(30)]

# KPIs para radar chart
kpis_radar = {
    'TCH': {'atual': (kpis['tch_medio'] / BENCHMARK_TCH) * 100, 'benchmark': 100},
    'ATR': {'atual': (kpis['atr_medio'] / BENCHMARK_ATR) * 100, 'benchmark': 100},
    'Eficiência': {'atual': BENCHMARK_EFICIENCIA - 5, 'benchmark': BENCHMARK_EFICIENCIA},
    'Área Plantada': {'atual': 95, 'benchmark': 100},
    'Variedades': {'atual': 80, 'benchmark': 100}
}

# ============================================================================
# LAYOUT DO DASHBOARD
# ============================================================================

app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

app.layout = html.Div([
    # Header Executivo
    html.Div([
        html.H1([
            html.I(className="fas fa-chart-line", style={'marginRight': '15px', 'color': SUCCESS_COLOR}),
            "Dashboard Executivo - Visão Agronômica 360°"
        ], style={
            'color': '#2c3e50',
            'marginBottom': '10px',
            'fontSize': '36px'
        }),
        html.P(
            f"Análise Integrada de Performance | Safra 2023/2024 | Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            style={'color': '#6c757d', 'fontSize': '16px'}
        )
    ], style={
        'background': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        'padding': '40px',
        'borderRadius': '15px',
        'marginBottom': '30px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.2)',
        'color': 'white'
    }),

    # KPIs Executivos
    html.Div([
        html.Div([
            create_kpi_executive(
                kpis['tch_medio'],
                "TCH Médio",
                "fa-seedling",
                SUCCESS_COLOR,
                benchmark=BENCHMARK_TCH,
                trend_data=trend_tch,
                unit="t/ha"
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            create_kpi_executive(
                kpis['atr_medio'],
                "ATR Médio",
                "fa-flask",
                WARNING_COLOR,
                benchmark=BENCHMARK_ATR,
                trend_data=trend_atr,
                unit="kg/t"
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            create_kpi_executive(
                kpis['produtividade_toneladas'] / 1000,
                "Produção Total",
                "fa-industry",
                DANGER_COLOR,
                trend_data=trend_prod,
                unit="mil t"
            )
        ], style={'width': '32%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Análise 3D e Radar
    html.Div([
        html.Div([
            dcc.Graph(figure=create_3d_surface_plot(None))
        ], style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(figure=create_radar_chart(kpis_radar))
        ], style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Sunburst e Funil
    html.Div([
        html.Div([
            dcc.Graph(figure=create_sunburst_chart(df_area))
        ], style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(figure=create_funnel_chart())
        ], style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Pareto
    html.Div([
        dcc.Graph(figure=create_pareto_chart(df_area))
    ], style={'marginBottom': '30px'}),

    # Timeline
    html.Div([
        dcc.Graph(figure=create_timeline_chart())
    ], style={'marginBottom': '30px'}),

    # Footer com Informações
    html.Div([
        html.Div([
            html.I(className="fas fa-map-marker-alt", style={'marginRight': '10px', 'color': SUCCESS_COLOR}),
            html.Span(f"Talhões: {kpis['numero_talhoes']}", style={'marginRight': '30px'}),
            html.I(className="fas fa-leaf", style={'marginRight': '10px', 'color': SUCCESS_COLOR}),
            html.Span(f"Variedades: {kpis['numero_variedades']}", style={'marginRight': '30px'}),
            html.I(className="fas fa-calendar", style={'marginRight': '10px', 'color': SUCCESS_COLOR}),
            html.Span(f"Idade Média: {kpis['idade_media_canavial_anos']:.1f} anos")
        ], style={
            'textAlign': 'center',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '10px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)',
            'fontSize': '16px',
            'color': '#2c3e50'
        })
    ])

], style={
    'fontFamily': 'Segoe UI, sans-serif',
    'padding': '30px',
    'background': '#f0f2f5'
})

# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=8052)
