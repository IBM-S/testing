#ifndef GA_H
#define GA_H

#include "problemdescription.h"

typedef struct {
    int populationSize;
    double crossoverRate;
    double intraDepotMutationRate;
    double interDepotMutationRate;
    int interDepotMutationAttemptRate;
    double bound;
    double alpha;
    double beta;
    double probBestIndividualTournament;
    double probReversal;
    double probSingle;
    double elitism;
} Parameters;

void optimize(int maxIterations, Parameters &parameters, ProblemDescription &problemDescription, int seed, const std::string& datafile);

#endif
