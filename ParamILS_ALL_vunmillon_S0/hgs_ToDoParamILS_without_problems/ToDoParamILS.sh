#!/bin/bash

toTune=$1
maxEvaluations=10000
algo=HGS

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
