from tabulate import tabulate
def Prioridades(procesos):
    #Ordeno los procesos segun sus tiempos de arribo para ir ejecutando el algoritmo
    #sobre esto y armar el gantt 
    procesos_ta=procesos
    procesos_ta.sort(key=lambda procesos_ta: procesos_ta[5])
    print("Procesos ordenados por tiempo de arribo")
    print(tabulate(procesos_ta,headers=['PID','Descripción','Prioridad','Tamaño','TI','TA'],tablefmt='fancy_grid'))
     
    tiempototal_cpu=0
    #Calculo el tiempo total de irrupción de todos los procesos juntos
    for i in range(len(procesos)):
        tiempototal_cpu=tiempototal_cpu+procesos[i][4]

    #Comienzo el algoritmo guardando resultados de cada instante de ejecución
    resultados=[]
    clock=1
    cola_listos=[]
    while clock<=tiempototal_cpu:
        #ejec_en_instante me va guardando filas para agregar al resultado con datos de
        #la ejecucion de cada proceso en cada instante
        ejec_en_instante=[]
        ejec_en_instante.append(clock)
        #agrego a la cola de listos todos aquellos procesos que llegaron, es decir que 
        #tienen su ta igual al clock actual
        for i in range(len(procesos_ta)):
            if procesos_ta[i][5]==clock:
                cola_listos.append(procesos_ta[i])
        #Ordeno la cola de listo por prioridad, asi puedo mandar a ejecutar siempre
        #al primero de mayor prioridad, recordando que a menor valor de prioridad mayor
        #es la prioridad, ej prioridad 2 es mayor que 4
        cola_listos.sort(key=lambda cola_listos: cola_listos[2])
        #elijo el proceso que va a ejecución
        ejecutar=cola_listos[0][1]
        ejec_en_instante.append(ejecutar)
        #para ver como se desenlaza el algoritmo y ver como va cambiando la cola de listos 
        print(cola_listos)
        #Voy descontando el tiempo restante de irrupción del proceso que 
        #mande a ejecutar
        cola_listos[0][4]=cola_listos[0][4]-1
        ti_restante=cola_listos[0][4]
        #Agrego el dato de tiempo restante de irrupción 
        ejec_en_instante.append(ti_restante)
        #Elimino de la cola de listos aquellos que ya completaron sus tiempos de irrupción
        if cola_listos[0][4]==0:
            cola_listos.remove(cola_listos[0])
        clock=clock+1
        #Agrego la fila completa con todos los datos cargados a los resultados
        resultados.append(ejec_en_instante)
    print("Resultados")   
    print(tabulate(resultados,headers=['Instante','Ejecutándose','TI restante'],tablefmt='fancy_grid',stralign='center',numalign='center'))



cargaTrabajo_prueba1=[[1,'aaa',3,25,5,1],
[2,'bbb',2,130,3,3],
[3,'ccc',1,65,2,3],
[4,'ddd',4,25,2,1]]
Prioridades(cargaTrabajo_prueba1)