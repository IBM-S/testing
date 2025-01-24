import os

def create_folder_with_files(folder_name):
    # Ruta base para la carpeta
    base_path = '../ParamILS_ALL_vunmillon_S0'
    folder_path = os.path.join(base_path, f'inst_{folder_name}')
    
    # Crear la carpeta si no existe
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Carpeta '{folder_path}' creada exitosamente.")
    else:
        print(f"La carpeta '{folder_path}' ya existe.")
    
    # Contenido de los archivos
    files_content = {
        "All.inst": f'{folder_name}.vrp',
        "FAll.scn": f"""algo = bash hgs.sh
execdir = .
deterministic = 0
run_obj = runlength
overall_obj = mean
cutoff_time = max
cutoff_length = max
tunerTimeout = 100000000
paramfile = ../FAll.params
outdir = out/
instance_file = All.inst
test_instance_file = All.inst
""",
        f'hgs.sh': """#!/bin/bash

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
,
        "ToDoParamILS.sh": """#!/bin/bash

toTune=$1
maxEvaluations=10000
algo=GA

respaldos=respaldos${algo}
rm -rf ${respaldos}
mkdir ${respaldos}

maxSeeds=10
for instanceSet in $(cat ${toTune}); do
        scenario=F${instanceSet}.scn
        instance=F${instanceSet}.inst
        params=F${instanceSet}.params
        
        seed=0
        while [ ${seed} -lt ${maxSeeds} ]; do
                outputTuner=ParamILS_A${algo}_IS${instanceSet}_S${seed}.out
                echo "time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}"
                time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}
                echo "mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}"
                mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}
                seed=$((seed + 1))
        done
done
"""
    }
    
    # Crear los archivos con su contenido
    for file_name, content in files_content.items():
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Archivo '{file_name}' creado en la carpeta '{folder_path}'.")

if __name__ == "__main__":
    folder_name = input("Introduce el nombre de la carpeta: ")
    create_folder_with_files(folder_name)
