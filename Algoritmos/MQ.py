from tabulate import tabulate
def tabla(m):
    headers=['tiempo','id particion','descripcion']
    print(tabulate(m,headers, tablefmt='grid'))

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
    print('FCFS')
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

def RR(procesos):
    print('RR')
    clock = 0
    processPerClock = []
    #quantom = input("plz input quantom: ")
    quantom = 2

    procesos.sort(key = lambda m: (m[5],m[4]))
    #print(procesos)
    while len(procesos) != 0:
        flag = False
        for i in range(len(procesos)):
            ti=procesos[i][4]
            for j in range(quantom):
                if ti > 0:
                    ti = ti - 1
                    procesos[i][4] = ti
                    #print(ti)
                    processPerClock.append(procesos[i])
                    
                else:
                    #print("0")
                    newTmp = i
                    flag = True
                    break
        if flag == True:
            del procesos[newTmp]
    #print('PROCESO\tTIEMPO')
    aux=[]
    contador_muestreo =1
    for valor in processPerClock:
        aux.append([contador_muestreo,valor[0],valor[1]])
        #print(str(valor[0]) + '\t'+str(contador_muestreo))
        contador_muestreo = contador_muestreo + 1
    tabla(aux)

def ordenarSegunAlgoritmo(valor,procesos):
    if valor == 0:
        procesos.sort(key = lambda m: (m[5],m[4]))
    if valor ==1:
        procesos.sort(key=lambda m: m[5])
    if valor == 2:
        procesos.sort(key=lambda m: m[2])
    return(procesos)
    
      
def buscarAlgoritmo(valor,procesos):
    if valor == 0:
        RR(procesos)
    if valor ==1:
        FCFS(procesos)
    if valor == 2:
        Prioridades(procesos)

def RR_Gral():
    print('MQ')
    global procesos
    global colas_multinivel
    global lista_algoritmos
    global quantum_gral 
    
    clock = 0
    processPerClock = []
    
    cont_cola=0
    vacio=False
    while vacio==False:        
        flag = False
        if len(colas_multinivel[cont_cola])>0:
            colas_multinivel[cont_cola]=ordenarSegunAlgoritmo(listAlgoritmoInt[cont_cola],colas_multinivel[cont_cola])
            caux=[]
            sumquantum=quantum_gral  
            b=True
            i=0
            while b:
                #Pregunta si el proceso i de la cola tiene un tiempo de irrupcion menor al quantum gral
                tipc=colas_multinivel[cont_cola][i][4]
                copia=[]
                if tipc<=sumquantum:
                    caux.append(colas_multinivel[cont_cola][i])
                    sumquantum=sumquantum-tipc
                    print('se borra',colas_multinivel[cont_cola][i])
                    del colas_multinivel[cont_cola][i]
                    print('caux',caux)
                    print(len(colas_multinivel[cont_cola]))
                    if (len(colas_multinivel[cont_cola])==0):
                        buscarAlgoritmo(listAlgoritmoInt[cont_cola],caux)
                        b=False
                else: 
                    if sumquantum!=0:
                        tinuevo=tipc-sumquantum
                        colas_multinivel[cont_cola][i][4]=tinuevo
                        copia=colas_multinivel[cont_cola][i]
                        print( 'copia',copia)
                        copia[4]=sumquantum
                        caux.append(copia)
                        sumquantum=sumquantum-tinuevo
                        print('sumquantum',sumquantum)
                        i=i+1
                if sumquantum<=0:
                    buscarAlgoritmo(listAlgoritmoInt[cont_cola],caux)
                    b=False
        if (cont_cola<4):
            cont_cola=cont_cola+1
        else:
            cont_cola=0
        if ((len(colas_multinivel[0])==0) and (len(colas_multinivel[1])==0) and (len(colas_multinivel[2])==0) and (len(colas_multinivel[3])==0) and (len(colas_multinivel[4])==0)):
            vacio=True

    
    


lista_algoritmos = ['rr','fcfs','prioridades','','']
#rr = 0
#fcfs = 1
#prioridades =2

colas_multinivel = [[],[],[],[],[]]


print(colas_multinivel)
limites_colas = [0,20,50,999999,999999]
#['idpc','Descripcion','Prioridad','Tamaño','TI','TA']
procesos= [[1,'aaa',0,25,20,2],
[2,'bbb',0,130,20,1],
[3,'ccc',3,65,60,0],
[4,'ddd',1,47,7,7],
[5,'eee',0,2,5,2],
[6,'fff',2,59,3,0],
[7,'ggg',2,30,2,8],
[8,'hhh',6,200,7,8]]

listAlgoritmoInt=[]
for i in range(len(lista_algoritmos)):
    if lista_algoritmos[i]=='rr':
        listAlgoritmoInt.insert(i,0)
    if lista_algoritmos[i]== 'fcfs':
        listAlgoritmoInt.insert(i,1)
    if lista_algoritmos[i]=='prioridades':
        listAlgoritmoInt.insert(i,2)
        

quantum_gral=10
for i in procesos:
    if i[3] >limites_colas[0] and i[3] <=limites_colas[1] :
        colas_multinivel[0].append(i)
    if i[3] >limites_colas[1] and i[3] <=limites_colas[2]:
        colas_multinivel[1].append(i)
    if i[3] > limites_colas[2] and i[3] <= limites_colas[3]:
        colas_multinivel[2].append(i)
    if i[3] > limites_colas[3] and i[3] <= limites_colas[4]:
        colas_multinivel[3].append(i)
    if i[3] >limites_colas[4]:
        colas_multinivel[3].append(i)

for x in colas_multinivel:
    print('primer for',x)


RR_Gral()
print('Algoritmo Terminado')
print(colas_multinivel)