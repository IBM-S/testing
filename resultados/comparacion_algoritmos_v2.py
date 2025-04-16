import os
import pandas as pd

def calcular_metricas(ruta_logs):
    """
    Calcula el mínimo de los valores para cada instancia priorizando soluciones factibles.

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
                        # Extraer factibilidad de la primera línea
                        factibilidad = int(lineas[0].split("=")[1].strip())

                        # Leer los valores desde la tercera línea
                        valores_con_factibilidad = []
                        for linea in lineas[2:]:
                            valor = float(linea.strip())
                            valores_con_factibilidad.append((valor, factibilidad))

                        if instancia not in resultados:
                            resultados[instancia] = []
                        resultados[instancia].extend(valores_con_factibilidad)
            except Exception as e:
                print(f"Error leyendo el archivo {ruta_completa}: {e}")

    # Calcular métricas
    metricas = {}
    for instancia, valores in resultados.items():
        # Separar factibles e infactibles
        factibles = [v for v in valores if v[1] == 1]
        infactibles = [v for v in valores if v[1] != 1]

        if factibles:
            mejores = factibles
        else:
            mejores = infactibles

        # Obtener la tupla con menor valor
        tupla_menor = min(mejores, key=lambda x: x[0])
        metricas[instancia] = {"min": f'{round(tupla_menor[0], 2)} {tupla_menor[1]}'}

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
            fila[f"{tipo}_min"] = resultados[instancia]["min"]
        else:
            fila[f"{tipo}_min"] = None
    data_combined.append(fila)

# Crear el DataFrame combinado
df_final = pd.DataFrame(data_combined)

# Guardar el DataFrame en un archivo CSV
df_final.to_csv('comparacion_min_v3_factible_primero.csv', index=False)

print("Archivo CSV generado: comparacion_min_v3_factible_primero.csv")
