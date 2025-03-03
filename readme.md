# codigos

## ejecucion.cpp
Ejecuta las lineas de consola por medio de un txt. Primero se crea el ejecutable:
g++ ejecucion.cpp -o ejec 
Luego se puede ejecutar de la sgiuente forma
(1) ./ejec 
(2) ./ejec -caso comandos2.txt

El primero ejecuta el caso por defecto que viene en el codigo ejecucion.cpp y el segundo 
se le puede especificar un archivo txt a probar.

## extraer_FO_ParamILS.py
crea el archivo resultados_parametros_2.csv el cual saca los valores de las funciones objetivos
de cada insntacia.

## extraer_resultados_ParamILS.py
crea el archivo resultados_parametros.csv el cual saca los valores de los parametros ocupados 
en cada insntacia.

## features&params.py
Me junta las features con los mejores parametros encontrados de las 10 instancias

# txt

## comandos.txt / comandos2.txt
Dentro de los txt hay lineas de codigo para comprobar que funciona bien el algoritmo.