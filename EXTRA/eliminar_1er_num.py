import os

def eliminar_primer_numero(archivo_entrada, archivo_salida):
    with open(archivo_entrada, 'r') as f_in, open(archivo_salida, 'w') as f_out:
        for line in f_in:
            if line.strip():  # Evita líneas vacías
                line = line[1:]  # Elimina el primer caracter
            f_out.write(line)

# Reemplaza 'tu_carpeta' con la ruta a tu carpeta
carpeta = '../Data/DataFiles'

print(os.listdir(carpeta))


for archivo in os.listdir(carpeta):
    if archivo.startswith('pr'):  # Ajusta la extensión si es necesario
        archivo_entrada = os.path.join(carpeta, archivo)
        archivo_salida = os.path.join(carpeta, 'nuevo_' + archivo)
        eliminar_primer_numero(archivo_entrada, archivo_salida)