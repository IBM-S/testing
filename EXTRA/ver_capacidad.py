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
        primera_linea = f.readline()
        numeros = primera_linea.split()
        segundo_numero = int(numeros[1])
        tercer_numero = int(numeros[2])
        for _ in range(tercer_numero):
            next(f)

        # Leer los datos
        datos = []
        contador_clientes = 0
        for linea in f:
            campos = linea.strip().split(' ')  # Ajusta el separador
            lista_sin_espacios = [elemento for elemento in campos if elemento.strip()]
            datos.append(int(lista_sin_espacios[4]))
            contador_clientes+=1
            if (contador_clientes == segundo_numero):
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
directorio = "../Data/DataFiles"  # Reemplaza con la ruta correcta

# Lista para almacenar los resultados
resultados = []

# Iterar sobre los archivos
for archivo in os.listdir(directorio):
    if archivo.startswith("p"):
        ruta_completa = os.path.join(directorio, archivo)
        resultados.append((archivo, procesar_instancia(ruta_completa)))

# Escribir los resultados en un archivo
with open("resumen.txt", "w") as f:
    for nombre, stats in resultados:
        f.write(f"{nombre} total: {stats['total']} - min: {stats['min']} - max: {stats['max']} - prom: {stats['prom']} - desv: {stats['desv']}\n")