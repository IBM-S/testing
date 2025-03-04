import os

# Lista de carpetas a procesar
carpetas = ["logs_ANN", "logs_KNN", "logs_RF"]

for carpeta in carpetas:
    resultado_path = os.path.join(carpeta, "resultados.txt")
    
    with open(resultado_path, "w") as resultado_file:
        # Obtener todos los archivos en la carpeta que empiezan con "salida_"
        archivos = [f for f in os.listdir(carpeta) if f.startswith("salida_")]

        # Ordenar archivos para mantener el orden correcto
        archivos.sort()

        for archivo in archivos:
            archivo_path = os.path.join(carpeta, archivo)
            
            # Extraer identificador después de "salida_"
            identificador = archivo.replace("salida_", "")

            # Leer el contenido del archivo
            with open(archivo_path, "r") as f:
                contenido = f.read().strip()  # Quita espacios y saltos de línea extra

            # Escribir en el archivo consolidado
            resultado_file.write(f"{identificador}\n{contenido}\n\n")

print("Proceso completado. Archivos resultados.txt generados en cada carpeta.")
