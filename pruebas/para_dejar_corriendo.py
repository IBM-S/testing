import os

# Ruta de la carpeta principal y subcarpetas
base_dir = "../ParamILS_ALL_vunmillon_S0"
inst_dir = os.path.join(base_dir, "inst_dejar_corriendo")
to_tune_dir = os.path.join(inst_dir, "toTune")

# Crear las carpetas necesarias
os.makedirs(to_tune_dir, exist_ok=True)

# Ruta del directorio que contiene las instancias
instances_dir = "../Instances/CVRP"

# Lista para almacenar los nombres de las instancias
instance_names = []

# Recorremos los archivos en el directorio de instancias
for filename in os.listdir(instances_dir):
    if filename.startswith("X-n") and filename.endswith(".vrp"):
        # Nombre base de la instancia (sin extensión)
        instance_name = filename[:-4]
        instance_names.append(instance_name)

        # Crear archivo {instancia}.scn
        scn_content = f"""algo = bash hgs.sh
execdir = .
deterministic = 0
run_obj = runlength
overall_obj = mean
cutoff_time = max
cutoff_length = max
tunerTimeout = 100000000
paramfile = params.params
outdir = out/
instance_file = {instance_name}.inst
test_instance_file = {instance_name}.inst
"""
        scn_path = os.path.join(inst_dir, f"{instance_name}.scn")
        with open(scn_path, "w") as scn_file:
            scn_file.write(scn_content)

        # Crear archivo {instancia}.inst
        inst_content = f"{filename}\n"
        inst_path = os.path.join(inst_dir, f"{instance_name}.inst")
        with open(inst_path, "w") as inst_file:
            inst_file.write(inst_content)

# Crear archivo All.tune dentro de toTune
all_tune_path = os.path.join(to_tune_dir, "All.tune")
with open(all_tune_path, "w") as all_tune_file:
    all_tune_file.write("\n".join(instance_names) + "\n")

print(f"Archivos creados correctamente en la carpeta '{inst_dir}'.")
