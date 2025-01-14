import os
import pandas as pd

def eliminar_comas_de_lista(lista):
    """Elimina todas las comas de los elementos de una lista.

    Args:
    lista: La lista de elementos.

    Returns:
    Una nueva lista con las comas eliminadas de los elementos.
    """

    nueva_lista = []
    for elemento in lista:
        nuevo_elemento = elemento.replace(",", "")
        nueva_lista.append(nuevo_elemento)
    return nueva_lista


def leer_archivo_result(ruta):
    """
    Busca y lee el archivo que contiene "result" en la ruta especificada.

    Args:
        ruta (str): Ruta principal donde se encuentran los archivos.

    Returns:
        str: Contenido del archivo si se encuentra, o un mensaje de error si no.
    """

    for archivo in os.listdir(ruta):
        if "result" in archivo:
            ruta_completa = os.path.join(ruta, archivo)
            #print(ruta_completa)
            try:
                with open(ruta_completa, 'r') as f:
                    contenido = f.readline().strip().split(" ")
                    parametros = contenido[4:]
                    return parametros
            except FileNotFoundError:
                print(f"El archivo {ruta_completa} no se pudo abrir.")
                return None
    
    print("No se encontró ningún archivo que contenga 'result' en la ruta especificada.")
    return None

# Ruta principal a los archivos
ruta_principal = "ParamILS_ALL_vunmillon_S0/respaldosGA/outAGA_ISAll_S0"

# Llamada a la función para leer el archivo
contenido = leer_archivo_result(ruta_principal)

if contenido:
    print(contenido)

configuracion = {}
for i in range(len(contenido)):
    contenido[i] = contenido[i].replace(",", "")
    pares = contenido[i].split("=")  # Separa los pares "parámetro=valor"
    configuracion[pares[0]] = pares[1]

print(configuracion)

#nombres_columnas = ["alpha", "beta", "bound", "crossoverRate", "elitism", "interAttemptRate", "interMutationRate", 
#                    "intraMutationRate", "populationSize", "probBestIndividual", "probReversal", "probSingle"]

# Crear un DataFrame a partir del diccionario de configuración
df = pd.DataFrame.from_dict(configuracion, orient='index').T

# Guardar el DataFrame en un archivo CSV
df.to_csv('configuracion.csv', index=False)