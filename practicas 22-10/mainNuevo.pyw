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
  #aca(en self.cargarProcesosYRafagasenBD), y cuando apreto el boton de importar tambien, habilito el boton de aceptar ALgoritmo
  self.AceptarMem.clicked.connect(self.AlmacenarTamMemIngresado)
  self.AceptarMem.clicked.connect(self.checkVariableSelected)
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
  self.listaIDprocesos=[]
  self.listaIDprocesosventImportar=[]
  self.lista_algoritmos=['','','','','']
  self.colaquantum=[0,0,0,0,0]


  #ACA DESHABILITO TODOS LOS CAMPOS DEL MAIN, Y LOS VOY HABILITANDO A MEDIDA QUE SE CUMPLEN LOS PASOS
  self.spinBoxPorcSO.setEnabled(False)
  self.radioButton_Fijas.setEnabled(False)
  self.radioButton_Variables.setEnabled(False)
  self.radioButton_First.setEnabled(False)
  self.radioButton_Best.setEnabled(False)
  self.radioButton_Worst.setEnabled(False)
  self.AceptarMem.setEnabled(False)
  self.boton_GestProcesos.setEnabled(False)
  self.comboBox_Algoritmos.setEnabled(False)
  self.label_Algoritmo.setEnabled(False)
  self.spinBox_Quantum.setEnabled(False)
  self.label_Quantum.setEnabled(False)
  self.pushButton_AceptarProc.setEnabled(False)
  self.pushButtonComparar.setEnabled(False)
  self.pushButton_Simular.setEnabled(False)
  #TAMBIEN DESHABILITO LOS QUANTUM DE LA VENTANA MQ, Y LOS ACTIVO SOLO CUANDO SELECCIONO RR
  self.dialogoMQ.spinBox_q1.setEnabled(False)
  self.dialogoMQ.label_q1.setEnabled(False)
  self.dialogoMQ.spinBox_q2.setEnabled(False)
  self.dialogoMQ.label_q2.setEnabled(False)
  self.dialogoMQ.spinBox_q3.setEnabled(False)
  self.dialogoMQ.label_q3.setEnabled(False)
  self.dialogoMQ.spinBox_q4.setEnabled(False)
  self.dialogoMQ.label_q4.setEnabled(False)
  self.dialogoMQ.spinBox_q5.setEnabled(False)
  self.dialogoMQ.label_q5.setEnabled(False)
  
  #DESABILITO EL CARGAR DE LA VENTANA DE PROCESOS
  #self.dialogo.pushButtonCargar.setEnabled(False)

  #ZONA DE FLAGS DE CONTROL DE INTERFAZ
  self.flagporcSO=False
  self.flagParticionesCargadas= False
  self.flagProcesosCargados = False


  self.dialogo.radioButtonES.setEnabled(False)



  self.clock=0
  #obtener desde interfaz
  #LISTA ALGORITMOS DE MQ ['rr', 'rr', '', '', '']
  #LISTA DE QUANTUM DE ALGORITMOS MQ [3, 2, 0, 0, 0]
  self.cant_cola=0
  #obtener desde interfaz
  #self.lista_algoritmos = ['rr','fcfs','prioridades','rr','fcfs']
  self.listAlgoritmoInt=[]
  self.colas_multinivel = [[],[],[],[],[]]
  self.mem_variable=[]
  self.Mq = False
  self.q=0
  self.quantom=0
  self.idpart=0
  self.listaprocesos= []
  self.rafagas={}
  self.listaImportarProcesos=[]
  self.colabloqueado=[]
  self.colaesgantt=[]
  self.label_MemProcesos.setText('0 KB')
  self.label_MemSO.setText('0 KB')
  self.spinBoxTamMemoria.setMaximum(1000000)
  self.spinBoxTamMemoria.setSingleStep(2**2)
  self.spinBoxPorcSO.setMaximum(90)
  self.spinBoxPorcSO.setSingleStep(5)
  self.flagVerprocesos = False
  self.spinBoxTamMemoria.valueChanged.connect(self.actTamMemoria)
  self.comboBox_Algoritmos.currentIndexChanged.connect(self.checkcampoq)
  #self.spinBoxTamMemoria.valueChanged.connect(self.updateLabels)
  self.spinBoxPorcSO.valueChanged.connect(self.actPorcSO)
  self.spinBoxPorcSO.valueChanged.connect(self.checkflagporcSO)
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
  #aca (agregar_fila_rafagas) hago el control de el orden de las rafagas)
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
  
  








  
  #self.pushButton_Simular.clicked.connect(self.ejecutar_algoritmos) 
  #llama a metodo fcfs cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_fcfs)
  #llama a metodo prioridad cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_prioridades)
  #llama a metodo rr cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_rr)
  #llama a metodo mq cuando se apreta el boton de simular
  #self.pushButton_Simular.clicked.connect(self.metodo_mq)
  self.pushButton_Simular.clicked.connect(self.mapa_de_memoria)
  self.pushButton_Simular.clicked.connect(self.mostrarResultSimulacion)
  

  
  self.pushButtonComparar.clicked.connect(self.mostrarComparacion)
  self.pushButton_AceptarProc.clicked.connect(self.aceptar_algoritmo_presionado)
  self.dialogo.pushButtonImportar.clicked.connect(self.mostrarTablaImportar)
  self.dialogoImportar.tableWidgetImportar.setColumnCount(7)
  self.dialogoImportar.tableWidgetImportar.setHorizontalHeaderLabels(['idpc','Descripcion','Prioridad','Tamaño','TI','TA'])
  self.dialogcompara.tableWidgetTEspera.setColumnCount(5)
  self.dialogcompara.tableWidgetTEspera.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','C.Multinivel'])
  self.dialogcompara.tableWidgetTRetorno.setColumnCount(5)
  self.dialogcompara.tableWidgetTRetorno.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','C.Multinivel'])
  
  self.dialogresultsim.tableWidgetCListo.setColumnCount(2)
  self.dialogresultsim.tableWidgetCListo.setHorizontalHeaderLabels(['idpc','Ti',])

  self.dialogoImportar.pushButtonImportar.clicked.connect(self.update_tablaProcesos)
  #dentro de este self(update_tablaProcesos) tambien habilito el boton de aceptar algoritmo
  self.dialogoImportar.pushButtonVertabla.clicked.connect(self.cargarTabla)
  self.dialogoMQ.spinBoxCantColas.valueChanged.connect(self.actualizarMQ)
  self.dialogoMQ.comboBox_alg1.currentIndexChanged.connect(self.checkQcola1)
  self.dialogoMQ.comboBox_alg2.currentIndexChanged.connect(self.checkQcola2)
  self.dialogoMQ.comboBox_alg3.currentIndexChanged.connect(self.checkQcola3)
  self.dialogoMQ.comboBox_alg4.currentIndexChanged.connect(self.checkQcola4)
  self.dialogoMQ.comboBox_alg5.currentIndexChanged.connect(self.checkQcola5)
  #self.dialogo.comboBoxTipoRaf.currentIndexChanged.connect(self.checkRaf)
  self.last_raf_item=2
  #0 es CPU, 1 es ES, 2 es DEFAULT
  #self.dialogo.comboBoxTipoRaf.currentIndexChanged
  self.dialogoMQ.pushButton_cancelar.clicked.connect(self.closeMQ)
  self.dialogoMQ.pushButton_aceptar.clicked.connect(self.loadAlgoritmosMQ)
  #----------------------------------------------------------------
  #pongo todo en disabled las opciones de cola de la ventana de MQ
  self.inicializarOpcMQ()

  #DATOS BD
  self.host='localhost'
  self.database='simulador'
  self.user='c1g1'
  self.password='1234'
  
  #considero que el calculo de los labels de tam de memoria para procesos y so, se hace recien cuando le 
  #di algun valor al spinbox de so, sino estaria dividiendo por el valor 0
 
 def checkcampoq(self):
   if not self.comboBox_Algoritmos.currentText()=='RR':
     if self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(False)
   else:
     if not self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(True)

 def loadAlgoritmosMQ(self):
   if self.dialogoMQ.comboBox_alg1.isEnabled():
     self.lista_algoritmos[0]=(self.dialogoMQ.comboBox_alg1.currentText()).lower()
   if self.dialogoMQ.spinBox_q1.isEnabled():
     self.colaquantum[0]=self.dialogoMQ.spinBox_q1.value()

   if self.dialogoMQ.comboBox_alg2.isEnabled():
     self.lista_algoritmos[1]=(self.dialogoMQ.comboBox_alg2.currentText()).lower()
   if self.dialogoMQ.spinBox_q2.isEnabled():
     self.colaquantum[1]=self.dialogoMQ.spinBox_q2.value()

   if self.dialogoMQ.comboBox_alg3.isEnabled():
     self.lista_algoritmos[2]=(self.dialogoMQ.comboBox_alg3.currentText()).lower()
   if self.dialogoMQ.spinBox_q3.isEnabled():
     self.colaquantum[2]=self.dialogoMQ.spinBox_q3.value()

   if self.dialogoMQ.comboBox_alg4.isEnabled():
     self.lista_algoritmos[3]=(self.dialogoMQ.comboBox_alg4.currentText()).lower()
   if self.dialogoMQ.spinBox_q4.isEnabled():
     self.colaquantum[3]=self.dialogoMQ.spinBox_q4.value()

   if self.dialogoMQ.comboBox_alg5.isEnabled():
     self.lista_algoritmos[4]=(self.dialogoMQ.comboBox_alg5.currentText()).lower()
   if self.dialogoMQ.spinBox_q5.isEnabled():
     self.colaquantum[4]=self.dialogoMQ.spinBox_q5.value()
     
   self.cant_cola=self.dialogoMQ.spinBoxCantColas.value()
   print("LISTA ALGORITMOS DE MQ",self.lista_algoritmos)
   print("LISTA DE QUANTUM DE ALGORITMOS MQ",self.colaquantum)

 def closeMQ(self):
   print("cerrando la ventana MQ")
   self.dialogoMQ.close()

 def checkQcola1(self):
   if not self.dialogoMQ.comboBox_alg1.currentText()=='RR':
     if self.dialogoMQ.spinBox_q1.isEnabled():
       self.dialogoMQ.spinBox_q1.setEnabled(False)
       self.dialogoMQ.label_q1.setEnabled(False)
   else:
     if not self.dialogoMQ.spinBox_q1.isEnabled():
       self.dialogoMQ.spinBox_q1.setEnabled(True)
       self.dialogoMQ.label_q1.setEnabled(True)

 def checkQcola2(self):
   if not self.dialogoMQ.comboBox_alg2.currentText()=='RR':
     if self.dialogoMQ.spinBox_q2.isEnabled():
       self.dialogoMQ.spinBox_q2.setEnabled(False)
       self.dialogoMQ.label_q2.setEnabled(False)
   else:
     if not self.dialogoMQ.spinBox_q2.isEnabled():
       self.dialogoMQ.spinBox_q2.setEnabled(True)
       self.dialogoMQ.label_q2.setEnabled(True)

 def checkQcola3(self):
   if not self.dialogoMQ.comboBox_alg3.currentText()=='RR':
     if self.dialogoMQ.spinBox_q3.isEnabled():
       self.dialogoMQ.spinBox_q3.setEnabled(False)
       self.dialogoMQ.label_q3.setEnabled(False)
   else:
     if not self.dialogoMQ.spinBox_q3.isEnabled():
       self.dialogoMQ.spinBox_q3.setEnabled(True)
       self.dialogoMQ.label_q3.setEnabled(True)

 def checkQcola4(self):
   if not self.dialogoMQ.comboBox_alg4.currentText()=='RR':
     if self.dialogoMQ.spinBox_q4.isEnabled():
       self.dialogoMQ.spinBox_q4.setEnabled(False)
       self.dialogoMQ.label_q4.setEnabled(False)
   else:
     if not self.dialogoMQ.spinBox_q4.isEnabled():
       self.dialogoMQ.spinBox_q4.setEnabled(True)
       self.dialogoMQ.label_q4.setEnabled(True)

 def checkQcola5(self):
   if not self.dialogoMQ.comboBox_alg5.currentText()=='RR':
     if self.dialogoMQ.spinBox_q5.isEnabled():
       self.dialogoMQ.spinBox_q5.setEnabled(False)
       self.dialogoMQ.label_q5.setEnabled(False)
   else:
     if not self.dialogoMQ.spinBox_q5.isEnabled():
       self.dialogoMQ.spinBox_q5.setEnabled(True)
       self.dialogoMQ.label_q5.setEnabled(True)
     
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
     
 def checkVariableSelected(self):
   if self.radioButton_Variables.isChecked():
     if not self.boton_GestProcesos.isEnabled():
       self.boton_GestProcesos.setEnabled(True)

 def checkflagporcSO(self):
   if self.flagporcSO and self.spinBoxTamMemoria.value()>0 and self.spinBoxPorcSO.value()>0:
     self.radioButton_Fijas.setEnabled(True)
     self.radioButton_Variables.setEnabled(True)
   else:
     self.radioButton_Fijas.setEnabled(False)
     self.radioButton_Variables.setEnabled(False)
  
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
        rafita=self.rafagas[str(self.colalisto[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        self.rafagas.update({str(self.colalisto[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colabloqueado.append(self.colalisto[0].copy())
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]

        """
        if self.colalisto[0][4]==0:
          del self.colalisto[0]
        """

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

        rafita=self.rafagas[str(self.colalisto[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        self.rafagas.update({str(self.colalisto[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        

        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
        self.q=self.q-1
        if self.q==0:
            self.q=self.quantom

            if rafita[0][3]==0:
              #Termina quantum y justo termina la rafaga
              if len(rafita)>1:
                #termina quantum y se bloquea el proceso (Lo manda al cola del bloqueado)
                self.colabloqueado.append(self.colalisto[0].copy())
              del rafita[0]
              self.rafagas.update({str(self.colalisto[0][0]):rafita})
              del self.colalisto[0]
            """
            if self.colalisto[0][4]==0:
                #Termina quantum y justo termina el proceso
                del self.colalisto[0]
               
            else:
                #termina quantum y se bloquea el proceso (Lo manda al final de la cola)
                aux=self.colalisto[0].copy()
                del self.colalisto[0]
                self.colalisto.append(aux.copy())"""
        else:
            #No termina quantum y justo termina la rafaga
            if rafita[0][3]==0:
              #Termina la rafaga
              if len(rafita)>1:
                #termina la rafaga pero no el proceso: se bloquea el proceso (Lo manda al cola del bloqueado)
                self.colabloqueado.append(self.colalisto[0].copy())
              del rafita[0]
              self.rafagas.update({str(self.colalisto[0][0]):rafita})
              del self.colalisto[0]
              self.q=self.quantom
            """              
            if self.colalisto[0][4]==0:
              #No termina quantum y justo termina el proceso
              del self.colalisto[0]"""
              
        print('colalisto',self.colalisto)
        print('colagantt',self.colagantt)
        print('q',self.q)
        
 def SRTF(self):
    print('SRTF')
    if len(self.colalisto)>0:
        self.colalisto.sort(key=lambda m: (m[4],m[5]))
        caux=self.colalisto[0].copy()
        caux[4]=1
        self.colalisto[0][4]=self.colalisto[0][4]-1
        rafita=self.rafagas[str(self.colalisto[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        self.rafagas.update({str(self.colalisto[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colabloqueado.append(self.colalisto[0].copy())
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]
        """if self.colalisto[0][4]==0:
            del self.colalisto[0]"""
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
   
 def FCFS(self):
    print('FCFS')
    if len(self.colalisto)>0:
        caux=self.colalisto[0].copy()
        caux[4]=1
        self.colalisto[0][4]=self.colalisto[0][4]-1
        rafita=self.rafagas[str(self.colalisto[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        self.rafagas.update({str(self.colalisto[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colabloqueado.append(self.colalisto[0].copy())
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]
        """if self.colalisto[0][4]==0:
            del self.colalisto[0]"""
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0]:
            self.colagantt[-1][4]=self.colagantt[-1][4]+1
        else:
            self.colagantt.append(caux.copy())
        print('mira como voy incrementando mi lista',self.colagantt)

 def limites(self):
   if self.cant_cola==2:
     self.limites_colas=[[0,49],[50,99],[999,999],[999,999],[999,999]]
   if self.cant_cola==3:
     self.limites_colas=[[0,32],[33,65],[66,99],[999,999],[999,999]]
   if self.cant_cola==4:
     self.limites_colas=[[0,24],[25,49],[50,74],[75,99],[999,999]]
   if self.cant_cola==5:
     self.limites_colas=[[0,19],[20,39],[40,59],[60,79],[80,99]]

 def MQ(self):
   def buscarAlgoritmo(valor,procesos):
        self.colalisto=procesos
        print("cola listo",self.colalisto)
        if valor==0:
            print("RR")
            #self.metodo_rr(procesos)
            #self.procesoRR = procesos
            #self.metodo_rr()
            self.RR()
        if valor ==1:
            print("FCFS")
            #self.procesoFCFS = procesos
            #print("\n\n\n\n",self.procesoFCFS,"\n\n\n\n\n\n")
            #self.metodo_fcfs()
            self.FCFS()
        if valor ==2:
            print("prio")
            #self.procesoPRIORIDAD = procesos
            #self.metodo_prioridades()
            self.PRIORIDAD()
        if valor ==3:
            print("srtf")
            #self.procesoPRIORIDAD = procesos
            #self.metodo_prioridades()
            self.SRTF()
  

   def EjecutarMQ():
        if len(self.colas_multinivel[0])>0:
            print('cola 0',self.colas_multinivel[0])
            buscarAlgoritmo(self.listAlgoritmoInt[0],self.colas_multinivel[0])
        elif len(self.colas_multinivel[1])>0:
            print('cola 1',self.colas_multinivel[1])
            buscarAlgoritmo(self.listAlgoritmoInt[1],self.colas_multinivel[1])
        elif len(self.colas_multinivel[2])>0:
            print('cola 2',self.colas_multinivel[2])
            buscarAlgoritmo(self.listAlgoritmoInt[2],self.colas_multinivel[2])
        elif len(self.colas_multinivel[3])>0:
            print('cola 3',self.colas_multinivel[3])
            buscarAlgoritmo(self.listAlgoritmoInt[3],self.colas_multinivel[3])
        elif len(self.colas_multinivel[4])>0:
            print('cola 4',self.colas_multinivel[4])
            buscarAlgoritmo(self.listAlgoritmoInt[4],self.colas_multinivel[4])
        else:
            pass
   
   print("MQ")
   self.listaAlgoritmoInt=[]
  
   #--------------------------------------------------SUPER BARRA DE RECORDATORIO---------------------------------------------------------
   #Esto puede ir un def afuera
   for i in range(len(self.lista_algoritmos)):
     if self.lista_algoritmos[i]=='rr':
       self.listAlgoritmoInt.insert(i,0)
     if self.lista_algoritmos[i]=='fcfs':
       self.listAlgoritmoInt.insert(i,1)
     if self.lista_algoritmos[i]=='prioridades':
       self.listAlgoritmoInt.insert(i,2)
     if self.lista_algoritmos[i]=='srtf':
       self.listAlgoritmoInt.insert(i,3)
   EjecutarMQ()
 
 def ejecutar_algoritmos(self):
   if self.comboBox_Algoritmos.currentText() == 'PRIORIDADES':
     self.PRIORIDAD()
   if self.comboBox_Algoritmos.currentText() == 'FCFS':
     self.FCFS()
   if self.comboBox_Algoritmos.currentText() == 'RR':
     self.RR()
   if self.comboBox_Algoritmos.currentText() == 'SRTF':
     self.SRTF()
   if self.comboBox_Algoritmos.currentText() =='COLAS MULTINIVEL':
     self.MQ()

 def asignacion_memoria(self):
  for i in self.lista_graficos:
    i[2]='disponible'
    i[4]=0
    i[5]=0
  if self.comboBox_Algoritmos.currentText() =='COLAS MULTINIVEL':  
    self.Mq=True
  else:
    self.Mq=False
  self.clock=0
  self.colagantt=[]
  self.colaesgantt=[]
  self.quantom = self.spinBox_Quantum.value()
  self.q=self.quantom
  if(self.radioButton_Fijas.isChecked()):
    self.asignacion_fija()
  if(self.radioButton_Variables.isChecked()):
    #['idpart',dir_rli,part_size,idpc]
    self.mem_variable=[[0,0,self.valor_memoria_procesos,0]]
    self.asignacion_variable()
 
 def arribo(self):
   self.colanuevo.extend(self.colaarribo.copy())

 def asignacion_variable(self):
   def asignacion_v():
     if self.colanuevo:
        if self.met_asig=='FF':
            self.mem_variable.sort(key = lambda m: (m[1]))
        if self.met_asig=='WF':
            self.mem_variable.sort(key = lambda m: (m[2]),reverse=True)
        i=0
        while i<len(self.colanuevo):
            j=0
            tipo=self.mem_variable[j][3]
            while (j<len(self.mem_variable) and (tipo!=0 or self.colanuevo[i][3]>self.mem_variable[j][2])):
                tipo=self.mem_variable[j][3]
                j=j+1
            if j!=0:
                j=j-1
            if j<len(self.mem_variable):
                if tipo==0 and self.colanuevo[i][3]<=self.mem_variable[j][2]:
                    nuevotam=self.mem_variable[j][2]-self.colanuevo[i][3]
                    nuevodir=self.mem_variable[j][1]+self.colanuevo[i][3]
                    if nuevotam==0:
                        self.mem_variable[j]=[self.idpart,self.mem_variable[j][1],self.colanuevo[i][3],self.colanuevo[i][0]]
                    else:
                        self.mem_variable[j]=[self.idpart,self.mem_variable[j][1],self.colanuevo[i][3],self.colanuevo[i][0]]
                        self.mem_variable.insert(j+1,[0,nuevodir,nuevotam,0])
                    self.idpart=self.idpart+1
                    self.colalisto.append(self.colanuevo[i].copy())
                    try:
                      connection = mysql.connector.connect(host=self.host,
                      database = self.database,
                      user=self.user,
                      password=self.password)
                      print("conecto")
                      cur=connection.cursor()
                      mySql_update_query="""SELECT * FROM rafagas r WHERE r.idpc=(%s)"""
                      recordTuple=(self.colanuevo[i][0],)
                      print(recordTuple)
                      cur.execute(mySql_update_query,recordTuple)
                      self.result=cur.fetchall()
                      print(self.result)
                      for k in range(len(self.result)):
                        self.result[k]=list(self.result[k])
                      print("aber",self.result)
                      self.rafagas.update({str(self.colanuevo[i][0]):self.result})
                    except mysql.connector.Error as error:
                      print("Fallo al conectarse {}",format(error))
                    else:
                      pass
                    finally:
                      if(connection.is_connected()):
                        connection.close()
                        print("Conexion cerrada")
                    self.colanuevo.pop(i)
                    print('cola nuevo despues de pop',self.colanuevo)
                    j=j+1
                else:
                    i=i+1
        self.mem_variable.sort(key = lambda m: (m[1]))
   #['idpart',dir_rli,part_size,idpc]
   #['idpc','Descripcion','Prioridad','Tamaño','TI','TA'] 
   self.idpart=1
   b=True
   j=0
   print("variable")
   self.procesos_sin_asignar=self.listaprocesos.copy()
   self.procesos_sin_asignar.sort(key=lambda m: m[5])
   while b:
     self.colaarribo=[]
     while j<len(self.procesos_sin_asignar) and self.procesos_sin_asignar[j][5]==self.clock:
       self.colaarribo.append(self.procesos_sin_asignar[j])
       j=j+1
     if len(self.colaarribo)>0:
       self.arribo()
     print('cola nuevo',self.colanuevo)
     asignacion_v()
     self.ejecutar_algoritmos()
     self.entrada_salida()

     self.clock=self.clock+1
     #if #completar aca: 
     #  b=False
     print('asignacion',self.mem_variable)
     if self.Mq:
       if (len(self.colanuevo)==0 and len(self.colaarribo)==0 and len(self.colabloqueado)==0 and len(self.procesos_sin_asignar)<=j and (len(self.colas_multinivel[0])==0) and (len(self.colas_multinivel[1])==0) and (len(self.colas_multinivel[2])==0) and (len(self.colas_multinivel[3])==0) and (len(self.colas_multinivel[4])==0)):
        b=False
     else:
       if len(self.colalisto)==0 and len(self.colanuevo)==0 and len(self.colabloqueado)==0 and len(self.colaarribo)==0 and len(self.procesos_sin_asignar)<=j:
        b=False

 def entrada_salida(self):
    print("entrada salida")
    if len(self.colabloqueado)>0:
        caux=self.colabloqueado[0].copy()
        caux[4]=1
        self.colabloqueado[0][4]=self.colabloqueado[0][4]-1
        rafita=self.rafagas[str(self.colabloqueado[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        self.rafagas.update({str(self.colabloqueado[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colalisto.append(self.colabloqueado[0].copy())
          del rafita[0]
          self.rafagas.update({str(self.colabloqueado[0][0]):rafita})
          del self.colabloqueado[0]

        """
        if self.colalisto[0][4]==0:
          del self.colalisto[0]
        """

        if len(self.colaesgantt)>0 and self.colaesgantt[-1][0]==caux[0]:
          self.colaesgantt[-1][4]=self.colaesgantt[-1][4]+1
        else:
          self.colaesgantt.append(caux.copy())
        print('colabloqueado',self.colabloqueado)
        print('colaesgantt',self.colaesgantt)
 
 def asignacion_fija(self):
   
   def asignacion_f():
       i=0
       while i<len(self.colanuevo):
           j=0
           if self.met_asig=='FF':
               self.lista_graficos.sort(key = lambda m: (m[0]))
           if self.met_asig=='BF':
               self.lista_graficos.sort(key=lambda m: m[3])
           while (j<len(self.lista_graficos)) and ((self.lista_graficos[j][3]<self.colanuevo[i][3]) or (self.lista_graficos[j][2]!='disponible')):
               j=j+1
           if j<len(self.lista_graficos): 
               if (self.lista_graficos[j][3])>=self.colanuevo[i][3] and (self.lista_graficos[j][2])=='disponible':
                   self.lista_graficos[j][4]=self.colanuevo[i][0] 
                   self.lista_graficos[j][5]=(self.lista_graficos[j][3])-self.colanuevo[i][3]
                   self.lista_graficos[j][2]='ocupado'
                   if self.Mq:
                     if self.colanuevo[i][2] >=self.limites_colas[0][0] and self.colanuevo[i][2] <=self.limites_colas[0][1] :
                       self.colas_multinivel[0].append(self.colanuevo[i].copy())
                     if self.colanuevo[i][2] >=self.limites_colas[1][0] and self.colanuevo[i][2] <=self.limites_colas[1][1] :
                       self.colas_multinivel[1].append(self.colanuevo[i].copy())
                     if self.colanuevo[i][2] >=self.limites_colas[2][0] and self.colanuevo[i][2] <=self.limites_colas[2][1] :
                       self.colas_multinivel[2].append(self.colanuevo[i].copy())
                     if self.colanuevo[i][2] >=self.limites_colas[3][0] and self.colanuevo[i][2] <=self.limites_colas[3][1] :
                       self.colas_multinivel[3].append(self.colanuevo[i].copy())
                     if self.colanuevo[i][2] >=self.limites_colas[4][0] and self.colanuevo[i][2] <=self.limites_colas[4][1] :
                       self.colas_multinivel[4].append(self.colanuevo[i].copy())
                     print('ESTO TIENE QUE APARECER',self.colas_multinivel)
                   else:
                     self.colalisto.append(self.colanuevo[i].copy())
                     try:
                       connection = mysql.connector.connect(host=self.host,
                       database = self.database,
                       user=self.user,
                       password=self.password)
                       print("conecto")
                       cur=connection.cursor()
                       mySql_update_query="""SELECT * FROM rafagas r WHERE r.idpc=(%s)"""
                       recordTuple=(self.colanuevo[i][0],)
                       print(recordTuple)
                       cur.execute(mySql_update_query,recordTuple)
                       self.result=cur.fetchall()
                       print(self.result)
                       for k in range(len(self.result)):
                         self.result[k]=list(self.result[k])
                       print("aber",self.result)
                       self.rafagas.update({str(self.colanuevo[i][0]):self.result})
                     except mysql.connector.Error as error:
                       print("Fallo al conectarse {}",format(error))
                     else:
                       pass
                     finally:
                       if(connection.is_connected()):
                         connection.close()
                         print("Conexion cerrada")
                   self.colanuevo.pop(i)
                   self.lista_graficos.sort(key=lambda m: m[0]) 
               else:
                   i=i+1
           else:
               i=i+1  
   self.procesos_sin_asignar=self.listaprocesos.copy()
   self.procesos_sin_asignar.sort(key=lambda m: m[5])
   j=0
   b=True
   self.limites()
   while b:
     self.colaarribo=[]
     while j<len(self.procesos_sin_asignar) and self.procesos_sin_asignar[j][5]==self.clock:
       self.colaarribo.append(self.procesos_sin_asignar[j])
       j=j+1
     if len(self.colaarribo)>0:
       self.arribo()
     asignacion_f()
     self.ejecutar_algoritmos()
     self.entrada_salida()
     self.clock=self.clock+1
     #Condicion de fin
     if self.Mq:
       if (len(self.colanuevo)==0 and len(self.colaarribo)==0 and len(self.colabloqueado)==0 and len(self.procesos_sin_asignar)<=j and (len(self.colas_multinivel[0])==0) and (len(self.colas_multinivel[1])==0) and (len(self.colas_multinivel[2])==0) and (len(self.colas_multinivel[3])==0) and (len(self.colas_multinivel[4])==0)):
        b=False
     else:
       if len(self.colalisto)==0 and len(self.colanuevo)==0 and len(self.colabloqueado)==0 and len(self.colaarribo)==0 and len(self.procesos_sin_asignar)<=j:
        b=False
     """if self.Mq:
       if ((len(self.colas_multinivel[0])==0) and (len(self.colas_multinivel[1])==0) and (len(self.colas_multinivel[2])==0) and (len(self.colas_multinivel[3])==0) and (len(self.colas_multinivel[4])==0)):
        b=False
     else:
       if len(self.colalisto)==0:
        b=False"""

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
     if i not in self.listaIDprocesos:
      self.dialogoImportar.label_error.setText("")
      self.listaIDprocesos.append(self.result[i-1][0])
      self.listaprocesos.append([self.result[i-1][0],self.result[i-1][1],self.result[i-1][2],self.result[i-1][3],self.result[i-1][4],self.result[i-1][5]])
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
     else:
      self.dialogoImportar.label_error.setText("Error: el proceso seleccionado ya esta cargado")
   if not self.pushButton_AceptarProc.isEnabled():
     self.pushButton_AceptarProc.setEnabled(True)
   if not self.comboBox_Algoritmos.isEnabled():
     self.comboBox_Algoritmos.setEnabled(True)
   if not self.spinBox_Quantum.isEnabled():
     self.spinBox_Quantum.setEnabled(True)
   if not self.pushButton_Simular.isEnabled():
     self.pushButton_Simular.setEnabled(True)


   """
   for i in self.result:
     item= self.dialogoImportar.tableWidgetImportar.item(self.contador_act,0)
     
     if item.checkState() == Qt.Checked:
       indice=item.row()
       elemento=self.result[indice]
       self.procesos_importados.append(elemento)
       print(self.procesos_importados)
       self.contador_act +=1
   #ahi guarde las filas tildadas en una tabla
   #ahora las agrego a la tabla de gestion de procesos
   print("El contador act vale {}".format(self.contador_act))
   for i in range(self.contador_act):
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
 
 def mapa_de_memoria(self):
   if(self.radioButton_Fijas.isChecked()):
    self.mapa_de_memoria_fija()
   if(self.radioButton_Variables.isChecked()):
     self.mapa_de_memoria_variable()
   
 def mapa_de_memoria_variable(self):
   print('entre al grafico variable')
   global cont_sim_2davez
   if cont_sim_2davez >=0:
    global conts
    print('entre al grafico variable aqui')
    fig= plt.figure('Mapa de memoria',figsize=(15,2))
    ax=fig.subplots()
    category_names=[]
    ys=[]
    i=0
    #['idpart',dir_rli,part_size,idpc]
    #self.lista_graficos.append([cont_agregar_particion,rli,'disponible',tampart,0,0])
    for elemento in self.mem_variable:
      print(elemento)
      if len(elemento)>1:
        if elemento[3]==0:
          category_names.append('Idpart: '+str(elemento[0])+'\nIdpc: Libre\nFragInt:'+str(0))
        else:
          category_names.append('Idpart: '+str(elemento[0])+'\nIdpc:    '+ str(elemento[3])+'\nFragInt:'+str(0))
        ys.append(elemento[2])
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

 def mapa_de_memoria_fija(self):
   print('entre al grafico')
   global cont_sim_2davez
   if cont_sim_2davez >=0:
    global conts
    fig= plt.figure('Mapa de memoria',figsize=(15,2))
    ax=fig.subplots()
    category_names=[]
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
       
       if i[0] not in self.listaIDprocesosventImportar:
        self.listaIDprocesosventImportar.append(i[0])
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
   if self.dialogo.radioButtonCPU.isEnabled():
     print("hola1")
     self.dialogo.radioButtonCPU.setChecked(False)
     self.dialogo.radioButtonCPU.setEnabled(False)
     self.dialogo.radioButtonES.setEnabled(True)
     if not self.dialogo.pushButtonCargar.isEnabled():
       self.dialogo.pushButtonCargar.setEnabled(True)

   #if self.dialogo.radioButtonES.isEnabled():
   else:
     print("hola2")
     self.dialogo.radioButtonES.setChecked(False)
     self.dialogo.radioButtonES.setEnabled(False)
     self.dialogo.radioButtonCPU.setEnabled(True)
     if self.dialogo.pushButtonCargar.isEnabled():
       self.dialogo.pushButtonCargar.setEnabled(False)

     #if not self.dialogo.radioButtonES.isEnabled():
      #self.dialogo.radioButtonES.setEnabled(True)
   #if self.dialogo.radioButtonES.isEnabled():
     #self.dialogo.radioButtonES.setEnabled(False)
     #if not self.dialogo.radioButtonCPU.isEnabled():
      #self.dialogo.radioButtonCPU.setEnabled(True)
   global contr
   #con este comando agrego una fila a la tabla
   self.dialogo.tableWidgetRafaga.insertRow(contr)
   #con este comando guardo lo que voy a meter en la tabla con una variable 
   tiempo = QTableWidgetItem(str(self.dialogo.lineEdit_Tiempo.text()))
   if self.dialogo.radioButtonES.isChecked():
     tipo = QTableWidgetItem("ES")
   if self.dialogo.radioButtonCPU.isChecked():
     tipo = QTableWidgetItem("CPU")


   
   self.dialogo.tableWidgetRafaga.setItem(contr,0,tipo)
   self.dialogo.tableWidgetRafaga.setItem(contr,1,tiempo)
   self.dialogo.lineEdit_Tiempo.setText('')
   contr=contr+1
  
 def graficar(self):
   self.carga_particionFijas.hide()
   self.flagParticionesCargadas=True
   self.habilitarGestionarProcesos()
   self.generar_grafico()

 def habilitarGestionarProcesos(self):
   self.boton_GestProcesos.setEnabled(True)
 
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
   if self.radioButton_Best.isChecked():
     self.radioButton_Best.setChecked(False)
   self.radioButton_Best.setEnabled(False)
   if not self.radioButton_First.isEnabled():
     self.radioButton_First.setEnabled(True)
   #nota: el set enable anda con los line Edit
 
 def fijaselected(self):
   #hace un disable del radio button de worst fit
   print(self.radioButton_Worst.isChecked())
   if self.radioButton_Worst.isChecked():
    self.radioButton_Worst.setChecked(False)
   self.radioButton_Worst.setEnabled(False)
   self.radioButton_Best.setEnabled(True)
   self.radioButton_First.setEnabled(True)

 def firstselected(self):
   self.met_asig='FF'
   if not self.AceptarMem.isEnabled():
     self.AceptarMem.setEnabled(True)
 
 def bestselected(self):
   self.met_asig='BF'
   if not self.AceptarMem.isEnabled():
     self.AceptarMem.setEnabled(True)

 def worstselected(self):
   self.met_asig='WF'
   if not self.AceptarMem.isEnabled():
     self.AceptarMem.setEnabled(True)

 def updateLabels(self):
   if self.por_so >0:
    self.valor_so = ((self.tam_Memoria)*(self.por_so))/100
    self.valor_memoria_procesos = self.tam_Memoria-self.valor_so
    self.valor_memoria_procesos = round(self.valor_memoria_procesos,2)
    self.label_MemProcesos.setText(''+str(self.valor_memoria_procesos) + " KB")
    self.label_MemSO.setText(''+str(self.valor_so) + " KB") 

 def actTamMemoria(self):
   if self.spinBoxTamMemoria.value()>0:
    self.tam_Memoria = self.spinBoxTamMemoria.value()
    print(self.tam_Memoria)
    self.spinBoxPorcSO.setEnabled(True)

 def actPorcSO(self):
   self.por_so=self.spinBoxPorcSO.value()
   print(self.por_so)
   self.flagporcSO=True

 def habilitarAlgYQuantum(self):
   self.comboBox_Algoritmos.setEnabled(True)
   self.label_Algoritmo.setEnabled(True)
   self.spinBox_Quantum.setEnabled(True)
   self.label_Quantum.setEnabled(True)

 def cargarProcesosYRafagasenBD(self):
   if self.dialogo.radioButtonES.isEnabled():
     self.dialogo.radioButtonES.setEnabled(False)
     self.dialogo.radioButtonCPU.setEnabled(True)
   if not self.pushButton_AceptarProc.isEnabled():
     self.pushButton_AceptarProc.setEnabled(True)
   if not self.pushButton_Simular.isEnabled():
     self.pushButton_Simular.setEnabled(True)

   def limpiar_carga_rafagas():
     global contr
     contr = 0
     self.dialogo.tableWidgetRafaga.setRowCount(0)
     self.dialogo.lineEdit_Tiempo.setText(" ")
     self.dialogo.lineEditDescrip.setText(" ")
     self.dialogo.spinBoxPriori.setValue(0)
     self.dialogo.spinBoxTamProc.setValue(0)
     self.dialogo.spinBoxTiempoarr.setValue(0)
     self.flagProcesosCargados=True
     self.habilitarAlgYQuantum()
   
   
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
     if codpc not in self.listaIDprocesos:
      self.listaIDprocesos.append(codpc)
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
   self.dialogo.spinBoxTamProc.setValue(0)
   self.dialogo.spinBoxPriori.setValue(0)
   if self.dialogo.radioButtonES.isEnabled():
     self.dialogo.radioButtonES.setEnabled(False)
     self.dialogo.radioButtonCPU.setEnabled(True)
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
    #df.append(dict(Task="ES",Start=3,Finish =7, Resource="Proceso 1"))

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
    
#estas lineas son para que se ejecute la ventana al inciar o ejecutar este archivo .pyw
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


