import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def grafico_distribucion_promedio(df: pd.DataFrame):
    """Genera un histograma interactivo de la distribución de promedios de notas."""
    fig = px.histogram(
        df,
        x="Promedio",
        nbins=20,
        title="Distribución General de Promedios",
        labels={"Promedio": "Promedio Final (0-20)"},
        color_discrete_sequence=["#3A86C8"],
        marginal="box", # Añade un diagrama de caja arriba
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis=dict(range=[0, 20.5]),
        yaxis_title="Cantidad de Estudiantes",
        title_font_size=20
    )
    return fig

def grafico_asistencia_vs_promedio(df: pd.DataFrame):
    """Genera un diagrama de dispersión de Asistencia vs Promedio coloreado por Nivel de Riesgo."""
    # Mapeo de colores coherente y estético
    colores = {"Alto": "#EF553B", "Medio": "#FECB52", "Bajo": "#00CC96"}
    
    fig = px.scatter(
        df,
        x="Asistencia_%",
        y="Promedio",
        color="Nivel_Riesgo",
        color_discrete_map=colores,
        title="Correlación: Asistencia vs. Promedio Académico",
        labels={
            "Asistencia_%": "Porcentaje de Asistencia (%)",
            "Promedio": "Promedio Académico",
            "Nivel_Riesgo": "Nivel de Riesgo"
        },
        hover_data=["Nombre", "Carrera"],
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis=dict(range=[0, 105]),
        yaxis=dict(range=[0, 21.5]),
        title_font_size=20
    )
    return fig

def grafico_riesgo_por_carrera(df: pd.DataFrame):
    """Genera un gráfico de barras apiladas de la cantidad de estudiantes por riesgo en cada carrera."""
    colores = {"Alto": "#EF553B", "Medio": "#FECB52", "Bajo": "#00CC96"}
    
    # Agrupamos por carrera y nivel de riesgo
    df_grouped = df.groupby(["Carrera", "Nivel_Riesgo"]).size().reset_index(name="Cantidad")
    
    fig = px.bar(
        df_grouped,
        x="Carrera",
        y="Cantidad",
        color="Nivel_Riesgo",
        color_discrete_map=colores,
        title="Distribución de Riesgo por Carrera Profesional",
        labels={"Cantidad": "Número de Estudiantes", "Nivel_Riesgo": "Nivel de Riesgo"},
        barmode="stack",
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_title="Carrera Profesional",
        yaxis_title="Cantidad de Alumnos",
        title_font_size=20
    )
    return fig

def grafico_horas_estudio_vs_promedio(df: pd.DataFrame):
    """Genera una línea de tendencia o scatter plot de Horas de estudio vs Promedio."""
    fig = px.scatter(
        df,
        x="Horas_Estudio_Semana",
        y="Promedio",
        trendline="ols", # Línea de regresión lineal por mínimos cuadrados
        title="Impacto del Tiempo de Estudio en las Notas",
        labels={"Horas_Estudio_Semana": "Horas de Estudio por Semana", "Promedio": "Promedio"},
        color_discrete_sequence=["#AB63FA"],
        hover_data=["Nombre"],
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis=dict(range=[0, df["Horas_Estudio_Semana"].max() + 2]),
        yaxis=dict(range=[0, 21.5]),
        title_font_size=20
    )
    return fig
