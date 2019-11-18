#Esto es un First fit con particion fija
from tabulate import tabulate


#tam_mem es tamano memoria
def tabla(m):
    headers=['id particion','direccion comienzo','estado particion','size','idproceso','fraginterna']
    print(tabulate(m,headers, tablefmt='grid'))

"""def asignacion(tam_so,tam_user,n):
    b=True
    while b:
        mem=[]
        sum=0
        for i in range(n):
            print ('cantidad de memoria disponible:{}'.format(tam_user-sum))
            x=int(input('insert the {} esima partition size \n'.format(i+1)))
            mem.append([i+1,tam_so+sum,'disponible',x,0,0])
            sum=sum+x
        if sum>tam_user:
            print('error! memoria insuficiente. Por favor reasigne las particiones')
        else:
            print('espacios restantes {}\n'.format(tam_user-sum))
            b=False
    return(mem)
"""

def asignacionp(mem,n,np):
    sum=0
    #mem.sort(key=lambda m: m[3])
    print(mem)
    for i in range(np):
        print ('cantidad de particiones disponible:{}'.format(n-sum))
        x=int(input('ingrese el tamano del programa nro{} \n'.format(i+1)))
        j=0
        while (j<n) and ((mem[j][3])<x or (mem[j][2])!='disponible'):
            j=j+1
        if j<n:
            if (mem[j][3])>=x and (mem[j][2])=='disponible':
                mem[j][4]=i+1
                mem[j][5]=(mem[j][3])-x
                mem[j][2]='ocupado'
                sum=sum+1
                tabla(mem)
            else:
                print('no existe particion que soporte el proceso. Se procedera a ejecutar el siguiente proceso')
        else:
            print('no existe particion que soporte el proceso. Se procedera a ejecutar el siguiente proceso')
    return(mem)

#self.lista_graficos.append([cont_agregar_particion,tampart,rli])
#aqui es donde guardamos todas las particiones creadas
n_proceso=8
tam_mem=1028
#tam_user es tamano memoria usuario
tam_user=int(tam_mem-tam_mem*0.1)
#tam_so es tamano memoria sistema operativo
tam_so=int(tam_mem-tam_user)


m1=[
[1,128,'disponible',20,0,0],
[2,148,'disponible',360,0,0],
[3,508,'disponible',135,0,0],
[4,643,'disponible',256,0,0],
[5,899,'disponible',100,0,0],
[6,999,'disponible',20,0,0]
] 
mem=asignacionp(m1,6,n_proceso)
#mem.sort(key=lambda m: m[0])
tabla(mem)