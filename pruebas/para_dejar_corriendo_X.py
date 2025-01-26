import os

# Ruta de la carpeta principal y subcarpetas
base_dir = "../ParamILS_ALL_vunmillon_S0"
inst_dir = os.path.join(base_dir, "_inst_X_dejar_corriendo")
to_tune_dir = os.path.join(inst_dir, "toTune")
scn_dir = os.path.join(inst_dir, "scn")
ins_dir = os.path.join(inst_dir, "ins")

# Crear las carpetas necesarias
os.makedirs(to_tune_dir, exist_ok=True)
os.makedirs(scn_dir, exist_ok=True)
os.makedirs(ins_dir, exist_ok=True)

# Ruta del directorio que contiene las instancias
instances_dir = "../Instances/CVRP"

# Lista para almacenar los nombres de las instancias
instance_names = []

hgs_content = """#/bin/bash

dirInstances="Instances/CVRP"
instance=$1
seed=$5
shift 5

# Evaluaciones totales máximas
evaluaciones=1000000

while [ $# != 0 ]; do
    flag="$1"
    case "$flag" in
        -mu) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              mu=$arg
            fi
            ;;
        -lambda) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              lambda=$arg
            fi
            ;;
        -nbElite) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              nbElite=$arg
            fi
            ;;
        -nbClose) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              nbClose=$arg
            fi
            ;;
        -nbGranular) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              nbGranular=$arg
            fi
            ;;
        -targetFeasible) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              targetFeasible=$arg
            fi
            ;;
        -repair) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              repair=$arg
            fi
            ;;
        -veh) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              veh=$arg
            fi
            ;;
        -round) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              round=$arg
            fi
            ;;
        -log) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              log=$arg
            fi
            ;;
        -nbIterPenaltyManagement) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              nbIterPenaltyManagement=$arg
            fi
            ;;
        -penaltyIncrease) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              penaltyIncrease=$arg
            fi
            ;;
        -penaltyDecrease) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              penaltyDecrease=$arg
            fi
            ;;
        -it) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              it=$arg
            fi
            ;;
        *) echo "Unrecognized flag or argument: $flag"
            ;;
        esac
    shift
done

# Extraer el número de la instancia
instance_num=$(echo "$instance" | cut -d'-' -f2 | cut -d'n' -f2)
# Calcular el nuevo número de instancia
new_instance_num=$((instance_num - 1))

t=$(awk "BEGIN {printf(\\"%.2f\\", ${new_instance_num} * (240 / 100))}")
cant_nbElite=$(awk "BEGIN {printf(\\"%d\\", ${nbElite}*${mu})}")
cant_nbClose=$(awk "BEGIN {printf(\\"%d\\", ${nbClose}*${mu})}")
cant_nbGranular=$(awk "BEGIN {printf(\\"%d\\", ${nbGranular}*${mu})}")

if [ "$cant_nbGranular" -eq 0 ]; then
    cant_nbGranular=1
fi

#nbElite {1, 2, 3, 4, 5, 10, 25, 40, 50, 75, 100, 150, 200}[4] 
#nbClose {1, 5, 10, 25, 40, 50}[5] 
#nbGranular {1, 2, 5, 10, 20, 25, 50}[20] 

params="-t ${t} -mu ${mu} -lambda ${lambda} -nbElite ${cant_nbElite} -nbClose ${cant_nbClose} -nbGranular ${cant_nbGranular} -targetFeasible ${targetFeasible} -repair ${repair} -round 1 -log 0 -nbIterPenaltyManagement ${nbIterPenaltyManagement} -penaltyIncrease ${penaltyIncrease} -penaltyDecrease ${penaltyDecrease} -it ${it}"
screen=mySolution.sol

rm -rf ${screen}

echo "../../build/hgs ../../${dirInstances}/${instance} ${screen} -seed ${seed} ${params} > ${screen}"
../../build/hgs ../../${dirInstances}/${instance} ${screen} -seed ${seed} ${params} > ${screen}

quality=$(tail -1 ${screen} | awk -F ' ' '{print $2}')

solved="SAT"
runtime=0
best_sol=0

echo "Result for ParamILS: ${solved}, ${runtime}, ${quality}, ${best_sol}, ${seed}"
"""

todo_paramils_content = """#/bin/bash

toTune=$1
maxEvaluations=10000
algo=hgs

respaldos=respaldos${algo}
rm -rf ${respaldos}
mkdir ${respaldos}

dirInst=ins
dirScn=scn
dirOutputs=outputs

maxSeeds=10
for instanceSet in $(cat ${toTune}); do
        scenario=${instanceSet}.scn
        instance=${instanceSet}.inst
        params=params.params
        
        instanceOutputDir=${dirOutputs}/outs_${instanceSet}
        mkdir -p ${instanceOutputDir}
        
        mv ${dirScn}/${scenario} .
        mv ${dirInst}/${instance} .
                
        seed=0
        while [ ${seed} -lt ${maxSeeds} ]; do
                outputTuner=ParamILS_A${algo}_IS${instanceSet}_S${seed}.out
                echo "time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}"
                time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}
                
                mv ${outputTuner} ${instanceOutputDir}/
                echo "mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}"
                mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}
                seed=$((seed + 1))
        done
                
        mv ${scenario} ${dirScn}
        mv ${instance} ${dirInst}

done
"""

params_content = """mu {5, 10, 25, 40, 50, 75, 100, 150, 200}[25]
lambda {1, 5, 10, 25, 40, 50, 75, 100, 150, 200}[40]
nbElite {0, 0.01, 0.05, 0.1, 0.16, 0.2, 0.3, 0.4, 0.5, 0.75, 1}[0.16]
nbClose {0.01, 0.05, 0.1, 0.15, 0.2, 0.25}[0.2]
nbGranular {0.01, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 0.8, 1}[0.8]
targetFeasible {0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}[0.2] 
repair {0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}[0.5] 
nbIterPenaltyManagement {1, 10, 50, 100, 200, 400, 500, 800, 1000, 2000}[100]
penaltyIncrease {1.001, 1.2, 1.5, 2, 5, 10}[1.2]
penaltyDecrease {0.1, 0.2, 0.5, 0.75, 0.85, 0.95, 0.99}[0.85]
it {1000, 5000, 10000, 15000, 20000, 30000}[20000]
"""


# Crear archivos hgs.sh y ToDoParamILS.sh
with open(os.path.join(inst_dir, "hgs.sh"), "w") as hgs_file:
    hgs_file.write(hgs_content)

with open(os.path.join(inst_dir, "ToDoParamILS.sh"), "w") as todo_file:
    todo_file.write(todo_paramils_content)

with open(os.path.join(inst_dir, "params.params"), "w") as params_file:
    params_file.write(params_content)

contador = 0

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
        scn_path = os.path.join(scn_dir, f"{instance_name}.scn")
        with open(scn_path, "w") as scn_file:
            scn_file.write(scn_content)

        # Crear archivo {instancia}.inst
        inst_content = f"{filename}\n"
        inst_path = os.path.join(ins_dir, f"{instance_name}.inst")
        with open(inst_path, "w") as inst_file:
            inst_file.write(inst_content)
        
        if contador == -1:
            break
        contador+=1

# Crear archivo All.tune dentro de toTune
all_tune_path = os.path.join(to_tune_dir, "All.tune")
with open(all_tune_path, "w") as all_tune_file:
    all_tune_file.write("\n".join(instance_names) + "\n")

print(f"Archivos creados correctamente en las carpetas:\n"
      f"  - {scn_dir} (archivos .scn)\n"
      f"  - {ins_dir} (archivos .inst)\n"
      f"  - {to_tune_dir} (archivo All.tune)\n"
      f"  - {inst_dir} (archivos hgs.sh, ToDoParamILS.sh y params.params).")