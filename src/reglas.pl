% ==========================================
% REGLAS LÓGICAS DE EVALUACIÓN ACADÉMICA
% ==========================================

% Regla para calcular el promedio simple de tres notas
promedio(Math, Prog, Redac, Promedio) :-
    Promedio is (Math + Prog + Redac) / 3.0.

% Regla auxiliar para obtener el mínimo entre dos números
minimo(A, B, A) :- A =< B, !.
minimo(_, B, B).

% Regla para calcular el índice de riesgo
indice_riesgo(Math, Prog, Redac, Asistencia, Horas, Indice) :-
    promedio(Math, Prog, Redac, P),
    minimo(Horas, 20, H20),
    Indice is (1 - (P / 20.0)) * 0.6 + (1 - (Asistencia / 100.0)) * 0.3 + (1 - (H20 / 20.0)) * 0.1.

% Reglas para determinar el nivel de riesgo cualitativo
nivel_riesgo(_, _, _, Asistencia, _, 'Alto') :-
    Asistencia < 70.0, !.

nivel_riesgo(Math, Prog, Redac, Asistencia, Horas, 'Alto') :-
    indice_riesgo(Math, Prog, Redac, Asistencia, Horas, Indice),
    Indice >= 0.55, !.

nivel_riesgo(Math, Prog, Redac, Asistencia, Horas, 'Medio') :-
    indice_riesgo(Math, Prog, Redac, Asistencia, Horas, Indice),
    Indice >= 0.35, !.

nivel_riesgo(_, _, _, _, _, 'Bajo').

% Hecho lógico que define la nota aprobatoria mínima del sistema
nota_aprobatoria(10.5).

% Reglas para generar recomendaciones (Hechos / Inferencias)
recomendar_alerta(Asistencia, 'Alerta de Asistencia') :-
    Asistencia < 75.0, !.
recomendar_alerta(_, '').

recomendar_math(Math, 'Tutoria de Matematicas') :-
    nota_aprobatoria(Limite),
    Math < Limite, !.
recomendar_math(_, '').

recomendar_prog(Prog, 'Tutoria de Programacion') :-
    nota_aprobatoria(Limite),
    Prog < Limite, !.
recomendar_prog(_, '').

recomendar_tiempo(Horas, 'Taller de Gestion del Tiempo') :-
    Horas < 8, !.
recomendar_tiempo(_, '').

% Predicado principal de evaluación
evaluar_estudiante(Math, Prog, Redac, Asistencia, Horas, Riesgo, RecAsis, RecMath, RecProg, RecTiempo) :-
    nivel_riesgo(Math, Prog, Redac, Asistencia, Horas, Riesgo),
    recomendar_alerta(Asistencia, RecAsis),
    recomendar_math(Math, RecMath),
    recomendar_prog(Prog, RecProg),
    recomendar_tiempo(Horas, RecTiempo).
