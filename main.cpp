#include "problemdescription.h"
#include "ga.h"

int main(int argc, char* argv[]) {
    if (argc < 14) {
        std::cerr << "Usage: " << argv[0] 
                << " <data_file> <seed> <crossover_rate> <intra_mutation_rate> "
                "<inter_mutation_rate> <inter_attempt_rate> <bound> "
                "<alpha> <beta> <probBestIndividual> <probReversal> " 
                "<probSingle> <elitism> <max_generations> <population_size>\n";
        return 1;
    }

    std::string dataFile = argv[1];
    int populationSize = std::stoi(argv[15]);
    double crossoverRate = std::stod(argv[3]);
    double intraMutationRate = std::stod(argv[4]);

    double interMutationRate = std::stod(argv[5]);
    int interAttemptRate = std::stoi(argv[6]);
    double bound =  std::stoi(argv[7]);
    
    double alpha = std::stoi(argv[8]);
    double beta = std::stod(argv[9]);
    double probBestIndividualTournament= std::stod(argv[10]);
    double probReversal = std::stod(argv[11]);
    
    double probSingle = std::stod(argv[12]);
    double elitism = std::stod(argv[13]);
    int maxGenerations = std::stoi(argv[14]);
    int seed = std::stoi(argv[2]);

    ProblemDescription problemDescription(dataFile);

    Parameters parameters;
    parameters.populationSize = populationSize;
    parameters.crossoverRate = crossoverRate;
    parameters.intraDepotMutationRate = intraMutationRate;
    parameters.interDepotMutationRate = interMutationRate;
    parameters.interDepotMutationAttemptRate = interAttemptRate;
    parameters.bound = bound;
    parameters.alpha = alpha;
    parameters.beta = beta;
    parameters.probBestIndividualTournament = probBestIndividualTournament;
    parameters.probReversal = probReversal;
    parameters.probSingle = probSingle;
    parameters.elitism = elitism;

    optimize(maxGenerations, parameters, problemDescription, seed, dataFile);
    return 0;
}