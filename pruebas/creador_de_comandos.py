import random
import os

def calculate_time(instance_name):
    # Extraer el número que acompaña a 'n' en el nombre de la instancia
    try:
        n_value = int(instance_name.split('-')[1].split('n')[1])
        return (n_value - 1) * (240 / 100)
    except (IndexError, ValueError):
        raise ValueError(f"El nombre de la instancia '{instance_name}' no tiene el formato esperado.")

def generate_commands(instance, instance_type, file_name):
    # Verificar que el tipo de instancia sea válido
    valid_types = ["verySmall", "small", "medium", "long", "veryLong"]
    if instance_type not in valid_types:
        raise ValueError(f"El tipo de instancia '{instance_type}' no es válido. Debe ser uno de {valid_types}.")

    # Mapear el tipo de instancia a su número correspondiente
    type_to_number = {"verySmall": 1, "small": 2, "medium": 3, "long": 4, "veryLong": 5}
    type_number = type_to_number[instance_type]

    # Formato base para el comando
    command_template = "./hgs ../Instances/CVRP/{instance}.vrp {type}_{index}_{instance}.sol -seed {seed} -t {time} > logs_{type}_{index}_{instance}"

    # Calcular el tiempo basado en el nombre de la instancia
    time = calculate_time(instance)

    # Generar comandos para la instancia
    commands = []
    for i in range(1, 11):  # Generar 10 iteraciones
        seed = random.randint(1, 100000)  # Generar un número aleatorio como semilla
        command = command_template.format(instance=instance, type=instance_type, index=i, seed=seed, time=time)
        commands.append(command)

    # Unir los comandos con saltos de línea
    commands_text = "\n".join(commands) + "\n"

    # Crear o agregar al archivo de salida
    if os.path.exists(file_name):
        print(f"El archivo '{file_name}' ya existe. Se agregarán nuevos comandos.")
        mode = "a"  # Modo append para agregar al archivo existente
    else:
        mode = "w"  # Modo write para crear un nuevo archivo

    with open(file_name, mode) as file:
        file.write(commands_text)

    return file_name

file_name = "comandos_para_probar.txt"

# Lista de configuraciones
configurations = [
    {"instances": ["X-n242-k48", "X-n916-k207"], "type": "verySmall", "file_name": "comandos.txt"},
    {"instances": ["X-n294-k50", "X-n599-k92"], "type": "small", "file_name": "comandos.txt"},
    {"instances": ["X-n157-k13", "X-n322-k28"], "type": "medium", "file_name": "comandos.txt"},
    {"instances": ["X-n115-k10", "X-n359-k29"], "type": "long", "file_name": "comandos.txt"},
    {"instances": ["X-n190-k8", "X-n1001-k43"], "type": "veryLong", "file_name": "comandos.txt"},
]

# Iterar sobre las configuraciones y generar comandos
for config in configurations:
    instance_type = config["type"]
    file_name = config["file_name"]
    for instance in config["instances"]:
        output_file = generate_commands(instance, instance_type, file_name)
        print(f"Comandos escritos en: {output_file}")
