import random
from tabulate import tabulate

def tabla(m):
    headers=['id particion','direccion comienzo','size','idproceso']
    print(tabulate(m,headers, tablefmt='grid'))
    
def arribo(lista_arribo):
    global colanew
    colanew.extend(lista_arribo)
    print('prueba colanew',colanew)

def unirhueco(mem):
    i=0
    while i+1<len(mem):
        if mem[i][3]==0 and mem[i+1][3]==0:
            mem[i][2]=mem[i][2]+mem[i+1][2]
            mem.pop(i+1)
        else:
            i=i+1
    return(mem)

def asignacion1():
    global mem
    global idpart
    global colanew
    if colanew:
        i=0
        b=True
        print('soy cola new',colanew)
        while i<len(colanew):
            print('soy i',i)
            print(len(colanew))
            j=0
            tipo=mem[j][3]
            while (j<len(mem) and (tipo!=0 or colanew[i][3]>mem[j][2])):
                if colanew[i][3]>mem[j][2]:
                    print('por que mierda no entras?',mem[j][2]-colanew[i][3])
                    print('averr si eres hueco',tipo)
                else:
                    print('entonces que?',j)
                tipo=mem[j][3]
                j=j+1
            print ('posicion de memoria',j)
            if j!=0:
                j=j-1
            if j<len(mem):
                if tipo==0 and colanew[i][3]<=mem[j][2]:
                    nuevotam=mem[j][2]-colanew[i][3]
                    nuevodir=mem[j][1]+colanew[i][3]
                    if nuevotam==0:
                        mem[j]=[idpart,mem[j][1],colanew[i][3],colanew[i][0]]
                    else:
                        mem[j]=[idpart,mem[j][1],colanew[i][3],colanew[i][0]]
                        mem.insert(j+1,[0,nuevodir,nuevotam,0])
                    idpart=idpart+1
                    colanew.pop(i)
                    j=j+1
                else:
                    i=i+1
            print('aber si incremento',i)
    unirhueco(mem)
    tabla(mem)

#['idpc','Descripcion','Prioridad','Tamaño','TI','TA']
procesos=[[1,'aaa',0,25,20,2],
    [2,'bbb',0,130,20,1],
    [3,'ccc',3,65,60,0],
    [4,'ddd',1,47,7,7],
    [5,'eee',0,2,5,2],
    [6,'fff',2,59,3,0],
    [7,'ggg',2,30,2,8],
    [8,'hhh',6,200,7,8]]
tam_user=256
mem=[[0,0,tam_user,0]]
#['idpart',dir_rli,part_size,idpc]
colanew=[]
procesos.sort(key=lambda m: m[5])
print(procesos)
dir=0
idpart=1
j=0
for i in range(9):
    colaarribo=[]
    while j<len(procesos) and procesos[j][5]==i:
        colaarribo.append(procesos[j])
        j=j+1
    if len(colaarribo)>0:
        print('cola arribo',colaarribo)
        arribo(colaarribo)
    asignacion1()

print(mem)

for j in colaarribo:
    i=random.randint(0, len(mem)-1)
    print('random',i)
    mem[i][3]=0
    asignacion1()
    print(mem)

    