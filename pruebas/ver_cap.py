import os
import pandas as pd
import numpy as np
import statistics


def procesar_instancia(archivo):
    """
    Lee una instancia y calcula las estadísticas de demanda.

    Args:
        archivo: Nombre del archivo de la instancia.

    Returns:
        Un diccionario con las estadísticas calculadas.
    """

    # Leemos solo la primera línea como una cadena de texto
    with open(archivo, 'r') as f:
        for _ in range(3):
            next(f)
        primera_linea = f.readline()
        numeros = primera_linea.split()
        dimension = int(numeros[2])
        clientes = dimension - 1
        for _ in range(3+1+dimension + 1+1):
            next(f)
        # Leer los datos
        datos = []
        contador_clientes = 0
        for linea in f:
            if (contador_clientes == (clientes)):
                break
            campos = linea.strip().split(' ')  # Ajusta el separador
            if len(campos) >= 2 and campos[0] != "1":  # Asegurarse de que hay al menos dos elementos
                try:
                    #print(campos)
                    datos.append(int(campos[1]))  # Intentar convertir a entero
                    contador_clientes+=1
                except ValueError:
                    print(f"Error al convertir a entero: {campos[1]}")
            if linea == ['DEPOT_SECTION']:
                break

    array_numeros = np.array(datos)

    # Calculando las estadísticas
    minimo = np.min(array_numeros)
    maximo = np.max(array_numeros)
    promedio = np.mean(array_numeros)
    desviacion_estandar = np.std(array_numeros)
    total = np.sum(array_numeros)

    return {'total': total, 'min': minimo, 'max': maximo, 'prom': round(promedio, 2), 'desv': round(desviacion_estandar, 2)}

# Directorio donde se encuentran las instancias
directorio = "../Instances/CVRP"  # Reemplaza con la ruta correcta

# Lista para almacenar los resultados
resultados = []

# Iterar sobre los archivos
for archivo in os.listdir(directorio):
    if archivo.startswith("Golden_"):
        ruta_completa = os.path.join(directorio, archivo)
        resultados.append((archivo, procesar_instancia(ruta_completa)))

# Escribir los resultados en un archivo
with open("resumen_Golden.txt", "w") as f:
    for nombre, stats in resultados:
        f.write(f"{nombre} total: {stats['total']} - min: {stats['min']} - max: {stats['max']} - prom: {stats['prom']} - desv: {stats['desv']}\n")