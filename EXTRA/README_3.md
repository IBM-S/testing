# Explicacion Codigos

## codigo_latex.py
lo cree para poder hacer mas facil colocar las imagenes en el latex, para el caso X-nA-kB, ya que
son 100

Ejecucion: python3 codigo_latex.py

## creador_para_dejar_corriendo_inst_pr.py / creador_para_dejar_corriendo_inst_pr.py

Crea las carpetas correspondientes para los dos tipos de instancias del MDVRP "inst_{tipo_instancia}_dejar_corriendo".
Luego crea dentro los archivos necesarios para dejar corriendo la sintonizacion. params.params, ga.sh, ToDoParamILS.sh. Los archivos
.scn e .ins se moveran de las carpetas scn e ins cuando se necesiten y luego cuando se dejen de ocupar se moveran donde estaban en un
principio. Esto se hace para cada tipo de instancia {pr, p} 

## eliminar_1er_num.py
toma las instancias prXX dentro de Data/DataFiles y les quita el numero extra que tenian en la primera linea y el 
nuevo nombre que tienen es el pr01

Ejecucion: python3 eliminar_1er_num.py

## feature_extracion.py
Extrae las caracteristicas de los 2 tipos de instancias "pr" y "p"
Se mete a la carpeta EXTRA/vrp_lib_mdvrp y de ahi saca las instancias, luego las caracteristicas las va dejando en 
una carpeta llamada features_inst
se ocupa de la siguiente forma:
python3 feature_extraction.py -d {carpeta donde se encuentran las instancias en el formato vrp lib}
Ejecucion: python3 feature_extraction.py -d vrp_lib_mdvrp/

## gif_maker.py
Crea un gif en base a la carpeta generations. Las cuales son las iteraciones del codigo cada cierto 
numero de iteraciones.

## output.js
Es el resultado final luego de correr el programa

## transformar_instance_to_vrplib.py
toma el formato que estan las instancias pXX y prXX en la carpeta Data/DataFiles (luego de haberles quitado el primer 
numero de la primera linea), y las transforma al formato vrplib, esto para
poder leer mas facilmente las instancias en el codigo feature_extraction.py

## ver_capacidad.py
Calcula la demanda total, la demanda minima, demanda maxima, promedio de demanda y desviacion de la demanda. 
Y luego crear un txt.
En la siguiente linea se puede modificar para poder especificar el tipo de instancia (Manualmente hay que cambiar
el tipo de instancia): "if archivo.startswith("pr"):"
Resultado ejemplo: p01 total: 777 - min: 3 - max: 41 - prom: 15.54 - desv: 7.98

## ver.py
crea una imagen en la carpeta images el cual es el resultado del final del algoritmo genetico, la
informacion la lee desde el archivo que se crea que es output.js


## features_inst/_features_{instancia}.csv
ahi se guardan los resultados de las features encontradas

carpeta solutions
aqui se gurda la solucion final del algoritmo genetico, el costo, las rutas.
