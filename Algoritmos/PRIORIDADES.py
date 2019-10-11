from tabulate import tabulate
def tabla(m):
    headers=['tiempo','id particion','descripcion']
    print(tabulate(m,headers, tablefmt='grid'))


def Prioridades(procesos):
    #Primero ordeno la lista de procesos según la prioridad que tenga cada uno
    procesos.sort(key=lambda procesos: procesos[2])
    print(procesos)
    tiempototal_cpu=0
    resultados=[]

     #Saco el tiempo total de uso de la cpu para hacer el gantt
    for i in procesos:
         tiempototal_cpu=tiempototal_cpu+i[4]
         resultados.append([])
    print(tiempototal_cpu)  

     #x solo utilizo como variable de control del bucle, t para mostrar instantes de tiempo en la salida
    t=0
    x=0
    print('PRIORIDADES')
    aux=[]
    #print("---INSTANTE---EJECUTANDOSE---")
    while tiempototal_cpu>0:
        for i in range(procesos[x][4]):
            aux.append([t,procesos[x][0],procesos[x][1]])
            #print("   t=",str(t),"             ",procesos[x][1])
            tiempototal_cpu=tiempototal_cpu-1
            int(t)
            t=t+1
        x=x+1  
    tabla(aux)
    #El tiempo de espera es el tiempo que un proceso esta en la cola de listo esperando a ejecutarse, para el primero
    #siempre es 0, para los demas es la acumulación de tiempos de irrupción de procesos anteriores
    resultados[0].append(procesos[0][1]) 
    resultados[0].append(("Tiempo de Espera:0"))
    te=0
    x=1
    while x<len(procesos):
        te=procesos[x-1][4]+te
        resultados[x].append(procesos[x][1])
        resultados[x].append("Tiempo de Espera:"+str(te))
        x=x+1
    print(resultados)



procesos= [[1,'aaa',0,25,20,2],
[2,'bbb',0,130,20,1],
[3,'ccc',3,65,60,0],
[4,'ddd',1,47,7,7],
[5,'eee',0,2,5,2],
[6,'fff',2,59,3,0],
[7,'ggg',2,30,2,8],
[8,'hhh',6,200,7,8]]

Prioridades(procesos)

