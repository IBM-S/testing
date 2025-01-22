import pandas as pd
import random 

def transform_line(line, nombre_algoritmo):
    """
    Transforma una línea del archivo de resultados al formato deseado.

    Args:
    line: Una línea del archivo de resultados en formato de cadena.

    Returns:
    Una cadena con la línea transformada.
    """

    # Dividir la línea en una lista de valores
    values = line.strip().split(',')

    # Asignar los valores a las variables correspondientes
    instance, alpha, beta, bound, crossoverRate, elitism, interAttemptRate, interMutationRate, intraMutationRate, populationSize, probBestIndividual, probReversal, probSingle = values

    # Convertir valores a absolutos si son negativos
    alpha = abs(float(alpha))
    beta = abs(float(beta))
    bound = abs(float(bound))
    crossoverRate = abs(float(crossoverRate))
    elitism = abs(float(elitism))
    interAttemptRate = abs(int(round(float(interAttemptRate))))
    interMutationRate = abs(float(interMutationRate))
    intraMutationRate = abs(float(intraMutationRate))
    populationSize = abs(float(populationSize))
    probBestIndividual = abs(float(probBestIndividual))
    probReversal = abs(float(probReversal))
    probSingle = abs(float(probSingle))

    evaluaciones = 100000
    maxGenerations = evaluaciones / int(float(populationSize))

    if int(float(populationSize)) > maxGenerations:
        maxGenerations = populationSize*2

    seed = random.randint(0,1000)
    lineas = []

    if interAttemptRate == 0:
        interAttemptRate = 1
    for i in range(10):
        seed = random.randint(0,1000)
        # Reorganizar los valores según el formato deseado
        new_line = f"../GA ../Data/DataFiles/{instance} {seed} {crossoverRate} {intraMutationRate} {interMutationRate} {interAttemptRate} {bound} {alpha} {beta} {probBestIndividual} {probReversal} {probSingle} {elitism} {int(round(float(maxGenerations)))} {int(round(float(populationSize)))} > logs_{nombre_algoritmo}/salida_{instance}_{i}"
        lineas.append(new_line)

    return lineas


# Leer el archivo de resultados (reemplaza 'resultados_KNN' con el nombre del archivo correcto)
nombre = ["ANN", "KNN", "RF"]
for i in iter(nombre):
    with open(f'resultados_{i}.txt', 'r') as f:
        with open(f'salida_{i}.txt', 'w') as output_file:
            for line in f:
                # Ignorar la primera línea si contiene encabezados
                if line.startswith('instance'):
                    continue
                
                new_lines = transform_line(line, i)
                for new_line in new_lines:
                    output_file.write(new_line + '\n')