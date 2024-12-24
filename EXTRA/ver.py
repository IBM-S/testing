import matplotlib.pyplot as plt
import re
import random
import ast
import os


# Función para leer y extraer datos desde output.js
def read_js_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Extraer las coordenadas del depósito
    depots_match = re.search(r"var depots = \[(.*?)\];", content)
    depots_raw = depots_match.group(1) if depots_match else ""
    depots = [float(coord) for coord in depots_raw.split(",") if coord.strip()]

    # Extraer las rutas
    routes_match = re.search(r"var routes = \[.*?\];", content, re.DOTALL)
    routes_section = routes_match.group(0) if routes_match else ""
    data = ast.literal_eval(str(routes_section.split("=")[1].split(";")[0]))

    # Crear un diccionario para almacenar las rutas
    rutas = {}

    # Iterar sobre los depósitos y las rutas
    for i, depot in enumerate(data):
        rutas[f"depot_{i+1}"] = []
        for ruta in depot:
            rutas[f"depot_{i+1}"].append(ruta)

    # Imprimir el diccionario resultante

    # Convertir el diccionario de rutas a una lista de listas de listas
    all_routes = []
    for depot_routes in rutas.values():
        depot_routes_list = []
        for route in depot_routes:
            # Convertir la cadena de la ruta en una lista de pares de coordenadas
            pares_coordenadas = [[route[i], route[i+1]] for i in range(0, len(route), 2)]
            depot_routes_list.append(pares_coordenadas)
        all_routes.append(depot_routes_list)

    return depots, all_routes

# Leer datos desde el archivo
file_path = "output.js"
depots, routes = read_js_file(file_path)

# Configurar gráfico
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_title("Routes Visualization")
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")

# Dibujar depósitos
for i in range(0, len(depots), 2):
    depot_x = depots[i]
    depot_y = depots[i+1]
    plt.scatter(depot_x, depot_y, color='blue', label="", s=100)

# Colores para cada ruta
#colors = ['red', 'green', 'orange', 'purple', 'brown']

def generar_paleta_rgb(num_rutas):
    """Genera una paleta de colores RGB aleatorios.

    Args:
    num_rutas: Número de colores a generar.

    Returns:
    Una lista de tuplas RGB, donde cada tupla representa un color.
    """

    paleta = []
    for _ in range(num_rutas):
        r = random.uniform(0.0, 1.0)  # Ajusta el rango si lo deseas
        g = random.uniform(0.0, 1.0)
        b = random.uniform(0.0, 1.0)
        paleta.append((r, g, b))
    return paleta

num_depots = len(routes)

conteo = 0
for rutas_deposito in routes:
    conteo += len(rutas_deposito)
colors = generar_paleta_rgb(conteo)

# Agrupamos las coordenadas en pares
depots_pares = []
for i in range(0, len(depots), 2):
    depots_pares.append([depots[i], depots[i+1]])

for depot_index, depot_routes in enumerate(routes):
    # Generar paleta de colores para este depósito
    depot_colors = generar_paleta_rgb(len(depot_routes))

    for route_index, route in enumerate(depot_routes):
        x_coords = []
        y_coords = []

        for coord in route:
            x_coords.append(coord[0])
            y_coords.append(coord[1])
        depot_x, depot_y = depots_pares[depot_index]

        # Conectar el depósito con el primer y último punto
        plt.plot([depot_x, x_coords[0]], [depot_y, y_coords[0]], color=depot_colors[route_index], linestyle='--')
        plt.plot(x_coords, y_coords, color=depot_colors[route_index], label=f"Route {route_index+1} - Depot {depot_index + 1}")
        plt.plot([x_coords[-1], depot_x], [y_coords[-1], depot_y], color=depot_colors[route_index], linestyle='--')

        # Dibujar los puntos
        plt.scatter(x_coords, y_coords, color=depot_colors[route_index])


# Configurar leyenda
plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.1), ncol=5, fontsize='small')

plt.grid()
plt.tight_layout()

directorio = "EXTRA"  # Reemplaza con la ruta correcta

# Buscar todos los archivos que comiencen con "solution_"
for archivo in os.listdir():
    if archivo.startswith("solution_"):
        # Extrae el nombre de la instancia
        nombre_instancia = archivo.split("_")[1].split(".")[0]

nombre_final = f'../images/final_route_{nombre_instancia}.png'

# Guardar y mostrar
plt.savefig(nombre_final)
plt.show()
