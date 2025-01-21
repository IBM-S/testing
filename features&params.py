import pandas as pd

# Cargar los datos de los archivos CSV
resultados_parametros = pd.read_csv("resultados_parametros.csv")
resultados_funcion_objetivo = pd.read_csv("resultados_parametros_2.csv")

features = pd.read_csv("EXTRA/features_inst/features_p.csv")


resultados_funcion_objetivo = resultados_funcion_objetivo.drop(["instance", "id_repeticion"], axis=1)

# Suponiendo que los datos están ordenados de manera que las filas correspondientes en ambos DataFrames representan la misma instancia y configuración
# Y que la columna con el valor de la función objetivo se llama 'valor_funcion_objetivo'

# Combinar los DataFrames para tener todos los datos en uno
datos_completos = pd.concat([resultados_parametros, resultados_funcion_objetivo], axis=1)

#print(datos_completos.head())

# Agrupar por instancia y encontrar la fila con el menor valor de la función objetivo
mejores_parametros = datos_completos.groupby('instance').apply(lambda x: x.loc[x['FO'].idxmin()], include_groups=False)
mejores_parametros = mejores_parametros.drop(["id_repeticion", "FO"], axis=1)

datos_completos = pd.merge(features, mejores_parametros, on='instance')

# Guardar los resultados en un nuevo archivo CSV
datos_completos.to_csv("features&params_p.csv", index=False)