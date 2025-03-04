import os
import pandas as pd

def calcular_metricas(ruta_logs):
    """
    Calcula el mínimo, máximo y promedio de los valores para cada instancia.

    Args:
        ruta_logs (str): Ruta de la carpeta donde se encuentran los archivos de salida.

    Returns:
        pd.DataFrame: DataFrame con las métricas calculadas para cada instancia.
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
    data = []
    for instancia, valores in resultados.items():
        minimo = min(valores)
        maximo = max(valores)
        promedio = sum(valores) / len(valores)
        data.append({"instance": instancia, "min": minimo, "max": maximo, "average": promedio})

    # Crear el DataFrame
    return pd.DataFrame(data)

# Ruta de la carpeta logs
ruta_logs = "logs"

# Calcular las métricas y generar el DataFrame
df_metricas = calcular_metricas(ruta_logs)

# Guardar el DataFrame en un archivo CSV
df_metricas.to_csv('metricas_instancias_v2.csv', index=False)

print("Archivo CSV generado: metricas_instancias_v2.csv")
