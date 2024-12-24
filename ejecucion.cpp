#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>  // Para la función system()

int main() {
    std::ifstream archivo("comandos.txt");  // Archivo con los comandos a ejecutar
    if (!archivo) {
        std::cerr << "No se pudo abrir el archivo." << std::endl;
        return 1;
    }

    std::string linea;
    // Leer cada línea del archivo
    while (std::getline(archivo, linea)) {
        if (!linea.empty()) {  // Solo ejecutar si la línea no está vacía
            std::cout << "" << std::endl;
            std::cout << "Ejecutando: " << linea << std::endl;
            int resultado = system(linea.c_str());  // Ejecuta el comando
            if (resultado != 0) {
                std::cerr << "Error al ejecutar el comando: " << linea << std::endl;
            }
        }
    }

    archivo.close();  // Cierra el archivo
    return 0;
}
