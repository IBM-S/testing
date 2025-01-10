import os
import pandas as pd
import numpy as np
import statistics


def procesar_instancia(archivo):
    """
    Transforma una instancia al formato vrpLIB

    Args:
        archivo: Nombre del archivo de la instancia.

    Returns:
        0
    """

    # Leemos solo la primera línea como una cadena de texto
    with open(archivo, 'r') as f:
        primera_linea = f.readline()
        numeros = primera_linea.split()

        if len(numeros) == 4:
            type = int(numeros[0])
            max_number_of_vehicles_in_each_depot = int(numeros[1])
            total_numbers_of_customer = int(numeros[2])
            number_of_depots = int(numeros[3])
        else:
            max_number_of_vehicles_in_each_depot = int(numeros[0])
            total_numbers_of_customer = int(numeros[1])
            number_of_depots = int(numeros[2])
        
        segunda_linea = f.readline()
        D, Q = segunda_linea.split()

        for _ in range(number_of_depots-1):
            next(f)
        
        # Leer los datos
        datos = []
        coords_Q_clientes = []
        contador_clientes = 0
        for linea in f:
            campos = linea.strip().split(' ')  # Ajusta el separador
            lista_sin_espacios = [elemento for elemento in campos if elemento.strip()]
            coords_x, coords_y = lista_sin_espacios[1:3]
            demanda_cliente = lista_sin_espacios[4]
            contador_clientes+=1
            coords_Q_clientes.append(( (coords_x, coords_y)  , demanda_cliente))
            if (contador_clientes == total_numbers_of_customer):
                break
        coords_depots = []
        for linea in f:
            campos = linea.strip().split(' ')  # Ajusta el separador
            lista_sin_espacios = [elemento for elemento in campos if elemento.strip()]
            coords_depot_x, coords_depot_y = lista_sin_espacios[1:3]
            coords_depots.append((coords_depot_x, coords_depot_y))
    _, _, _, nombre = archivo.split("/")

    # Crear el nombre del archivo de salida
    nombre_salida = f'lib_{nombre}.mdvrp'

    # Crear la carpeta si no existe
    carpeta_salida = "vrp_lib_mdvrp"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    nombre_final = nombre.split(".")[0]

    with open(os.path.join(carpeta_salida, nombre_salida), "w") as f:
        f.write(f'NAME : {nombre_final}\n')
        f.write(f'COMMENT : ""\n')
        f.write(f'TYPE : MDVRP\n')
        f.write(f'VEHICLES : {max_number_of_vehicles_in_each_depot*number_of_depots}\n')
        f.write(f'DIMENSION : {total_numbers_of_customer+number_of_depots}\n')
        f.write(f'EDGE_WEIGHT_TYPE : EUC_2D\n')
        f.write(f'CAPACITY : {Q}\n')
        if D != "0":
            f.write(f'VEHICLES_MAX_DISTANCE : {D}\n')
        f.write(f'NODE_COORD_SECTION\n')

        #Coordenadas depots
        for i, (x, y) in enumerate(coords_depots, start=1):
            f.write(f'{i:<7}{x:<15}{y}\n')
    
        # Coordenadas clientes
        for i, ((x, y), _) in enumerate(coords_Q_clientes, start=1+number_of_depots):
            f.write(f'{i:<7}{x:<15}{y}\n')  
        f.write(f'DEMAND_SECTION\n')

        #Demanda depots
        for i in range(1, number_of_depots+1, 1):
            f.write(f'{i:<7}0\n')  
        #Demanda clientes
        for i, ((_, _), demanda) in enumerate(coords_Q_clientes, start=1+number_of_depots):
            f.write(f'{i:<7}{demanda}\n')  

        f.write(f'VEHICLES_DEPOT_SECTION\n')
        total_numbers_of_vehicles = max_number_of_vehicles_in_each_depot*number_of_depots
        cont = 1
        for i in range(1, total_numbers_of_vehicles+1, 1):
            f.write(f'{i:<7}{cont}\n')
            if (i%max_number_of_vehicles_in_each_depot == 0):
                cont+=1

        f.write(f'DEPOT_SECTION\n')
        for i in range(1, number_of_depots+1, 1):
            f.write(f'{i}\n')  
        # Finalizar archivo
        f.write(f'EOF\n')

    # Calculando las estadísticas

    return 0

# Directorio donde se encuentran las instancias
directorio = "../Data/DataFiles"  # Reemplaza con la ruta correcta

# Lista para almacenar los resultados
resultados = []

# Iterar sobre los archivos
for archivo in os.listdir(directorio):
    if archivo.startswith("pr"):
        ruta_completa = os.path.join(directorio, archivo)
        resultados.append((archivo, procesar_instancia(ruta_completa)))