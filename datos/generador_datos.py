import csv
import random
from datetime import datetime, timedelta

def generar_datos_sinteticos(num_registros=1000, ruta_salida="estudiantes_sucios.csv"):
    nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Gabriela", "Jose", "Sofia", "Diego", "Lucia",
               "Andres", "Camila", "Fernando", "Valeria", "Jorge", "Isabella", "Mateo", "Valentina", "Lucas", "Elena"]
    apellidos = ["Rodriguez", "Gomez", "Lopez", "Perez", "Garcia", "Martinez", "Sanchez", "Diaz", "Torres", "Ramirez",
                 "Flores", "Espinoza", "Quispe", "Mamani", "Chavez", "Vargas", "Ramos", "Castro", "Mendoza", "Rojas"]
    carreras = ["Ingeniería de Sistemas", "Psicología", "Administración", "Ingeniería Industrial", "Derecho"]
    
    fechas_base = [datetime(2026, 3, 1) + timedelta(days=x) for x in range(25)]
    formatos_fecha = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

    # Generamos la lista base de registros
    registros = []
    
    for i in range(1, num_registros + 1):
        id_est = f"U{20260000 + i}"
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        carrera = random.choice(carreras)
        
        # Generar notas con una distribución lógica
        # (ej. algunos alumnos van muy bien, otros regular, otros mal)
        perfil = random.choice(["excelente", "promedio", "bajo_rendimiento"])
        if perfil == "excelente":
            nota_math = round(random.uniform(15, 20), 1)
            nota_prog = round(random.uniform(16, 20), 1)
            nota_redac = round(random.uniform(14, 20), 1)
            asistencia = round(random.uniform(90, 100), 1)
            horas_estudio = random.randint(15, 35)
        elif perfil == "promedio":
            nota_math = round(random.uniform(10, 16), 1)
            nota_prog = round(random.uniform(10, 16), 1)
            nota_redac = round(random.uniform(11, 16), 1)
            asistencia = round(random.uniform(75, 95), 1)
            horas_estudio = random.randint(8, 20)
        else:
            nota_math = round(random.uniform(4, 11), 1)
            nota_prog = round(random.uniform(3, 11), 1)
            nota_redac = round(random.uniform(6, 12), 1)
            asistencia = round(random.uniform(40, 80), 1)
            horas_estudio = random.randint(1, 10)
            
        ingreso = round(random.uniform(950, 7500), 2)
        fecha_mat = random.choice(fechas_base)
        
        # Inyección deliberada de errores y suciedad para el análisis de Pandas
        # 1. Valores Nulos (aprox 5% de probabilidad para campos numéricos y fechas)
        if random.random() < 0.05: nota_math = ""
        if random.random() < 0.05: nota_prog = ""
        if random.random() < 0.05: nota_redac = ""
        if random.random() < 0.04: asistencia = ""
        if random.random() < 0.05: ingreso = ""
        if random.random() < 0.03: fecha_mat = ""
        
        # 2. Valores erróneos fuera de límites o tipos inconsistentes
        if asistencia != "" and random.random() < 0.03:
            # Asistencia errónea (negativa o mayor a 100%)
            asistencia = random.choice([-15.0, 120.0, 150.5])
            
        if nota_math != "" and random.random() < 0.02:
            # Nota fuera de escala (0-20)
            nota_math = random.choice([-5.0, 25.0])
            
        if ingreso != "" and random.random() < 0.02:
            # Ingreso familiar negativo
            ingreso = -random.uniform(500, 2000)

        # 3. Formateo de fecha inconsistente
        fecha_str = ""
        if fecha_mat != "":
            fmt = random.choice(formatos_fecha)
            fecha_str = fecha_mat.strftime(fmt)

        registros.append({
            "ID_Estudiante": id_est,
            "Nombre": nombre,
            "Carrera": carrera,
            "Nota_Math": nota_math,
            "Nota_Prog": nota_prog,
            "Nota_Redac": nota_redac,
            "Asistencia_%": asistencia,
            "Horas_Estudio_Semana": horas_estudio,
            "Ingreso_Familiar": ingreso,
            "Fecha_Matricula": fecha_str
        })
        
    # 4. Inyección de registros duplicados
    for _ in range(int(num_registros * 0.03)): # 3% de duplicados
        duplicado = random.choice(registros).copy()
        # A veces es exactamente idéntico, a veces cambia alguna nota
        if random.random() < 0.5:
            duplicado["Nota_Prog"] = round(random.uniform(5, 18), 1)
        registros.append(duplicado)
        
    # Barajar para mezclar los duplicados
    random.shuffle(registros)
    
    # Escribir a CSV
    columnas = ["ID_Estudiante", "Nombre", "Carrera", "Nota_Math", "Nota_Prog", "Nota_Redac", "Asistencia_%", "Horas_Estudio_Semana", "Ingreso_Familiar", "Fecha_Matricula"]
    with open(ruta_salida, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(registros)
        
    print(f"Dataset generado exitosamente con {len(registros)} registros en: {ruta_salida}")

if __name__ == "__main__":
    generar_datos_sinteticos(num_registros=1000, ruta_salida="estudiantes_sucios.csv")
