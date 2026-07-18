import os
import streamlit as st
import pandas as pd
import numpy as np
from datos.generador_datos import generar_datos_sinteticos
from src.analitica import (
    ejecutar_pipeline_limpieza, 
    agregar_analitica_riesgo, 
    filtrar_estudiantes_por_riesgo,
    verificar_swipl_instalado,
    consultar_riesgo_prolog
)
from src.modelos import Estudiante, ReporteCarrera, NOTA_APROBATORIA
from src.graficos import (
    grafico_distribucion_promedio,
    grafico_asistencia_vs_promedio,
    grafico_riesgo_por_carrera,
    grafico_horas_estudio_vs_promedio
)

# Configuración de página con tema oscuro/moderno
st.set_page_config(
    page_title="EduAnalytics - Alerta Académica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para estética premium (diseño fluido, tarjetas con sombras, bordes redondeados)
st.markdown("""
<style>
    /* Estilo de contenedores y KPIs */
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #3B82F6;
        margin-bottom: 10px;
    }
    .metric-title {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 700;
        margin-top: 5px;
    }
    /* Encabezado principal gradient */
    .header-banner {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }
    .header-banner h1 {
        margin: 0;
        font-size: 36px;
        font-weight: 800;
    }
    .header-banner p {
        margin: 5px 0 0 0;
        font-size: 16px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# CARGA Y PREPARACIÓN DE DATOS
# ----------------------------------------------------
RUTA_SUCIO = "datos/estudiantes_sucios.csv"

# Asegurar que el archivo de datos existe
if not os.path.exists(RUTA_SUCIO):
    os.makedirs("datos", exist_ok=True)
    generar_datos_sinteticos(num_registros=1000, ruta_salida=RUTA_SUCIO)

@st.cache_data
def obtener_datos():
    """Carga y procesa los datos aplicando caché para mejorar rendimiento."""
    df_sucio = pd.read_csv(RUTA_SUCIO)
    df_limpio = ejecutar_pipeline_limpieza(df_sucio)
    df_analizado = agregar_analitica_riesgo(df_limpio)
    return df_sucio, df_analizado

df_sucio, df_analizado = obtener_datos()

# ----------------------------------------------------
# SIDEBAR / PANEL DE CONTROL
# ----------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/graduation-cap.png", width=90)
st.sidebar.title("Panel de Control")
st.sidebar.markdown("Filtrar datos para análisis interactivo:")

# Selector de Carrera
carreras = ["Todas"] + list(df_analizado["Carrera"].unique())
carrera_seleccionada = st.sidebar.selectbox("Carrera Profesional:", carreras)

# Selector de Riesgo
riesgos = ["Todos", "Alto", "Medio", "Bajo"]
riesgo_seleccionado = st.sidebar.selectbox("Nivel de Riesgo de Deserción:", riesgos)

# Estado del Motor Lógico (Prolog)
st.sidebar.markdown("### Paradigma Lógico")
prolog_activo = verificar_swipl_instalado()
if prolog_activo:
    st.sidebar.success("🟢 SWI-Prolog Activo")
else:
    st.sidebar.warning("🟡 Python (Modo Compatibilidad)")

st.sidebar.markdown("---")
st.sidebar.markdown("### Acciones de Datos")

# Botón para regenerar datos
if st.sidebar.button("♻️ Regenerar Datos Sintéticos"):
    generar_datos_sinteticos(num_registros=1000, ruta_salida=RUTA_SUCIO)
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("""
<div style='font-size: 12px; color: #94A3B8; margin-top: 30px;'>
    <strong>EduAnalytics v1.0</strong><br>
    Proyecto Final - Lenguaje de Programación<br>
    Desarrollado en Python con POO y PF.
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# FILTRADO DE DATOS SEGÚN SIDEBAR
# ----------------------------------------------------
df_filtrado = df_analizado.copy()

if carrera_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Carrera"] == carrera_seleccionada]

if riesgo_seleccionado != "Todos":
    df_filtrado = filtrar_estudiantes_por_riesgo(df_filtrado, riesgo_seleccionado)

# Instanciar objetos POO del modelo a partir del dataframe filtrado
# Esto demuestra la integración entre POO y los DataFrames de Pandas
estudiantes_instancias = [
    Estudiante(
        id_estudiante=r["ID_Estudiante"],
        nombre=r["Nombre"],
        carrera=r["Carrera"],
        nota_math=r["Nota_Math"],
        nota_prog=r["Nota_Prog"],
        nota_redac=r["Nota_Redac"],
        asistencia=r["Asistencia_%"],
        horas_estudio=r["Horas_Estudio_Semana"],
        ingreso_familiar=r["Ingreso_Familiar"],
        fecha_matricula=str(r["Fecha_Matricula"])
    )
    for _, r in df_filtrado.iterrows()
]

# ----------------------------------------------------
# ENCABEZADO PRINCIPAL
# ----------------------------------------------------
st.markdown(f"""
<div class="header-banner">
    <h1>🎓 EduAnalytics</h1>
    <p>Dashboard Inteligente de Rendimiento Académico y Prevención de Deserción (UTP)</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# INDICADORES CLAVE (KPIs)
# ----------------------------------------------------
total_alumnos = len(df_filtrado)
avg_gpa = df_filtrado["Promedio"].mean() if total_alumnos > 0 else 0.0
avg_asistencia = df_filtrado["Asistencia_%"].mean() if total_alumnos > 0 else 0.0

total_alto_riesgo = len(df_filtrado[df_filtrado["Nivel_Riesgo"] == "Alto"])
tasa_riesgo = (total_alto_riesgo / total_alumnos * 100) if total_alumnos > 0 else 0.0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #3B82F6;">
        <div class="metric-title">Total Estudiantes</div>
        <div class="metric-value">{total_alumnos}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #10B981;">
        <div class="metric-title">Promedio de Notas (GPA)</div>
        <div class="metric-value">{avg_gpa:.2f} / 20</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #F59E0B;">
        <div class="metric-title">Asistencia Promedio</div>
        <div class="metric-value">{avg_asistencia:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: #EF4444;">
        <div class="metric-title">Tasa de Riesgo Alto</div>
        <div class="metric-value">{tasa_riesgo:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# PESTAÑAS (TABS) DEL DASHBOARD
# ----------------------------------------------------
tab_dashboard, tab_riesgo, tab_limpieza = st.tabs([
    "📊 Análisis General y Gráficos", 
    "🚨 Alertas y Alumnos en Riesgo", 
    "🧹 Proceso de Limpieza (Rúbrica)"
])

# ====================================================
# TAB 1: DASHBOARD GENERAL
# ====================================================
with tab_dashboard:
    st.markdown("### Visualizaciones de Datos Académicos")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.plotly_chart(grafico_asistencia_vs_promedio(df_filtrado), use_container_width=True)
        st.plotly_chart(grafico_horas_estudio_vs_promedio(df_filtrado), use_container_width=True)
        
    with col_g2:
        st.plotly_chart(grafico_distribucion_promedio(df_filtrado), use_container_width=True)
        st.plotly_chart(grafico_riesgo_por_carrera(df_filtrado), use_container_width=True)

# ====================================================
# TAB 2: ALERTAS Y DETALLE DE ALUMNOS
# ====================================================
with tab_riesgo:
    st.markdown("### Alertas de Deserción y Rendimiento Crítico")
    
    # Filtrar solo riesgo alto para la tabla de alertas
    df_alto = df_filtrado[df_filtrado["Nivel_Riesgo"] == "Alto"].sort_values(by="Indice_Riesgo", ascending=False)
    
    if len(df_alto) == 0:
        st.success("🎉 ¡Excelente! No se registran estudiantes en nivel de Riesgo Alto con los filtros actuales.")
    else:
        st.warning(f"⚠️ Se han detectado **{len(df_alto)}** estudiantes con riesgo crítico de deserción o reprobación.")
        
        # Mostrar tabla resumida de riesgo alto
        st.dataframe(
            df_alto[["ID_Estudiante", "Nombre", "Carrera", "Promedio", "Asistencia_%", "Horas_Estudio_Semana", "Indice_Riesgo"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.markdown("### Búsqueda Detallada y Plan de Acción Individual (POO)")
        
        # Selector para ver detalles de un alumno específico
        nombres_estudiantes = [f"{e.id_estudiante} - {e.nombre}" for e in estudiantes_instancias]
        
        if nombres_estudiantes:
            alumno_sel_str = st.selectbox("Seleccione un estudiante para inspección:", nombres_estudiantes)
            id_sel = alumno_sel_str.split(" - ")[0]
            
            # Buscar la instancia del objeto Estudiante (POO)
            estudiante_obj = next((e for e in estudiantes_instancias if e.id_estudiante == id_sel), None)
            
            if estudiante_obj:
                # Obtener la fila completa de datos analíticos correspondientes
                fila_analitica = df_filtrado[df_filtrado["ID_Estudiante"] == id_sel].iloc[0]
                
                col_det1, col_det2 = st.columns([1, 2])
                
                with col_det1:
                    st.markdown(f"""
                    <div style="background-color: #1E293B; padding: 20px; border-radius: 12px;">
                        <h4 style="margin-top:0; color:#3B82F6;">Ficha Académica</h4>
                        <strong>ID:</strong> {estudiante_obj.id_estudiante}<br>
                        <strong>Nombre:</strong> {estudiante_obj.nombre}<br>
                        <strong>Carrera:</strong> {estudiante_obj.carrera}<br>
                        <strong>Fecha Matrícula:</strong> {estudiante_obj.fecha_matricula.split(' ')[0]}<br>
                        <hr style="border-color:#334155;">
                        <strong>Nota Matematicas:</strong> {estudiante_obj.nota_math}<br>
                        <strong>Nota Programación:</strong> {estudiante_obj.nota_prog}<br>
                        <strong>Nota Redacción:</strong> {estudiante_obj.nota_redac}<br>
                        <strong>Promedio General:</strong> <span style="font-size:16px; font-weight:bold; color:{'#10B981' if estudiante_obj.calcular_promedio() >= NOTA_APROBATORIA else '#EF4444'};">{estudiante_obj.calcular_promedio()}</span> ({estudiante_obj.obtener_estado()})
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_det2:
                    st.markdown("#### Diagnóstico y Recomendaciones de Tutoría")
                    
                    riesgo_nivel = fila_analitica["Nivel_Riesgo"]
                    indice_r = fila_analitica["Indice_Riesgo"]
                    
                    # Intentamos resolver con Prolog si está activo
                    resultado_prolog = None
                    if prolog_activo:
                        resultado_prolog = consultar_riesgo_prolog(
                            estudiante_obj.nota_math or 0.0,
                            estudiante_obj.nota_prog or 0.0,
                            estudiante_obj.nota_redac or 0.0,
                            estudiante_obj.asistencia or 0.0,
                            estudiante_obj.horas_estudio or 0
                        )
                    
                    if resultado_prolog:
                        riesgo_nivel_pl = resultado_prolog["Nivel_Riesgo"]
                        color_riesgo = "#EF4444" if riesgo_nivel_pl == "Alto" else ("#F59E0B" if riesgo_nivel_pl == "Medio" else "#10B981")
                        
                        st.markdown(f"Nivel de Riesgo (Deducido por Prolog): <span style='color:{color_riesgo}; font-weight:bold; font-size:18px;'>{riesgo_nivel_pl}</span>", unsafe_allow_html=True)
                        st.markdown("##### Acciones Recomendadas por el Motor Lógico (.pl):")
                        
                        hay_recomendacion = False
                        if resultado_prolog["RecAsistencia"]:
                            st.write(f"❌ **{resultado_prolog['RecAsistencia']}:** El estudiante está por debajo del límite de asistencia reglamentaria (30% inasistencias).")
                            hay_recomendacion = True
                        if resultado_prolog["RecProg"]:
                            st.write(f"📖 **{resultado_prolog['RecProg']}:** Taller obligatorio de programación los días sábados.")
                            hay_recomendacion = True
                        if resultado_prolog["RecMath"]:
                            st.write(f"📐 **{resultado_prolog['RecMath']}:** Derivar al grupo de nivelación de Matemáticas.")
                            hay_recomendacion = True
                        if resultado_prolog["RecTiempo"]:
                            st.write(f"⏱️ **{resultado_prolog['RecTiempo']}:** Invitar al taller virtual de técnicas de estudio.")
                            hay_recomendacion = True
                            
                        if not hay_recomendacion and riesgo_nivel_pl == "Bajo":
                            st.write("✅ **Rendimiento Óptimo:** No requiere intervenciones inmediatas. Se sugiere invitarlo como alumno mentor.")
                    else:
                        # Fallback: Lógica nativa en Python
                        color_riesgo = "#EF4444" if riesgo_nivel == "Alto" else ("#F59E0B" if riesgo_nivel == "Medio" else "#10B981")
                        st.markdown(f"Nivel de Riesgo (Fallback Python): <span style='color:{color_riesgo}; font-weight:bold; font-size:18px;'>{riesgo_nivel}</span> (Índice de Riesgo: {indice_r})", unsafe_allow_html=True)
                        
                        st.markdown("##### Acciones Recomendadas (Python):")
                        if estudiante_obj.asistencia < 75.0:
                            st.write("❌ **Alerta de Asistencia:** El estudiante está por debajo del límite de asistencia reglamentaria (30% inasistencias). Comunicarse con Bienestar Universitario de inmediato.")
                        if estudiante_obj.nota_prog < NOTA_APROBATORIA:
                            st.write("📖 **Tutoría de Programación:** Agendar de forma obligatoria al taller de programación los días sábados.")
                        if estudiante_obj.nota_math < NOTA_APROBATORIA:
                            st.write("📐 **Tutoría de Matemáticas:** Derivar al grupo de nivelación de Cálculo/Álgebra.")
                        if estudiante_obj.horas_estudio < 8:
                            st.write("⏱️ **Taller de Gestión del Tiempo:** Invitar al estudiante al taller virtual de técnicas de estudio y organización.")
                        
                        if riesgo_nivel == "Bajo":
                            st.write("✅ **Felicitaciones:** El alumno mantiene un rendimiento óptimo. Se sugiere invitarlo a formar parte del programa de alumnos mentores.")

# ====================================================
# TAB 3: PROCESO DE LIMPIEZA DE DATOS (MUESTRA RÚBRICA)
# ====================================================
with tab_limpieza:
    st.markdown("### Evidencia de Limpieza y Transformación de Datos (Criterio 3)")
    st.write("La rúbrica califica con **Excelente** el uso de Pandas y Numpy para realizar limpieza de datos faltantes, duplicados, outliers y formatos erróneos. A continuación se demuestra el estado de los datos **Antes** (Datos Sintéticos Sucios) y **Después** (Datos Procesados por el Pipeline).")
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.subheader("1. Dataset Original (Sucio)")
        st.write("Se observan notas vacías, asistencias erróneas (-15.0%, 120.0%), duplicados e ingresos familiares negativos:")
        st.dataframe(df_sucio.head(10), use_container_width=True)
        
    with col_l2:
        st.subheader("2. Dataset Procesado y Limpio")
        st.write("Los duplicados se eliminaron, las notas vacías se imputaron con la mediana de su carrera, las asistencias erróneas se acotaron con `numpy.clip` a [0-100] y los ingresos se normalizaron:")
        st.dataframe(df_analizado.head(10), use_container_width=True)

    st.markdown("---")
    st.markdown("### Reporte Estadístico del Proceso de Limpieza")
    
    # Calcular algunas métricas de qué se limpió
    total_sucios = len(df_sucio)
    total_limpios = len(df_analizado)
    duplicados_eliminados = total_sucios - total_limpios
    
    notas_imputadas_math = df_sucio["Nota_Math"].isna().sum()
    notas_imputadas_prog = df_sucio["Nota_Prog"].isna().sum()
    notas_imputadas_redac = df_sucio["Nota_Redac"].isna().sum()
    
    col_rep1, col_rep2, col_rep3 = st.columns(3)
    
    with col_rep1:
        st.info(f"👥 **Registros Duplicados Eliminados:** {duplicados_eliminados}")
    with col_rep2:
        st.info(f"✏️ **Notas Vacías Imputadas:** {notas_imputadas_math + notas_imputadas_prog + notas_imputadas_redac} calificaciones")
    with col_rep3:
        # Calcular cuántas asistencias estaban fuera de rango en el original
        asistencias_corregidas = len(df_sucio[(df_sucio["Asistencia_%"] < 0) | (df_sucio["Asistencia_%"] > 100) | (df_sucio["Asistencia_%"].isna())])
        st.info(f"📈 **Porcentajes de Asistencia Corregidos:** {asistencias_corregidas}")
