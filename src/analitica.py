import pandas as pd
import numpy as np
import subprocess
import shutil
import os

# ==========================================
# PIPELINE DE LIMPIEZA DE DATOS (FUNCIONAL)
# ==========================================

def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina registros duplicados basándose en el ID del estudiante, conservando el último."""
    return df.drop_duplicates(subset=["ID_Estudiante"], keep="last").copy()

def limpiar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza los diferentes formatos de fecha a YYYY-MM-DD."""
    df_clean = df.copy()
    # Coerce convierte errores en NaT (Not a Time)
    df_clean["Fecha_Matricula"] = pd.to_datetime(
        df_clean["Fecha_Matricula"], 
        format='mixed', 
        errors='coerce'
    )
    # Llenamos las fechas vacías con una fecha por defecto (ej. inicio de semestre)
    fecha_defecto = pd.to_datetime("2026-03-01")
    df_clean["Fecha_Matricula"] = df_clean["Fecha_Matricula"].fillna(fecha_defecto)
    return df_clean

def limpiar_asistencias(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige porcentajes de asistencia fuera de rango (0 a 100) usando numpy.clip."""
    df_clean = df.copy()
    
    # Primero convertimos la asistencia a valores numéricos
    df_clean["Asistencia_%"] = pd.to_numeric(df_clean["Asistencia_%"], errors='coerce')
    
    # Rellenamos nulos con la mediana de la columna
    mediana_asistencia = df_clean["Asistencia_%"].median()
    df_clean["Asistencia_%"] = df_clean["Asistencia_%"].fillna(mediana_asistencia)
    
    # Recortamos los valores erróneos al rango lógico [0, 100] usando numpy vectorizado
    df_clean["Asistencia_%"] = np.clip(df_clean["Asistencia_%"], 0.0, 100.0)
    
    return df_clean

def imputar_notas_nulas(df: pd.DataFrame) -> pd.DataFrame:
    """Imputa las notas nulas usando la mediana del respectivo curso según la carrera."""
    df_clean = df.copy()
    columnas_notas = ["Nota_Math", "Nota_Prog", "Nota_Redac"]
    
    for col in columnas_notas:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        # En caso de que la nota esté fuera de rango (0-20), la seteamos como NaN para imputarla
        df_clean.loc[(df_clean[col] < 0) | (df_clean[col] > 20), col] = np.nan
        
        # Agrupamos por carrera e imputamos con la mediana del grupo
        df_clean[col] = df_clean.groupby("Carrera")[col].transform(
            lambda x: x.fillna(x.median())
        )
        
        # Si aún quedan nulos (ej. toda una carrera sin notas, poco probable), llenamos con nota de aprobación (11)
        df_clean[col] = df_clean[col].fillna(11.0)
        
    return df_clean

def limpiar_ingreso_familiar(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige los ingresos familiares negativos y rellena los nulos."""
    df_clean = df.copy()
    df_clean["Ingreso_Familiar"] = pd.to_numeric(df_clean["Ingreso_Familiar"], errors='coerce')
    
    # Corregir ingresos negativos tomándolos en valor absoluto
    df_clean["Ingreso_Familiar"] = df_clean["Ingreso_Familiar"].abs()
    
    # Rellenar nulos con la mediana de ingresos
    mediana_ingreso = df_clean["Ingreso_Familiar"].median()
    df_clean["Ingreso_Familiar"] = df_clean["Ingreso_Familiar"].fillna(mediana_ingreso)
    
    return df_clean

def ejecutar_pipeline_limpieza(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función de orden superior que ejecuta la composición de todo el pipeline de limpieza.
    Sigue los principios de la programación funcional al retornar un nuevo DataFrame.
    """
    # Flujo secuencial de funciones puras
    df_clean = (
        df.pipe(eliminar_duplicados)
          .pipe(limpiar_fechas)
          .pipe(limpiar_asistencias)
          .pipe(imputar_notas_nulas)
          .pipe(limpiar_ingreso_familiar)
    )
    return df_clean

# ==========================================
# ANALÍTICA Y CÁLCULO DE RIESGOS (FUNCIONAL)
# ==========================================

# Expresión lambda pura para calcular un índice cuantitativo de riesgo
# El riesgo pondera: baja nota (60%), baja asistencia (30%) y pocas horas de estudio (10%)
calcular_indice_riesgo = lambda gpa, asistencia, horas: round(
    (1 - (gpa / 20.0)) * 0.6 + 
    (1 - (asistencia / 100.0)) * 0.3 + 
    (1 - (min(horas, 20) / 20.0)) * 0.1, 
    3
)

def evaluar_riesgo_desercion(row: pd.Series) -> str:
    """
    Evalúa el nivel cualitativo de riesgo de deserción académica de un estudiante
    basándose en su promedio, asistencia y horas de estudio.
    """
    # Calculamos el promedio de notas
    promedio = (row["Nota_Math"] + row["Nota_Prog"] + row["Nota_Redac"]) / 3.0
    asistencia = row["Asistencia_%"]
    horas = row["Horas_Estudio_Semana"]
    
    indice = calcular_indice_riesgo(promedio, asistencia, horas)
    
    # Reglas de negocio para categorizar
    if indice >= 0.55 or asistencia < 70.0:
        return "Alto"
    elif indice >= 0.35:
        return "Medio"
    else:
        return "Bajo"

def agregar_analitica_riesgo(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega las columnas de Promedio, Indice_Riesgo y Nivel_Riesgo de forma funcional."""
    df_analizado = df.copy()
    
    # Promedio
    df_analizado["Promedio"] = df_analizado[["Nota_Math", "Nota_Prog", "Nota_Redac"]].mean(axis=1).round(2)
    
    # Índice numérico de riesgo
    df_analizado["Indice_Riesgo"] = df_analizado.apply(
        lambda r: calcular_indice_riesgo(r["Promedio"], r["Asistencia_%"], r["Horas_Estudio_Semana"]),
        axis=1
    )
    
    # Categoría de riesgo
    df_analizado["Nivel_Riesgo"] = df_analizado.apply(evaluar_riesgo_desercion, axis=1)
    
    return df_analizado

# Función de orden superior para filtrar (similar a un filter funcional)
def filtrar_estudiantes_por_riesgo(df: pd.DataFrame, nivel: str) -> pd.DataFrame:
    """Filtra y devuelve a los estudiantes que pertenecen a un determinado nivel de riesgo."""
    filtrar_riesgo = lambda d: d[d["Nivel_Riesgo"] == nivel]
    return filtrar_riesgo(df).copy()

# ==========================================
# PUENTE DE COMUNICACIÓN CON SWI-PROLOG
# ==========================================

def verificar_swipl_instalado() -> bool:
    """Verifica si swipl (SWI-Prolog) está disponible en el PATH o en la ruta de instalación por defecto."""
    return shutil.which("swipl") is not None or os.path.exists(r"C:\Program Files\swipl\bin\swipl.exe")

def consultar_riesgo_prolog(math: float, prog: float, redac: float, asistencia: float, horas: int) -> dict:
    """
    Realiza una consulta lógica a reglas.pl usando SWI-Prolog y retorna el riesgo y recomendaciones.
    Retorna None si swipl no está instalado o si falla.
    """
    if not verificar_swipl_instalado():
        return None
        
    try:
        # Resolver la ruta del ejecutable de Prolog
        swipl_cmd = "swipl" if shutil.which("swipl") else r"C:\Program Files\swipl\bin\swipl.exe"
        
        # Construimos la consulta Prolog:
        # evaluar_estudiante(Math, Prog, Redac, Asistencia, Horas, Riesgo, RecAsis, RecMath, RecProg, RecTiempo)
        consulta = (
            f"evaluar_estudiante({math}, {prog}, {redac}, {asistencia}, {horas}, Riesgo, RecAsis, RecMath, RecProg, RecTiempo), "
            f"format('~w;~w;~w;~w;~w', [Riesgo, RecAsis, RecMath, RecProg, RecTiempo]), halt."
        )
        
        # Ejecutamos swipl por CLI
        proceso = subprocess.run(
            [swipl_cmd, "-s", "src/reglas.pl", "-g", consulta, "-t", "halt."],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if proceso.returncode == 0:
            salida = proceso.stdout.strip()
            # En caso de que haya outputs previos de swipl, filtramos para obtener la línea con los punto y comas
            lineas = [l for l in salida.splitlines() if ";" in l]
            if lineas:
                salida = lineas[-1]
            partes = salida.split(";")
            if len(partes) == 5:
                return {
                    "Nivel_Riesgo": partes[0],
                    "RecAsistencia": partes[1] if partes[1] != "''" else "",
                    "RecMath": partes[2] if partes[2] != "''" else "",
                    "RecProg": partes[3] if partes[3] != "''" else "",
                    "RecTiempo": partes[4] if partes[4] != "''" else ""
                }
    except Exception as e:
        print(f"Error en consulta Prolog: {e}")
        
    return None
