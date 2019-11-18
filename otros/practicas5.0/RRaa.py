from tabulate import tabulate
def tabla(m):
    headers=['tiempo','id particion','descripcion']
    print(tabulate(m,headers, tablefmt='grid'))


def RR(procesos):
    print('RR')
    clock = 0
    processPerClock = []
    #quantom = input("plz input quantom: ")
    quantom = 2

    procesos.sort(key = lambda m: (m[5],m[4]))
    print('original',procesos)
    i=0
    while len(procesos) != 0:
        #flag = False
        #for i in range(len(procesos)):
        ti=procesos[i][4]
        b=True
        q=quantom
        if ti>= q:
            ti=ti-q
            aux=procesos[i].copy()
            if ti>0:
                procesos[i][4] = ti
                aux[4]=q
                i=i+1
            else:
                del procesos[i]
            q=0
            processPerClock.append(aux)
        else:
            q=q-ti
            processPerClock.append(procesos[i])
            del procesos[i]
        if i==len(procesos):
            i=0
        """
                if ti > 0:
                    ti = ti - 1
                    procesos[i][4] = ti
                    #print(ti)
                    processPerClock.append(procesos[i])
                    print('qcyo',procesos[i])
                    print('y weno nose',processPerClock[-1])
                else:
                    #print("0")
                    newTmp = i
                    flag = True
                    break
            print('eee',processPerClock)
        if flag == True:
            del procesos[newTmp]
        """
    #print('PROCESO\tTIEMPO')
    aux=[]
    contador_muestreo =1
    """
    for valor in processPerClock:
        aux.append([contador_muestreo,valor[0],valor[1]])
        #print(str(valor[0]) + '\t'+str(contador_muestreo))
        contador_muestreo = contador_muestreo + 1
    """
    #tabla(aux)
    print('final',processPerClock)
    #print(aux)

"""
procesos= [[1,'aaa',0,25,20,2],
[2,'bbb',0,130,20,1],
[3,'ccc',3,65,60,0],
[4,'ddd',1,47,7,7],
[5,'eee',0,2,5,2],
[6,'fff',2,59,3,0],
[7,'ggg',2,30,2,8],
[8,'hhh',6,200,7,8]]
"""
procesos= [[1,'aaa',0,25,20,2],
    [2,'bbb',0,130,20,1],
    [3,'ccc',3,65,60,0],
    [4,'ddd',1,47,7,7],
    [5,'eee',0,2,5,2]]

RR(procesos)

