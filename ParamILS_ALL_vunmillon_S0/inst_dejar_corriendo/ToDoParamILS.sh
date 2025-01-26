#!/bin/bash

toTune=$1
maxEvaluations=5
algo=hgs

respaldos=respaldos${algo}
rm -rf ${respaldos}
mkdir ${respaldos}

dirInst=ins
dirScn=scn
dirOutputs=ouputs

maxSeeds=10
for instanceSet in $(cat ${toTune}); do
        scenario=${instanceSet}.scn
        instance=${instanceSet}.inst
        params=params.params
        
        mv ${dirScn}/${scenario} .
        mv ${dirInst}/${instance} .
                
        seed=0
        while [ ${seed} -lt ${maxSeeds} ]; do
                outputTuner=ParamILS_A${algo}_IS${instanceSet}_S${seed}.out
                echo "time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}"
                time ruby ../paramils2.3.8-source/param_ils_2_3_run.rb -numRun ${seed} -approach focused -userunlog 1 -validN 0 -pruning 0 -maxEvals ${maxEvaluations} -scenariofile ${scenario} > ${outputTuner}
                echo "mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}"
                mv out ${respaldos}/outA${algo}_IS${instanceSet}_S${seed}
                seed=$((seed + 1))
        done
                                
        mv ${scenario} ${dirScn}
        mv ${instance} ${dirInst}

done
