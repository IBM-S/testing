import os

# Ruta de la carpeta principal y subcarpetas
base_dir = "../ParamILS_ALL_vunmillon_S0"
inst_dir = os.path.join(base_dir, "inst_pr_dejar_corriendo")
to_tune_dir = os.path.join(inst_dir, "toTune")
scn_dir = os.path.join(inst_dir, "scn")
ins_dir = os.path.join(inst_dir, "ins")

# Crear las carpetas necesarias
os.makedirs(to_tune_dir, exist_ok=True)
os.makedirs(scn_dir, exist_ok=True)
os.makedirs(ins_dir, exist_ok=True)

# Ruta del directorio que contiene las instancias
instances_dir = "../ParamILS_ALL_vunmillon_S0/Instances"

# Lista para almacenar los nombres de las instancias
instance_names = []

ga_content = """#/bin/bash

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
maxGenerations=$(awk "BEGIN {printf \\"%d\\",(${evaluaciones}/${populationSize})}")

params="${crossoverRate} ${intraMutationRate} ${interMutationRate} ${interAttemptRate} ${bound} ${alpha} ${beta} ${probBestIndividual} ${probReversal} ${probSingle} ${elitism} ${maxGenerations} ${populationSize}"
screen=salida

rm -rf ${screen}

echo "../../GA ../${dirInstances}/${instance} ${seed} ${params} > ${screen}"
../../GA ../Instances/${instance} ${seed} ${params} > ${screen}

quality=`tail -2 ${screen} |head -1 |awk -F ' = ' '{print $2}'`
feasibility=`tail -3 ${screen} |head -1 |awk -F ' = ' '{print $2}'`

solved="SAT"
runtime=0
best_sol=0

penalidad=10

if [ "$feasibility" -eq 0 ]; then
  quality=$(awk "BEGIN {printf \\"%d\\",(${quality}*${penalidad})}")
fi


echo "Result for ParamILS: ${solved}, ${runtime}, ${quality}, ${best_sol}, ${seed}"
"""

todo_paramils_content = """#/bin/bash

toTune=$1
maxEvaluations=10000
algo=GA

respaldos=respaldos${algo}
rm -rf ${respaldos}
mkdir ${respaldos}

dirInst=ins
dirScn=scn
dirOutputs=outputs
        
mkdir -p ${dirOutputs}


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

params_content = """crossoverRate {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75, 1.0}[0.6]
intraMutationRate {0.1, 0.2, 0.25, 0.5, 0.75, 1.0}[0.2]
interMutationRate {0.1, 0.2, 0.25, 0.5, 0.75, 1.0}[0.25]
interAttemptRate {1, 2, 5, 10, 20}[10]
bound {0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0}[2.0]
alpha {10, 50, 100, 150, 200}[100]
beta {0.001 , 0.01, 0.05, 0.1, 0.5, 1.0, 10.0}[0.001]
probBestIndividual {0.6, 0.7, 0.8, 0.9, 1.0}[0.8]
probReversal {0.0, 0.25, 0.33, 0.50, 0.75, 1.0}[0.33]
probSingle {0.0, 0.25, 0.33, 0.50, 0.75, 1.0}[0.33]
elitism {0.01, 0.05, 0.1, 0.15, 0.20}[0.01]
populationSize {50, 100, 200, 400, 500, 800, 1000, 2000}[400]
"""


# Crear archivos ga.sh y ToDoParamILS.sh
with open(os.path.join(inst_dir, "GA.sh"), "w") as ga_file:
    ga_file.write(ga_content)

with open(os.path.join(inst_dir, "ToDoParamILS.sh"), "w") as todo_file:
    todo_file.write(todo_paramils_content)

with open(os.path.join(inst_dir, "params.params"), "w") as params_file:
    params_file.write(params_content)

contador = 0

# Recorremos los archivos en el directorio de instancias
for filename in os.listdir(instances_dir):
    if filename.startswith("pr") and ("problem") not in filename and filename.endswith(".dat"):
        # Nombre base de la instancia (sin extensión)
        instance_name = filename[:-4]
        instance_names.append(instance_name)

        # Crear archivo {instancia}.scn
        scn_content = f"""algo = bash GA.sh
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
      f"  - {inst_dir} (archivos ga.sh, ToDoParamILS.sh y params.params).")