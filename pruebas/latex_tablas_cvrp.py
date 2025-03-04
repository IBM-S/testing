import os
import re

# Ruta de la carpeta que contiene todas las instancias
carpeta_instancias = "../Instances/CVRP"

# Función para extraer la dimensión del archivo (número de clientes = dimensión - 1)
def extraer_num_clientes(archivo_path):
    with open(archivo_path, "r") as f:
        for linea in f:
            match = re.search(r"DIMENSION\s*:\s*(\d+)", linea)
            if match:
                return int(match.group(1)) - 1  # Número de clientes = DIMENSION - 1
    return "?"  # Si no encuentra la dimensión, devuelve "?"


# Diccionario para almacenar las instancias según su tipo
instancias_por_tipo = {"CMT": [], "golden": [], "X-nA-kB": []}

# Leer los archivos en la carpeta
if os.path.exists(carpeta_instancias):
    archivos = sorted(os.listdir(carpeta_instancias))  # Ordenar archivos por nombre

    for archivo in archivos:
        if archivo.endswith(".vrp"):  # Solo procesar archivos de texto
            ruta_archivo = os.path.join(carpeta_instancias, archivo)
            num_clientes = extraer_num_clientes(ruta_archivo)

            # Clasificar las instancias según el nombre del archivo
            if archivo.startswith("CMT"):
                match = re.match(r"CMT(\d+)", archivo)
                if match:
                    valor_A = int(match.group(1))
                instancias_por_tipo["CMT"].append((archivo, num_clientes, valor_A))
            elif archivo.startswith("Golden_"):
                match = re.match(r"Golden_(\d+)", archivo)
                if match:
                    valor_A = int(match.group(1))
                
                instancias_por_tipo["golden"].append((archivo, num_clientes, valor_A))
            elif archivo.startswith("X"):
                match = re.match(r"X-n(\d+)-k\d+", archivo)
                if match:
                    valor_A = int(match.group(1))
                    instancias_por_tipo["X-nA-kB"].append((archivo, num_clientes, valor_A))

# Función para ordenar las instancias por el valor_A
def ordenar_por_valor_A(instancias):
    return sorted(instancias, key=lambda x: x[2])  # Ordenar por el valor_A (tercer elemento en la tupla)


# Función para generar una tabla en LaTeX
def generar_tabla(tipo, instancias):
    tabla = "\\begin{table}[!ht]\n"
    tabla += "\\centering\n"
    tabla += "\\begin{tabular}{cc|c|ccc}\n"
    tabla += "\\toprule\n"
    tabla += "Inst. & n & BKS & \\multicolumn{3}{c}{Best(HGS) On 10 runs} \\\\\n"
    tabla += "      &   & (2023) & ANN & KNN & RF\\\\\n"
    tabla += "\\midrule\n"

    for datos in instancias:
        archivo = datos[0]
        num_clientes = datos[1]
        # Si es del tipo 'golden', reemplazar el guion bajo por \_
        if tipo == "golden":
            instancia = archivo.replace(".vrp", "").replace("Golden_", "Golden\\_")  # Reemplazar "Golden_" por "Golden\_"
        else:
            instancia = archivo.replace(".vrp", "")  # Eliminar extensión de archivo para otros tipos
        tabla += f"{instancia} & {num_clientes} & bks & ANN & KNN & RF \\\\\n"

    tabla += "\\bottomrule\n"
    tabla += "\\end{tabular}\n"
    tabla += f"\\caption{{Resultados finales para {tipo}. n: número de clientes.}}\n"
    tabla += f"\\label{{tab:Instancias_{tipo}}}\n"
    tabla += "\\end{table}\n\n"
    return tabla

# Guardar cada tabla en su propio archivo .txt
for tipo, instancias in instancias_por_tipo.items():
    if instancias:  # Si hay instancias para ese tipo
        # Ordenar las instancias por valor_A
        instancias_ordenadas = ordenar_por_valor_A(instancias)
        
        # Generar la tabla en LaTeX
        contenido_tabla = generar_tabla(tipo, instancias_ordenadas)
        
        # Guardar la tabla en un archivo de texto
        nombre_archivo = f"tabla_{tipo}.txt"
        with open(nombre_archivo, "w") as f:
            f.write(contenido_tabla)
        
        print(f"Tabla guardada en '{nombre_archivo}'. ✅")


print("Todas las tablas han sido generadas y guardadas en archivos separados.")
