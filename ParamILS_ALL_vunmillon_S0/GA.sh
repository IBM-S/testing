#/bin/bash

dirInstances="Instances"
instance=$1
seed=$5
shift 5

#Evaluaciones totales maximas
evaluaciones=1000000
#Considera 10 minutos máximo de ejecución
TMAX=420

while [ $# != 0 ]; do
    flag="$1"
    case "$flag" in
        -crossoverRate) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              crossoverRate=$arg
            fi
            ;;
        -intraMutationRate) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              intraMutationRate=$arg
            fi
            ;;
        -interMutationRate) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              interMutationRate=$arg
            fi
            ;;
        -interAttemptRate) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              interAttemptRate=$arg
            fi
            ;;
        -bound) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              bound=$arg
            fi
            ;;
        -alpha) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              alpha=$arg
            fi
            ;;
        -beta) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              beta=$arg
            fi
            ;;
        -probBestIndividual) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              probBestIndividual=$arg
            fi
            ;;
        -probReversal) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              probReversal=$arg
            fi
            ;;
        -probSingle) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              probSingle=$arg
            fi
            ;;
        -elitism) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              elitism=$arg
            fi
            ;;
        -populationSize) if [ $# -gt 1 ]; then
              arg="$2"
              shift
              populationSize=$arg
            fi
            ;;
        *) echo "Unrecognized flag or argument: $flag"
            ;;
        esac
    shift
done

evaluaciones=100000
maxGenerations=$(awk "BEGIN {printf \"%d\",(${evaluaciones}/${populationSize})}")

params="${crossoverRate} ${intraMutationRate} ${interMutationRate} ${interAttemptRate} ${bound} ${alpha} ${beta} ${probBestIndividual} ${probReversal} ${probSingle} ${elitism} ${maxGenerations} ${populationSize}"
screen=salida

rm -rf ${screen}

echo "./GA ${dirInstances}/${instance} ${seed} ${params} > ${screen}"
./GA Instances/${instance} ${seed} ${params} > ${screen}

quality=`tail -2 ${screen} |head -1 |awk -F ' = ' '{print $2}'`


solved="SAT"
runtime=0
best_sol=0


echo "Result for ParamILS: ${solved}, ${runtime}, ${quality}, ${best_sol}, ${seed}"




