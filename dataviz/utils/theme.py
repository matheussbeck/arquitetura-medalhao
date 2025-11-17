"""
Tema Corporativo para Dashboards
==================================
Define cores, estilos e layout padrão para todos os dashboards.
Inspirado nos melhores dashboards do Power BI.
"""

import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# PALETA DE CORES CORPORATIVA
# ============================================================================

# Cores Primárias (ajuste para as cores da sua empresa)
PRIMARY_COLOR = "#2E7D32"  # Verde (cana-de-açúcar)
SECONDARY_COLOR = "#1565C0"  # Azul
ACCENT_COLOR = "#F57C00"  # Laranja
SUCCESS_COLOR = "#43A047"  # Verde claro
WARNING_COLOR = "#FFA726"  # Amarelo/Laranja
DANGER_COLOR = "#E53935"  # Vermelho
INFO_COLOR = "#29B6F6"  # Azul claro

# Cores de Fundo
BACKGROUND_COLOR = "#F5F5F5"  # Cinza muito claro
CARD_BACKGROUND = "#FFFFFF"  # Branco
SIDEBAR_BACKGROUND = "#263238"  # Cinza escuro

# Cores de Texto
TEXT_PRIMARY = "#212121"  # Quase preto
TEXT_SECONDARY = "#757575"  # Cinza médio
TEXT_ON_PRIMARY = "#FFFFFF"  # Branco

# Paleta para Gráficos (tons de verde - agronegócio)
CHART_COLORS = [
    "#2E7D32",  # Verde escuro
    "#66BB6A",  # Verde médio
    "#A5D6A7",  # Verde claro
    "#1565C0",  # Azul
    "#42A5F5",  # Azul claro
    "#F57C00",  # Laranja
    "#FFB74D",  # Laranja claro
    "#7E57C2",  # Roxo
    "#BA68C8",  # Roxo claro
]

# Paleta Sequencial (para mapas de calor)
SEQUENTIAL_COLORS = px.colors.sequential.Greens

# Paleta Divergente (para comparações)
DIVERGENT_COLORS = px.colors.diverging.RdYlGn

# ============================================================================
# LAYOUT PADRÃO PLOTLY
# ============================================================================

PLOTLY_LAYOUT = {
    "font": {
        "family": "Segoe UI, Arial, sans-serif",
        "size": 12,
        "color": TEXT_PRIMARY
    },
    "plot_bgcolor": CARD_BACKGROUND,
    "paper_bgcolor": CARD_BACKGROUND,
    "hovermode": "closest",
    "hoverlabel": {
        "bgcolor": "white",
        "font_size": 13,
        "font_family": "Segoe UI"
    },
    "margin": {"l": 50, "r": 30, "t": 50, "b": 50},
}

# ============================================================================
# CONFIGURAÇÕES DE GRÁFICOS
# ============================================================================

def get_default_layout(**kwargs):
    """
    Retorna layout padrão para gráficos Plotly.

    Args:
        **kwargs: Sobrescreve valores padrão

    Returns:
        dict: Layout configurado
    """
    layout = PLOTLY_LAYOUT.copy()
    layout.update(kwargs)
    return layout


def create_kpi_card(value, label, icon=None, color=PRIMARY_COLOR, prefix="", suffix=""):
    """
    Cria um card de KPI estilizado.

    Args:
        value: Valor do KPI
        label: Rótulo do KPI
        icon: Ícone (opcional)
        color: Cor do card
        prefix: Prefixo (ex: "R$", "+")
        suffix: Sufixo (ex: "%", "ha")

    Returns:
        dict: Configuração do card
    """
    return {
        "value": f"{prefix}{value:,.0f}{suffix}" if isinstance(value, (int, float)) else value,
        "label": label,
        "icon": icon,
        "color": color
    }


# ============================================================================
# ESTILOS CSS
# ============================================================================

# CSS para Cards de KPI
KPI_CARD_STYLE = {
    "background": CARD_BACKGROUND,
    "border-radius": "8px",
    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)",
    "padding": "20px",
    "text-align": "center",
    "transition": "transform 0.2s, box-shadow 0.2s",
}

KPI_CARD_HOVER = {
    "transform": "translateY(-2px)",
    "box-shadow": "0 4px 8px rgba(0,0,0,0.15)"
}

# CSS para Filtros
FILTER_STYLE = {
    "background": CARD_BACKGROUND,
    "border-radius": "4px",
    "border": f"1px solid {TEXT_SECONDARY}",
    "padding": "8px 12px",
    "font-size": "14px"
}

# CSS para Sidebar
SIDEBAR_STYLE = {
    "background": SIDEBAR_BACKGROUND,
    "padding": "20px",
    "color": TEXT_ON_PRIMARY
}

# ============================================================================
# TEMPLATES DE GRÁFICOS
# ============================================================================

def create_bar_chart(df, x, y, title, color=None, orientation='v'):
    """
    Cria gráfico de barras estilizado.

    Args:
        df: DataFrame com dados
        x: Coluna do eixo X
        y: Coluna do eixo Y
        title: Título do gráfico
        color: Coluna para colorir (opcional)
        orientation: 'v' (vertical) ou 'h' (horizontal)

    Returns:
        plotly.graph_objects.Figure
    """
    if color:
        fig = px.bar(df, x=x, y=y, color=color,
                    title=title,
                    color_discrete_sequence=CHART_COLORS,
                    orientation=orientation)
    else:
        fig = px.bar(df, x=x, y=y,
                    title=title,
                    color_discrete_sequence=[PRIMARY_COLOR],
                    orientation=orientation)

    fig.update_layout(**get_default_layout(title={"font": {"size": 16, "color": TEXT_PRIMARY}}))
    fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside')

    return fig


def create_line_chart(df, x, y, title, color=None, markers=True):
    """
    Cria gráfico de linhas estilizado.

    Args:
        df: DataFrame com dados
        x: Coluna do eixo X
        y: Coluna do eixo Y
        title: Título do gráfico
        color: Coluna para múltiplas linhas (opcional)
        markers: Se deve mostrar marcadores

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.line(df, x=x, y=y, color=color,
                  title=title,
                  color_discrete_sequence=CHART_COLORS,
                  markers=markers)

    fig.update_layout(**get_default_layout(
        title={"font": {"size": 16, "color": TEXT_PRIMARY}},
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title()
    ))

    return fig


def create_pie_chart(df, values, names, title, hole=0.4):
    """
    Cria gráfico de pizza (donut) estilizado.

    Args:
        df: DataFrame com dados
        values: Coluna de valores
        names: Coluna de nomes
        title: Título do gráfico
        hole: Tamanho do buraco central (0-1, 0=pizza, >0=donut)

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.pie(df, values=values, names=names,
                 title=title,
                 color_discrete_sequence=CHART_COLORS,
                 hole=hole)

    fig.update_layout(**get_default_layout(title={"font": {"size": 16, "color": TEXT_PRIMARY}}))
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig


def create_scatter_plot(df, x, y, title, color=None, size=None, trendline=None):
    """
    Cria gráfico de dispersão estilizado.

    Args:
        df: DataFrame com dados
        x: Coluna do eixo X
        y: Coluna do eixo Y
        title: Título do gráfico
        color: Coluna para colorir pontos (opcional)
        size: Coluna para tamanho dos pontos (opcional)
        trendline: Tipo de linha de tendência ('ols', 'lowess', etc.)

    Returns:
        plotly.graph_objects.Figure
    """
    fig = px.scatter(df, x=x, y=y, color=color, size=size,
                    title=title,
                    color_discrete_sequence=CHART_COLORS,
                    trendline=trendline)

    fig.update_layout(**get_default_layout(title={"font": {"size": 16, "color": TEXT_PRIMARY}}))

    return fig


def create_heatmap(df, x, y, z, title, colorscale=None):
    """
    Cria mapa de calor estilizado.

    Args:
        df: DataFrame com dados
        x: Coluna do eixo X
        y: Coluna do eixo Y
        z: Coluna de valores
        title: Título do gráfico
        colorscale: Escala de cores (padrão: Greens)

    Returns:
        plotly.graph_objects.Figure
    """
    # Pivot dos dados
    pivot_df = df.pivot(index=y, columns=x, values=z)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale=colorscale or SEQUENTIAL_COLORS,
        text=pivot_df.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar={"title": z.replace("_", " ").title()}
    ))

    fig.update_layout(**get_default_layout(
        title=title,
        xaxis={"title": x.replace("_", " ").title()},
        yaxis={"title": y.replace("_", " ").title()}
    ))

    return fig


def create_gauge_chart(value, title, max_value, ranges=None):
    """
    Cria gráfico gauge (velocímetro) estilizado.

    Args:
        value: Valor atual
        title: Título do gauge
        max_value: Valor máximo
        ranges: Lista de dicts com 'range' e 'color' para faixas

    Returns:
        plotly.graph_objects.Figure
    """
    if ranges is None:
        ranges = [
            {'range': [0, max_value * 0.33], 'color': DANGER_COLOR},
            {'range': [max_value * 0.33, max_value * 0.66], 'color': WARNING_COLOR},
            {'range': [max_value * 0.66, max_value], 'color': SUCCESS_COLOR}
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title, 'font': {'size': 16}},
        delta={'reference': max_value * 0.8},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': PRIMARY_COLOR},
            'steps': ranges,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))

    fig.update_layout(**get_default_layout(height=250))

    return fig


# ============================================================================
# CONFIGURAÇÕES PARA TABELAS (AG Grid)
# ============================================================================

AG_GRID_DEFAULT_CONFIG = {
    "theme": "ag-theme-alpine",
    "defaultColDef": {
        "resizable": True,
        "sortable": True,
        "filter": True,
        "floatingFilter": True,
    },
    "enableEnterpriseModules": True,
    "pagination": True,
    "paginationPageSize": 20,
}
