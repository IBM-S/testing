import random
import os


def process_solution_files(directory):
    results = []
    instance_costs = {}

    # Iterar sobre los archivos en el directorio
    for file_name in os.listdir(directory):
        if file_name.endswith(".sol"):
            instance_type, iteration, instance_name = parse_solution_filename(file_name)

            # Leer el archivo y extraer el costo
            with open(os.path.join(directory, file_name), "r") as file:
                for line in file:
                    if line.startswith("Cost"):
                        cost = int(line.split()[1])
                        results.append(f"{instance_type} - {instance_name} - It: {iteration} - Cost: {cost}")

                        if instance_name not in instance_costs:
                            instance_costs[instance_name] = []
                        instance_costs[instance_name].append(cost)
                        break

    # Imprimir resultados y promedios
    for instance_name, costs in instance_costs.items():
        for result in results:
            if instance_name in result:
                print(result)
        avg_cost = sum(costs) / len(costs)
        instance_type = [result.split(" - ")[0] for result in results if instance_name in result][0]
        print(f"Promedio para {instance_name} ({instance_type}): {avg_cost}")


def parse_solution_filename(file_name):
    # Parsear el nombre del archivo para extraer tipo, iteración y nombre de instancia
    parts = file_name.split("_")
    instance_type = parts[0]
    iteration = parts[1]
    instance_name = parts[2].replace(".sol", "")
    return instance_type, iteration, instance_name

# Procesar los archivos .sol en un directorio
directory = "sol/"
process_solution_files(directory)