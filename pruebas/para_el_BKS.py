import os
import re

# Ruta de las instancias
path = "../Instances/CVRP"

# Listas para almacenar los nombres de las instancias
instancias_x = []
instancias_cmt = []
instancias_golden = []

# Función para extraer el número que sigue a la letra 'n' en el caso de las instancias X
def extraer_numero_x(instancia):
    match = re.search(r'n(\d+)', instancia)
    if match:
        return int(match.group(1))
    return -1

# Función para extraer el número en el caso de las instancias CMT
def extraer_numero_cmt(instancia):
    match = re.search(r'CMT(\d+)', instancia)
    if match:
        return int(match.group(1))
    return -1

# Recorrer todos los archivos en el directorio
for filename in os.listdir(path):
    # Verificar si el archivo tiene la extensión '.vrp'
    if filename.endswith('.vrp'):
        if filename.startswith('X'):
            # Eliminar la extensión '.vrp' y agregar a la lista de instancias X
            instancias_x.append(filename[:-4])
        elif filename.startswith('CMT'):
            # Eliminar la extensión '.vrp' y agregar a la lista de instancias CMT
            instancias_cmt.append(filename[:-4])
        elif filename.startswith('Golden'):
            # Eliminar la extensión '.vrp' y agregar a la lista de instancias Golden
            instancias_golden.append(filename[:-4])

# Ordenar las instancias X por el número que sigue a la letra 'n'
instancias_x.sort(key=extraer_numero_x)

# Ordenar las instancias CMT por el número después de CMT
instancias_cmt.sort(key=extraer_numero_cmt)

# Crear los archivos .txt con los nombres de las instancias ordenados
with open("instancias_x.txt", "w") as file_x:
    for instancia in instancias_x:
        # Formato X-nA-kB
        file_x.write(f"{instancia}\n")

with open("instancias_cmt.txt", "w") as file_cmt:
    for i, instancia in enumerate(instancias_cmt, start=1):
        # Formato CMT1, CMT2, ...
        file_cmt.write(f"CMT{i}_\n")

with open("instancias_golden.txt", "w") as file_golden:
    for i, instancia in enumerate(instancias_golden, start=1):
        # Formato Golden_1_, Golden_2_, ...
        file_golden.write(f"Golden_{i}_\n")

print("Archivos de instancias creados con éxito.")
