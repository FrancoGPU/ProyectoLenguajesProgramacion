from typing import List, Dict, Any

NOTA_APROBATORIA = 11.50

class Estudiante:
    """
    Representa a un estudiante universitario y encapsula sus datos y comportamientos básicos (POO).
    """
    def __init__(
        self,
        id_estudiante: str,
        nombre: str,
        carrera: str,
        nota_math: float,
        nota_prog: float,
        nota_redac: float,
        asistencia: float,
        horas_estudio: int,
        ingreso_familiar: float,
        fecha_matricula: str
    ):
        self.id_estudiante = id_estudiante
        self.nombre = nombre
        self.carrera = carrera
        self.nota_math = nota_math
        self.nota_prog = nota_prog
        self.nota_redac = nota_redac
        self.asistencia = asistencia
        self.horas_estudio = horas_estudio
        self.ingreso_familiar = ingreso_familiar
        self.fecha_matricula = fecha_matricula

    def calcular_promedio(self) -> float:
        """Calcula el promedio simple de las tres asignaturas."""
        notas = [self.nota_math, self.nota_prog, self.nota_redac]
        # Filtrar valores no válidos si los hubiera
        notas_validas = [n for n in notas if n is not None and 0 <= n <= 20]
        if not notas_validas:
            return 0.0
        return round(sum(notas_validas) / len(notas_validas), 2)

    def obtener_estado(self) -> str:
        """Determina si el estudiante está aprobado (promedio >= NOTA_APROBATORIA en escala vigesimal)."""
        return "Aprobado" if self.calcular_promedio() >= NOTA_APROBATORIA else "Desaprobado"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte los atributos de la instancia en un diccionario para análisis."""
        return {
            "ID_Estudiante": self.id_estudiante,
            "Nombre": self.nombre,
            "Carrera": self.carrera,
            "Nota_Math": self.nota_math,
            "Nota_Prog": self.nota_prog,
            "Nota_Redac": self.nota_redac,
            "Promedio": self.calcular_promedio(),
            "Asistencia_%": self.asistencia,
            "Horas_Estudio_Semana": self.horas_estudio,
            "Ingreso_Familiar": self.ingreso_familiar,
            "Fecha_Matricula": self.fecha_matricula,
            "Estado": self.obtener_estado()
        }


class ReporteCarrera:
    """
    Clase compuesta que agrupa a estudiantes de una misma carrera para generar estadísticas agregadas (POO).
    """
    def __init__(self, carrera: str, estudiantes: List[Estudiante]):
        self.carrera = carrera
        self.estudiantes = [e for e in estudiantes if e.carrera == carrera]

    def total_estudiantes(self) -> int:
        return len(self.estudiantes)

    def calcular_promedio_general(self) -> float:
        """Obtiene el promedio de calificaciones de todos los alumnos de la carrera."""
        if not self.estudiantes:
            return 0.0
        promedios = [e.calcular_promedio() for e in self.estudiantes]
        return round(sum(promedios) / len(promedios), 2)

    def calcular_tasa_aprobacion(self) -> float:
        """Calcula el porcentaje de estudiantes aprobados en la carrera."""
        total = self.total_estudiantes()
        if total == 0:
            return 0.0
        aprobados = sum(1 for e in self.estudiantes if e.obtener_estado() == "Aprobado")
        return round((aprobados / total) * 100, 2)

    def obtener_resumen(self) -> Dict[str, Any]:
        return {
            "Carrera": self.carrera,
            "Total_Estudiantes": self.total_estudiantes(),
            "Promedio_General": self.calcular_promedio_general(),
            "Tasa_Aprobacion_%": self.calcular_tasa_aprobacion()
        }
