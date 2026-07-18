# INFORME DE PROYECTO FINAL: EduAnalytics

**Curso:** Lenguaje de Programación  
**Institución:** Universidad Tecnológica del Perú (UTP)  
**Proyecto:** Dashboard Inteligente de Rendimiento Académico y Alerta de Deserción Escolar  

---

## 1. Introducción
La deserción universitaria y el bajo rendimiento académico representan retos críticos para las instituciones educativas de nivel superior. La detección tardía de estudiantes con dificultades se traduce frecuentemente en la reprobación de asignaturas o en el abandono definitivo de sus estudios. 

**EduAnalytics** es una solución tecnológica desarrollada en **Python** que integra técnicas de análisis de datos con programación estructurada, modular y multiparadigma. El sistema genera datos simulados de estudiantes con inconsistencias comunes de registro, los procesa a través de un pipeline funcional de limpieza de datos, analiza métricas académicas combinando Programación Orientada a Objetos (POO), Programación Funcional (PF), y **Programación Lógica (Prolog)**, presentando finalmente un dashboard interactivo completo para la toma de decisiones.

---

## 2. Objetivos
* **Objetivo General:** Desarrollar un sistema de software modular en Python y Prolog para identificar a estudiantes universitarios en riesgo académico y de deserción utilizando análisis de datos y visualización interactiva.
* **Objetivos Específicos:**
  1. Implementar la generación y limpieza de datos sintéticos con anomalías simulando escenarios reales de gestión escolar mediante las librerías `pandas` y `numpy`.
  2. Aplicar el paradigma de **Programación Orientada a Objetos** para modelar entidades académicas.
  3. Aplicar el paradigma de **Programación Funcional** para estructurar un flujo inmutable de procesamiento de datos y un algoritmo de cálculo de riesgo.
  4. Aplicar el paradigma de **Programación Lógica (Prolog)** para la deducción inductiva de alertas y tutorías académicas.
  5. Garantizar la confiabilidad del código mediante **Pruebas Unitarias** exhaustivas.
  6. Crear un dashboard web intuitivo, dinámico e interactivo mediante la herramienta **Streamlit** y gráficos de **Plotly**.

---

## 3. Diseño y Arquitectura del Sistema
El proyecto cumple con los principios de modularidad y separación de responsabilidades (Clean Architecture):

### Arquitectura de Módulos:
* `datos/generador_datos.py`: Genera un archivo CSV con 1000 estudiantes e inyecta intencionalmente anomalías (valores nulos, negativos, fechas inconsistentes y duplicados).
* `src/modelos.py` (Paradigma POO):
  * Clase `Estudiante`: Modela al alumno, encapsula su información y calcula de forma individual su promedio y estado académico.
  * Clase `ReporteCarrera`: Agrupa estudiantes de una carrera específica y calcula estadísticas agregadas (tasa de aprobación y promedio general).
* `src/analitica.py` (Paradigma Funcional y Enlace Lógico):
  * Contiene funciones de limpieza de datos puras que no modifican los dataframes de entrada sino que retornan nuevas copias.
  * Implementa funciones de orden superior y expresiones lambda para calcular el **Índice cuantitativo de Riesgo**.
  * Contiene el puente de comunicación por subprocess para consultar las reglas de Prolog.
* `src/reglas.pl` (Paradigma Lógico - Prolog):
  * Define la base de conocimientos y reglas inductivas en sintaxis SWI-Prolog para categorizar riesgos y recomendar planes de tutorías individuales.
* `src/graficos.py`: Contiene funciones encargadas de estructurar y generar las figuras gráficas de Plotly para el dashboard.
* `app.py`: Archivo de ejecución principal que levanta el dashboard web interactivo con Streamlit.
* `tests/test_analitica.py`: Conjunto de pruebas automatizadas diseñadas con la librería `pytest` para validar la fiabilidad de las funciones de negocio.

---

## 4. Algoritmo de Cálculo de Riesgo de Deserción
El sistema evalúa el riesgo ponderando tres factores académicos clave:
1. **Rendimiento Académico (Peso 60%):** A menor nota (escala 0-20), mayor es el factor de riesgo.
2. **Porcentaje de Asistencia (Peso 30%):** A menor asistencia a clases, mayor es el factor de riesgo.
3. **Horas de Estudio Semanales (Peso 10%):** Estudiantes con pocas horas de estudio independientes tienen un recargo en el riesgo.

### Fórmula Matemática (Lambda):
$$\text{Índice de Riesgo} = \left(1 - \frac{\text{Promedio}}{20}\right) \times 0.6 + \left(1 - \frac{\text{Asistencia}}{100}\right) \times 0.3 + \left(1 - \frac{\min(\text{Horas}, 20)}{20}\right) \times 0.1$$

* **Riesgo Alto:** $\text{Índice} \ge 0.55$ o $\text{Asistencia} < 70\%$.
* **Riesgo Medio:** $0.35 \le \text{Índice} < 0.55$.
* **Riesgo Bajo:** $\text{Índice} < 0.35$.

---

## 5. Proceso de Limpieza y Tratamiento de Datos
El pipeline en `src/analitica.py` ejecuta consecutivamente los siguientes tratamientos sobre el dataset crudo:
1. **Eliminación de Duplicados:** Remueve registros con `ID_Estudiante` repetidos, conservando el último registro.
2. **Imputación de Calificaciones Nulas:** Identifica notas vacías (`NaN`) o fuera de rango (menores a 0 o mayores a 20) y las reemplaza con la mediana de las notas de ese curso para la carrera del estudiante.
3. **Limpieza de Asistencia:** Clampa los porcentajes de asistencia erróneos (como -15% o 130%) al rango lógico $[0, 100]$ usando `numpy.clip`.
4. **Tratamiento del Ingreso Familiar:** Transforma valores monetarios negativos a positivos (valor absoluto) y llena vacíos con la mediana general.
5. **Estandarización de Fechas:** Analiza múltiples formatos de fecha e introduce una fecha de inicio de semestre única para registros faltantes.

---

## 6. Pruebas y Validación (Pytest)
Para garantizar la solidez de las funciones de analítica y limpieza, se utiliza `pytest`. Las pruebas validan de forma aislada:
* Que las asistencias sean acotadas correctamente.
* Que los duplicados de estudiantes se purguen.
* Que los valores nulos reciban la imputación estadística correspondiente.
* Que los niveles de riesgo concuerden con las notas del estudiante.

Ejecución de pruebas:
```bash
pytest tests/
```

---

## 7. Instrucciones de Instalación y Ejecución

### Requisitos Previos:
Tener instalado **Python 3.10 o superior**.

### Instalación de dependencias:
1. Clonar o abrir la carpeta del proyecto.
2. Abrir la consola y ejecutar:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecutar la aplicación:
Para iniciar el Dashboard interactivo local, ejecutar:
```bash
streamlit run app.py
```
Se abrirá automáticamente una ventana en el navegador web (por defecto en `http://localhost:8501`).

---

## 8. Conclusiones y Fuentes
* **Conclusión 1:** El uso conjunto de POO y Programación Funcional permite un diseño óptimo. POO estructura la lógica del dominio, mientras que las técnicas funcionales optimizan la manipulación inmutable de tablas de datos.
* **Conclusión 2:** Las herramientas de visualización interactiva facilitan enormemente el trabajo de los tutores académicos al resumir cientos de registros escolares en alarmas visuales tempranas e intuitivas.
* **Conclusión 3:** El uso de Numpy y Pandas demostró ser eficiente para procesar de forma vectorizada tareas de limpieza de datos, reduciendo considerablemente la complejidad del código.

### Fuentes:
* Documentación Oficial de Pandas: https://pandas.pydata.org/
* Documentación de Streamlit: https://docs.streamlit.io/
* Rúbrica oficial del curso de Lenguaje de Programación.
