# -*- coding: UTF-8 -*- 
import sys
import os
from datetime import date
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMessageBox, QWidget, QMainWindow, QDialog, QPushButton, QLabel
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.figure_factory as ff
import plotly
import plotly.graph_objects as go
from  matplotlib.backends.backend_qt5agg  import  ( NavigationToolbar2QT  as  NavigationToolbar )
import  numpy  as  np 
import  random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
matplotlib.use('Qt4Agg')
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

class Dialogo(QDialog):
  def __init__(self):
    super().__init__()
    self.resize(763,448)
    self.setWindowTitle("Carga de procesos")
    #cargo la interfaz de la ventana de carga de procesos
    uic.loadUi("nuevoproceso.ui",self)
  
class DialogoImportar(QDialog):
  def __init__(self):
    QDialog.__init__(self)
    self.setWindowTitle("Importar procesos")
    uic.loadUi("DialogImportar.ui",self)
   
class DialogoComparacion(QDialog):
  def __init__(self):
    QDialog.__init__(self)
    self.setWindowTitle("Comparacion de Algoritmos")
    uic.loadUi("dialogComparacion.ui",self)

class DialogoresultSim(QDialog):
  def __init__(self):
    QDialog.__init__(self)
    self.setWindowTitle("Resultado Simulacion")
    uic.loadUi("resultSimulacion.ui",self)

class DialogoMQ(QDialog):
  def __init__(self):
    QDialog.__init__(self)
    uic.loadUi("MQ.ui",self)

class Particiones_Fijas(QDialog):
  def __init__(self):
    QDialog.__init__(self)
    self.setWindowTitle("Carga de particiones fijas")
    uic.loadUi("carga_particiones_fijas.ui",self)
    
    #self.addToolBar(NavigationToolbar(self.MplWidget.canvas,self))

class Ventana(QMainWindow):
 def __init__(self):
  QMainWindow.__init__(self)
  self.resize(600, 600)
  self.setWindowTitle("Ventana principal")
  #cargo la interfaz .ui para la ventana principal
  uic.loadUi("MainWindow.ui",self)
  self.dialogo = Dialogo()
  self.dialogoImportar = DialogoImportar()
  self.dialogoMQ = DialogoMQ()
  self.cont=0
  self.colagantt=[]
  self.carga_particionFijas = Particiones_Fijas()
  self.dialogresultsim = DialogoresultSim()
  self.dialogcompara = DialogoComparacion()
  #una vez que cargue la interfaz .ui e hice una instancia de Dialogo. me puedo referir a los elementos que fui poniendo en la interfaz, con sus nombres
  self.boton_GestProcesos.clicked.connect(self.abrirDialogoCarga)
  #self.botonGantt.clicked.connect(self.gantt)
  self.dialogo.pushButtonCargar.clicked.connect(self.cargarProcesosYRafagasenBD)
  self.AceptarMem.clicked.connect(self.AlmacenarTamMemIngresado)
  self.tam_Memoria=0
  self.por_so=0 
  self.checkbox=QTableWidgetItem()
  self.valor_memoria_procesos=0
  self.contabla_raf=0
  self.lista_graficos=[]
  self.listaprocesos= []
  self.procesos_sin_asignar=[]
  self.procesos_importados=[]
  self.colaarribo=[]
  self.colanuevo=[]

  self.colalisto=[]
  self.met_asig=''
  self.result= []
  self.procesoparaprobar = []
  self.contador_act = 0
  self.procesoFCFS = []
  self.procesoRR =[]
  self.procesoPRIORIDAD = []
  
  self.clock=0
  
  self.MQ = False
  self.q=0
  self.quantom=0
  self.listaprocesos= []
  self.listaImportarProcesos = []
  self.label_MemProcesos.setText('0 KB')
  self.label_MemSO.setText('0 KB')
  self.spinBoxTamMemoria.setMaximum(1000000)
  self.spinBoxTamMemoria.setSingleStep(2**2)
  self.spinBoxPorcSO.setMaximum(90)
  self.spinBoxPorcSO.setSingleStep(5)
  self.flagVerprocesos = False
  self.spinBoxTamMemoria.valueChanged.connect(self.actTamMemoria)
  #self.spinBoxTamMemoria.valueChanged.connect(self.updateLabels)
  self.spinBoxPorcSO.valueChanged.connect(self.actPorcSO)
  self.spinBoxPorcSO.valueChanged.connect(self.updateLabels)
  self.spinBoxTamMemoria.valueChanged.connect(self.updateLabels)
  self.radioButton_Fijas.toggled.connect(self.fijaselected)
  self.radioButton_Variables.toggled.connect(self.variableselected)
  self.radioButton_First.toggled.connect(self.firstselected)
  self.radioButton_Best.toggled.connect(self.bestselected)
  self.radioButton_Worst.toggled.connect(self.worstselected)
  self.dialogo.tableWidgetRafaga.setColumnCount(2)
  self.dialogo.tableWidgetRafaga.setHorizontalHeaderLabels(['Tipo','Tiempo'])
  self.carga_particionFijas.botonFinalizar.clicked.connect(self.graficar)
  self.dialogo.pushButtonAgregarRafaga.clicked.connect(self.agregar_fila_rafagas)
  self.dialogo.tableWidgetProcesos.setColumnCount(6)
  self.dialogo.tableWidgetProcesos.setHorizontalHeaderLabels(['idpc','Descripcion','Prioridad','Tamaño','TI','TA'])
  self.carga_particionFijas.tableWidgetCargaParticion.setColumnCount(4)
  self.carga_particionFijas.tableWidgetCargaParticion.setHorizontalHeaderLabels(['idSim','idPart','dirRli','partSize'])
  self.carga_particionFijas.pushButtonAgregarParticion.clicked.connect(self.agregar_fila_particiones)
  self.dialogoImportar.pushButtonCargar.clicked.connect(self.loadProceso)
  

  self.pushButton_Simular.clicked.connect(self.asignacion_memoria)

  self.dialogresultsim.pushButton_verGantt.clicked.connect(self.gantt)
  #cosas que disparan al apretar "Simular" en Ventana
  #self.pushButton_Simular.clicked.connect(self.gantt) #vamos a ver que hacemos con esto
  
  #si,te
  #################################self.pushButton_Simular.clicked.connect(self.ejecutar_algoritmos) 
  #llama a metodo fcfs cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_fcfs)
  #llama a metodo prioridad cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_prioridades)
  #llama a metodo rr cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_rr)
  #llama a metodo mq cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_mq)
  self.pushButton_Simular.clicked.connect(self.generar_grafico_durante_simulacion)
  self.pushButton_Simular.clicked.connect(self.mostrarResultSimulacion)
  

  
  self.pushButtonComparar.clicked.connect(self.mostrarComparacion)
  self.pushButton_AceptarProc.clicked.connect(self.aceptar_algoritmo_presionado)
  self.dialogo.pushButtonImportar.clicked.connect(self.mostrarTablaImportar)
  self.dialogoImportar.tableWidgetImportar.setColumnCount(7)
  self.dialogoImportar.tableWidgetImportar.setHorizontalHeaderLabels([' ','idpc','Descripcion','Prioridad','Tamaño','TI','TA'])
  self.dialogcompara.tableWidgetTEspera.setColumnCount(5)
  self.dialogcompara.tableWidgetTEspera.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','C.Multinivel'])
  self.dialogcompara.tableWidgetTRetorno.setColumnCount(5)
  self.dialogcompara.tableWidgetTRetorno.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','C.Multinivel'])
  
  self.dialogresultsim.tableWidgetCListo.setColumnCount(2)
  self.dialogresultsim.tableWidgetCListo.setHorizontalHeaderLabels(['idpc','Ti',])

  self.dialogoImportar.pushButtonImportar.clicked.connect(self.update_tablaProcesos)
  self.dialogoImportar.pushButtonVertabla.clicked.connect(self.cargarTabla)
  self.dialogoMQ.spinBoxCantColas.valueChanged.connect(self.actualizarMQ)
  #----------------------------------------------------------------
  #pongo todo en disabled las opciones de cola de la ventana de MQ
  self.inicializarOpcMQ()

  #DATOS BD
  self.host='localhost'
  self.database='simulador'
  self.user='root'
  self.password='letra123'
     
  #considero que el calculo de los labels de tam de memoria para procesos y so, se hace recien cuando le 
  #di algun valor al spinbox de so, sino estaria dividiendo por el valor 0
  #muy feo, pero anda jajajaja

 def loadProceso(self):
   if int(self.dialogoImportar.spinBox_Proceso.value()) >0:
     self.listaImportarProcesos.append(self.dialogoImportar.spinBox_Proceso.value())
     pro_cargados= str(self.dialogoImportar.label_PC.text())+str(self.dialogoImportar.spinBox_Proceso.value())+","
     self.dialogoImportar.label_PC.setText(pro_cargados)
   

 def inicializarOpcMQ(self):
   self.dialogoMQ.label_algCola1.setEnabled(True)
   self.dialogoMQ.label_algCola2.setEnabled(True)
   self.dialogoMQ.label_algCola3.setEnabled(False)
   self.dialogoMQ.label_algCola4.setEnabled(False)
   self.dialogoMQ.label_algCola5.setEnabled(False)
   self.dialogoMQ.comboBox_alg1.setEnabled(True)
   self.dialogoMQ.comboBox_alg2.setEnabled(True)
   self.dialogoMQ.comboBox_alg3.setEnabled(False)
   self.dialogoMQ.comboBox_alg4.setEnabled(False)
   self.dialogoMQ.comboBox_alg5.setEnabled(False)
   self.dialogoMQ.label_q1.setEnabled(True)
   self.dialogoMQ.label_q2.setEnabled(True)
   self.dialogoMQ.label_q3.setEnabled(False)
   self.dialogoMQ.label_q4.setEnabled(False)
   self.dialogoMQ.label_q5.setEnabled(False)
   self.dialogoMQ.spinBox_q1.setEnabled(True)
   self.dialogoMQ.spinBox_q2.setEnabled(True)
   self.dialogoMQ.spinBox_q3.setEnabled(False)
   self.dialogoMQ.spinBox_q4.setEnabled(False)
   self.dialogoMQ.spinBox_q5.setEnabled(False)

 def aceptar_algoritmo_presionado(self):
   if self.comboBox_Algoritmos.currentText()=="COLAS MULTINIVEL":
     self.dialogoMQ.exec_()
     
 def actualizarMQ(self):
   if self.dialogoMQ.spinBoxCantColas.value() == 2:
     if not self.dialogoMQ.label_algCola1.isEnabled() :
       self.dialogoMQ.label_algCola1.setEnabled(True)
       self.dialogoMQ.comboBox_alg1.setEnabled(True)
       self.dialogoMQ.spinBox_q1.setEnabled(True)
       self.dialogoMQ.label_q1.setEnabled(True)
  
     if not self.dialogoMQ.label_algCola2.isEnabled():
       self.dialogoMQ.label_algCola2.setEnabled(True)
       self.dialogoMQ.comboBox_alg2.setEnabled(True)
       self.dialogoMQ.spinBox_q2.setEnabled(True)
       self.dialogoMQ.label_q2.setEnabled(True)

     if self.dialogoMQ.label_algCola3.isEnabled():
       self.dialogoMQ.label_algCola3.setEnabled(False)
       self.dialogoMQ.comboBox_alg3.setEnabled(False)
       self.dialogoMQ.spinBox_q3.setEnabled(False)
       self.dialogoMQ.label_q3.setEnabled(False)
     if self.dialogoMQ.label_algCola4.isEnabled():
       self.dialogoMQ.label_algCola4.setEnabled(False)
       self.dialogoMQ.comboBox_alg4.setEnabled(False)
       self.dialogoMQ.spinBox_q4.setEnabled(False)
       self.dialogoMQ.label_q4.setEnabled(False)
     if self.dialogoMQ.label_algCola5.isEnabled():
       self.dialogoMQ.label_algCola5.setEnabled(False)
       self.dialogoMQ.comboBox_alg5.setEnabled(False)
       self.dialogoMQ.spinBox_q5.setEnabled(False)
       self.dialogoMQ.label_q5.setEnabled(False)


     #self.dialogoMQ.label_algCola3 = self.dialogoMQ.label_algCola3.setEnabled(False)
     #self.dialogoMQ.comboBox_alg3 =self.dialogoMQ.comboBox_alg3.setEnabled(False)
     #self.dialogoMQ.spinBox_q3 = self.dialogoMQ.spinBox_q3.setEnabled(False)
     #self.dialogoMQ.label_q3 =self.dialogoMQ.label_q3.setEnabled(False)

     #self.dialogoMQ.label_algCola4 = self.dialogoMQ.label_algCola4.setEnabled(False)
     #self.dialogoMQ.label_q4 =self.dialogoMQ.label_q4.setEnabled(False)
     #self.dialogoMQ.comboBox_alg4 =self.dialogoMQ.comboBox_alg4.setEnabled(False)
     #self.dialogoMQ.spinBox_q4 = self.dialogoMQ.spinBox_q4.setEnabled(False)

     #self.dialogoMQ.label_algCola5 = self.dialogoMQ.label_algCola5.setEnabled(False)
     #self.dialogoMQ.comboBox_alg5 =self.dialogoMQ.comboBox_alg5.setEnabled(False)
     #self.dialogoMQ.label_q5 =self.dialogoMQ.label_q5.setEnabled(False)
     #self.dialogoMQ.spinBox_q5 = self.dialogoMQ.spinBox_q5.setEnabled(False)
     


   if self.dialogoMQ.spinBoxCantColas.value() == 3:
     if not self.dialogoMQ.label_algCola1.isEnabled() :
       self.dialogoMQ.label_algCola1.setEnabled(True)
       self.dialogoMQ.comboBox_alg1.setEnabled(True)
       self.dialogoMQ.spinBox_q1.setEnabled(True)
       self.dialogoMQ.label_q1.setEnabled(True)
  
     if not self.dialogoMQ.label_algCola2.isEnabled():
       self.dialogoMQ.label_algCola2.setEnabled(True)
       self.dialogoMQ.comboBox_alg2.setEnabled(True)
       self.dialogoMQ.spinBox_q2.setEnabled(True)
       self.dialogoMQ.label_q2.setEnabled(True)

     if not self.dialogoMQ.label_algCola3.isEnabled():
       self.dialogoMQ.label_algCola3.setEnabled(True)
       self.dialogoMQ.comboBox_alg3.setEnabled(True)
       self.dialogoMQ.spinBox_q3.setEnabled(True)
       self.dialogoMQ.label_q3.setEnabled(True)
    
     if self.dialogoMQ.label_algCola4.isEnabled():
       self.dialogoMQ.label_algCola4.setEnabled(False)
       self.dialogoMQ.comboBox_alg4.setEnabled(False)
       self.dialogoMQ.spinBox_q4.setEnabled(False)
       self.dialogoMQ.label_q4.setEnabled(False)
     if self.dialogoMQ.label_algCola5.isEnabled():
       self.dialogoMQ.label_algCola5.setEnabled(False)
       self.dialogoMQ.comboBox_alg5.setEnabled(False)
       self.dialogoMQ.spinBox_q5.setEnabled(False)
       self.dialogoMQ.label_q5.setEnabled(False)

     
     print("HOLAAAA ENTRE")
     
     #self.dialogoMQ.label_algCola4 = self.dialogoMQ.label_algCola4.setEnabled(False)
     #self.dialogoMQ.comboBox_alg4 =self.dialogoMQ.comboBox_alg4.setEnabled(False)
     #self.dialogoMQ.label_q4 =self.dialogoMQ.label_q4.setEnabled(False)
     #self.dialogoMQ.spinBox_q4 = self.dialogoMQ.spinBox_q4.setEnabled(False)

     #self.dialogoMQ.label_algCola5 = self.dialogoMQ.label_algCola5.setEnabled(False)
     #self.dialogoMQ.comboBox_alg5 =self.dialogoMQ.comboBox_alg5.setEnabled(False)
     #self.dialogoMQ.label_q5 =self.dialogoMQ.label_q5.setEnabled(False)
     #self.dialogoMQ.spinBox_q5 = self.dialogoMQ.spinBox_q5.setEnabled(False)
   
   if self.dialogoMQ.spinBoxCantColas.value() == 4:
     if not self.dialogoMQ.label_algCola1.isEnabled() :
       self.dialogoMQ.label_algCola1.setEnabled(True)
       self.dialogoMQ.comboBox_alg1.setEnabled(True)
       self.dialogoMQ.spinBox_q1.setEnabled(True)
       self.dialogoMQ.label_q1.setEnabled(True)
  
     if not self.dialogoMQ.label_algCola2.isEnabled():
       self.dialogoMQ.label_algCola2.setEnabled(True)
       self.dialogoMQ.comboBox_alg2.setEnabled(True)
       self.dialogoMQ.spinBox_q2.setEnabled(True)
       self.dialogoMQ.label_q2.setEnabled(True)

     if not self.dialogoMQ.label_algCola3.isEnabled():
       self.dialogoMQ.label_algCola3.setEnabled(True)
       self.dialogoMQ.comboBox_alg3.setEnabled(True)
       self.dialogoMQ.spinBox_q3.setEnabled(True)
       self.dialogoMQ.label_q3.setEnabled(True)

     if not self.dialogoMQ.label_algCola4.isEnabled():
       self.dialogoMQ.label_algCola4.setEnabled(True)
       self.dialogoMQ.comboBox_alg4.setEnabled(True)
       self.dialogoMQ.spinBox_q4.setEnabled(True)
       self.dialogoMQ.label_q4.setEnabled(True)
     
     if self.dialogoMQ.label_algCola5.isEnabled():
       self.dialogoMQ.label_algCola5.setEnabled(False)
       self.dialogoMQ.comboBox_alg5.setEnabled(False)
       self.dialogoMQ.spinBox_q5.setEnabled(False)
       self.dialogoMQ.label_q5.setEnabled(False)
     print("hola")
     #self.dialogoMQ.label_algCola5 = self.dialogoMQ.label_algCola5.setEnabled(False)
     #self.dialogoMQ.comboBox_alg5 =self.dialogoMQ.comboBox_alg5.setEnabled(False)
     #self.dialogoMQ.label_q5 =self.dialogoMQ.label_q5.setEnabled(False)
     #self.dialogoMQ.spinBox_q5 = self.dialogoMQ.spinBox_q5.setEnabled(False)


   if self.dialogoMQ.spinBoxCantColas.value() ==5:
     if not self.dialogoMQ.label_algCola1.isEnabled() :
       self.dialogoMQ.label_algCola1.setEnabled(True)
       self.dialogoMQ.comboBox_alg1.setEnabled(True)
       self.dialogoMQ.spinBox_q1.setEnabled(True)
       self.dialogoMQ.label_q1.setEnabled(True)
  
     if not self.dialogoMQ.label_algCola2.isEnabled():
       self.dialogoMQ.label_algCola2.setEnabled(True)
       self.dialogoMQ.comboBox_alg2.setEnabled(True)
       self.dialogoMQ.spinBox_q2.setEnabled(True)
       self.dialogoMQ.label_q2.setEnabled(True)

     if not self.dialogoMQ.label_algCola3.isEnabled():
       self.dialogoMQ.label_algCola3.setEnabled(True)
       self.dialogoMQ.comboBox_alg3.setEnabled(True)
       self.dialogoMQ.spinBox_q3.setEnabled(True)
       self.dialogoMQ.label_q3.setEnabled(True)

     if not self.dialogoMQ.label_algCola4.isEnabled():
       self.dialogoMQ.label_algCola4.setEnabled(True)
       self.dialogoMQ.comboBox_alg4.setEnabled(True)
       self.dialogoMQ.spinBox_q4.setEnabled(True)
       self.dialogoMQ.label_q4.setEnabled(True)

     if not self.dialogoMQ.label_algCola5.isEnabled():
       self.dialogoMQ.label_algCola5.setEnabled(True)
       self.dialogoMQ.comboBox_alg5.setEnabled(True)
       self.dialogoMQ.spinBox_q5.setEnabled(True)
       self.dialogoMQ.label_q5.setEnabled(True)
     print("hola")

 def PRIORIDAD(self):
    print('PRIORIDAD')
    if len(self.colalisto)>0:
        self.colalisto.sort(key=lambda m: (m[2],m[5]))
        caux=self.colalisto[0].copy()
        caux[4]=1
        self.colalisto[0][4]=self.colalisto[0][4]-1
        if self.colalisto[0][4]==0:
            del self.colalisto[0]
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
        print('colalisto',self.colalisto)
        print('colagantt',self.colagantt)
 




 def RR(self):
    print('RR')
    print(self.colalisto)
    if len(self.colalisto)>0:
        caux=self.colalisto[0].copy()
        caux[4]=1
        self.colalisto[0][4]=self.colalisto[0][4]-1
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
        self.q=self.q-1
        if self.q==0:
            self.q=self.quantom
            if self.colalisto[0][4]==0:
                #Termina quantum y justo termina el proceso
                del self.colalisto[0]
            else:
                #termina quantum y se bloquea el proceso (Lo manda al final de la cola)
                aux=self.colalisto[0].copy()
                del self.colalisto[0]
                self.colalisto.append(aux.copy())
        else:
            if self.colalisto[0][4]==0:
                #No termina quantum y justo termina el proceso
                del self.colalisto[0]
                self.q=self.quantom
        print('colalisto',self.colalisto)
        print('colagantt',self.colagantt)
        print('q',self.q)



   
 def FCFS(self):
    print('FCFS')
    if len(self.colalisto)>0:
        caux=self.colalisto[0].copy()
        caux[4]=1
        self.colalisto[0][4]=self.colalisto[0][4]-1
        if self.colalisto[0][4]==0:
            del self.colalisto[0]
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
        print('mira como voy incrementando mi lista',self.colagantt)


 def metodo_fcfs(self):
   procesos= [[1,'aaa',0,25,20,2],
   [2,'bbb',0,130,20,1],
   [3,'ccc',3,65,60,0],
   [4,'ddd',1,47,7,7],
   [5,'eee',0,2,5,2]]  
   if self.MQ == False:
     self.procesoFCFS = procesos.copy()
   self.procesoFCFS.sort(key=lambda procesos: procesos[5])
   self.procesoparaprobar.extend(self.procesoFCFS.copy())
   print('\n\n\nFCFS\n\n\n',self.procesoparaprobar)
   #self.procesos_importados = procesos
   #global cont_sim_2davez
   #if cont_sim_2davez >1:
   

 def metodo_rr(self):
    print('RR')
    procesos= [[1,'aaa',0,25,20,2],
    [2,'bbb',0,130,20,1],
    [3,'ccc',3,65,60,0],
    [4,'ddd',1,47,7,7],
    [5,'eee',0,2,5,2]]  
    if self.MQ == False:
      self.procesoRR = procesos.copy()
    global cant_procesos
    cant_procesos= len(procesos)
    clock = 0
    processPerClock = []
    #quantom = input("plz input quantom: ")
    quantom = 2

    self.procesoRR.sort(key = lambda m: (m[5],m[4]))
    #print(procesos)
    i = 0
    while len(self.procesoRR) != 0:
        #flag = False
        #for i in range(len(procesos)):
        ti=self.procesoRR[i][4]
        b = True
        q= quantom
        if ti >= q:
          ti=ti-q
          aux=self.procesoRR[i].copy()
          if ti>0:
            self.procesoRR[i][4] = ti
            aux[4]=q
            i=i+1
          else:
            del self.procesoRR[i]
          q=0
          processPerClock.append(aux)
        else:
          q=q-ti
          processPerClock.append(self.procesoRR[i])
          del self.procesoRR[i]
        if i==len(self.procesoRR):
          i=0
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
    #procesos_rr = processPerClock
    #print(procesos_rr)
    self.procesoparaprobar.extend(processPerClock.copy())
    print("\n\n\n\n\n\n\nRR ",self.procesoparaprobar)

 def metodo_prioridades(self):
   print("Metodo prioridades")
   procesos= [[1,'aaa',0,25,20,2],
   [2,'bbb',0,130,20,1],
   [3,'ccc',3,65,60,0],
   [4,'ddd',1,47,7,7],
   [5,'eee',0,2,5,2]]  
   if self.MQ == False:
     self.procesoPRIORIDAD = procesos.copy()
   
   procesos_ta=self.procesoPRIORIDAD
   procesos_ta.sort(key=lambda procesos_ta: procesos_ta[5])
   tiempototal_cpu=0
   #Calculo el tiempo total de irrupción de todos los procesos juntos
   for i in range(len(self.procesoPRIORIDAD)):
       tiempototal_cpu=tiempototal_cpu+self.procesoPRIORIDAD[i][4]
   #Comienzo el algoritmo guardando resultados de cada instante de ejecución
   resultados=[]
   clock=0
   cola_listos=[]
   ant=1
   procesoresultado=[]
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
     #ejecutar=cola_listos[0][1]

     #para ver como se desenlaza el algoritmo y ver como va cambiando la cola de listos 
     #Voy descontando el tiempo restante de irrupción del proceso que 
     #mande a ejecutar
     print(cola_listos)
     
     if len(cola_listos) >0:
       cola_listos[0][4]=cola_listos[0][4]-1
       """
       ti_restante=cola_listos[0][4]
       #Agrego el dato de tiempo restante de irrupción 
       ejec_en_instante.append(ti_restante)
       resultados.append(ejec_en_instante)
       """
       if len(procesoresultado)>0 and ant==cola_listos[0][0]:
         procesoresultado[-1][4]=(procesoresultado[-1][4])+1
       else:
         procesoresultado.append([cola_listos[0][0],cola_listos[0][1],cola_listos[0][2],cola_listos[0][3],1,cola_listos[0][5]])       
       #Elimino de la cola de listos aquellos que ya completaron sus tiempos de irrupción
       ant=cola_listos[0][0]
       if cola_listos[0][4]==0:
         cola_listos.remove(cola_listos[0])  
     clock=clock+1
         #Agrego la fila completa con todos los datos cargados a los resultados
         #['idpc','Descripcion','Prioridad','Tamaño','TI','TA']
         
   self.procesoparaprobar.extend(procesoresultado.copy()) 
   print(self.procesoparaprobar)
 
 def metodo_mq(self):
   print("Metodo colas multiples")
   colas_multinivel = [[],[],[],[],[]]
   def ordenarSegunAlgoritmo(valor,procesos):
     if valor == 0:
       procesos.sort(key = lambda m: (m[5],m[4]))
     if valor == 1:
       procesos.sort(key = lambda m: m[5])
     if valor == 2:
       procesos.sort(key=lambda m: (m[5],m[2]))
     return (procesos)
   def buscarAlgoritmo(valor,procesos):
     self.MQ = True
     if valor==0:
       print("RR")
       #self.metodo_rr(procesos)
       self.procesoRR = procesos
       self.metodo_rr()
     if valor ==1:
       print("FCFS")
       self.procesoFCFS = procesos
       print("\n\n\n\n",self.procesoFCFS,"\n\n\n\n\n\n")
       self.metodo_fcfs()
     if valor ==2:
       print("prio")
       self.procesoPRIORIDAD = procesos
       self.metodo_prioridades()
    
   def RR_Gral():
     print('MQ')
     #global procesos
     #global colas_multinivel
     #global lista_algoritmos
     #global quantum_gral 
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
               copia=colas_multinivel[cont_cola][i].copy()
               #print( 'copia',copia)
               copia[4]=sumquantum
               caux.append(copia.copy())
               sumquantum=sumquantum-tinuevo
               print('sumquantum',sumquantum)
               i=i+1
           if sumquantum<=0:
             buscarAlgoritmo(listAlgoritmoInt[cont_cola],caux)
             b=False
           if i>= len(colas_multinivel[cont_cola]):
                    i=0
       if (cont_cola<4):
         cont_cola = cont_cola +1
       else:
         cont_cola =0
       if ((len(colas_multinivel[0])==0) and (len(colas_multinivel[1])==0) and (len(colas_multinivel[2])==0) and (len(colas_multinivel[3])==0) and (len(colas_multinivel[4])==0)):
         vacio = True
             
   lista_algoritmos = ['rr','fcfs','prioridades','','']
   #rr = 0
   #fcfs = 1
   #prioridades =2
   
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
     if lista_algoritmos[i]=='fcfs':
       listAlgoritmoInt.insert(i,1)
     if lista_algoritmos[i]=='prioridades':
       listAlgoritmoInt.insert(i,2)
   quantum_gral=10
   for i in procesos:
     if i[3] >limites_colas[0] and i[3] <=limites_colas[1] :
       colas_multinivel[0].append(i)
     if i[3] >limites_colas[1] and i[3] <=limites_colas[2] :
       colas_multinivel[1].append(i)
     if i[3] >limites_colas[2] and i[3] <=limites_colas[3] :
       colas_multinivel[2].append(i)
     if i[3] >limites_colas[3] and i[3] <=limites_colas[4] :
       colas_multinivel[3].append(i)
     if i[3] >limites_colas[4]:
       colas_multinivel[3].append(i)
   RR_Gral()



 def ejecutar_algoritmos(self):
   if self.comboBox_Algoritmos.currentText() == 'PRIORIDADES':
     self.PRIORIDAD()
   if self.comboBox_Algoritmos.currentText() == 'FCFS':
     self.FCFS()
   if self.comboBox_Algoritmos.currentText() == 'RR':
     self.RR()
   """if self.comboBox_Algoritmos.currentText() == 'COLAS MULTINIVEL':
     self.metodo_mq()"""

 """def ejecutar_algoritmos(self):
   global cont_sim_2davez
   
   print('que problema tenes?')
   self.clock=0
   print('otra vez soy clock',self.clock)
   if self.comboBox_Algoritmos.currentText() == 'PRIORIDADES':
     self.metodo_prioridades()
   if self.comboBox_Algoritmos.currentText() == 'FCFS':
     self.metodo_fcfs()
   if self.comboBox_Algoritmos.currentText() == 'RR':
     self.metodo_rr()
   if self.comboBox_Algoritmos.currentText() == 'COLAS MULTINIVEL':
     self.metodo_mq()"""

 def asignacion_memoria(self):
  for i in self.lista_graficos:
    i[2]='disponible'
    i[4]=0
    i[5]=0

  self.clock=0
  self.colagantt=[]
  if(self.radioButton_Fijas.isChecked()):
    self.asignacion_fija()
 
 def arribo(self):
    self.colanuevo.extend(self.colaarribo.copy())

 def asignacion_fija(self):
   
   def asignacionp():
       #mem
       self.lista_graficos
       #Especie de clock
       cont_tiempo=0
       i=0
       while i<len(self.colaarribo):
           j=0
           if self.met_asig=='FF':
               self.lista_graficos.sort(key = lambda m: (m[0]))
               #print('quiero ver que onda',self.lista_graficos)
           if self.met_asig=='BF':
               self.lista_graficos.sort(key=lambda m: m[3])
           while (j<len(self.lista_graficos)) and ((self.lista_graficos[j][3]<self.colaarribo[i][3]) or (self.lista_graficos[j][2]!='disponible')):
               j=j+1
           if j<len(self.lista_graficos): 
               if (self.lista_graficos[j][3])>=self.colaarribo[i][3] and (self.lista_graficos[j][2])=='disponible':
                   self.lista_graficos[j][4]=self.colaarribo[i][0] 
                   self.lista_graficos[j][5]=(self.lista_graficos[j][3])-self.colaarribo[i][3]
                   self.lista_graficos[j][2]='ocupado'
                   #sum=sum+1
                   self.colalisto.append(self.colaarribo[i].copy())
                   self.colaarribo.pop(i)
                   self.lista_graficos.sort(key=lambda m: m[0])
                   print('Tiempo=',cont_tiempo)
                   #tabla(mem) 
                   cont_tiempo=cont_tiempo+1
               else:
                   i=i+1
           else:
               i=i+1  
   procesos=[[1,'aaa',0,25,20,2],
   [2,'bbb',0,130,20,1],
   [3,'ccc',3,65,60,0],
   [4,'ddd',1,47,7,7],
   [5,'eee',0,2,5,2],
   [6,'fff',2,59,3,0],
   [7,'ggg',2,30,2,8],
   [8,'hhh',6,200,7,8]]
   print('ENTER ACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
   self.procesos_sin_asignar=self.listaprocesos.copy()
   self.procesos_sin_asignar.sort(key=lambda m: m[5])
   self.quantom = 2
   self.q=self.quantom
   j=0
   b=True
   #for i in range(9):
   while b:
     self.colaarribo=[]
     while j<len(self.procesos_sin_asignar) and self.procesos_sin_asignar[j][5]==self.clock:
       self.colaarribo.append(self.procesos_sin_asignar[j])
       j=j+1
     if len(self.colaarribo)>0:
       self.arribo()
     print('cola nuevo',self.colanuevo)
     asignacionp()
     print('particiones',self.lista_graficos)
     print('cola arribo',self.colaarribo)
     self.ejecutar_algoritmos()
     #self.FCFS()
     #self.RR()
     #self.PRIORIDAD()
     self.clock=self.clock+1
     if len(self.colalisto)==0:
       b=False

 def mostrarResultSimulacion(self):
   global cont_sim_2davez
   if cont_sim_2davez >=0:
    self.dialogresultsim.move(640,315)
    self.dialogresultsim.exec_()
    self.dialogresultsim.tableWidgetCListo.insertRow(0)
    self.dialogresultsim.tableWidgetCListo.setItem(0,0,QTableWidgetItem('1'))
    self.dialogresultsim.tableWidgetCListo.setItem(0,1,QTableWidgetItem('5'))
    self.dialogresultsim.tableWidgetCListo.insertRow(1)
    self.dialogresultsim.tableWidgetCListo.setItem(1,0,QTableWidgetItem('2'))
    self.dialogresultsim.tableWidgetCListo.setItem(1,1,QTableWidgetItem('10'))
    self.dialogresultsim.tableWidgetCListo.insertRow(2)
    self.dialogresultsim.tableWidgetCListo.setItem(2,0,QTableWidgetItem('3'))
    self.dialogresultsim.tableWidgetCListo.setItem(2,1,QTableWidgetItem('7'))
    cont_sim_2davez = 0
   

 def mostrarComparacion(self):
   self.dialogcompara.exec_()
   self.dialogcompara.tableWidgetTEspera.insertRow(0)
   self.dialogcompara.tableWidgetTEspera.setItem(0,0,QTableWidgetItem('0'))
   self.dialogcompara.tableWidgetTEspera.setItem(0,1,QTableWidgetItem('50'))
   self.dialogcompara.tableWidgetTEspera.setItem(0,2,QTableWidgetItem('30'))
   self.dialogcompara.tableWidgetTEspera.setItem(0,3,QTableWidgetItem('25'))
   self.dialogcompara.tableWidgetTEspera.setItem(0,4,QTableWidgetItem('45'))
   self.dialogcompara.tableWidgetTRetorno.insertRow(0)
   self.dialogcompara.tableWidgetTRetorno.setItem(0,0,QTableWidgetItem('0'))
   self.dialogcompara.tableWidgetTRetorno.setItem(0,1,QTableWidgetItem('70'))
   self.dialogcompara.tableWidgetTRetorno.setItem(0,2,QTableWidgetItem('50'))
   self.dialogcompara.tableWidgetTRetorno.setItem(0,3,QTableWidgetItem('65'))
   self.dialogcompara.tableWidgetTRetorno.setItem(0,4,QTableWidgetItem('45'))


 def update_tablaProcesos(self):
   def cambio_estado():
     print("cambie de estado")
   print(self.listaImportarProcesos)
   for i in self.listaImportarProcesos:
     print(self.result[i-1])
     #hago un item de tabla, al item de otra tabla
     nueva_idpc= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,0))
     nueva_desc= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,1))
     nueva_prio= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,2))
     nueva_tam= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,3))
     nueva_ti= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,4))
     nueva_ta= QTableWidgetItem(self.dialogoImportar.tableWidgetImportar.item(i-1,5))
     ultima_fila_tabla_procesos= self.dialogo.tableWidgetProcesos.rowCount()
     print("ultima fila",ultima_fila_tabla_procesos)
     self.dialogo.tableWidgetProcesos.insertRow(ultima_fila_tabla_procesos)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,0,nueva_idpc)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,1,nueva_desc)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,2,nueva_prio)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,3,nueva_tam)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,4,nueva_ti)
     self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,5,nueva_ta)
     #rint("item",item)
     """
     if item.checkState() == Qt.Checked:
       indice=item.row()
       print("entreeee")
       print("entre2")
       print(self.result[indice])
       elemento=self.result[indice]
       print("elemento",elemento)
       self.procesos_importados.append(elemento)
       print(self.procesos_importados)
       self.contador_act = self.contador_act +1
       print("valor del contador",self.contador_act)
   #ahi guarde las filas tildadas en una tabla
   #ahora las agrego a la tabla de gestion de procesos
   print("El contador act vale {}".format(self.contador_act))
   for i in range(self.contador_act):
    print("aaaaaaaaaaaaa",self.procesos_importados[i][0])
    print("aaaaaaaaa",self.procesos_importados[i][3])
    nuevo_idpc= QTableWidgetItem(self.procesos_importados[i][0])
    nueva_desc = QTableWidgetItem(self.procesos_importados[i][1])
    nueva_prio = QTableWidgetItem(self.procesos_importados[i][2])
    nuevo_tam =QTableWidgetItem(self.procesos_importados[i][3])
    nuevo_ti = QTableWidgetItem(self.procesos_importados[i][4])
    nuevo_ta = QTableWidgetItem(self.procesos_importados[i][5])
    ultima_fila_tabla_procesos= self.dialogo.tableWidgetProcesos.rowCount()
    self.dialogo.tableWidgetProcesos.insertRow(ultima_fila_tabla_procesos)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,0,nuevo_idpc)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,1,nueva_desc)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,2,nueva_prio)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,3,nuevo_tam)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,4,nuevo_ti)
    self.dialogo.tableWidgetProcesos.setItem(ultima_fila_tabla_procesos,5,nuevo_ta)
    print("Nuevo proceso actualizado en tabla")
    """
 def generar_grafico_durante_simulacion(self):
   print('entre al grafico')
   global cont_sim_2davez
   if cont_sim_2davez >=0:
    global conts
    fig= plt.figure('Mapa de memoria',figsize=(15,2))
    ax=fig.subplots()
    category_names=[]
    
    procesosejemplos=['P1','P2','P3','P4','P5','P6','P7','P8','P9','P10']
    ys=[]
    i=0
    for elemento in self.lista_graficos:
      print(elemento)
      if len(elemento)>1:
        category_names.append('Idpart: '+str(elemento[0])+'\nIdpc:    '+ str(elemento[4])+'\nFragInt:'+str(elemento[5]))
        ys.append(elemento[3])
        i=i+1       
    results={'mem':ys}
    print(results)
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(
    np.linspace(0.15, 0.45, data.shape[1]))
    #fig, ax = plt.subplots(figsize=(9.2, 5))
    ax.clear()
    ax.invert_yaxis()
    ax.xaxis.set_visible(True)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    print('llegue aqui')
    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
      widths = data[:, i]
      starts = data_cum[:, i] - widths
      ax.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)
      xcenters = starts + widths / 2
      r, g, b, _ = color
      text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
      for y, (x, c) in enumerate(zip(xcenters, widths)):
        ax.text(x, y, str(int(c)), ha='center', va='center', color=text_color)
    ax.legend(bbox_to_anchor=(1,1),loc='best')
    #ncol=len(category_names), bbox_to_anchor=(0,1),
    #          loc='lower left', fontsize='small')
    #ani=animation.FuncAnimation(fig,animate(), interval=3000,repeat=True)

    
    plt.show()

 def cargarTabla(self):
   if self.flagVerprocesos ==False:
     
    self.flagVerprocesos = True
    print("entre")
    try:
      connection = mysql.connector.connect(host=self.host,
      database = self.database,
      user=self.user,
      password=self.password)
      print("conecto")
      cur=connection.cursor()
      cur.execute("SELECT * FROM procesos")
      self.result=cur.fetchall()
      contador_rows_importar =0
      for i in self.result:
        
      
        idpc= QTableWidgetItem(str(i[0]))
        desc =QTableWidgetItem(str(i[1]))
        prioridad = QTableWidgetItem(str(i[2]))
        tam= QTableWidgetItem(str(i[3]))
        ti= QTableWidgetItem(str(i[4]))
        ta= QTableWidgetItem(str(i[5]))

        self.dialogoImportar.tableWidgetImportar.insertRow(contador_rows_importar)
        
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,0,idpc)
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,1,desc)
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,2,prioridad)
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,3,tam)
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,4,ti)
        self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,5,ta)
        



        contador_rows_importar = contador_rows_importar + 1
    except mysql.connector.Error as error:
      print("Fallo al conectarse {}",format(error))
    else:
      pass
    finally:
      if(connection.is_connected()):
        connection.close()
        print("Conexion cerrada")

 def mostrarTablaImportar(self):
   self.dialogoImportar.exec_()
   #print("por lo menos")
   #self.item= QTableWidgetItem()
   #self.item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
   #self.item.setCheckState(Qt.Unchecked) 
   #self.tableWidgetImportar.setItem(1,1,self.item)
   
 def agregar_fila_particiones(self):
   global cont_agregar_particion
   tampart= int(self.carga_particionFijas.lineEditTam.text())
   global rli
   global conts
   if ((self.valor_memoria_procesos - tampart>=0) and self.valor_memoria_procesos != 0):
     self.valor_memoria_procesos= self.valor_memoria_procesos - tampart
     self.carga_particionFijas.label_MemDisp.setText("Memoria Disponible: "+str(round(self.valor_memoria_procesos,2)) + " KB")
     self.carga_particionFijas.tableWidgetCargaParticion.insertRow(cont_agregar_particion)
     id_sim = QTableWidgetItem(str(conts))
     tam_part = QTableWidgetItem(str(self.carga_particionFijas.lineEditTam.text()))
     id_part=QTableWidgetItem(str(cont_agregar_particion+1))
     dir_rli=QTableWidgetItem(str(rli))
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,0,id_sim)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,3,tam_part)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,1,id_part)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,2,dir_rli)
     cont_agregar_particion+=1
     self.lista_graficos.append([cont_agregar_particion,rli,'disponible',tampart,0,0])
     rli=rli+tampart
     print(self.lista_graficos)
     self.carga_particionFijas.lineEditTam.setText('')
     
 def agregar_fila_rafagas(self):
   global contr
   #con este comando agrego una fila a la tabla
   self.dialogo.tableWidgetRafaga.insertRow(contr)
   #con este comando guardo lo que voy a meter en la tabla con una variable 
   tiempo = QTableWidgetItem(str(self.dialogo.lineEdit_Tiempo.text()))
   tipo = QTableWidgetItem(str(self.dialogo.comboBoxTipoRaf.currentText()))
   self.dialogo.tableWidgetRafaga.setItem(contr,0,tipo)
   self.dialogo.tableWidgetRafaga.setItem(contr,1,tiempo)
   self.dialogo.lineEdit_Tiempo.setText('')
   contr=contr+1

 def graficar(self):
   self.carga_particionFijas.hide()
   self.generar_grafico()
 
 def generar_grafico(self):
   global conts
   fig= plt.figure('Particiones',figsize=(9.2, 5))
   ax=fig.subplots()
   #graph_data= open('prueba.txt','r').read()
   #lines=graph_data.split('\n')
   category_names=[]
   ys=[]
   try:
     global conts
     connection = mysql.connector.connect(host=self.host,
     database = self.database,
     user=self.user,
     password=self.password)
     for elemento in self.lista_graficos:
       print(elemento)
       if len(elemento)>1:
         category_names.append(elemento[0])
         ys.append(elemento[3])
         print(conts, elemento[0], elemento[1], elemento[2], elemento[5],elemento[3])
         mySql_insert_query= """INSERT INTO part_fija (idsim, idpart, dir_rli, estado, frag_int, part_size)
         VALUES (%s,%s,%s,%s,%s,%s)""" 
         recordTuple=(conts, elemento[0], elemento[1], elemento[2], elemento[5],elemento[3])
         cursor= connection.cursor()
         result= cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
         connection.commit()
         print("Record se inserto bien ") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
         cursor.close()
   except mysql.connector.Error as error:
     print("Fallo al conectarse {}",format(error))
   else:
     pass
   finally:
     if(connection.is_connected()):
      connection.close()
      print("Conexion cerrada")      
   results={'mem':ys}
   print(results)
   labels = list(results.keys())
   data = np.array(list(results.values()))
   data_cum = data.cumsum(axis=1)
   category_colors = plt.get_cmap('RdYlGn')(
   np.linspace(0.15, 0.85, data.shape[1]))
   #fig, ax = plt.subplots(figsize=(9.2, 5))
   ax.clear()
   ax.invert_yaxis()
   ax.xaxis.set_visible(True)
   ax.set_xlim(0, np.sum(data, axis=1).max())
   print('llegue aqui')
   for i, (colname, color) in enumerate(zip(category_names, category_colors)):
    widths = data[:, i]
    starts = data_cum[:, i] - widths
    ax.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)
    xcenters = starts + widths / 2
    r, g, b, _ = color
    text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
    for y, (x, c) in enumerate(zip(xcenters, widths)):
     ax.text(x, y, str(int(c)), ha='center', va='center', color=text_color)
   ax.legend(bbox_to_anchor=(1,1))
   #ncol=len(category_names), bbox_to_anchor=(0,1),
   #          loc='lower left', fontsize='small')
   #ani=animation.FuncAnimation(fig,animate(), interval=3000,repeat=True)
   plt.show()

 
 def AlmacenarTamMemIngresado(self):
   self.carga_particionFijas.label_MemDisp.setText('Memoria disponible: '+str(round(self.valor_memoria_procesos,2)) + " KB")
   #Carga o actualiza en BD el tamaño memoria y porcentaje so ingresado
   try:
     global conts
     connection = mysql.connector.connect(host=self.host,
     database = self.database,
     user=self.user,
     password=self.password)
        
     if conts==0:
       conts=conts+1
       print (conts)
     
     #Verifica si la tabla simu esta vacia o no 
     cursor= connection.cursor()
     cursor.execute("select idsim from simu ORDER BY idsim DESC LIMIT 1") # aca le paso la tupla, para que remplaze por los %s en la consulta
     codsim=cursor.fetchall()
     lens=len(codsim)
     print("select exitoso") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
     if lens==0:
       #La tabla esta vacia x lo tanto hace un insert con idsim 1
       conts=1
       mySql_insert_query= """INSERT INTO simu(idsim,mem_size,so_porcent,fecha)
       VALUES (%s,%s,%s,%s)""" #este seria el script para MySQL, para meter una fila a la tabla procesos
       #no incluyo el campo de id(que es clave) porque lo declare como auto incremental en la tabla, aumenta solo
       #en (%s,%s,%s,%s) se ponen luego los valores que estan acontinuacion, en recordTuple
       recordTuple=(conts,self.tam_Memoria,self.por_so,date.today())
       cursor= connection.cursor()
       result = cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
       connection.commit()
       print("Record se inserto bien ") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
       cursor.close()
     else:
       #La tabla no esta vacia x lo tanto guarda el idsim de la ultima carga
       codsim=codsim[0][0]
       print (codsim)
       if codsim == conts:
         #La ultima carga es de la simulacion actual por lo tanto se actualiza los datos
         mySql_update_query="""update simu set mem_size=(%s),so_porcent=(%s) where idsim = (%s)"""
         cursor= connection.cursor()
         recordTuple=(self.tam_Memoria,self.por_so,conts)
         cursor.execute(mySql_update_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
         connection.commit()
         print("actualizado") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
         cursor.close()
       else:
         #La ultima carga no es la simulacion actual x lo tanto se carga uno nuevo
         mySql_insert_query= """INSERT INTO simu(idsim,mem_size,so_porcent,fecha)
         VALUES (%s,%s,%s,%s)""" #este seria el script para MySQL, para meter una fila a la tabla procesos
         #no incluyo el campo de id(que es clave) porque lo declare como auto incremental en la tabla, aumenta solo
         #en (%s,%s,%s,%s) se ponen luego los valores que estan acontinuacion, en recordTuple
         c=conts
         print(c)
         recordTuple=(c,self.tam_Memoria,self.por_so,date.today())
         cursor= connection.cursor()
         result = cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
         connection.commit()
         print("Record se inserto bien ") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
         cursor.close()
   except mysql.connector.Error as error:
     print("Fallo al conectarse {}",format(error))
   else:
     pass
   finally:
     if(connection.is_connected()):
      connection.close()
      print("Conexion cerrada")
   #aaaaa
   if(self.radioButton_Fijas.isChecked()):
     self.carga_particionFijas.exec_()

 def variableselected(self):
   self.radioButton_Worst.setEnabled(True)
   self.radioButton_Best.setEnabled(False)
   #nota: el set enable anda con los line Edit
 
 def fijaselected(self):
   #hace un disable del radio button de worst fit
   self.radioButton_Worst.setEnabled(False)
   self.radioButton_Best.setEnabled(True)

 def firstselected(self):
   self.met_asig='FF'
 
 def bestselected(self):
   self.met_asig='BF'

 def worstselected(self):
   self.met_asig='WF'


 def updateLabels(self):
   if self.por_so >0:
    self.valor_so = ((self.tam_Memoria)*(self.por_so))/100
    self.valor_memoria_procesos = self.tam_Memoria-self.valor_so
    self.label_MemProcesos.setText(''+str(round(self.valor_memoria_procesos,2)) + " KB")
    self.label_MemSO.setText(''+str(self.valor_so) + " KB") 

 def actTamMemoria(self):
   self.tam_Memoria = self.spinBoxTamMemoria.value()
   print(self.tam_Memoria)

 def actPorcSO(self):
   self.por_so=self.spinBoxPorcSO.value()
   print(self.por_so)

 def cargarProcesosYRafagasenBD(self):
   def limpiar_carga_rafagas():
     global contr
     contr = 0
     self.dialogo.tableWidgetRafaga.setRowCount(0)
     self.dialogo.lineEdit_Tiempo.setText(" ")
     self.dialogo.lineEditDescrip.setText(" ")
     self.dialogo.spinBoxPriori.setValue(0)
     self.dialogo.spinBoxTamProc.setValue(0)
     self.dialogo.spinBoxTiempoarr.setValue(0)
   
   
   try:
     connection = mysql.connector.connect(host=self.host,
     database = self.database,
     user=self.user,
     password=self.password)

     #guardo en variables los datos del formulario, para despues ponerlos en el INSERT
     descripcion = self.dialogo.lineEditDescrip.text() #cada uno de estos comandos .text() obtiene el texto que fui poniendo en cada linea del formulario
     t_arribo = int(self.dialogo.spinBoxTiempoarr.text()) #hago un casting a int, pq en la bd los declaro como INT
     p_priori = int(self.dialogo.spinBoxPriori.text()) #hago un casting a int, pq en la bd los declaro como INT
     #rafaga_cpu_es = int(self.dialogo.lineRafaga.text())
     tam_pro = int(self.dialogo.spinBoxTamProc.text())
     
     mySql_insert_query= """INSERT INTO procesos(descripcion,priori,pc_size,ta)
     VALUES
     (%s,%s,%s,%s)""" #este seria el script para MySQL, para meter una fila a la tabla procesos
     #no incluyo el campo de id(que es clave) porque lo declare como auto incremental en la tabla, aumenta solo
     #en (%s,%s,%s,%s) se ponen luego los valores que estan acontinuacion, en recordTuple
     recordTuple=(descripcion,p_priori,tam_pro,t_arribo)
     cursor= connection.cursor()
     result = cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
     connection.commit()
     print("Record se inserto bien ") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
     #obtencion de idpc del ultimo proceso cargado
     cursor= connection.cursor()
     codpc = cursor.execute("select idpc from procesos ORDER BY idpc DESC LIMIT 1") # aca le paso la tupla, para que remplaze por los %s en la consulta
     codpc=cursor.fetchall()
     codpc=codpc[0][0]
     print("select exitoso") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
     #carga de rafagas de un proceso
     sumti=0
     for i in range(self.dialogo.tableWidgetRafaga.rowCount()):
         sumti=sumti+int(self.dialogo.tableWidgetRafaga.item(i,1).text())
         mySql_insert_query= """INSERT INTO rafagas(idraf,idpc,raf_type,ti)
         VALUES
         (%s,%s,%s,%s)"""
         recordTuple=(i+1,codpc,str(self.dialogo.tableWidgetRafaga.item(i,0).text()),int(self.dialogo.tableWidgetRafaga.item(i,1).text()))
         cursor= connection.cursor()
         result = cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
         connection.commit()
         print("Record se inserto bien ") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
         cursor.close() 
     #actualizar valor de ti del proceso actual
     mySql_update_query="""update procesos set ti=(%s) where idpc = (%s)"""
     cursor= connection.cursor()
     recordTuple=(sumti,codpc)
     cursor.execute(mySql_update_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
     connection.commit()
     print("ti actualizado") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
     #mostrar en la tabla el proceso cargado
     global contpc
     self.listaprocesos.append([codpc,descripcion,p_priori,tam_pro,sumti,t_arribo])
     id_pc = QTableWidgetItem(str(codpc))
     desc = QTableWidgetItem(descripcion)
     prio= QTableWidgetItem(str(p_priori))
     tampc = QTableWidgetItem(str(tam_pro))
     ti = QTableWidgetItem(str(sumti))
     ta = QTableWidgetItem(str(t_arribo))
     self.dialogo.tableWidgetProcesos.insertRow(contpc)
     self.dialogo.tableWidgetProcesos.setItem(contpc,0,id_pc)
     self.dialogo.tableWidgetProcesos.setItem(contpc,1,desc)
     self.dialogo.tableWidgetProcesos.setItem(contpc,2,prio)
     self.dialogo.tableWidgetProcesos.setItem(contpc,3,tampc)
     self.dialogo.tableWidgetProcesos.setItem(contpc,4,ti)
     self.dialogo.tableWidgetProcesos.setItem(contpc,5,ta)
     contpc=contpc+1
   except mysql.connector.Error as error:
     print("Fallo al conectarse {}",format(error))
   else:
     pass
   finally:
     if(connection.is_connected()):
      connection.close()
      print("Conexion cerrada")

   limpiar_carga_rafagas()
   #aca limpio los valores que quedaron antes de cargar 
   

 def abrirDialogoCarga(self): #bueno, sentiende por el nombre lo que hace el metodo supongo, ejecuta la nueva ventana o dialogo de carga
   self.dialogo.exec_()
   self.dialogo.lineEditDescrip.setText('')
   #self.dialogo.spinBoxTiempoarr.setText('')
   self.dialogo.spinBoxTamProc.setText('')
   self.dialogo.spinBoxPriori.setText('')
   while (self.dialogo.tableWidgetRafaga.rowCount()>0):
    self.dialogo.tableWidgetRafaga.removeRow(0)
  
 def gantt(self):
  global cont_sim_2davez
  print ('cuantas veces entre aca?')
  cont_sim_2davez= cont_sim_2davez + 1
  if cont_sim_2davez >=0:
    global procesos
    #aca armo el diagrama de gantt
    #es un ej nomas, con fechas y demas
    #tabla= QTableWidget()
    #tabla.setColumnCount(2)
    #tabla.setHorizontalHeaderLabels(['hola','jajaja'])
    #print('\n\n\nLA LISTA DE PROCESOS GANTT ES :\n\n\n\n',procesos_gantt)


    ##==========================PARA FCFS========================
    procesos_gantt = []
    sumati =0
    print('MIRA ACA',self.colagantt)
    for x in self.colagantt:
      print('x',x)
      sumati = sumati + x[4]
      print('sumati',sumati)
      procesos_gantt.append([x[0],x[4],sumati])
    df = []
    for x in procesos_gantt:
      res= 'Proceso '+str(x[0])
      df.append(dict(Task="CPU", Start=x[2]-x[1], Finish = x[2],Resource=res))
    df.append(dict(Task="ES",Start=3,Finish =7, Resource="Proceso 1"))
    print("LISTA DE GANTT",procesos_gantt)
    #igual no puedo ver la interfaz xd  
    # ves cmd?
    #nop, banca ahi si  
    #sigue siendo error de otro lado
    ##======================================================================
    
    """
    ##===========================PARA RR==============================
    procesos_gantt = []
    lista_procesos= []
    for i in range(cant_procesos):
      lista_procesos.append([])
    sumata=0
    for x in procesos_rr:
      lista_procesos[x[1]-1].append([x[0]-1,x[0]])
      #procesos_gantt.append([x[1],x[0]-1,x[0]])
    #df = []



    print('\n\nTIEMPOS DEL PROCESO 1\n\n',lista_procesos[0])
    print('\n\nTIEMPOS DEL PROCESO 2\n\n',lista_procesos[1])
    print('\n\nTIEMPOS DEL PROCESO 3\n\n',lista_procesos[2])
    print('\n\nTIEMPOS DEL PROCESO 4\n\n',lista_procesos[3])
    print('\n\nTIEMPOS DEL PROCESO 5\n\n',lista_procesos[4])

    df = []
    nro_proceso = 1
    for z in lista_procesos:
      res = "Proceso "+str(nro_proceso)
      for x in z:
        df.append(dict(Task = "CPU", Start = x[0], Finish = x[1], Resource= res))
      nro_proceso = nro_proceso +1
    """
    # ==============================================================================
    """
    
    
    df = [dict(Task="CPU", Start='0', Finish=procesos_gantt[0][2],Resource='Proceso1'),
    dict(Task="CPU", Start=procesos_gantt[0][2], Finish=procesos_gantt[1][2],Resource='Proceso2'),
    #dict(Task='CPU',Start='3',Finish='6',Resource='Proceso3'),
    dict(Task="CPU", Start=procesos_gantt[1][2], Finish=procesos_gantt[2][2],Resource='Proceso3'),
    dict(Task="CPU", Start=procesos_gantt[2][2], Finish=procesos_gantt[3][2],Resource='Proceso4'),
    #dict(Task="ES", Start='6', Finish='9',Resource='Proceso3'),
    dict(Task="CPU", Start=procesos_gantt[3][2], Finish=procesos_gantt[4][2],Resource='Proceso5'),
    dict(Task="CPU", Start=procesos_gantt[4][2], Finish=procesos_gantt[5][2],Resource='Proceso6'),]
    """

    fig = ff.create_gantt(df,index_col='Resource',show_colorbar=True,group_tasks=True,width=1200,height=400)
    #estas dos lineas son para que pueda poner numeros en lugar de fechas
    fig.layout.xaxis.rangeselector = None
    fig.layout.xaxis.type = 'linear'
    #con el auto_open = False hago que no se me abra automaticamente una ventana del navegador
    plotly.offline.plot(fig, filename='diagrama_gantt.html',auto_open=False)
    #guardo el diagrama en la carpeta donde esta este archivo .pyw, en un formato .html
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "diagrama_gantt.html")) #obtengo la direccion abosuluta del archivo
    local_url = QUrl.fromLocalFile(file_path)
    
    self.web = QWebEngineView() #aca hago una instancia de QWebEngineView, que es necesario para que se pueda mostrar el diagrama en una ventana
    self.web.tabla= QTableWidget()
    self.web.tabla.setColumnCount(2)
    self.web.tabla.setHorizontalHeaderLabels(["HOla","jaja"])
    self.web.tabla.setRowCount(50)

    self.web.load(local_url) #cargo la url, que seria la ruta del archivo generado .html
    self.web.setWindowTitle("Diagrama de Gantt")
    self.web.resize(900,400) #defino nombre y tamaño de la ventana
    self.web.move(0,500)
    self.web.show() #muestro la ventana
    
    
  
#estas 4 lineas son para que se ejecute la ventana al inciar o ejecutar este archivo .pyw
contr = 0
conts = 0
contpc= 0
cont_sim_2davez = 0
cont_agregar_particion=0
rli=0
procesos = []
app = QApplication(sys.argv) 
ventana = Ventana()
ventana.show()
app.exec_()


