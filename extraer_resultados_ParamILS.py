import os
import pandas as pd

def leer_archivo_result(ruta_completa):
    """
    Lee el archivo que contiene los parámetros en la ruta especificada.

    Args:
        ruta_completa (str): Ruta completa del archivo a leer.

    Returns:
        dict: Diccionario con los parámetros y sus valores.
    """
    try:
        with open(ruta_completa, 'r') as f:
            contenido = f.readline().strip().split(" ")
            parametros = contenido[4:]  # Asume que los parámetros comienzan desde la posición 4
            configuracion = {}
            for param in parametros:
                param = param.replace(",", "")
                clave, valor = param.split("=")
                configuracion[clave] = valor
            return configuracion
    except Exception as e:
        print(f"Error leyendo el archivo {ruta_completa}: {e}")
        return None

def procesar_resultados(ruta_principal):
    """
    Procesa todas las carpetas y archivos para generar un DataFrame con los resultados.

    Args:
        ruta_principal (str): Ruta principal donde se encuentran las carpetas de las instancias.

    Returns:
        pd.DataFrame: DataFrame con los resultados consolidados.
    """
    data = []
    # Iterar sobre las carpetas de instancias
    for instancia in os.listdir(ruta_principal):
        if ("inst_") in instancia:
            ruta_instancia = os.path.join(ruta_principal, instancia)
            if not os.path.isdir(ruta_instancia):
                continue

            respaldos_path = os.path.join(ruta_instancia, "respaldosGA")
            if not os.path.exists(respaldos_path):
                print(f"No se encontró la carpeta respaldosGA en {ruta_instancia}")
                continue
            # Iterar sobre las carpetas de out
            for carpeta_out in os.listdir(respaldos_path):
                if carpeta_out.startswith("out"):
                    id_repeticion = carpeta_out.split("_S")[-1]  # Extraer el ID de repetición
                    ruta_out = os.path.join(respaldos_path, carpeta_out)
                    # Buscar el archivo result_X.txt
                    for archivo in os.listdir(ruta_out):
                        if ("result") in archivo and archivo.endswith(".txt"):
                            ruta_result = os.path.join(ruta_out, archivo)
                            parametros = leer_archivo_result(ruta_result)
                            if parametros:
                                fila = {"instancia": instancia.split("_")[-1], "id_repeticion": id_repeticion}
                                fila.update(parametros)
                                data.append(fila)
    # Crear el DataFrame
    df = pd.DataFrame(data)
    return df

cant_num = 9

# Ruta principal
ruta_principal = "ParamILS_ALL_vunmillon_S0"

# Procesar los resultados y generar el DataFrame
df_resultados = procesar_resultados(ruta_principal)

# Guardar el DataFrame en un archivo CSV
df_resultados.to_csv('resultados_parametros.csv', index=False)

print("Archivo CSV generado: resultados_parametros.csv")
