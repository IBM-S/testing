#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>  // Para la función system()
#include <chrono> // Para medir el tiempo


int main(int argc, char* argv[]) {
    std::string nombreArchivo;

    // Verificar si se pasó un argumento
    if (argc > 1) {
        if (argc == 3 && std::string(argv[1]) == "-caso") {
            nombreArchivo = argv[2];  // Archivo pasado con el flag -caso
        } else if (argc == 2) {
            nombreArchivo = argv[1];  // Archivo pasado directamente
        } else {
            std::cerr << "Uso: " << argv[0] << " [nombreArchivo | -caso nombreArchivo]" << std::endl;
            return 1;
        }


        // Intentar abrir el archivo
        std::ifstream archivo(nombreArchivo);
        if (!archivo) {
            std::cerr << "No se pudo abrir el archivo: " << nombreArchivo << std::endl;
            return 1;
        }

        std::string linea;
        auto tiempo_total_start = std::chrono::high_resolution_clock::now();
        // Leer cada línea del archivo
        while (std::getline(archivo, linea)) {
            if (!linea.empty()) {  // Solo ejecutar si la línea no está vacía
                // Iniciar el cronómetro
                auto start = std::chrono::high_resolution_clock::now();

                std::cout << "Ejecutando: " << linea << std::endl;
                int resultado = system(linea.c_str());  // Ejecuta el comando

                // Detener el cronómetro y calcular la duración
                auto finish = std::chrono::high_resolution_clock::now();
                std::chrono::duration<double> elapsed = finish - start;
                std::cout << "Tiempo de ejecución: " << elapsed.count() << " segundos" << std::endl;
                if (resultado != 0) {
                    std::cerr << "Error al ejecutar el comando: " << linea << std::endl;
                }
            }
        }
        auto tiempo_total_finish = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> t_total = tiempo_total_finish - tiempo_total_start;
        std::cout << "Tiempo de ejecución: " << t_total.count() << " segundos" << std::endl;

    archivo.close();  // Cierra el archivo

    } else {
        // Caso de prueba
        std::string linea_juguete = "../build/hgs ../Instances/CVRP/X-n157-k13.vrp sol/medium_0_X-n157-k13.sol -seed 12155 -t 5 > logs/logs_medium_0_X-n157-k13";
        std::cout << "Ejecutando: " << linea_juguete << std::endl;
        int resultado = system(linea_juguete.c_str()); //Ejecutar comando
        if (resultado != 0) {
            std::cerr << "Error al ejecutar el comando de prueba por defecto." << std::endl;
        }
    }

    return 0;
}
