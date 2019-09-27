import mysql.connector
def FCFS(procesos):
    #Primero que nada ordeno la lista de procesos según orden de llegada ta
    procesos.sort(key=lambda procesos: procesos[5])
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
    print("---INSTANTE---EJECUTANDOSE---")
    while tiempototal_cpu>0:
        for i in range(procesos[x][4]):
            print("   t=",str(t),"             ",procesos[x][1])
            tiempototal_cpu=tiempototal_cpu-1
            int(t)
            t=t+1
        x=x+1  
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
    print("---INSTANTE---EJECUTANDOSE---")
    while tiempototal_cpu>0:
        for i in range(procesos[x][4]):
            print("   t=",str(t),"             ",procesos[x][1])
            tiempototal_cpu=tiempototal_cpu-1
            int(t)
            t=t+1
        x=x+1  

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

"""Me conecto a la BDD simulador y saco mediante 2consultas los procesos y los procesos con cada una de sus
rafagas para poder probar los distintos algoritmos"""

cnx = mysql.connector.connect(user='root', password='administrador',host='localhost',database='simulador')
cursor = cnx.cursor()
query2 = ("select * from procesos p, rafagas r where p.idpc=r.idpc")
query1 =("select * from procesos")
cursor.execute(query1)
proc_conrafagas=[]
procesos=[]
for (i) in cursor:
    procesos.append(i)
cursor.execute(query2)
for (i) in cursor:
    proc_conrafagas.append(i)


""" Llamo a las funciones de los algoritmos de planificación para probarlas"""
FCFS(procesos)
carga_2=[(7, 'D', 4, 8, 4, 2), (8, ' E', 1, 4, 3, 4), (9, ' F', 3, 16, 7, 4)]
Prioridades(carga_2)
cursor.close()
cnx.close()