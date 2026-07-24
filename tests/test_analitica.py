import pytest
import pandas as pd
import numpy as np
from src.analitica import (
    eliminar_duplicados,
    limpiar_asistencias,
    imputar_notas_nulas,
    limpiar_ingreso_familiar,
    calcular_indice_riesgo,
    evaluar_riesgo_desercion
)

# Datos de prueba para limpieza
@pytest.fixture
def df_sucio():
    data = {
        "ID_Estudiante": ["U001", "U002", "U001", "U003"],
        "Nombre": ["Ana Gomez", "Luis Perez", "Ana Gomez", "Carlos Diaz"],
        "Carrera": ["Psicología", "Psicología", "Psicología", "Derecho"],
        "Nota_Math": [15.0, np.nan, 15.0, 8.0],
        "Nota_Prog": [18.0, 12.0, 14.0, np.nan],
        "Nota_Redac": [14.0, np.nan, 14.0, 10.0],
        "Asistencia_%": [95.0, -10.0, 95.0, 120.0],
        "Horas_Estudio_Semana": [15, 10, 15, 5],
        "Ingreso_Familiar": [2500.0, -1200.0, 2500.0, np.nan],
        "Fecha_Matricula": ["2026-03-01", "05/03/2026", "2026-03-01", "2026-03-10"]
    }
    return pd.DataFrame(data)

def test_eliminar_duplicados(df_sucio):
    df_clean = eliminar_duplicados(df_sucio)
    print("\n   [OK] PURGA DE DUPLICADOS: 4 registros iniciales -> 3 registros unicos procesados.")
    assert len(df_clean) == 3
    registro_u001 = df_clean[df_clean["ID_Estudiante"] == "U001"].iloc[0]
    assert registro_u001["Nota_Prog"] == 14.0

def test_limpiar_asistencias(df_sucio):
    df_clean = limpiar_asistencias(df_sucio)
    print("\n   [OK] NORMALIZACION DE ASISTENCIA: Asistencias -10% y 120% acotadas a [0%, 100%].")
    assert df_clean.loc[df_clean["ID_Estudiante"] == "U002", "Asistencia_%"].values[0] == 0.0
    assert df_clean.loc[df_clean["ID_Estudiante"] == "U003", "Asistencia_%"].values[0] == 100.0

def test_imputar_notas_nulas(df_sucio):
    df_clean = imputar_notas_nulas(df_sucio)
    nota_u002 = df_clean.loc[df_clean["ID_Estudiante"] == "U002", "Nota_Math"].values[0]
    nota_u003 = df_clean.loc[df_clean["ID_Estudiante"] == "U003", "Nota_Prog"].values[0]
    print(f"\n   [OK] IMPUTACION ESTADISTICA: Nota nula de U002 imputada con mediana de Psicologia ({nota_u002}).")
    assert nota_u002 == 15.0
    assert nota_u003 == 11.0

def test_limpiar_ingreso_familiar(df_sucio):
    df_clean = limpiar_ingreso_familiar(df_sucio)
    ingreso_u002 = df_clean.loc[df_clean["ID_Estudiante"] == "U002", "Ingreso_Familiar"].values[0]
    print(f"\n   [OK] CORRECCION MONETARIA: Ingreso negativo de -1200 a valor absoluto ({ingreso_u002}) y nulos imputados.")
    assert ingreso_u002 == 1200.0
    assert df_clean.loc[df_clean["ID_Estudiante"] == "U003", "Ingreso_Familiar"].values[0] == 2500.0

def test_calcular_indice_riesgo():
    riesgo_bajo = calcular_indice_riesgo(18.0, 95.0, 20)
    riesgo_alto = calcular_indice_riesgo(5.0, 50.0, 2)
    print(f"\n   [OK] CALCULO MATEMATICO DE RIESGO: Alumno regular (Indice={riesgo_bajo}) vs Alumno critico (Indice={riesgo_alto}).")
    assert riesgo_bajo < riesgo_alto
    assert riesgo_bajo < 0.3
    assert riesgo_alto > 0.6

def test_evaluar_riesgo_desercion():
    alumno_ausente = pd.Series({
        "Nota_Math": 15.0, "Nota_Prog": 16.0, "Nota_Redac": 15.0,
        "Asistencia_%": 65.0, "Horas_Estudio_Semana": 15
    })
    alumno_bueno = pd.Series({
        "Nota_Math": 18.0, "Nota_Prog": 17.0, "Nota_Redac": 16.0,
        "Asistencia_%": 98.0, "Horas_Estudio_Semana": 20
    })
    res_ausente = evaluar_riesgo_desercion(alumno_ausente)
    res_bueno = evaluar_riesgo_desercion(alumno_bueno)
    print(f"\n   [OK] CLASIFICACION CUALITATIVA: Asistencia < 70% clasificada como '{res_ausente}' | Alumno excelente como '{res_bueno}'.")
    assert res_ausente == "Alto"
    assert res_bueno == "Bajo"
