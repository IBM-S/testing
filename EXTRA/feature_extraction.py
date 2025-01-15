# Feature extractor for CVRPTW problem instances
# Input: A directory containing CVRPTW problem instances as .txt files.

import pyvrp as p
import numpy as np
import argparse
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import OPTICS

import vrplib


parser = argparse.ArgumentParser(prog="VRPFeatureExtractor",
                                 description="Produces metrics for VRP instance description")
parser.add_argument("-d", "--dir", required=True)
args = parser.parse_args()

def client_dist(A,B):
    return np.sqrt((A.y - B.y)**2 + (A.x - B.x)**2)
def dist(tuple1, tuple2):
    return np.sqrt((tuple1[0] - tuple2[0])**2 + (tuple1[1] - tuple2[1])**2)

# Funcion para obtener la maxima y minima cantidad de overlaps de ventanas de tiempo
# Este metodo de time sweep es extremadamente ineficiente, sería mejor sortear primero
# los comienzos y fines de las time windows y recorrerlos en orden, sumando al pasar por
# un comienzo y restando al pasar por un fin
def get_time_window_features(clients_list):
    time_windows_early = dict()
    time_windows_late = dict()
    overlaps = 0
    time_overlaps_dict = dict()
    window_lengths = list()
    for client in clients_list:
        if client.tw_late not in time_windows_late:
            time_windows_late[client.tw_late] = 0
        if client.tw_early not in time_windows_early:
            time_windows_early[client.tw_early] = 0
        time_windows_late[client.tw_late] += 1
        time_windows_early[client.tw_early] += 1
        window_lengths.append(client.tw_late - client.tw_early)
    max_time = max(time_windows_late) 
    for t in range(max_time):
        if t in time_windows_early:
            overlaps += time_windows_early[t]
        if t in time_windows_late:
            overlaps -= time_windows_late[t]
        time_overlaps_dict[t] = overlaps
    max_overlaps = max(list(time_overlaps_dict.values()))
    avg_overlaps = np.mean(list(time_overlaps_dict.values()))
    mean_window_length = np.mean(window_lengths)
    max_window_length = max(window_lengths)
    return {"max_overlaps": np.round(max_overlaps/len(clients),2), 
            "avg_overlaps": np.round(avg_overlaps/len(clients),2),
            "avg_window_length":np.round(mean_window_length/max_window_length,2),
            "cv_window_length":np.round((np.std(window_lengths)/mean_window_length)*100/max_window_length,2)}

def clusteringQuality(clients, labels):
    #Almacenamos los clientes en listas separadas para cada cluster
    client_clusters = dict()
    for i in range(len(clients)):
        if labels[i] not in client_clusters.keys():
            client_clusters[labels[i]] = []
        client_clusters[labels[i]].append(clients[i])

    #Obtenemos centroides
    centroids = dict()
    for label, cluster in client_clusters.items():
        centroid = np.array([0,0])
        for client in cluster:
            centroid += np.array([client.x,client.y])
        centroid = np.divide(centroid,len(cluster))
        centroids[label] = centroid

    #Obtenemos average intra cluster distance
    intra_cluster_distances = dict()
    for label,cluster in client_clusters.items():
        distance_to_centroid = 0
        for client in cluster:
            distance_to_centroid += np.sqrt((client.x - centroids[label][0])**2 + (client.y - centroids[label][1])**2)
        distance_to_centroid /= len(cluster)
        
        intra_cluster_distances[label] = distance_to_centroid
    average_intra_cluster_distance = np.mean(list(intra_cluster_distances.values()))

    #Obtenemos distancia de cada cluster al cluster vecino más cercano
    centroid_locations = list(centroids.values())
    if len(centroid_locations) > 1:
        neighbors = NearestNeighbors(n_neighbors=2, algorithm='auto').fit(centroid_locations)
        distances, indices = neighbors.kneighbors(centroid_locations)
        average_inter_cluster_distance = np.mean(distances)
    else:
        average_inter_cluster_distance = 0
    
    #Normalizamos los valores para que escala de instancia no afecte
    max_x = 0
    max_y = 0
    for client in clients:
        if (client.x > max_x):
            max_x = client.x
        if (client.y > max_y):
            max_y = client.y

    max_possible_distance = np.sqrt(max_x**2 + max_y**2)
    average_intra_cluster_distance /= max_possible_distance
    average_inter_cluster_distance /= max_possible_distance

    #Queremos minimizar la distancia intra cluster mientras maximizamos al distancia inter cluster
    #Penalizamos tener demasiados outliers
    outlier_ratio = (sum([i for i in labels if i == -1])*-1) / len(labels)
    quality = -2*average_intra_cluster_distance + 1*average_inter_cluster_distance + -1*outlier_ratio
    return quality
    

def calcular_clientes_mas_cercanos (clients, depots):
    coords_depots = []
    for i, depot in enumerate(depots):
        nombre_depot = f'Depot {i+1}'
        coords_depots.append(((depot.x, depot.y), nombre_depot))

    coords_clients = []
    for i, client in enumerate(clients):
        nombre_client = f'Client {i+1}'
        coords_clients.append(((client.x, client.y), nombre_client))

    cant_clients = len(coords_clients)
    i = 0
    mas_cercanos = []
    for i in range(1, len(coords_depots)+1):
        mas_cercanos.append([])
    while i < cant_clients:
        distancias_al_depot = []
        for coord, name in coords_depots:
            distancias = dist(coords_clients[i][0], coord)
            distancias_al_depot.append(distancias)
        minimo = min(distancias_al_depot)
        depot_minimo = distancias_al_depot.index(minimo)
        mas_cercanos[depot_minimo].append((minimo, coords_clients[i][1]))
        i+=1
    return mas_cercanos

def calcular_dist_max_depot(distancias):
    numero_de_depots = len(distancias)
    max_depot = []
    i = 0
    while i < numero_de_depots:
        values = [x[0] for x in distancias[i]]
        max = np.max(values)
        max_depot.append(max)
        i+=1
    return max_depot

def calcular_dist_min_depot(distancias):
    numero_de_depots = len(distancias)
    min_depot = []
    i = 0
    while i < numero_de_depots:
        values = [x[0] for x in distancias[i]]
        min = np.min(values)
        min_depot.append(min)
        i+=1
    return min_depot

def calcular_dist_prom_depot(distancias):
    numero_de_depots = len(distancias)
    proms_depot = []
    i = 0
    while i < numero_de_depots:
        values = [x[0] for x in distancias[i]]
        average = np.mean(values)
        proms_depot.append(average)
        i+=1
    return proms_depot

def calcular_std_client_distance_to_depot(distancias):
    numero_de_depots = len(distancias)
    desv_standard_depot = []
    i = 0
    while i < numero_de_depots:
        values = [x[0] for x in distancias[i]]
        desv_standard = np.std(values)
        desv_standard_depot.append(desv_standard)
        i+=1
    return desv_standard_depot


base_dir = "features_inst"
os.makedirs(base_dir, exist_ok=True)

features = dict()
#Leemos instancia y generamos modelo
directory = args.dir
instances = os.listdir(directory)
instances = [i for i in instances if not ("__") in i]
first_pass = True


leer_Data = []
for i in instances:
    instance = p.read(directory + i, round_func="round")
    leer_Data.append(instance)

#print(leer_Data)
#print(instances)
contador = 0
for instance_name in leer_Data:
    features.clear()
    print("Extracting features for: " + instances[contador] + "   Path: " + directory + instances[contador])
    
    #instance = p.read(directory + instance_name, round_func="round")
    model = p.Model.from_data(instance_name)
    
    #print(dir(model))
    #Debug
    #cliente_codificados = getattr(model, "_clients")
    #contador = 0
    # Iterar sobre los clientes e inspeccionar atributos
    """ for i, client in enumerate(cliente_codificados):
        contador +=1
        print(f"Cliente {i+1}:")
        for attr in dir(client):  # Lista todos los atributos y métodos del cliente
            if not attr.startswith("_"):  # Ignorar atributos o métodos privados
                try:
                    value = getattr(client, attr)  # Obtén el valor del atributo
                    #print(f"  {attr}: {value}")
                except AttributeError as e:
                    print(f"  No se pudo obtener {attr}: {e}")
        demand = getattr(client, 'delivery')
        print(f"x: {getattr(client, 'x')}, y: {getattr(client, 'y')}, demand: {demand[0]}")
        if contador == 2:
            break """

    #Construimos matriz de distancias (pyvrp ya trabaja con una interna pero no es facilmente accesible)
    clients = model._clients
    distance_matrix = [[] for client in clients]
    for i,client in enumerate(clients):
        for j,_client in enumerate(clients):
            distance_matrix[i].append(client_dist(client, _client))
    
    #Obtenemos distancia diagonal de la boundbox para normalizar todas las features espaciales
    max_x_value = max([client.x for client in clients])
    max_y_value = max([client.y for client in clients])
    max_possible_distance = np.sqrt(max_x_value**2 + max_y_value**2)

    ##################################################
    #                                                #
    #  DC1: Number of clients                        #
    #                                                #
    ##################################################

    features["client_number"] = float(len(clients))

    #Centroid of the nodes
    centroid = model.data().centroid()

    num_depots = len(model._depots)
    features["n_depots"] = num_depots

    ###################################################
    #                                                 #
    #  DC3: Distance between centroid and depots      #
    #                                                 #
    #  Dos descriptores seleccionados:                #
    #  distance centroid depot i                      #
    #  Avg distance centroid depot i                  #
    #                                                 #
    ###################################################

    distances_centroid_depots = []
    # DC3: Distance between centroid and depots
    for i in range(0, len(model._depots)):
        distance_value = dist((model._depots[i].x, model._depots[i].y),centroid) / max_possible_distance
        features[f'dist_centroid_depot_{i+1}'] = distance_value
        distances_centroid_depots.append(distance_value)

    # Calcular el promedio de las distancias
    avg_dist_centroid_depots = np.mean(distances_centroid_depots)
    features[f'avg_dist_centroid_depots'] = avg_dist_centroid_depots

    ###################################################
    #                                                 #
    #  DC4: Average client distance to depot          #
    #  Se divide por max_possible_distance para       #
    #  normalizar las metricas espaciales y hacerlas  #
    #  independientes de la escala de la instancia    #
    #                                                 #
    #  Dos descriptores seleccionados:                #
    #  Avg distance to depot i                        #
    #  Avg Avg distance to depots                     #
    #  CV distance to depot i                         #
    #  Avg CV distance to depot i                     #
    #                                                 #
    ###################################################

    mas_cercanos = calcular_clientes_mas_cercanos(model._clients, model._depots)
    dist_prom_to_depot = calcular_dist_prom_depot(mas_cercanos)
    dist_min_to_depot = calcular_dist_min_depot(mas_cercanos)
    dist_max_to_depot = calcular_dist_max_depot(mas_cercanos)
    desv_standar_client_to_depot = calcular_std_client_distance_to_depot(mas_cercanos)
    features[f'avg_avg_dist_to_depots'] = np.mean(dist_prom_to_depot) / max_possible_distance
    features[f'avg_dist_min_to_depots'] = np.mean(dist_min_to_depot) / max_possible_distance
    features[f'avg_dist_max_to_depots'] = np.mean(dist_max_to_depot) / max_possible_distance

    for i in range(0, len(model._depots)):
        features[f'avg_dist_to_depot_{i+1}'] = dist_prom_to_depot[i] / max_possible_distance
        # features[f'cv_dist_to_depot_{i+1}'] = (desv_standar_client_to_depot[i]/dist_prom_to_depot[i])*100 / max_possible_distance
        # features[f'dist_min_to_depot_{i+1}'] = dist_min_to_depot[i] / max_possible_distance
        # features[f'dist_max_to_depot_{i+1}'] = dist_max_to_depot[i] / max_possible_distance

    for i in range(0, len(model._depots)):
        features[f'cv_dist_to_depot_{i+1}'] = (desv_standar_client_to_depot[i]/dist_prom_to_depot[i])*100 / max_possible_distance


    features[f'avg_cv_dist_to_depots'] = np.mean([features[f'cv_dist_to_depot_{i+1}'] for i in range(len(model._depots))])

    ###################################################
    #                                                 #
    #  ND4: Distance to centroid (Interpretado como   #
    #  Average Distance to Centroid y CV of Distance  #
    #  to Centroid)                                   #
    #                                                 #
    #  Dos descriptores seleccionados:                #
    #  Average Distance to Centroid                   #
    #  CV of Distance to Centroid                     #
    #                                                 #
    ###################################################

    # ND4A: Average Distance to Centroid
    distances_to_centroid = [dist(centroid,(c.x,c.y)) for c in clients]
    mean_distance_to_centroid = np.mean(distances_to_centroid)
    features["average_distance_to_centroid"] = mean_distance_to_centroid / max_possible_distance
    # ND4B: CV of Distance to Centroid
    features["cv_distance_to_centroid"] = (np.std(distances_to_centroid)/mean_distance_to_centroid)*100 / max_possible_distance    

    ###################################################
    #                                                 #
    #  DC5: Client Demands (Aqui no está claro a que  #
    #  se refiere el paper, se incluyeron 2 métricas) #
    #                                                 #
    #  Dos descriptores seleccionados:                #
    #  Ratio of Mean of Client Demands to capacity    #
    #  Ratio of CV of Client Demands to capacity      #
    #                                                 #
    ###################################################

    # DC5B: Ratio of Mean of Client Demands to capacity
    capacity = model._vehicle_types[0].capacity[0] # todos los vehiculos tienen la misma capacidad
    all_demands = [client.delivery[0] for client in clients] 
    mean_demand = np.mean(all_demands)  # promedio de todas las demandas
    features["ratio_mean_client_demand_capacity"] = mean_demand/capacity
    
    # DC5A: Ratio of CV of Client Demands to capacity
    features["ratio_cv_client_demand_capacity"] = (np.std(all_demands)/mean_demand)*100/capacity

    ##################################################
    #                                                #
    #  DC10: Average number of clients per vehicle   #
    #  Numero de clientes / numero de vehiculos      #
    #                                                #
    ##################################################
    features["average_clients_per_vehicle"] = features["client_number"]/model.data().num_vehicles


    ##################################################
    #                                                #
    #  the average of the normalized nearest         #
    #  neighbour distances (nNNd’s)                  #
    #                                                #
    ##################################################
    X = np.array([[client.x,client.y] for client in clients])
    nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(X)
    distances, indices = nbrs.kneighbors(X)
    distances = np.array([d[1] for d in distances])
    mean_distance =  np.mean(distances)
    features["avg_NN_distances"] = mean_distance / max_possible_distance
    #the cv of the normalized nearest neighbour distances (nNNd’s)
    features["cv_NN_distances"] = (np.std(distances)/mean_distance) / max_possible_distance    


    # No sirve en este caso
    # Extra: Features de Time Windows
    # time_window_features = get_time_window_features(clients)
    # features["tw_ratio_max_overlaps_to_total"] = time_window_features["max_overlaps"]
    # features["tw_ratio_avg_overlaps_to_total"] = time_window_features["avg_overlaps"]
    # features["tw_ratio_avg_window_length_to_longest"] = time_window_features["avg_window_length"]
    # features["tw_ratio_cv_window_length_to_longest"] = time_window_features["cv_window_length"]

    #CLUSTERING FEATURES
    #Iteramos sobre valores de min_samples y usamos el clustering de mayor calidad.
    best_quality = -10000
    best_min_samples = 0
    for min_samples in range(2,48):
        clustering = OPTICS(min_samples=min_samples).fit(X)
        quality = clusteringQuality(clients,clustering.labels_)
        if (quality > best_quality):
            best_quality = quality
            best_clustering = clustering
            best_min_samples = min_samples
            
    # CLS1 - Optimal min_samples value
    features["optimal_min_samples"] = best_min_samples
    # CLS1 - the cluster ratio (the ratio of the number of clusters to the number of clients with clusters generated using the GDBSCAN algorithm [29])
    cluster_amount = len(set(best_clustering.labels_))
    features["cluster_ratio"] = cluster_amount / len(clients)
    
    # CLS2 - the outlier ratio (ratio of number of outliers to clients)
    outlier_amount = len([label for label in best_clustering.labels_ if label == -1])
    features["outlier_ratio"] = outlier_amount / len(clients)

    # CLS3 - the average of the number of clients per cluster relative to total client amount
    clients_per_cluster = dict()
    for label in best_clustering.labels_:
        if label not in clients_per_cluster.keys():
            clients_per_cluster[label] = 0
        clients_per_cluster[label] += 1
    mean_clients_per_cluster = np.mean(list(clients_per_cluster.values()))
    features["avg_clients_per_cluster"] = mean_clients_per_cluster / len(clients)

    # CLS4 - the CV to the number of clients per cluster relative to total client amount
    features["cv_clients_per_cluster"] = (np.std(list(clients_per_cluster.values()))/mean_clients_per_cluster) / len(clients)

    # CLS5 - cluster density (normalized intra cluster distance)
    # CLS6 - cluster spread (normalized distance to nearest cluster)
    # Este es un bloque enorme de codigo sacado de la funcion clusteringQuality.
    client_clusters = dict()
    for i in range(len(clients)):
        if best_clustering.labels_[i] not in client_clusters.keys():
            client_clusters[best_clustering.labels_[i]] = []
        client_clusters[best_clustering.labels_[i]].append(clients[i])

    #Obtenemos centroides
    centroids = dict()
    for label, cluster in client_clusters.items():
        centroid = np.array([0,0])
        for client in cluster:
            centroid += np.array([client.x,client.y])
        centroid = np.divide(centroid,len(cluster))
        centroids[label] = centroid

    intra_cluster_distances = dict()
    for label,cluster in client_clusters.items():
        distance_to_centroid = 0
        for client in cluster:
            distance_to_centroid += np.sqrt((client.x - centroids[label][0])**2 + (client.y - centroids[label][1])**2)
        distance_to_centroid /= len(cluster)
        
        intra_cluster_distances[label] = distance_to_centroid
    average_intra_cluster_distance = np.mean(list(intra_cluster_distances.values()))

    #Obtenemos distancia de cada cluster al cluster vecino más cercano
    centroid_locations = list(centroids.values())
    if len(centroid_locations) > 1:
        neighbors = NearestNeighbors(n_neighbors=2, algorithm='auto').fit(centroid_locations)
        distances, indices = neighbors.kneighbors(centroid_locations)
        average_inter_cluster_distance = np.mean(distances)
    else:
        average_inter_cluster_distance = 0

    average_intra_cluster_distance /= max_possible_distance
    average_inter_cluster_distance /= max_possible_distance
    #Finalmente registramos las features CLS5 y CLS6
    features["intra_cluster_distance"] = average_intra_cluster_distance
    features["inter_cluster_distance"] = average_inter_cluster_distance

    # Escritura final de features
    csv_file = os.path.join(base_dir, f"features_{num_depots}_depots.csv")

    write_header = not os.path.exists(csv_file)  # Escribir encabezado solo si el archivo no existe

    with open(csv_file, "a") as f:
        # Escribir encabezado si es la primera vez
        if write_header:
            f.write("instance")
            for feature in features.keys():
                f.write("," + feature)
            f.write("\n")
        
        # Escribir fila de datos
        f.write(instances[contador].split(".")[0].split("_")[1])  # Usar nombre de instancia
        for _, value in features.items():
            if isinstance(value, np.ndarray):
                rounded_value = np.round(value, 4).tolist()
                f.write("," + str(rounded_value))
            else:
                rounded_value = round(value, 4)
                f.write("," + str(rounded_value))
        f.write("\n")
        f.close()
        contador+=1






