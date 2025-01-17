#!/bin/bash

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

t=$(awk "BEGIN {printf(\"%.2f\", ${new_instance_num} * (240 / 100))}")
cant_nbElite=$(awk "BEGIN {printf(\"%d\", ${nbElite}*${mu})}")
cant_nbClose=$(awk "BEGIN {printf(\"%d\", ${nbClose}*${mu})}")
cant_nbGranular=$(awk "BEGIN {printf(\"%d\", ${nbGranular}*${mu})}")

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
