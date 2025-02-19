import os

def generar_codigo_latex(lista_instancias, ruta_base):
    """
    Genera el código LaTeX para subfiguras a partir de una lista de instancias y una ruta base.

    Args:
        lista_instancias: Lista de nombres de las instancias.
        ruta_base: Ruta base de las imágenes.

    Returns:
        Una cadena con el código LaTeX generado.
    """

    codigo_latex = "\\begin{figure}[htbp]\n"
    codigo_latex += "    \\centering\n"
    contador = 1
    for instancia in lista_instancias:
        codigo_latex += f"    \\begin{{subfigure}}{{0.24\\textwidth}}\n"
        codigo_latex += f"        \\includegraphics[width=\\textwidth]{{{ruta_base}/{instancia}.png}}\n"
        parte1, parte2 = instancia.split("_")
        instancia = f'{parte1}'
        codigo_latex += f"        \\caption{{{instancia}}}\n"
        codigo_latex += "    \\end{subfigure}\n"
        if contador % 24 == 0:
            codigo_latex += "    \\end{figure}\n"
            codigo_latex += "\\begin{figure}[htbp]\n"
            codigo_latex += "    \\centering\n"

        else: 
            codigo_latex += "    \\hfill\n"
            
        contador+=1

    codigo_latex += "    \\caption{Instancias X-nA-kB. Con Cluster, las hice con codigo JupyterNotebook}\n"
    codigo_latex += "    \\label{fig:subfigures}\n"
    codigo_latex += "\\end{figure}"

    return codigo_latex

# Ejemplo de uso:
lista_instancias = ['X-n101-k25.vrp', 'X-n106-k14.vrp', 'X-n110-k13.vrp', 'X-n115-k10.vrp', 'X-n120-k6.vrp', 'X-n125-k30.vrp', 'X-n129-k18.vrp', 
                    'X-n134-k13.vrp', 'X-n139-k10.vrp', 'X-n143-k7.vrp', 'X-n148-k46.vrp', 'X-n153-k22.vrp', 'X-n157-k13.vrp', 'X-n162-k11.vrp', 
                    'X-n167-k10.vrp', 'X-n172-k51.vrp', 'X-n176-k26.vrp', 'X-n181-k23.vrp', 'X-n186-k15.vrp', 'X-n190-k8.vrp', 'X-n195-k51.vrp', 
                    'X-n200-k36.vrp', 'X-n204-k19.vrp', 'X-n209-k16.vrp', 'X-n214-k11.vrp', 'X-n219-k73.vrp', 'X-n223-k34.vrp', 'X-n228-k23.vrp', 
                    'X-n233-k16.vrp', 'X-n237-k14.vrp', 'X-n242-k48.vrp', 'X-n247-k50.vrp', 'X-n251-k28.vrp', 'X-n256-k16.vrp', 'X-n261-k13.vrp', 
                    'X-n266-k58.vrp', 'X-n270-k35.vrp', 'X-n275-k28.vrp', 'X-n280-k17.vrp', 'X-n284-k15.vrp', 'X-n289-k60.vrp', 'X-n294-k50.vrp', 
                    'X-n298-k31.vrp', 'X-n303-k21.vrp', 'X-n308-k13.vrp', 'X-n313-k71.vrp', 'X-n317-k53.vrp', 'X-n322-k28.vrp', 'X-n327-k20.vrp', 
                    'X-n331-k15.vrp', 'X-n336-k84.vrp', 'X-n344-k43.vrp', 'X-n351-k40.vrp', 'X-n359-k29.vrp', 'X-n367-k17.vrp', 'X-n376-k94.vrp', 
                    'X-n384-k52.vrp', 'X-n393-k38.vrp', 'X-n401-k29.vrp', 'X-n411-k19.vrp', 'X-n420-k130.vrp', 'X-n429-k61.vrp', 'X-n439-k37.vrp', 
                    'X-n449-k29.vrp', 'X-n459-k26.vrp', 'X-n469-k138.vrp', 'X-n480-k70.vrp', 'X-n491-k59.vrp', 'X-n502-k39.vrp', 'X-n513-k21.vrp', 
                    'X-n524-k153.vrp', 'X-n536-k96.vrp', 'X-n548-k50.vrp', 'X-n561-k42.vrp', 'X-n573-k30.vrp', 'X-n586-k159.vrp', 'X-n599-k92.vrp', 
                    'X-n613-k62.vrp', 'X-n627-k43.vrp', 'X-n641-k35.vrp', 'X-n655-k131.vrp', 'X-n670-k130.vrp', 'X-n685-k75.vrp', 'X-n701-k44.vrp', 
                    'X-n716-k35.vrp', 'X-n733-k159.vrp', 'X-n749-k98.vrp', 'X-n766-k71.vrp', 'X-n783-k48.vrp', 'X-n801-k40.vrp', 'X-n819-k171.vrp', 
                    'X-n837-k142.vrp', 'X-n856-k95.vrp', 'X-n876-k59.vrp', 'X-n895-k37.vrp', 'X-n916-k207.vrp', 'X-n936-k151.vrp', 'X-n957-k87.vrp', 
                    'X-n979-k58.vrp', 'X-n1001-k43.vrp']

nombres = os.listdir("../../imgs_Instancias_With Cluster/imgs_X")

for i in range(0, len(lista_instancias)):
    nombres[i] = nombres[i][:-4]

ruta_base = "imgs_Instancias_With Cluster/imgs_X"  # Ruta base de las imágenes

codigo_latex_generado = generar_codigo_latex(nombres, ruta_base)
print(codigo_latex_generado)