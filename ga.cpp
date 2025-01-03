#include <vector> // vector
#include <list> // list
#include <string> // string, to_string
#include <unordered_map> // unordered_map
#include <cmath> // sqrt
#include <algorithm> // shuffle
#include <random> // default_random_engine
#include <chrono> // chrono::system_clock::now().time_since_epoch().count()
#include <cstdlib> // rand
#include <iostream> // cout, endl
#include <sstream> // ostringstream
#include <fstream> // ofstream
#include <csignal> // signal, SIGINT

#include "ga.h"
#include "problemdescription.h"


typedef std::vector<std::list<int>> Chromosome;
typedef std::vector<std::vector<std::list<int>>> Routing;


// Global object with every data from the problem loaded
ProblemDescription problemDescription;

// Global vector with the swappable depots for each customers
std::vector<std::vector<int>> swappableCustomers;

int seed_global;


// Euclidean distance
double l2(double x, double y){
    return std::sqrt(x * x + y * y);
}


// Check if a random double is less than a given probability
bool randomCheck(double p){
    double r = (double) (((double) rand()) / ((double) RAND_MAX)); // Random double between 0 and 1
    return r < p;
}


// Assign customers to the depot that is closest in terms of euclidian distance
// Store everything as a vector of vectors and return it
// No need to use linkedlists, as the method is only called once and the shuffling is much easier
std::vector<std::vector<int>> assignCustomersDepots(double bound){
    std::vector<std::vector<int>> assignment(problemDescription.t); // Initialize a vector of empty vectors
    swappableCustomers = std::vector<std::vector<int>>(problemDescription.n); // Initialize a vector of vectors containing other close depots to each customer
    for(int i = 0; i < problemDescription.n; i++){
        double customerX = problemDescription.customers[i].x;
        double customerY = problemDescription.customers[i].y;
        double depotX = problemDescription.depots[0].x;
        double depotY = problemDescription.depots[0].y;
        int closestDepot = 0;
        double closestDistance = l2(customerX - depotX, customerY - depotY);
        double dist;

        for(int j = 1; j < problemDescription.t; j++){
            depotX = problemDescription.depots[j].x;
            depotY = problemDescription.depots[j].y;
            dist = l2(customerX - depotX, customerY - depotY);
            if(dist < closestDistance){
                closestDepot = j;
                closestDistance = dist;
            }
        }

        assignment[closestDepot].push_back(i);

        // Also include the assigned depot as the crossover operator can remove the customer, thus making it unable to come back
        for(int j = 0; j < problemDescription.t; j++){
            depotX = problemDescription.depots[j].x;
            depotY = problemDescription.depots[j].y;
            dist = l2(customerX - depotX, customerY - depotY);
            if((dist - closestDistance) / closestDistance <= bound && 2 * dist <= problemDescription.depots[j].D){
                swappableCustomers[i].push_back(j);
            }
        }
    }
    return assignment;
}


// Create a vector of chromosomes to return as the population
// Then create an initial assignment of customers to depots
// To make a random population, go through every chromosome, and assign to it a random shuffle of the distance-assignment
std::vector<Chromosome> generatePopulation(int populationSize, double bound){
    std::vector<Chromosome> population(populationSize, std::vector<std::list<int>>(problemDescription.t));

    std::vector<std::vector<int>> assignment = assignCustomersDepots(bound); // vector instead of list because of std::shuffle()

    //unsigned int pseed = std::chrono::system_clock::now().time_since_epoch().count();
    unsigned int pseed = seed_global;

    for(int i = 0; i < populationSize; i++){
        for(int j = 0; j < problemDescription.t; j++){
            std::shuffle(assignment[j].begin(), assignment[j].end(), std::default_random_engine(pseed));
            population[i][j] = std::list<int>(assignment[j].begin(), assignment[j].end());
        }
    }

    return population;
}


// Get the distance for one route
// Return the sum of euclidian distances
double getRouteDistance(int depot, std::list<int> &route){
    if(route.size() == 0){
        return 0;
    }
    double distance = 0;
    double depotX = problemDescription.depots[depot].x;
    double depotY = problemDescription.depots[depot].y;
    double x0 = depotX;
    double y0 = depotY;
    double x1, y1;
    
    for(int customer : route){
        x1 = problemDescription.customers[customer].x;
        y1 = problemDescription.customers[customer].y;
        distance += l2(x1 - x0, y1 - y0);
        x0 = x1;
        y0 = y1;
    }

    distance += l2(depotX - x0, depotY - y0); // Complete the round-trip

    return distance;
}


// Get the load for one route
int getRouteLoad(std::list<int> &route){
    int load = 0;
    for(int customer : route){
        load += problemDescription.customers[customer].q;
    }
    return load;
}


// Get the total distance for a routing
double getRoutingDistance(Routing &routing){
    double d = 0;
    for(int i = 0; i < problemDescription.t; i++){
        for(int j = 0; j < routing[i].size(); j++){
            d += getRouteDistance(i, routing[i][j]);
        }
    }
    return d;
}


// Get the amount of vehicles above the max limit
int getRoutingVehicleAmount(Routing &routing){
    int vehicles = 0;
    for(int i = 0; i < problemDescription.t; i++){
        int vehicleAmount = routing[i].size();
        if(vehicleAmount > problemDescription.m){
            vehicles += vehicleAmount - problemDescription.m;
        }
    }
    return vehicles;
}


// Check if a routing is feasible or not by checking constraints
bool feasible(Routing &routing){
    for(int i = 0; i < problemDescription.t; i++){
        if(routing[i].size() > problemDescription.m){
            return false;
        }
        for(int j = 0; j < routing[i].size(); j++){
            if(getRouteDistance(i, routing[i][j]) > problemDescription.depots[i].D){
                return false;
            }
            if(getRouteLoad(routing[i][j]) > problemDescription.depots[i].Q){
                return false;
            }
        }
    }
    return true;
}


// Create a routing from a chromosome
// Two-phase process as described in the paper
Routing getRouting(Chromosome &chromosome){

    Routing routing(problemDescription.t);

    // Phase 1
    for(int i = 0; i < problemDescription.t; i++){
        std::list<int> route;

        int vehicleLoad = 0;

        double depotX = problemDescription.depots[i].x;
        double depotY = problemDescription.depots[i].y;
        double x0 = depotX;
        double y0 = depotY;
        double x1 = 0;
        double y1 = 0;
        int customerDemand = 0;

        for(int customer : chromosome[i]){
            x1 = problemDescription.customers[customer].x;
            y1 = problemDescription.customers[customer].y;
            customerDemand = problemDescription.customers[customer].q;
            
            vehicleLoad += customerDemand;
            if(vehicleLoad <= problemDescription.depots[i].Q){
                route.push_back(customer);
            }else{
                routing[i].push_back(route);
                route.clear();
                route.push_back(customer);
                vehicleLoad = customerDemand;
            }
            x0 = x1;
            y0 = y1;
        }

        if(route.size() > 0){
            routing[i].push_back(route);
        }
    }

    //Phase 2
    for(int i = 0; i < problemDescription.t; i++){
        for(int j = 0; j < routing[i].size() - 1; j++){
            double oldRoute1Distance = getRouteDistance(i, routing[i][j]);
            double oldRoute2Distance = getRouteDistance(i, routing[i][j + 1]);

            int lastCustomer = routing[i][j].back();
            routing[i][j].pop_back();
            routing[i][j + 1].push_front(lastCustomer);
            
            double newRoute1Distance = getRouteDistance(i, routing[i][j]);
            double newRoute2Distance = getRouteDistance(i, routing[i][j + 1]);
            
            if(newRoute1Distance + newRoute2Distance >= oldRoute1Distance + oldRoute2Distance){ // Not better so revert
                routing[i][j].push_back(lastCustomer);
                routing[i][j + 1].pop_front();
                continue;
            }

            if(getRouteLoad(routing[i][j + 1]) > problemDescription.depots[i].Q){ // Not feasible
                routing[i][j].push_back(lastCustomer);
                routing[i][j + 1].pop_front();
                continue;
            }

            if(routing[i][j].size() == 0){
                routing[i].erase(routing[i].begin() + j);
                j--;
            }
        }
    }

    return routing;
}


// Compute the fitness as a weighted sum of:
// - total routing distance (objective)
// - vehicles over the max allowed (constraint)
// - vehicle distance over the max allowed (constraint)
// Weight the constraints highest to ensure that they are prioritized
double fitness(Routing &routing, double alpha, double beta){

    /* double overDistance = 0;
    for(int i = 0; i < routing.size(); i++){
        for(int j = 0; j < routing[i].size(); j++){
            double d = getRouteDistance(i, routing[i][j]);
            double dd = d - problemDescription.depots[i].D;
            if(dd > 0){
                overDistance += dd;
            }
        }
    } */

    return alpha * getRoutingVehicleAmount(routing) + beta * getRoutingDistance(routing); //+ 2 * overDistance;
}


// Calculate the fitness of every individual in the population and return them as a vector
// Also calculate the average and optimal fitnesses of the entire population and insert it as the two last elements of the vector
std::vector<double> calculatePopulationFitness(std::vector<Routing> &population, double alpha, double beta){
    int n = population.size();
    std::vector<double> populationFitness(n + 2);
    double averageFitness = 0;
    double optimalFitness = 1000000;

    for(int i = 0; i < n; i++){
        double f = fitness(population[i], alpha, beta);
        populationFitness[i] = f;
        averageFitness += f;
        if(f < optimalFitness){
            optimalFitness = f;
        }
    }
    averageFitness /= ((double) n);
    populationFitness[n] = averageFitness;
    populationFitness[n + 1] = optimalFitness;

    return populationFitness;
}


// Tournament selection with k = 2
int parentSelection(std::vector<double> &populationFitness, double probBestindividualTournament){
    int index1 = rand() % (populationFitness.size() - 2);
    int index2 = rand() % (populationFitness.size() - 2);
    //std::cout << "prob best individual tournament" << probBestindividualTournament << std::endl;
    if(randomCheck(probBestindividualTournament)){
        if(populationFitness[index1] < populationFitness[index2]){
            return index1;
        }
        return index2;
    }else{
        if(randomCheck(0.5)){
            return index1;
        }
        return index2;
    }
}


// Crossover as described in the paper
// Insert customers at the first feasible location found
void crossoverOld(Routing &parent1, Routing &parent2){

    int depot = rand() % problemDescription.t;

    if(parent1[depot].size() == 0 || parent2[depot].size() == 0){
        return;
    }

    // Select two random routes for each parent
    int parent1RouteIndex = rand() % parent1[depot].size();
    int parent2RouteIndex = rand() % parent2[depot].size();
    
    std::list<int> route1 = parent1[depot][parent1RouteIndex];
    std::list<int> route2 = parent2[depot][parent2RouteIndex];

    std::list<int>::iterator it;
    for(int i = 0; i < problemDescription.t; i++){
        for(int j = 0; j < parent2[i].size(); j++){
            it = parent2[i][j].begin();
            while(it != parent2[i][j].end()){
                if(std::find(route1.begin(), route1.end(), *it) != route1.end()){
                    it = parent2[i][j].erase(it);
                    it--;
                }
                it++;
            }
            if(parent2[i][j].size() == 0){
                parent2[i].erase(parent2[i].begin() + j);
                j--;
            }
        }
        for(int j = 0; j < parent1[i].size(); j++){
            it = parent1[i][j].begin();
            while(it != parent1[i][j].end()){
                if(std::find(route2.begin(), route2.end(), *it) != route2.end()){
                    it = parent1[i][j].erase(it);
                    it--;
                }
                it++;
            }
            if(parent1[i][j].size() == 0){
                parent1[i].erase(parent1[i].begin() + j);
                j--;
            }
        }
    }

    for(int customer : route1){
        bool inserted = false;
        if(randomCheck(0.8)){
            for(int i = 0; i < parent2[depot].size(); i++){
                it = parent2[depot][i].begin();
                while(it != parent2[depot][i].end()){
                    it = parent2[depot][i].insert(it, customer);
                    int vehicleLoad = getRouteLoad(parent2[depot][i]);
                    if(vehicleLoad <= problemDescription.depots[depot].Q){
                        inserted = true;
                        break;
                    }
                    it = parent2[depot][i].erase(it);
                    it++;
                }
                if(inserted){
                    break;
                }
            }
            if(!inserted){
                parent2[depot].push_back({customer});
            }

        }else{
            parent2[depot][0].push_front(customer);
        }
    }

    for(int customer : route2){
        bool inserted = false;
        if(randomCheck(0.8)){
            for(int i = 0; i < parent1[depot].size(); i++){
                it = parent1[depot][i].begin();
                while(it != parent1[depot][i].end()){
                    it = parent1[depot][i].insert(it, customer);
                    int vehicleLoad = getRouteLoad(parent1[depot][i]);
                    if(vehicleLoad <= problemDescription.depots[depot].Q){
                        inserted = true;
                        break;
                    }
                    it = parent1[depot][i].erase(it);
                    it++;
                }
                if(inserted){
                    break;
                }
            }
            if(!inserted){
                parent1[depot].push_back({customer});
            }

        }else{
            parent1[depot][0].push_front(customer);
        }
    }
}


// Improved version of the crossover from the paper
// Insert customers at the best feasible location instead of the first feasible location
void crossover(Routing &parent1, Routing &parent2){

    int depot = rand() % problemDescription.t;

    if(parent1[depot].size() == 0 || parent2[depot].size() == 0){
        return;
    }

    // Select two random routes for each parent
    int parent1RouteIndex = rand() % parent1[depot].size();
    int parent2RouteIndex = rand() % parent2[depot].size();
    
    std::list<int> route1 = parent1[depot][parent1RouteIndex];
    std::list<int> route2 = parent2[depot][parent2RouteIndex];

    // Find and remove the customers from the route in the other parent
    std::list<int>::iterator it;
    for(int i = 0; i < problemDescription.t; i++){
        for(int j = 0; j < parent2[i].size(); j++){
            it = parent2[i][j].begin();
            while(it != parent2[i][j].end()){
                if(std::find(route1.begin(), route1.end(), *it) != route1.end()){
                    it = parent2[i][j].erase(it);
                    it--;
                }
                it++;
            }
            if(parent2[i][j].size() == 0){ // Erase empty routes
                parent2[i].erase(parent2[i].begin() + j);
                j--;
            }
        }
        for(int j = 0; j < parent1[i].size(); j++){
            it = parent1[i][j].begin();
            while(it != parent1[i][j].end()){
                if(std::find(route2.begin(), route2.end(), *it) != route2.end()){
                    it = parent1[i][j].erase(it);
                    it--;
                }
                it++;
            }
            if(parent1[i][j].size() == 0){
                parent1[i].erase(parent1[i].begin() + j);
                j--;
            }
        }
    }

    // Insert the customers again, at the best feasible location
    for(int customer : route1){
        double bestInsertionCost = 10000000;
        int bestRoute = -1;
        int bestIndex = 0;
        int index = 0;
        for(int i = 0; i < parent2[depot].size(); i++){
            it = parent2[depot][i].begin();
            index = 0;
            while(it != parent2[depot][i].end()){
                double oldVehicleDistance = getRouteDistance(depot, parent2[depot][i]);
                it = parent2[depot][i].insert(it, customer);
                double newVehicleDistance = getRouteDistance(depot, parent2[depot][i]);
                double insertionCost = newVehicleDistance - oldVehicleDistance;
                int vehicleLoad = getRouteLoad(parent2[depot][i]);
                if(insertionCost < bestInsertionCost && vehicleLoad <= problemDescription.depots[depot].Q){
                    bestInsertionCost = insertionCost;
                    bestRoute = i;
                    bestIndex = index;
                }
                it = parent2[depot][i].erase(it);
                it++;
                index++;
            }
        }

        if(bestRoute == -1){
            parent2[depot].push_back({customer});
            continue;
        }

        it = parent2[depot][bestRoute].begin();
        for(int i = 0; i < bestIndex; i++){
            it++;
        }
        parent2[depot][bestRoute].insert(it, customer);
    }

    for(int customer : route2){
        double bestInsertionCost = 10000000;
        int bestRoute = -1;
        int bestIndex = 0;
        int index = 0;
        for(int i = 0; i < parent1[depot].size(); i++){
            it = parent1[depot][i].begin();
            index = 0;
            while(it != parent1[depot][i].end()){
                double oldVehicleDistance = getRouteDistance(depot, parent1[depot][i]);
                it = parent1[depot][i].insert(it, customer);
                double newVehicleDistance = getRouteDistance(depot, parent1[depot][i]);
                double insertionCost = newVehicleDistance - oldVehicleDistance;
                int vehicleLoad = getRouteLoad(parent1[depot][i]);
                if(insertionCost < bestInsertionCost && vehicleLoad <= problemDescription.depots[depot].Q){
                    bestInsertionCost = insertionCost;
                    bestRoute = i;
                    bestIndex = index;
                }
                it = parent1[depot][i].erase(it);
                it++;
                index++;
            }
        }

        if(bestRoute == -1){
            parent1[depot].push_back({customer});
            continue;
        }

        it = parent1[depot][bestRoute].begin();
        for(int i = 0; i < bestIndex; i++){
            it++;
        }
        parent1[depot][bestRoute].insert(it, customer);
    }
}


// Choose one of three random mutations for routes within the same depot
// Each mutation has an equal probability to be selected
void intraDepotMutate(int depot, Routing &offspring, double probReversal, double probSingle){
    if(offspring[depot].size() == 0){
        return;
    }

    double probSwap;

    if (probReversal > 1.0) {
        probReversal = 1.0;
        probSingle = 0.0;
        //probSwap = 0.0;
    } else if (probReversal + probSingle > 1.0) {
        probSingle = 1.0 - probReversal; 
        //probSwap = 0.0;
    } else {
        //probSwap = 1.0 - (probReversal + probSingle);
    }
    /* std::cout << "acum prob reversal " << probReversal << std::endl;
    std::cout << " prob single " << probSingle << std::endl;
    std::cout << "acum prob single " << probSingle + probReversal << std::endl;

    std::cout << " prob swap " << 1 - (probReversal + probSingle) << std::endl;
    std::cout << "acum prob swap " << 1 << std::endl; */
    if(randomCheck(probReversal)){ // Reversal mutation

        // Convert to the chromosome to make it easier to ensure that constraints are satisfied
        Chromosome offspringChromosome(problemDescription.t);
        for(int i = 0; i < offspring.size(); i++){
            std::list<int> customers;
            for(int j = 0; j < offspring[i].size(); j++){
                for(int customer : offspring[i][j]){
                    customers.push_back(customer);
                }
            }
            offspringChromosome[i] = customers;
        }

        //Generate a lower and upper index for reversing the chromosome
        int n = offspringChromosome[depot].size();
        int cutIndex1 = rand() % (n / 2);
        int cutIndex2 = (rand() % (n / 2)) + n / 2;

        // Find the list iterators to the cutpoints
        std::list<int>::iterator cut1;
        std::list<int>::iterator cut2;
        std::list<int>::iterator it = offspringChromosome[depot].begin();
        for(int i = 0; i <= cutIndex2; i++){
            if(i == cutIndex1){
                cut1 = it;
            }else if(i == cutIndex2){
                cut2 = it;
            }
            it++;
        }

        // Reverse the sub-list defined by the two iterators
        std::reverse(cut1, cut2);

        // Convert back to the routing
        offspring = getRouting(offspringChromosome);

    }else if(randomCheck(probSingle + probReversal)){ // Single customer re-routing
        int routeIndex = rand() % offspring[depot].size();

        if(offspring[depot][routeIndex].size() == 0){
            return;
        }

        // Find and erase a random customer
        int customerIndex = rand() % offspring[depot][routeIndex].size();
        std::list<int>::iterator it = offspring[depot][routeIndex].begin();
        for(int i = 0; i < customerIndex; i++){
            it++;
        }
        
        int customer = *it;
        offspring[depot][routeIndex].erase(it);

        if(offspring[depot][routeIndex].size() == 0){
            offspring[depot].erase(offspring[depot].begin() + routeIndex);
        }

        // Find the best feasible insertion location within the same depot
        // Try to insert the customer at every location and compute the insertion cost by subtracting the vehicle distances
        // If the location is feasible and better than previous locations, update the indexes
        double bestInsertionCost = 10000000;
        int bestRoute = -1;
        int bestIndex = 0;
        int index = 0;
        for(int i = 0; i < offspring[depot].size(); i++){
            it = offspring[depot][i].begin();
            index = 0;
            while(it != offspring[depot][i].end()){
                double oldVehicleDistance = getRouteDistance(depot, offspring[depot][i]);
                it = offspring[depot][i].insert(it, customer);
                double newVehicleDistance = getRouteDistance(depot, offspring[depot][i]);
                double insertionCost = newVehicleDistance - oldVehicleDistance;
                int vehicleLoad = getRouteLoad(offspring[depot][i]);
                if(insertionCost < bestInsertionCost && vehicleLoad <= problemDescription.depots[depot].Q){
                    bestInsertionCost = insertionCost;
                    bestRoute = i;
                    bestIndex = index;
                }
                it = offspring[depot][i].erase(it);
                it++;
                index++;
            }
        }
        if(bestRoute == -1){ // No feasible location found, so make a new route
            offspring[depot].push_back({customer});
            return;
        }

        it = offspring[depot][bestRoute].begin();
        for(int i = 0; i < bestIndex; i++){
            it++;
        }
        offspring[depot][bestRoute].insert(it, customer);
        

    }else{ // Swapping
        if(offspring[depot].size() == 0){
            return;
        }
        int route1Index = rand() % offspring[depot].size();
        int route2Index = rand() % offspring[depot].size();
        if(offspring[depot][route1Index].size() == 0 || offspring[depot][route2Index].size() == 0){
            return;
        }
        
        // Generate 2 random customer indexes to be swapped
        int customer1Index = rand() % offspring[depot][route1Index].size();
        int customer2Index = rand() % offspring[depot][route2Index].size();

        int customer1 = 0;
        int customer2 = 0;

        // Iterate over both routes to get the customer values
        int index = 0;
        for(int customer : offspring[depot][route1Index]){
            if(index == customer1Index){
                customer1 = customer;
                break;
            }
            index++;
        }
        index = 0;
        for(int customer : offspring[depot][route2Index]){
            if(index == customer2Index){
                customer2 = customer;
                break;
            }
            index++;
        }

        // Convert back to a chromosome while also swapping the customers
        // Then convert back again to the routing
        // Makes it easier to ensure that the constraints are satisfied
        Chromosome offspringChromosome(problemDescription.t);
        for(int i = 0; i < offspring.size(); i++){
            std::list<int> customers;
            for(int j = 0; j < offspring[i].size(); j++){
                for(int customer : offspring[i][j]){
                    if(customer == customer1){
                        customers.push_back(customer2);
                    }else if(customer == customer2){
                        customers.push_back(customer1);
                    }else{
                        customers.push_back(customer);
                    }
                }
            }
            offspringChromosome[i] = customers;
        }
        offspring = getRouting(offspringChromosome);
    }
}


// Find and remove a random customer from the given depot
// Insert the customer to the best feasible location in a route in another depot
// The next depot is selected from the swappableCustomer depots found when in the initial assignment
void interDepotMutate(int depot, Routing &offspring){
    if(rand() % offspring[depot].size() == 0){
        return;
    }
    int routeIndex = rand() % offspring[depot].size();
    if(offspring[depot][routeIndex].size() == 0){
        return;
    }
    int customerIndex = rand() % offspring[depot][routeIndex].size();
    std::list<int>::iterator it = offspring[depot][routeIndex].begin();
    for(int i = 0; i < customerIndex; i++){
        it++;
    }
    int customer = *it;
    offspring[depot][routeIndex].erase(it);

    if(offspring[depot][routeIndex].size() == 0){
        offspring[depot].erase(offspring[depot].begin() + routeIndex);
    }

    int nextDepotIndex = rand() % swappableCustomers[customer].size();
    int nextDepot = swappableCustomers[customer][nextDepotIndex];

    if(offspring[nextDepot].size() == 0){
        offspring[nextDepot].push_back({customer});
        return;
    }

    double bestInsertionCost = 10000000;
    int bestRoute = -1;
    int bestIndex = 0;
    int index = 0;
    for(int i = 0; i < offspring[nextDepot].size(); i++){
        it = offspring[nextDepot][i].begin();
        index = 0;
        while(it != offspring[nextDepot][i].end()){
            double oldVehicleDistance = getRouteDistance(nextDepot, offspring[nextDepot][i]);
            it = offspring[nextDepot][i].insert(it, customer);
            double newVehicleDistance = getRouteDistance(nextDepot, offspring[nextDepot][i]);
            double insertionCost = newVehicleDistance - oldVehicleDistance;
            int vehicleLoad = getRouteLoad(offspring[nextDepot][i]);
            if(insertionCost < bestInsertionCost && vehicleLoad <= problemDescription.depots[nextDepot].Q){
                bestInsertionCost = insertionCost;
                bestRoute = i;
                bestIndex = index;
            }
            it = offspring[nextDepot][i].erase(it);
            it++;
            index++;
        }
    }

    if(bestRoute == -1){
        offspring[nextDepot].push_back({customer});
        return;
    }

    it = offspring[nextDepot][bestRoute].begin();
    for(int i = 0; i < bestIndex; i++){
        it++;
    }
    offspring[nextDepot][bestRoute].insert(it, customer);
}


bool stop = false;
// Called on Ctrl+c
// Makes it possible to stop at any time
void signalHandler(int signum){
    stop = true;
}


// Run the GA with the given parameters and problem description
// Save the output to solution.txt and the visualiztion to output.js
void optimize(int maxGenerations, Parameters &parameters, ProblemDescription &pd, int seed, const std::string& datafile){
    
    signal(SIGINT, signalHandler);

    int populationSize = parameters.populationSize;
    double crossoverRate = parameters.crossoverRate;
    double intraDepotMutationRate = parameters.intraDepotMutationRate;
    double interDepotMutationRate = parameters.interDepotMutationRate;
    int interDepotMutationAttemptRate = parameters.interDepotMutationAttemptRate;
    double bound = parameters.bound; 
    double alpha = parameters.alpha;
    double beta = parameters.beta;
    double probBestIndividualTournament = parameters.probBestIndividualTournament;
    double probReversal = parameters.probReversal;
    double probSingle = parameters.probSingle;
    double elitism = parameters.elitism;

    seed_global = seed;


    problemDescription = pd;

    //srand((time(0)));
    srand(seed);

    std::vector<double> averageFitness(maxGenerations + 1, 0);
    std::vector<double> optimalFitness(maxGenerations + 1, 0);

    std::vector<Chromosome> chromosomePopulation = generatePopulation(populationSize, bound);

    std::vector<Routing> population(populationSize);
    for(int i = 0; i < populationSize; i++){
        population[i] = getRouting(chromosomePopulation[i]);
    }

    std::vector<double> populationFitness = calculatePopulationFitness(population, alpha, beta);
    averageFitness[0] = populationFitness[populationSize];
    optimalFitness[0] = populationFitness[populationSize + 1];

    std::vector<Routing> nextPopulation(populationSize); // Initialize outside the main loop

    int elitismCount = (populationSize * elitism );
    if(elitismCount % 2 == 1){
        elitismCount++;
    }

    std::vector<int> populationIndexes(populationSize);
    for(int i = 0; i < populationSize; i++){
        populationIndexes[i] = i;
    }

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();

    Routing bestRouting;
    int contador_imagen = 0;
    for(int i = 0; i < maxGenerations; i++){
        int mutationDepot = rand() % problemDescription.t;

        for(int j = 0; j < populationSize - elitismCount; j += 2){
            int parent1Index = parentSelection(populationFitness, probBestIndividualTournament);
            int parent2Index = parentSelection(populationFitness, probBestIndividualTournament);
            nextPopulation[j] = population[parent1Index];
            nextPopulation[j + 1] = population[parent2Index];

            if(randomCheck(crossoverRate)){
                crossover(nextPopulation[j], nextPopulation[j + 1]);
            }
            if(i % interDepotMutationAttemptRate == 0 && randomCheck(interDepotMutationRate)){
                interDepotMutate(mutationDepot, nextPopulation[j]);
                interDepotMutate(mutationDepot, nextPopulation[j + 1]);
            }else if(randomCheck(intraDepotMutationRate)){
                intraDepotMutate(mutationDepot, nextPopulation[j], probReversal, probSingle);
                intraDepotMutate(mutationDepot, nextPopulation[j + 1], probReversal, probSingle);
            }
        }

        // Elitism
        std::sort(populationIndexes.begin(), populationIndexes.end(), [populationFitness](int index1, int index2){
            return populationFitness[index1] < populationFitness[index2];
        });
        for(int j = 0; j < elitismCount; j++){
            nextPopulation[populationSize - elitismCount + j] = population[populationIndexes[j]];
        }

        //Para mostrar rendimineto del algoritmo genetico cada 50 segundos
        if(i % 500 == 0){
            std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
            int minutes = std::chrono::duration_cast<std::chrono::minutes>(end - begin).count();
            int seconds = std::chrono::duration_cast<std::chrono::seconds>(end - begin).count();
            seconds %= 60;

            bestRouting = population[populationIndexes[0]];
            /* std::cout << "Generation: " << i << ", time: " << minutes << "m " << seconds << "s" << std::endl;
            std::cout << "Optimal distance: " << getRoutingDistance(bestRouting);
            std::cout << ", feasible: " << feasible(bestRouting) << std::endl;
            std::cout << "Optimal fitness: " << optimalFitness[i] << std::endl;
            std::cout << "Average fitness: " << averageFitness[i] << std::endl;
            std::cout << std::endl; */
        } 

        /* // Definir el intervalo de generaciones
        int saveInterval = 25; // Guardar la mejor solución cada 25 generaciones

        // Guardar la mejor solución solo si es el múltiplo de 'saveInterval'
        if (i % saveInterval == -1) {
            // Obtener la mejor solución de la población
            bestRouting = population[populationIndexes[0]];

            // Crear y abrir el archivo para guardar la solución de la generación
            std::ofstream generationFile;
            generationFile.open("generations/" + std::to_string(contador_imagen + 1) + ".res");
            contador_imagen++;
            // Guardar la distancia total de la mejor ruta
            generationFile << getRoutingDistance(bestRouting) << std::endl;

            // Guardar las rutas y los clientes en la solución
            for (int q = 0; q < problemDescription.t; q++) {
                for (int c = 0; c < bestRouting[q].size(); c++) {
                    generationFile << q + 1 << "\t" << c + 1 << "\t";
                    generationFile << getRouteDistance(q, bestRouting[q][c]) << "\t";
                    int vehicleLoad = 0;
                    std::string routeCustomerString = "0 ";
                    for (int w : bestRouting[q][c]) {
                        vehicleLoad += problemDescription.customers[w].q;
                        routeCustomerString += std::to_string(w + 1) + " ";
                    }
                    generationFile << vehicleLoad << "\t";
                    generationFile << routeCustomerString << "0" << std::endl;
                }
            }
            
            // Cerrar el archivo después de guardar la información
            generationFile.close();
        } */

        population = nextPopulation;

        populationFitness = calculatePopulationFitness(population, alpha, beta);
        averageFitness[i + 1] = populationFitness[populationSize];
        optimalFitness[i + 1] = populationFitness[populationSize + 1];

        if(stop){
            break;
        }
    }

    std::sort(populationIndexes.begin(), populationIndexes.end(), [populationFitness](int index1, int index2){
        return populationFitness[index1] < populationFitness[index2];
    });
    bestRouting = population[populationIndexes[0]];
    std::cout << "Feasible = " << feasible(bestRouting) << std::endl;
    std::cout << "F.O = " << getRoutingDistance(bestRouting) << std::endl;
    std::cout << getRoutingDistance(bestRouting);

    /* std::string separador = "/"; // El separador de la ruta
    // Encuentra la última posición del separador
    size_t pos = datafile.find_last_of(separador);
    // Extrae la subcadena a partir de la posición encontrada hasta el final
    std::string ultimaParte = datafile.substr(pos + 1);

    std::ofstream outputFile;
    bool isfeasible = feasible(bestRouting);
    std::string isfeasibleStr = isfeasible ? "true" : "false";  // Convierte el valor bool a string
    outputFile.open("EXTRA/solution_"+ ultimaParte +"_"+ isfeasibleStr +".txt");  // Abre el archivo en la carpeta "images"
    outputFile << getRoutingDistance(bestRouting) << std::endl;
    for(int q = 0; q < problemDescription.t; q++){
        for(int c = 0; c < bestRouting[q].size(); c++){
            outputFile << q + 1 << "\t" << c + 1 << "\t";
            outputFile << getRouteDistance(q, bestRouting[q][c]) << "\t";
            int vehicleLoad = 0;
            std::string routeCustomerString = "0 ";
            for(int w : bestRouting[q][c]){
                vehicleLoad += problemDescription.customers[w].q;
                routeCustomerString += std::to_string(w + 1) + " ";
            }
            outputFile << vehicleLoad << "\t";
            outputFile << routeCustomerString << "0" << std::endl;
        }
    }
    outputFile.close();

    // Write the coordinates of the depots and customers in every route to a javascript file as arrays
    // The javascript file can then be read by the html to draw the routing
    std::string depotStringJS = "var depots = [";
    std::string routeStringJS = "var routes = [";
    for(int q = 0; q < problemDescription.t; q++){
        depotStringJS += std::to_string(problemDescription.depots[q].x) + ", " + std::to_string(problemDescription.depots[q].y) + ", ";
        routeStringJS += "[";
        for(int c = 0; c < bestRouting[q].size(); c++){
            routeStringJS += "[";
            for(int w : bestRouting[q][c]){
                routeStringJS += std::to_string(problemDescription.customers[w].x) + ", " + std::to_string(problemDescription.customers[w].y) + ", ";
            }
            routeStringJS += "], ";
        }
        routeStringJS += "], ";
    }
    depotStringJS += "];";
    routeStringJS += "];";

    std::ofstream outputFileJS;
    outputFileJS.open("EXTRA/output.js");
    outputFileJS << depotStringJS << std::endl;
    outputFileJS << routeStringJS << std::endl;
    outputFileJS.close(); */
}
