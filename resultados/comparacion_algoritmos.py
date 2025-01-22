import os
import pandas as pd

def calcular_metricas(ruta_logs):
    """
    Calcula el mínimo, máximo y promedio de los valores para cada instancia.

    Args:
        ruta_logs (str): Ruta de la carpeta donde se encuentran los archivos de salida.

    Returns:
        dict: Diccionario con las métricas calculadas para cada instancia.
    """
    resultados = {}

    # Iterar sobre los archivos en la carpeta de logs
    for archivo in os.listdir(ruta_logs):
        if archivo.startswith("salida_"):
            # Extraer el nombre de la instancia
            partes = archivo.split("_")
            instancia = partes[1]

            ruta_completa = os.path.join(ruta_logs, archivo)
            try:
                # Leer el archivo y obtener el último valor (resultado)
                with open(ruta_completa, 'r') as f:
                    lineas = f.readlines()
                    if lineas:
                        valor = float(lineas[-1].strip())  # Asume que el resultado está en la última línea

                        if instancia not in resultados:
                            resultados[instancia] = []
                        resultados[instancia].append(valor)
            except Exception as e:
                print(f"Error leyendo el archivo {ruta_completa}: {e}")

    # Calcular métricas
    metricas = {}
    for instancia, valores in resultados.items():
        minimo = min(valores)
        maximo = max(valores)
        promedio = sum(valores) / len(valores)
        metricas[instancia] = {"min": minimo, "max": maximo, "average": promedio}

    return metricas

# Rutas de las carpetas logs
rutas_logs = {"ANN": "logs_ANN", "KNN": "logs_KNN", "RF": "logs_RF"}

# Diccionario para almacenar los resultados por tipo
resultados_totales = {}
for tipo, ruta in rutas_logs.items():
    resultados_totales[tipo] = calcular_metricas(ruta)

# Combinar los resultados en un DataFrame final
data_combined = []
instancias = set()
for resultados in resultados_totales.values():
    instancias.update(resultados.keys())

for instancia in sorted(instancias):
    fila = {"instance": instancia}
    for tipo, resultados in resultados_totales.items():
        if instancia in resultados:
            fila[f"{tipo}_prom"] = resultados[instancia]["average"]
            fila[f"{tipo}_min"] = resultados[instancia]["min"]
            fila[f"{tipo}_max"] = resultados[instancia]["max"]
        else:
            fila[f"{tipo}_prom"] = None
            fila[f"{tipo}_min"] = None
            fila[f"{tipo}_max"] = None
    data_combined.append(fila)

# Crear el DataFrame combinado
df_final = pd.DataFrame(data_combined)

# Guardar el DataFrame en un archivo CSV
df_final.to_csv('comparacion_metricas.csv', index=False)

print("Archivo CSV generado: comparacion_metricas.csv")
