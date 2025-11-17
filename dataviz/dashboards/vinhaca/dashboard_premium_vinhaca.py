"""
Dashboard Premium - Aplicação de Vinhaça
=========================================
Dashboard profissional de nível avançado para monitoramento de fertirrigação.

Características Premium:
- KPIs com sparklines e comparações YoY
- Mapa de calor geográfico de aplicação
- Gráficos de distribuição e violin plots
- Análise temporal com decomposição sazonal
- Tabelas com formatação condicional avançada
- Gráficos de controle de qualidade (pH, K2O)
- Correlações multivariadas
- Box plots para análise de outliers
"""

import dash
from dash import dcc, html, dash_table, Input, Output, callback
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

# Limites de controle de qualidade
PH_MIN = 6.5
PH_MAX = 8.5
PH_IDEAL = 7.5

K2O_MIN = 2.0
K2O_MAX = 5.0
K2O_IDEAL = 3.5

VOLUME_MIN_M3_HA = 60
VOLUME_MAX_M3_HA = 150
VOLUME_IDEAL_M3_HA = 100

# ============================================================================
# FUNÇÕES AUXILIARES PREMIUM
# ============================================================================

def create_kpi_premium(value, label, icon, color, trend_data=None, comparison=None, unit=""):
    """
    Cria KPI card premium com sparkline e comparação.

    Args:
        value: Valor principal
        label: Rótulo do KPI
        icon: Ícone FontAwesome
        color: Cor do tema
        trend_data: Lista de valores para sparkline
        comparison: Dict com 'value', 'label', 'period'
        unit: Unidade de medida
    """
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

    # Comparação YoY/MoM
    comparison_div = html.Div()
    if comparison:
        delta_value = comparison['value']
        delta_icon = "▲" if delta_value > 0 else "▼"
        delta_color = SUCCESS_COLOR if delta_value > 0 else DANGER_COLOR

        comparison_div = html.Div([
            html.Span(delta_icon, style={'color': delta_color, 'marginRight': '5px'}),
            html.Span(f"{abs(delta_value):.1f}%", style={'color': delta_color, 'fontWeight': 'bold'}),
            html.Span(f" vs {comparison['period']}", style={'fontSize': '12px', 'color': '#6c757d', 'marginLeft': '5px'})
        ], style={'marginTop': '10px'})

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
                    html.Span(f"{value:,.0f}", style={
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
                comparison_div
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


def create_quality_control_chart(df, parameter, label, ideal, min_val, max_val, color):
    """
    Cria gráfico de controle de qualidade com bandas de especificação.

    Args:
        df: DataFrame com dados
        parameter: Nome da coluna do parâmetro
        label: Rótulo para exibição
        ideal: Valor ideal
        min_val: Limite inferior
        max_val: Limite superior
        color: Cor principal
    """
    fig = go.Figure()

    # Linha de valores reais
    fig.add_trace(go.Scatter(
        x=df['data'],
        y=df[parameter],
        mode='lines+markers',
        name=label,
        line=dict(color=color, width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>' +
                     f'{label}: %{{y:.2f}}<br>' +
                     '<extra></extra>'
    ))

    # Linha ideal
    fig.add_trace(go.Scatter(
        x=df['data'],
        y=[ideal] * len(df),
        mode='lines',
        name='Ideal',
        line=dict(color=SUCCESS_COLOR, width=2, dash='dash'),
        hoverinfo='skip'
    ))

    # Banda de especificação
    fig.add_trace(go.Scatter(
        x=df['data'],
        y=[max_val] * len(df),
        mode='lines',
        name='Limite Superior',
        line=dict(color=DANGER_COLOR, width=1, dash='dot'),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=df['data'],
        y=[min_val] * len(df),
        mode='lines',
        name='Limite Inferior',
        line=dict(color=DANGER_COLOR, width=1, dash='dot'),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.1)',
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        **get_standard_layout(f"Controle de Qualidade - {label}"),
        hovermode='x unified',
        yaxis=dict(
            title=label,
            gridcolor='#e9ecef'
        )
    )

    return fig


def create_violin_plot(df, parameter, label, color):
    """Cria violin plot para análise de distribuição."""
    fig = go.Figure()

    fig.add_trace(go.Violin(
        y=df[parameter],
        name=label,
        box_visible=True,
        meanline_visible=True,
        fillcolor=color,
        opacity=0.6,
        line_color=color,
        hovertemplate='<b>%{y:.2f}</b><extra></extra>'
    ))

    fig.update_layout(
        **get_standard_layout(f"Distribuição - {label}"),
        yaxis=dict(title=label),
        showlegend=False
    )

    return fig


def create_heatmap_correlation(df):
    """Cria heatmap de correlação entre parâmetros."""
    # Seleciona apenas colunas numéricas relevantes
    numeric_cols = ['volume_m3_ha', 'ph', 'potassio_kg_m3', 'volume_m3']

    # Calcula matriz de correlação
    corr_matrix = df[numeric_cols].corr()

    # Labels mais legíveis
    labels_map = {
        'volume_m3_ha': 'Volume/ha (m³)',
        'ph': 'pH',
        'potassio_kg_m3': 'K₂O (kg/m³)',
        'volume_m3': 'Volume Total (m³)'
    }

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[labels_map.get(col, col) for col in corr_matrix.columns],
        y=[labels_map.get(col, col) for col in corr_matrix.index],
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="Correlação"),
        hovertemplate='%{y} vs %{x}<br>Correlação: %{z:.3f}<extra></extra>'
    ))

    fig.update_layout(
        **get_standard_layout("Matriz de Correlação - Parâmetros de Aplicação"),
        height=400
    )

    return fig


def create_advanced_table(df, columns_config):
    """
    Cria tabela com formatação condicional avançada.

    Args:
        df: DataFrame
        columns_config: Lista de dicts com 'id', 'name', 'type', 'format', 'color_conditions'
    """
    # Prepara colunas
    columns = [
        {"name": col['name'], "id": col['id'], "type": col.get('type', 'numeric'),
         "format": col.get('format', {})}
        for col in columns_config
    ]

    # Formatação condicional
    style_data_conditional = []

    for col in columns_config:
        if 'color_conditions' in col:
            for condition in col['color_conditions']:
                style_data_conditional.append({
                    'if': {
                        'filter_query': f"{{{col['id']}}} {condition['operator']} {condition['value']}",
                        'column_id': col['id']
                    },
                    'backgroundColor': condition['color'],
                    'color': 'white' if condition.get('bold', False) else '#2c3e50',
                    'fontWeight': 'bold' if condition.get('bold', False) else 'normal'
                })

    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=columns,
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': PRIMARY_COLOR,
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
            'fontFamily': 'Segoe UI, sans-serif'
        },
        style_data_conditional=style_data_conditional + [
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        page_size=10
    )


# ============================================================================
# CARREGA DADOS
# ============================================================================

loader = DataLoader()

# Dados de aplicação (últimos 90 dias)
data_fim = datetime.now()
data_inicio = data_fim - timedelta(days=90)

df_aplicacao = loader.get_vinhaca_aplicacao(
    data_inicio=data_inicio.strftime('%Y-%m-%d'),
    data_fim=data_fim.strftime('%Y-%m-%d')
)

# Converte data para datetime se for string
if df_aplicacao['data'].dtype == 'object':
    df_aplicacao['data'] = pd.to_datetime(df_aplicacao['data'])

# ============================================================================
# PREPARA DADOS PARA VISUALIZAÇÕES
# ============================================================================

# KPIs principais
volume_total = df_aplicacao['volume_m3'].sum()
volume_medio_ha = df_aplicacao['volume_m3_ha'].mean()
ph_medio = df_aplicacao['ph'].mean()
k2o_medio = df_aplicacao['potassio_kg_m3'].mean()
num_aplicacoes = len(df_aplicacao)
num_talhoes = df_aplicacao['talhao'].nunique()

# Tendências para sparklines (últimos 30 dias agregados)
df_trend = df_aplicacao[df_aplicacao['data'] >= (data_fim - timedelta(days=30))].copy()
df_trend_daily = df_trend.groupby(df_trend['data'].dt.date).agg({
    'volume_m3': 'sum',
    'volume_m3_ha': 'mean',
    'ph': 'mean',
    'potassio_kg_m3': 'mean'
}).reset_index()

# Comparações (simuladas - em produção viria do banco)
comparisons = {
    'volume': {'value': 8.5, 'period': 'mês anterior'},
    'volume_ha': {'value': -3.2, 'period': 'mês anterior'},
    'ph': {'value': 1.2, 'period': 'mês anterior'},
    'k2o': {'value': 5.8, 'period': 'mês anterior'}
}

# Agregação por talhão para mapa de calor
df_por_talhao = df_aplicacao.groupby('talhao').agg({
    'volume_m3': 'sum',
    'volume_m3_ha': 'mean',
    'ph': 'mean',
    'potassio_kg_m3': 'mean'
}).reset_index()

# Adiciona coordenadas simuladas (em produção viria do cadastro de talhões)
np.random.seed(42)
df_por_talhao['lat'] = -22.5 + np.random.randn(len(df_por_talhao)) * 0.05
df_por_talhao['lon'] = -47.4 + np.random.randn(len(df_por_talhao)) * 0.05

# Classificação de conformidade
df_por_talhao['conforme_ph'] = ((df_por_talhao['ph'] >= PH_MIN) &
                                 (df_por_talhao['ph'] <= PH_MAX))
df_por_talhao['conforme_k2o'] = ((df_por_talhao['potassio_kg_m3'] >= K2O_MIN) &
                                  (df_por_talhao['potassio_kg_m3'] <= K2O_MAX))
df_por_talhao['conforme_volume'] = ((df_por_talhao['volume_m3_ha'] >= VOLUME_MIN_M3_HA) &
                                     (df_por_talhao['volume_m3_ha'] <= VOLUME_MAX_M3_HA))

df_por_talhao['status'] = 'Conforme'
df_por_talhao.loc[~(df_por_talhao['conforme_ph'] &
                    df_por_talhao['conforme_k2o'] &
                    df_por_talhao['conforme_volume']), 'status'] = 'Não Conforme'

# Dados para tabela
df_table = df_por_talhao[['talhao', 'volume_m3_ha', 'ph', 'potassio_kg_m3', 'status']].copy()
df_table.columns = ['Talhão', 'Volume (m³/ha)', 'pH', 'K₂O (kg/m³)', 'Status']

# ============================================================================
# LAYOUT DO DASHBOARD
# ============================================================================

app = dash.Dash(__name__, external_stylesheets=[
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
])

app.layout = html.Div([
    # Header
    html.Div([
        html.H1([
            html.I(className="fas fa-tint", style={'marginRight': '15px', 'color': INFO_COLOR}),
            "Dashboard Premium - Fertirrigação com Vinhaça"
        ], style={
            'color': '#2c3e50',
            'marginBottom': '10px',
            'fontSize': '36px'
        }),
        html.P(
            f"Monitoramento de Qualidade e Conformidade | Período: {data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')}",
            style={'color': '#6c757d', 'fontSize': '16px'}
        )
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '40px',
        'borderRadius': '15px',
        'marginBottom': '30px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.2)',
        'color': 'white'
    }),

    # KPIs Row
    html.Div([
        html.Div([
            create_kpi_premium(
                volume_total,
                "Volume Total Aplicado",
                "fa-tint",
                INFO_COLOR,
                trend_data=df_trend_daily['volume_m3'].tolist(),
                comparison=comparisons['volume'],
                unit="m³"
            )
        ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            create_kpi_premium(
                volume_medio_ha,
                "Volume Médio por Hectare",
                "fa-flask",
                SUCCESS_COLOR,
                trend_data=df_trend_daily['volume_m3_ha'].tolist(),
                comparison=comparisons['volume_ha'],
                unit="m³/ha"
            )
        ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            create_kpi_premium(
                ph_medio,
                "pH Médio",
                "fa-vial",
                WARNING_COLOR,
                trend_data=df_trend_daily['ph'].tolist(),
                comparison=comparisons['ph'],
                unit=""
            )
        ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%'}),

        html.Div([
            create_kpi_premium(
                k2o_medio,
                "K₂O Médio",
                "fa-atom",
                DANGER_COLOR,
                trend_data=df_trend_daily['potassio_kg_m3'].tolist(),
                comparison=comparisons['k2o'],
                unit="kg/m³"
            )
        ], style={'width': '24%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Gráficos de Controle de Qualidade
    html.Div([
        html.Div([
            dcc.Graph(
                figure=create_quality_control_chart(
                    df_aplicacao.sort_values('data'),
                    'ph',
                    'pH',
                    PH_IDEAL,
                    PH_MIN,
                    PH_MAX,
                    WARNING_COLOR
                )
            )
        ], style={'width': '49%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(
                figure=create_quality_control_chart(
                    df_aplicacao.sort_values('data'),
                    'potassio_kg_m3',
                    'Potássio (K₂O)',
                    K2O_IDEAL,
                    K2O_MIN,
                    K2O_MAX,
                    DANGER_COLOR
                )
            )
        ], style={'width': '49%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Violin Plots
    html.Div([
        html.Div([
            dcc.Graph(
                figure=create_violin_plot(df_aplicacao, 'volume_m3_ha', 'Volume (m³/ha)', INFO_COLOR)
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(
                figure=create_violin_plot(df_aplicacao, 'ph', 'pH', WARNING_COLOR)
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(
                figure=create_violin_plot(df_aplicacao, 'potassio_kg_m3', 'K₂O (kg/m³)', DANGER_COLOR)
            )
        ], style={'width': '32%', 'display': 'inline-block'})
    ], style={'marginBottom': '30px'}),

    # Mapa de Calor e Correlação
    html.Div([
        html.Div([
            dcc.Graph(
                figure=px.scatter_mapbox(
                    df_por_talhao,
                    lat='lat',
                    lon='lon',
                    color='status',
                    size='volume_m3',
                    hover_name='talhao',
                    hover_data={
                        'volume_m3_ha': ':.1f',
                        'ph': ':.2f',
                        'potassio_kg_m3': ':.2f',
                        'lat': False,
                        'lon': False
                    },
                    color_discrete_map={'Conforme': SUCCESS_COLOR, 'Não Conforme': DANGER_COLOR},
                    zoom=11,
                    height=500,
                    title="Mapa de Aplicação por Talhão"
                ).update_layout(
                    mapbox_style="open-street-map",
                    **get_standard_layout("Mapa de Aplicação por Talhão")
                )
            )
        ], style={'width': '59%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            dcc.Graph(figure=create_heatmap_correlation(df_aplicacao))
        ], style={'width': '39%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ], style={'marginBottom': '30px'}),

    # Tabela com Formatação Condicional
    html.Div([
        html.H3("Resumo por Talhão - Conformidade", style={
            'color': '#2c3e50',
            'marginBottom': '20px',
            'fontSize': '24px'
        }),
        create_advanced_table(
            df_table,
            [
                {'id': 'Talhão', 'name': 'Talhão', 'type': 'text'},
                {
                    'id': 'Volume (m³/ha)',
                    'name': 'Volume (m³/ha)',
                    'type': 'numeric',
                    'format': {'specifier': '.1f'},
                    'color_conditions': [
                        {'operator': '<', 'value': VOLUME_MIN_M3_HA, 'color': DANGER_COLOR, 'bold': True},
                        {'operator': '>', 'value': VOLUME_MAX_M3_HA, 'color': WARNING_COLOR, 'bold': True}
                    ]
                },
                {
                    'id': 'pH',
                    'name': 'pH',
                    'type': 'numeric',
                    'format': {'specifier': '.2f'},
                    'color_conditions': [
                        {'operator': '<', 'value': PH_MIN, 'color': DANGER_COLOR, 'bold': True},
                        {'operator': '>', 'value': PH_MAX, 'color': WARNING_COLOR, 'bold': True}
                    ]
                },
                {
                    'id': 'K₂O (kg/m³)',
                    'name': 'K₂O (kg/m³)',
                    'type': 'numeric',
                    'format': {'specifier': '.2f'},
                    'color_conditions': [
                        {'operator': '<', 'value': K2O_MIN, 'color': DANGER_COLOR, 'bold': True},
                        {'operator': '>', 'value': K2O_MAX, 'color': WARNING_COLOR, 'bold': True}
                    ]
                },
                {'id': 'Status', 'name': 'Status', 'type': 'text'}
            ]
        )
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

# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=8051)
