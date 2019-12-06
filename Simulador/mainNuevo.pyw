# -*- coding: UTF-8 -*- 
import sys
import os
from copy import deepcopy
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
import time

#update:06/12set

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
  self.AceptarMem.clicked.connect(self.checkproceso)
  self.tam_Memoria=0
  self.por_so=0 
  self.grado_multiprogramacion=0
  self.checkbox=QTableWidgetItem()
  self.valor_memoria_procesos=0
  self.contabla_raf=0
  self.lista_graficos=[]
  self.listaprocesos= []
  self.procesos_sin_asignar=[]
  self.procesos_importados=[]
  self.colaarribo=[]
  self.colanuevo=[]
  self.mapaporclock=[]
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
  self.tamPartFijMax=0


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
  self.pushButtonComparar.setEnabled(True)
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
  self.dialogo.radioButtonCPU.setEnabled(False)
  self.dialogo.pushButtonCargar.setEnabled(False)



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
  self.colaauxiliarantirupturadegantt=[]
  
  self.rafagas={}
  self.tiempoespera={}
  self.tiemporetorno={}
  self.listaImportarProcesos=[]
  self.colanuevoporclock=[]
  self.colalistoporclock=[]
  self.colabloqueadoporclock=[]
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
  self.dialogo.radioButtonCPU.toggled.connect(self.checkpushButtonAgregarRafaga)
  self.dialogo.radioButtonES.toggled.connect(self.checkpushButtonAgregarRafaga)
  self.dialogo.spinBoxTiempo.valueChanged.connect(self.primeravezvalor)
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

  #self.pushButton_Simular.clicked.connect(self.asignacion_memoria)

  self.dialogresultsim.pushButton_verGantt.clicked.connect(self.gantt)
  #cosas que disparan al apretar "Simular" en Ventana
  #self.dialogresultsim.pushButton_verGantt.clicked.connect(self.mapa_de_memoria)

  #self.pushButton_Simular.clicked.connect(self.mapa_de_memoria)
  self.dialogresultsim.pushButtonStart.clicked.connect(self.asignacion_memoria)
  self.dialogresultsim.pushButtonStop.clicked.connect(self.abortar)



  
  self.pushButton_Simular.clicked.connect(self.mostrarResultSimulacion)
    
  self.pushButtonComparar.clicked.connect(self.mostrarComparacion)
  self.pushButton_AceptarProc.clicked.connect(self.aceptar_algoritmo_presionado)
  self.dialogo.pushButtonImportar.clicked.connect(self.mostrarTablaImportar)
  self.dialogo.pushButtonQuitar.clicked.connect(self.borrarProcesoCargado)
  self.dialogoImportar.tableWidgetImportar.setColumnCount(6)
  self.dialogoImportar.tableWidgetImportar.setHorizontalHeaderLabels(['idpc','Descripcion','Prioridad','Tamaño','TI','TA'])
  self.dialogcompara.tableWidgetTEspera.setColumnCount(6)
  self.dialogcompara.tableWidgetTEspera.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','SRTF','C.Multinivel'])
  self.dialogcompara.tableWidgetTRetorno.setColumnCount(6)
  self.dialogcompara.tableWidgetTRetorno.setHorizontalHeaderLabels(['idpc','FCFS','Prioridades','RR','SRTF','C.Multinivel'])
  self.dialogcompara.tableWidgetTEsperaP.setColumnCount(5)
  self.dialogcompara.tableWidgetTEsperaP.setHorizontalHeaderLabels(['FCFS','Prioridades','RR','SRTF','C.Multinivel'])
  self.dialogcompara.tableWidgetTRetornoP.setColumnCount(5)
  self.dialogcompara.tableWidgetTRetornoP.setHorizontalHeaderLabels(['FCFS','Prioridades','RR','SRTF','C.Multinivel'])
  self.dialogresultsim.tableWidgetCListo.setColumnCount(2)
  self.dialogresultsim.tableWidgetCListo.setHorizontalHeaderLabels(['idpc','Ti - CPU Total',])
  self.dialogresultsim.tableWidgetCBloqueado.setColumnCount(2)
  self.dialogresultsim.tableWidgetCBloqueado.setHorizontalHeaderLabels(['idpc','Ti - ES Total',])
  self.dialogresultsim.tableWidgetCNuevo.setColumnCount(1)
  self.dialogresultsim.tableWidgetCNuevo.setHorizontalHeaderLabels(['idpc',])
  self.dialogresultsim.pushButtonStop.clicked.connect(self.enablestart)
  self.spinBoxTamMemoria.valueChanged.connect(self.bloquearparteder)
  self.spinBoxPorcSO.valueChanged.connect(self.bloquearparteder)
  self.radioButton_Fijas.toggled.connect(self.bloquearparteder)
  self.radioButton_Variables.toggled.connect(self.bloquearparteder)
  self.radioButton_First.toggled.connect(self.bloquearparteder)
  self.radioButton_Best.toggled.connect(self.bloquearparteder)
  self.radioButton_Worst.toggled.connect(self.bloquearparteder)
  self.labelEP.setText('')
  self.dialogoImportar.pushButtonImportar.clicked.connect(self.update_tablaProcesos)
  #dentro de este self(update_tablaProcesos) tambien habilito el boton de aceptar algoritmo
  self.dialogoImportar.pushButtonVertabla.clicked.connect(self.cargarTabla)
  self.dialogoMQ.spinBoxCantColas.valueChanged.connect(self.actualizarMQ)
  self.dialogoMQ.comboBox_alg1.currentIndexChanged.connect(self.checkQcola1)
  self.dialogoMQ.comboBox_alg2.currentIndexChanged.connect(self.checkQcola2)
  self.dialogoMQ.comboBox_alg3.currentIndexChanged.connect(self.checkQcola3)
  self.dialogoMQ.comboBox_alg4.currentIndexChanged.connect(self.checkQcola4)
  self.dialogoMQ.comboBox_alg5.currentIndexChanged.connect(self.checkQcola5)
  self.dialogo.spinBoxTamProc.valueChanged.connect(self.checktam_proceso)
  self.dialogoImportar.spinBox_Proceso.valueChanged.connect(self.check_procesoValido)
  self.spinBox_Quantum.valueChanged.connect(self.qchanged)
  self.dialogo.pushButtonAgregarRafaga.setEnabled(False)
  self.carga_particionFijas.pushButtonQuitarPart.clicked.connect(self.LimpiarParticion)


  



  #self.dialogo.comboBoxTipoRaf.currentIndexChanged.connect(self.checkRaf)
  self.last_raf_item=2
  #0 es CPU, 1 es ES, 2 es DEFAULT
  #self.dialogo.comboBoxTipoRaf.currentIndexChanged
  self.dialogoMQ.pushButton_cancelar.clicked.connect(self.closeMQ)
  self.dialogoMQ.pushButton_aceptar.clicked.connect(self.loadAlgoritmosMQ)
  self.dialogresultsim.spinBoxClock.valueChanged.connect(self.clockchanged)

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



 def LimpiarParticion(self):
   for i in range(self.carga_particionFijas.tableWidgetCargaParticion.rowCount()):
     self.carga_particionFijas.tableWidgetCargaParticion.removeRow(0)
   self.valor_memoria_procesos = self.tam_Memoria-self.valor_so
   self.carga_particionFijas.label_MemDisp.setText("Memoria Disponible: "+str(round(self.valor_memoria_procesos,2)) + " KB")
   self.lista_graficos=[]
   print(self.lista_graficos)

#['idpc','Descripcion','Prioridad','Tamaño','TI','TA','TI-ES','InicioGantt','FinGantt']
 def checkproceso(self):
   if self.listaprocesos:
     self.labelEP.setText("")
     if not self.comboBox_Algoritmos.isEnabled():
       self.comboBox_Algoritmos.setEnabled(True)
     if not self.label_Algoritmo.isEnabled():
       self.label_Algoritmo.setEnabled(True)
     if not self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(True)
     if not self.label_Quantum.isEnabled():
       self.label_Quantum.setEnabled(True)
     if not self.pushButton_AceptarProc.isEnabled():
       self.pushButton_AceptarProc.setEnabled(True)
     if not self.pushButtonComparar.isEnabled():
       self.pushButtonComparar.setEnabled(True)
     if not self.pushButton_Simular.isEnabled():
       self.pushButton_Simular.setEnabled(True)
     invalido=False
     #Variables - Fijas
     if self.radioButton_Variables.isChecked():
       for i in self.listaprocesos:
         if i[3] >self.valor_memoria_procesos:
           invalido=True
     if self.radioButton_Fijas.isChecked():
       for i in self.listaprocesos:
         if i[3]>self.tamPartFijMax:
           invalido=True
     #invalido
     if invalido:
       self.labelEP.setText("Tamaño procesos invalidos\nControlar procesos cargados")
       if self.comboBox_Algoritmos.isEnabled():
         self.comboBox_Algoritmos.setEnabled(False)
       if self.label_Algoritmo.isEnabled():
         self.label_Algoritmo.setEnabled(False)
       if self.spinBox_Quantum.isEnabled():
         self.spinBox_Quantum.setEnabled(False)
       if self.label_Quantum.isEnabled():
         self.label_Quantum.setEnabled(False)
       if self.pushButton_AceptarProc.isEnabled():
         self.pushButton_AceptarProc.setEnabled(False)
       if self.pushButtonComparar.isEnabled():
         self.pushButtonComparar.setEnabled(True)
       if self.pushButton_Simular.isEnabled():
         self.pushButton_Simular.setEnabled(False)
   else:
     self.labelEP.setText("")
     if self.comboBox_Algoritmos.isEnabled():
       self.comboBox_Algoritmos.setEnabled(False)
     if self.label_Algoritmo.isEnabled():
       self.label_Algoritmo.setEnabled(False)
     if self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(False)
     if self.label_Quantum.isEnabled():
       self.label_Quantum.setEnabled(False)
     if self.pushButton_AceptarProc.isEnabled():
       self.pushButton_AceptarProc.setEnabled(False)
     if self.pushButtonComparar.isEnabled():
       self.pushButtonComparar.setEnabled(True)
     if self.pushButton_Simular.isEnabled():
       self.pushButton_Simular.setEnabled(False)

 def bloquearparteder(self):
   if self.boton_GestProcesos.isEnabled():
     self.boton_GestProcesos.setEnabled(False)

   if self.comboBox_Algoritmos.isEnabled():
     self.comboBox_Algoritmos.setEnabled(False)

   if self.label_Algoritmo.isEnabled():
     self.label_Algoritmo.setEnabled(False)
     

   if self.spinBox_Quantum.isEnabled():
     self.spinBox_Quantum.setEnabled(False)

   if self.label_Quantum.isEnabled():
     self.label_Quantum.setEnabled(False)
  
   if self.pushButton_AceptarProc.isEnabled():
     self.pushButton_AceptarProc.setEnabled(False)

   if self.pushButtonComparar.isEnabled():
     self.pushButtonComparar.setEnabled(True)

   if self.pushButton_Simular.isEnabled():
     self.pushButton_Simular.setEnabled(False)

 def enablestart(self):
   if not self.dialogresultsim.pushButtonStart.isEnabled():
     self.dialogresultsim.pushButtonStart.setEnabled(True)

 def check_procesoValido(self):
   if self.dialogoImportar.spinBox_Proceso.value() not in self.listaIDprocesosventImportar:
     if self.dialogoImportar.pushButtonImportar.isEnabled():
       self.dialogoImportar.pushButtonImportar.setEnabled(False)
     if self.dialogoImportar.pushButtonCargar.isEnabled():
       self.dialogoImportar.pushButtonCargar.setEnabled(False)
   else:
     if not self.dialogoImportar.pushButtonImportar.isEnabled():
       self.dialogoImportar.pushButtonImportar.setEnabled(True)
     if not self.dialogoImportar.pushButtonCargar.isEnabled():
       self.dialogoImportar.pushButtonCargar.setEnabled(True)

 def checktam_proceso(self):
   if self.radioButton_Variables.isChecked():
     if (int(self.dialogo.spinBoxTamProc.value())>self.valor_memoria_procesos):
       self.dialogo.label_error_tam.setText("Tamaño de proceso inválido")
       if(self.dialogo.spinBoxTiempo.isEnabled()):
         self.dialogo.spinBoxTiempo.setEnabled(False)
     else:
       self.dialogo.label_error_tam.setText("")
       if(not self.dialogo.spinBoxTiempo.isEnabled()):
         self.dialogo.spinBoxTiempo.setEnabled(True)
   if(self.radioButton_Fijas.isChecked()):
     if (int(self.dialogo.spinBoxTamProc.value())>self.tamPartFijMax):
       self.dialogo.label_error_tam.setText("Tamaño de proceso inválido")
       if(self.dialogo.spinBoxTiempo.isEnabled()):
         self.dialogo.spinBoxTiempo.setEnabled(False)
     else:
       self.dialogo.label_error_tam.setText("")
       if(not self.dialogo.spinBoxTiempo.isEnabled()):
         self.dialogo.spinBoxTiempo.setEnabled(True)

 def qchanged(self):
   if self.spinBox_Quantum.value()>0:
     if not self.pushButton_Simular.isEnabled():
       self.pushButton_Simular.setEnabled(True)
   if self.spinBox_Quantum.value()==0:
     if self.pushButton_Simular.isEnabled():
       self.pushButton_Simular.setEnabled(False)

 def clockchanged(self):
   if self.b==False and self.stop==False:
     self.dialogresultsim.spinBoxClock.setMaximum(self.clock)
     #Tiempo ejecutado inexistente
     if self.clock<self.dialogresultsim.spinBoxClock.value():
       print('SE TE FUE LA MANO')
     else:
       self.show_colalistoybloq()
       #Tiempo ejecutado existente
       if(self.radioButton_Fijas.isChecked()):
         self.lista_graficos=self.mapaporclock[self.dialogresultsim.spinBoxClock.value()].copy()
         self.mapa_de_memoria_fija()
       if(self.radioButton_Variables.isChecked()):
         #self.mem_variable=[[0,0,self.valor_memoria_procesos,0]]
         self.mem_variable=self.mapaporclock[self.dialogresultsim.spinBoxClock.value()].copy()
         self.mapa_de_memoria_variable()
         
 def primeravezvalor(self):
   if not self.dialogo.spinBoxTiempo.value()==0:
     if not self.dialogo.radioButtonES.isEnabled():
       if not self.dialogo.radioButtonCPU.isEnabled():
         self.dialogo.radioButtonCPU.setEnabled(True)
       if self.dialogo.radioButtonCPU.isChecked():
         if not self.dialogo.pushButtonAgregarRafaga.isEnabled():
           self.dialogo.pushButtonAgregarRafaga.setEnabled(True)
     if self.dialogo.radioButtonES.isEnabled():
       if self.dialogo.radioButtonES.isChecked():
         if not self.dialogo.pushButtonAgregarRafaga.isEnabled():
           self.dialogo.pushButtonAgregarRafaga.setEnabled(True)
    
 def checkpushButtonAgregarRafaga(self):
   if not self.dialogo.spinBoxTiempo.value() ==0:
     print("distinto de 0")
     if not self.dialogo.pushButtonAgregarRafaga.isEnabled():
       print("no esta habilitado")
       self.dialogo.pushButtonAgregarRafaga.setEnabled(True)

 def checkcampoq(self):
   if not self.comboBox_Algoritmos.currentText()=='RR':
     if self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(False)
     if self.comboBox_Algoritmos.currentText()=='COLAS MULTINIVEL':
       if not self.pushButton_AceptarProc.isEnabled():
         self.pushButton_AceptarProc.setEnabled(True)
       if self.pushButton_Simular.isEnabled():
         self.pushButton_Simular.setEnabled(False)
     else:
       if self.pushButton_AceptarProc.isEnabled():
         self.pushButton_AceptarProc.setEnabled(False)

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

   if not self.pushButton_Simular.isEnabled():
     self.pushButton_Simular.setEnabled(True)

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
   if int(self.dialogoImportar.spinBox_Proceso.value()) >0 and self.dialogoImportar.spinBox_Proceso.value() not in self.listaIDprocesos:
     self.listaImportarProcesos.append(self.dialogoImportar.spinBox_Proceso.value())
     pro_cargados= str(self.dialogoImportar.label_PC.text())+str(self.dialogoImportar.spinBox_Proceso.value())+","
     self.dialogoImportar.label_PC.setText(pro_cargados)
     if not self.dialogoImportar.pushButtonImportar.isEnabled():
       self.dialogoImportar.pushButtonImportar.setEnabled(True)
    
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
     self.dialogoMQ.spinBox_q1.setMinimum(1)
     self.dialogoMQ.spinBox_q2.setMinimum(1)
     self.dialogoMQ.spinBox_q3.setMinimum(1)
     self.dialogoMQ.spinBox_q4.setMinimum(1)
     self.dialogoMQ.spinBox_q5.setMinimum(1)
     self.dialogoMQ.exec_()

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

 def unirhueco(self):
    i=0
    while i+1<len(self.mem_variable):
        if self.mem_variable[i][3]==0 and self.mem_variable[i+1][3]==0:
            self.mem_variable[i][2]=self.mem_variable[i][2]+self.mem_variable[i+1][2]
            self.mem_variable.pop(i+1)
        else:
            i=i+1

 def liberarparticion(self):
   if(self.radioButton_Fijas.isChecked()):
     for i in self.lista_graficos:
       if i[4]==self.procactual:
         i[4]=0
         i[5]=0
         i[2]='disponible'
   if(self.radioButton_Variables.isChecked()):
     for i in self.mem_variable:
       if i[3]==self.procactual:
         i[3]=0
     self.unirhueco()
     #['idpart',dir_rli,part_size,idpc]
     #self.mem_variable[j]
     
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
        self.tiempo=self.tiempoespera[str(self.colalisto[0][0])]
        if self.Mq:
          if rafita[0][0]==1 and self.tiempo[4][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        else:
          if rafita[0][0]==1 and self.tiempo[1][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colaauxiliarantirupturadegantt=self.colalisto[0].copy()

            #self.colabloqueado.append(self.colalisto[0].copy())
          else:
            self.procactual=self.colalisto[0][0]
            self.seterminoalgo=True
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]

        """
        if self.colalisto[0][4]==0:
          del self.colalisto[0]
        """
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0] and self.clock==self.colagantt[-1][7]:
          self.colagantt[-1][4]=self.colagantt[-1][4]+1
          self.colagantt[-1][7]=self.clock+1
        else:
          self.colagantt.append(caux.copy())
          self.colagantt[-1].extend([self.clock,self.clock+1])
        print('colalisto',self.colalisto)
        print('colabloqueado',self.colabloqueado)
        print('colanuevo',self.colanuevo)
        print('colagantt',self.colagantt)
        #['idpc','Descripcion','Prioridad','Tamaño','TI','TA','TI-ES','InicioGantt','FinGantt']
 
 def RR(self):
    print('RR')
    print('quantum',self.quantom)
    print('colalisto antes de ejecutar RR',self.colalisto)
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
        
        self.tiempo=self.tiempoespera[str(self.colalisto[0][0])]
        if self.Mq:
          if rafita[0][0]==1 and self.tiempo[4][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        else:
          if rafita[0][0]==1 and self.tiempo[2][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})

        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0] and self.clock==self.colagantt[-1][7]:
          self.colagantt[-1][4]=self.colagantt[-1][4]+1
          self.colagantt[-1][7]=self.clock+1
        else:
          self.colagantt.append(caux.copy())
          self.colagantt[-1].extend([self.clock,self.clock+1])
        self.q=self.q-1
        if self.q==0:
            self.q=self.quantom

            if rafita[0][3]==0:
              #Termina quantum y justo termina la rafaga
              if len(rafita)>1:
                print('QUE PASO ACA?',rafita)
                #termina quantum y se bloquea el proceso (Lo manda al cola del bloqueado)
                self.colaauxiliarantirupturadegantt=self.colalisto[0].copy()
               
                #self.colabloqueado.append(self.colalisto[0].copy())
              else:
                print('llego aca?')
                self.procactual=self.colalisto[0][0]
                self.seterminoalgo=True
              del rafita[0]
              self.rafagas.update({str(self.colalisto[0][0]):rafita})
              del self.colalisto[0]
            else:
                #termina quantum y no termina la rafaga, manda el proceso al final de la colalisto
                aux=self.colalisto[0].copy()
                del self.colalisto[0]
                self.colalisto.append(aux.copy())
        else:
            #No termina quantum y justo termina la rafaga
            if rafita[0][3]==0:
              #Termina la rafaga
              if len(rafita)>1:
                print('Osea entro aca?',rafita)
                #termina la rafaga pero no el proceso: se bloquea el proceso (Lo manda al cola del bloqueado)
                self.colaauxiliarantirupturadegantt=self.colalisto[0].copy()
                
              else:
                self.procactual=self.colalisto[0][0]
                self.seterminoalgo=True
              """if rafita[0][0]==1:
                self.tiempo=self.tiempoespera[str(self.colalisto[0][0])]
                self.cerrartiempo()
                self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})"""
              del rafita[0]
              self.rafagas.update({str(self.colalisto[0][0]):rafita})
              del self.colalisto[0]
              self.q=self.quantom
            """              
            if self.colalisto[0][4]==0:
              #No termina quantum y justo termina el proceso
              del self.colalisto[0]"""
              
        print('colalisto',self.colalisto)
        print('colabloqueado',self.colabloqueado)
        print('colanuevo',self.colanuevo)
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
        self.tiempo=self.tiempoespera[str(self.colalisto[0][0])]
        if self.Mq:
          if rafita[0][0]==1 and self.tiempo[4][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        else:
          if rafita[0][0]==1 and self.tiempo[3][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colaauxiliarantirupturadegantt=self.colalisto[0].copy()
            
            #self.colabloqueado.append(self.colalisto[0].copy())
          else:
            self.procactual=self.colalisto[0][0]
            self.seterminoalgo=True
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]
        """if self.colalisto[0][4]==0:
            del self.colalisto[0]"""
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0] and self.clock==self.colagantt[-1][7]:
          self.colagantt[-1][4]=self.colagantt[-1][4]+1
          self.colagantt[-1][7]=self.clock+1
        else:
          self.colagantt.append(caux.copy())
          self.colagantt[-1].extend([self.clock,self.clock+1])
        print('colalisto',self.colalisto)
        print('colabloqueado',self.colabloqueado)
        print('colanuevo',self.colanuevo)
        print('colagantt',self.colagantt)
        
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
        self.tiempo=self.tiempoespera[str(self.colalisto[0][0])]
        if self.Mq:
          if rafita[0][0]==1 and self.tiempo[4][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        else:
          if rafita[0][0]==1 and self.tiempo[0][1]=='':
            self.cerrartiempo()
            self.tiempoespera.update({str(self.colalisto[0][0]):self.tiempo})
        if rafita[0][3]==0:
          if len(rafita)>1:
            self.colaauxiliarantirupturadegantt=self.colalisto[0].copy()
            
            #self.colabloqueado.append(self.colalisto[0].copy())
          else:
            self.procactual=self.colalisto[0][0]
            self.seterminoalgo=True
          del rafita[0]
          self.rafagas.update({str(self.colalisto[0][0]):rafita})
          del self.colalisto[0]
        """if self.colalisto[0][4]==0:
            del self.colalisto[0]"""
        if len(self.colagantt)>0 and self.colagantt[-1][0]==caux[0] and self.clock==self.colagantt[-1][7]:
          self.colagantt[-1][4]=self.colagantt[-1][4]+1
          self.colagantt[-1][7]=self.clock+1
        else:
          self.colagantt.append(caux.copy())
          self.colagantt[-1].extend([self.clock,self.clock+1])
        print('colalisto',self.colalisto)
        print('colabloqueado',self.colabloqueado)
        print('colanuevo',self.colanuevo)
        print('colagantt',self.colagantt)

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
        print("cola listo antes de buscar algoritmo",self.colalisto)
        if valor==0:
            print("RR")
            self.RR()
        if valor ==1:
            print("FCFS")
            self.FCFS()
        if valor ==2:
            print("prio")
            self.PRIORIDAD()
        if valor ==3:
            print("srtf")
            self.SRTF()
 
   def EjecutarMQ():
        if len(self.colas_multinivel[0])>0:
            print('cola 0',self.colas_multinivel[0])
            self.quantom=self.colaquantum[0]
            self.q=self.listaq[0]
            buscarAlgoritmo(self.listAlgoritmoInt[0],self.colas_multinivel[0])
            self.listaq[0]=self.q
        elif len(self.colas_multinivel[1])>0:
            print('cola 1',self.colas_multinivel[1])
            self.quantom=self.colaquantum[1]
            self.q=self.listaq[1]
            buscarAlgoritmo(self.listAlgoritmoInt[1],self.colas_multinivel[1])
            self.listaq[1]=self.q
        elif len(self.colas_multinivel[2])>0:
            print('cola 2',self.colas_multinivel[2])
            self.quantom=self.colaquantum[2]
            self.q=self.listaq[2]
            buscarAlgoritmo(self.listAlgoritmoInt[2],self.colas_multinivel[2])
            self.listaq[2]=self.q
        elif len(self.colas_multinivel[3])>0:
            print('cola 3',self.colas_multinivel[3])
            self.quantom=self.colaquantum[3]
            self.q=self.listaq[3]
            buscarAlgoritmo(self.listAlgoritmoInt[3],self.colas_multinivel[3])
            self.listaq[3]=self.q
        elif len(self.colas_multinivel[4])>0:
            print('cola 4',self.colas_multinivel[4])
            self.quantom=self.colaquantum[4]
            self.q=self.listaq[4]
            buscarAlgoritmo(self.listAlgoritmoInt[4],self.colas_multinivel[4])
            self.listaq[4]=self.q
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

 def iniciartiempo(self):
   #fcfs,prioridad,rr,srtf,mq
   if self.comboBox_Algoritmos.currentText() == 'PRIORIDADES':
     self.tiempo[1]=[self.clock,'']
   if self.comboBox_Algoritmos.currentText() == 'FCFS':
     self.tiempo[0]=[self.clock,'']
   if self.comboBox_Algoritmos.currentText() == 'RR':
     self.tiempo[2]=[self.clock,'']
   if self.comboBox_Algoritmos.currentText() == 'SRTF':
     self.tiempo[3]=[self.clock,'']
   if self.comboBox_Algoritmos.currentText() =='COLAS MULTINIVEL':
     self.tiempo[4]=[self.clock,'']
   
 def cerrartiempo(self):
   #fcfs,prioridad,rr,srtf,mq
   if self.seterminoalgo==True:
     clock=self.clock+1
   else:
     clock=self.clock
   #----------------------------------------------------------
   if self.comboBox_Algoritmos.currentText() == 'PRIORIDADES':
     self.tiempo[1][1]=clock
   if self.comboBox_Algoritmos.currentText() == 'FCFS':
     self.tiempo[0][1]=clock
   if self.comboBox_Algoritmos.currentText() == 'RR':
     self.tiempo[2][1]=clock
   if self.comboBox_Algoritmos.currentText() == 'SRTF':
     self.tiempo[3][1]=clock
   if self.comboBox_Algoritmos.currentText() =='COLAS MULTINIVEL':
     self.tiempo[4][1]=clock

 def asignacion_memoria(self):
  print('entre aqui')
  if not self.dialogresultsim.pushButtonStop.isEnabled():
    self.dialogresultsim.pushButtonStop.setEnabled(True)
  if self.dialogresultsim.pushButtonStart.isEnabled():
    self.dialogresultsim.pushButtonStart.setEnabled(False)
  for i in self.lista_graficos:
    i[2]='disponible'
    i[4]=0
    i[5]=0
  if self.comboBox_Algoritmos.currentText() =='COLAS MULTINIVEL':  
    self.Mq=True
    self.limites()
    self.listaq=self.colaquantum.copy()
  else:
    self.Mq=False
  self.clock=0
  self.stop=False
  #self.dialogresultsim.spinBoxClock.setValue(self.clock)
  print('puede ser que entre de nuevo aqui?',self.clock)
  self.dialogresultsim.spinBoxClock.setValue(0)
  print(self.dialogresultsim.spinBoxClock.value())
  self.rafagas={}
  self.mapaporclock=[]
  self.colanuevoporclock=[]
  self.colalistoporclock=[]
  self.colabloqueadoporclock=[]
  self.colagantt=[]
  self.colaesgantt=[]
  self.colaarribo=[]
  self.colanuevo=[]
  self.colalisto=[]
  self.colabloqueado=[]
  self.colaauxiliarantirupturadegantt=[]
  
  self.dialogresultsim.spinBoxClock.setMaximum(9999)
  self.show_colalistoybloq()
  self.quantom = self.spinBox_Quantum.value()
  self.q=self.quantom
  if(self.radioButton_Fijas.isChecked()):
    for i in self.lista_graficos:
      i[2]='disponible'
    self.asignacion_fija()
  if(self.radioButton_Variables.isChecked()):
    #['idpart',dir_rli,part_size,idpc]
    self.mem_variable=[[0,0,self.valor_memoria_procesos,0]]
    self.asignacion_variable()
  if not self.dialogresultsim.pushButton_verGantt.isEnabled():
    self.dialogresultsim.pushButton_verGantt.setEnabled(True)
  self.disable_stop()
  self.enable_start()
  print('ACA MIRA LOS RESULTADO DE TIEMPO',self.tiempoespera)
  print('Y ACA VA RETORNO',self.tiemporetorno)

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
        print('cola nuevo antes de asignar',self.colanuevo)
        while i<len(self.colanuevo):
            print('dentro del while grande',self.colanuevo)
            j=0
            tipo=self.mem_variable[j][3]
            while (j<len(self.mem_variable) and not(tipo==0 and self.colanuevo[i][3]<=self.mem_variable[j][2])):
                tipo=self.mem_variable[j][3]
                j=j+1
            if j>=len(self.mem_variable):
              if j!=0:
                j=j-1
                print('entre')
            tipo=self.mem_variable[j][3]
            print('aber el tipo',tipo,'la memoria libre que encontro',self.mem_variable[j],'y el proceso',self.colanuevo[i],i)
            if j<len(self.mem_variable):
                print('entre qui')
                if tipo==0 and self.colanuevo[i][3]<=self.mem_variable[j][2]:
                    print('pero no aqui o si?')
                    nuevotam=self.mem_variable[j][2]-self.colanuevo[i][3]
                    nuevodir=self.mem_variable[j][1]+self.colanuevo[i][3]
                    if nuevotam==0:
                        self.mem_variable[j]=[self.idpart,self.mem_variable[j][1],self.colanuevo[i][3],self.colanuevo[i][0]]
                    else:
                        self.mem_variable[j]=[self.idpart,self.mem_variable[j][1],self.colanuevo[i][3],self.colanuevo[i][0]]
                        self.mem_variable.insert(j+1,[0,nuevodir,nuevotam,0])
                    #['idpart',dir_rli,part_size,idpc]
                    #self.mem_variable[j]

                    #CREEEEO QUE ACA, antes que incremente el self.idpart, hay que cargar en la BD
                    #(pls no me odies si me estoy mandando una re cagada jajajaja)
                    #okey, pq se me hace que estoy por hacer cagadas aca ajajja 
                   
                    #['idpc','Descripcion','Prioridad','Tamaño','TI','TA','InicioGantt','FinGantt']
                    self.idpart=self.idpart+1
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
                      print('Colas multinivel despues de asignar',self.colas_multinivel)
                    else:
                      self.colalisto.append(self.colanuevo[i].copy())

                      print('Cola listo despues de asignar',self.colalisto)
                    #iniciar tiempo espera
                    if str(self.colanuevo[i][0]) in self.tiempoespera:
                      self.tiempo=self.tiempoespera[str(self.colanuevo[i][0])]
                    else:
                      self.tiempo=[[],[],[],[],[]]
                    self.iniciartiempo()
                    self.tiempoespera.update({str(self.colanuevo[i][0]):self.tiempo})
                    #iniciar tiempo retorno
                    if str(self.colanuevo[i][0]) in self.tiemporetorno:
                      self.tiempo=self.tiemporetorno[str(self.colanuevo[i][0])]
                    else:
                      self.tiempo=[[],[],[],[],[]]
                    self.iniciartiempo()
                    self.tiemporetorno.update({str(self.colanuevo[i][0]):self.tiempo})
                    
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
                      #
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
        
        print("asi quedo la memoria",self.mem_variable)
   #['idpart',dir_rli,part_size,idpc]
   #['idpc','Descripcion','Prioridad','Tamaño','TI','TA'] 
   self.idpart=1
   self.b=True
   j=0
   print("variable")
   self.procesos_sin_asignar=self.listaprocesos.copy()
   self.procesos_sin_asignar.sort(key=lambda m: m[5])
   print('procesos antes de asignacion',self.procesos_sin_asignar)
   while self.b:
     print('SOY EL CLOOOOOOCK',self.clock)
     self.seterminoalgo=False
     self.colaarribo=[]
     while j<len(self.procesos_sin_asignar) and self.procesos_sin_asignar[j][5]==self.clock:
       self.colaarribo.append(self.procesos_sin_asignar[j])
       j=j+1
     if len(self.colaarribo)>0:
       self.arribo()
     print('cola nuevo antes de asignacion v',self.colanuevo)
     
     asignacion_v()
     self.colanuevoporclock.append(deepcopy(self.colanuevo))
     if self.Mq:
       aux=[]
       for i in self.colas_multinivel:
         aux.extend(deepcopy(i))
       self.colalistoporclock.append(deepcopy(aux))
     else:
       self.colalistoporclock.append(deepcopy(self.colalisto))
     self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
     print('colalistoporclock',self.colalistoporclock)
     
     #iniciar rafaga CPU
     """
     if self.colalisto:
       print('entre aca?',self.clock)
       rafita=self.rafagas[str(self.colalisto[0][0])]
       if (not self.rafagacpuactualporclock) or (len(self.rafagacpuactualporclock)<=self.clock):
         if rafita[0][3]!=0:
           self.rafagacpuactualporclock.append(rafita[0].copy())
     else:
       self.rafagacpuactualporclock.append([])
     """

     #iniciar rafaga ES
     """if self.colabloqueado:
       rafita=self.rafagas[str(self.colabloqueado[0][0])]
       if rafita[0][3]!=0:
         if (not self.rafagaesactualporclock) or (len(self.rafagaesactualporclock)<=self.clock):
           self.rafagaesactualporclock.append(deepcopy(self.rafagaesactual.copy()))
           #self.rafagaesactualporclock.append(rafita[0].copy())
     else:
       self.rafagaesactualporclock.append([])
     """
     #
     self.show_colalistoybloq()
     self.ejecutar_algoritmos()
     self.entrada_salida()

     if len(self.colaauxiliarantirupturadegantt)>0:
       self.colabloqueado.append(self.colaauxiliarantirupturadegantt.copy())
       self.colaauxiliarantirupturadegantt=[]
     self.mapa_de_memoria_variable()
     
     plt.waitforbuttonpress(timeout=0.5)
     self.mapaporclock.append(deepcopy(self.mem_variable))
    
     if self.seterminoalgo==True:
       #cerrar tiempo retorno
       self.tiempo=self.tiemporetorno[str(self.procactual)]
       self.cerrartiempo()
       self.tiemporetorno.update({str(self.procactual):self.tiempo})
       #liberar particion
       self.liberarparticion()
     self.clock=self.clock+1
     print('aqui aumenta supus',self.clock)
     self.dialogresultsim.spinBoxClock.setValue(self.clock)
     
     print('memoria despues de asignacion',self.mem_variable)
     
     if self.Mq:
       if (len(self.colanuevo)==0 and len(self.colaarribo)==0 and len(self.colabloqueado)==0 and len(self.procesos_sin_asignar)<=j and (len(self.colas_multinivel[0])==0) and (len(self.colas_multinivel[1])==0) and (len(self.colas_multinivel[2])==0) and (len(self.colas_multinivel[3])==0) and (len(self.colas_multinivel[4])==0)):
         self.b=False
         self.mapaporclock.append(deepcopy(self.mem_variable))
         self.mapa_de_memoria_variable()
         self.colanuevoporclock.append(deepcopy(self.colanuevo))
         aux=[]
         for i in self.colas_multinivel:
           aux.extend(deepcopy(i))
         self.colalistoporclock.append(deepcopy(aux))
         self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
         self.show_colalistoybloq()
         
     else:
       if len(self.colalisto)==0 and len(self.colanuevo)==0 and len(self.colabloqueado)==0 and len(self.colaarribo)==0 and len(self.procesos_sin_asignar)<=j:
         self.b=False
         self.mapaporclock.append(deepcopy(self.mem_variable))
         self.mapa_de_memoria_variable()
         self.colanuevoporclock.append(deepcopy(self.colanuevo))
         self.colalistoporclock.append(deepcopy(self.colalisto))
         self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
         self.show_colalistoybloq()
         
 def enable_start(self):
   if not self.dialogresultsim.pushButtonStart.isEnabled():
     self.dialogresultsim.pushButtonStart.setEnabled(True)
   
 def disable_stop(self):
   if self.dialogresultsim.pushButtonStop.isEnabled():
     self.dialogresultsim.pushButtonStop.setEnabled(False)

 def show_colalistoybloq(self):
   #Obtencion de datos a mostrar
   if self.colanuevoporclock:
     colanuevo=deepcopy(self.colanuevoporclock[self.dialogresultsim.spinBoxClock.value()])
   else:
     colanuevo=[]
   if self.colalistoporclock:
     colalisto=deepcopy(self.colalistoporclock[self.dialogresultsim.spinBoxClock.value()])
   else:
     colalisto=[]
   if self.colabloqueadoporclock:
     colabloqueado=deepcopy(self.colabloqueadoporclock[self.dialogresultsim.spinBoxClock.value()])
   else:
     colabloqueado=[]
   print("COLA DE BLOQUEADOOOOOO",colabloqueado)
   print("COLA LISTOOOOOOOOOOOOO",colalisto)
   print("COLA NUEVOOOOOOOOOOOOO",colanuevo)
   
   
   #Grado multiprogramacion
   self.grado_multiprogramacion=len(colalisto)+len(colabloqueado)
   self.dialogresultsim.labelGradoMulti.setText("Grado Multiprogramacion:"+str(self.grado_multiprogramacion))  
   
   #Limpiar filas anteriores
   for w in range(self.dialogresultsim.tableWidgetCNuevo.rowCount()):
     self.dialogresultsim.tableWidgetCNuevo.removeRow(0)

   for w1 in range(self.dialogresultsim.tableWidgetCListo.rowCount()):
     self.dialogresultsim.tableWidgetCListo.removeRow(0)

   for w2 in range(self.dialogresultsim.tableWidgetCBloqueado.rowCount()):
     self.dialogresultsim.tableWidgetCBloqueado.removeRow(0)

   #Mostrar datos actualizados
   for z in range(0,len(colanuevo)):
     self.dialogresultsim.tableWidgetCNuevo.insertRow(z)
     self.dialogresultsim.tableWidgetCNuevo.setItem(z,0,QTableWidgetItem(str(colanuevo[z][0])))
     
   for z1 in range(0,len(colalisto)):
     self.dialogresultsim.tableWidgetCListo.insertRow(z1)
     self.dialogresultsim.tableWidgetCListo.setItem(z1,0,QTableWidgetItem(str(colalisto[z1][0])))
     #self.dialogresultsim.tableWidgetCListo.setItem(z1,1,QTableWidgetItem(str(cpuactual[z1][3])))
     self.dialogresultsim.tableWidgetCListo.setItem(z1,1,QTableWidgetItem(str(colalisto[z1][4])))
     
   for z2 in range(0,len(colabloqueado)):
     self.dialogresultsim.tableWidgetCBloqueado.insertRow(z2)
     self.dialogresultsim.tableWidgetCBloqueado.setItem(z2,0,QTableWidgetItem(str(colabloqueado[z2][0])))
     self.dialogresultsim.tableWidgetCBloqueado.setItem(z2,1,QTableWidgetItem(str(colabloqueado[z2][6])))

 def entrada_salida(self):
    print("entrada salida")
    if len(self.colabloqueado)>0:
        caux=self.colabloqueado[0].copy()
        caux[4]=1
        self.colabloqueado[0][6]=self.colabloqueado[0][6]-1
        rafita=self.rafagas[str(self.colabloqueado[0][0])]
        print('ESTE ES RAFITA ANTES DE DECREMENTAR',rafita)
        rafita[0][3]=rafita[0][3]-1
        print("ESTE ES RAFITA DESPUES DE DECREMENTAR",rafita)
        
        self.rafagas.update({str(self.colabloqueado[0][0]):rafita})
        print("RAFAGA",self.rafagas)
        if rafita[0][3]==0:
          if len(rafita)>1:
            if self.Mq:
              if self.colabloqueado[0][2] >=self.limites_colas[0][0] and self.colabloqueado[0][2] <=self.limites_colas[0][1] :
                self.colas_multinivel[0].append(self.colabloqueado[0].copy())
              if self.colabloqueado[0][2] >=self.limites_colas[1][0] and self.colabloqueado[0][2] <=self.limites_colas[1][1] :
                self.colas_multinivel[1].append(self.colabloqueado[0].copy())
              if self.colabloqueado[0][2] >=self.limites_colas[2][0] and self.colabloqueado[0][2] <=self.limites_colas[2][1] :
                self.colas_multinivel[2].append(self.colabloqueado[0].copy())
              if self.colabloqueado[0][2] >=self.limites_colas[3][0] and self.colabloqueado[0][2] <=self.limites_colas[3][1] :
                self.colas_multinivel[3].append(self.colabloqueado[0].copy())
              if self.colabloqueado[0][2] >=self.limites_colas[4][0] and self.colabloqueado[0][2] <=self.limites_colas[4][1] :
                self.colas_multinivel[4].append(self.colabloqueado[0].copy())
            else:
              self.colalisto.append(self.colabloqueado[0].copy())
              #todavia no borra rafita de ES
              
              print('entre aca en bloqueados volviendo a listo')
              
          del rafita[0]
          self.rafagas.update({str(self.colabloqueado[0][0]):rafita})
          del self.colabloqueado[0]
        """
        if self.colalisto[0][4]==0:
          del self.colalisto[0]
        """
        #a esto cambiale colagantt por colaesgantt
        if len(self.colaesgantt)>0 and self.colaesgantt[-1][0]==caux[0] and self.clock==self.colaesgantt[-1][7]:
          self.colaesgantt[-1][4]=self.colaesgantt[-1][4]+1
          self.colaesgantt[-1][7]=self.clock+1
        else:
          self.colaesgantt.append(caux.copy())
          self.colaesgantt[-1].extend([self.clock,self.clock+1])


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
                   #iniciar tiempo espera
                   if str(self.colanuevo[i][0]) in self.tiempoespera:
                     self.tiempo=self.tiempoespera[str(self.colanuevo[i][0])]
                   else:
                     self.tiempo=[[],[],[],[],[]]
                   self.iniciartiempo()
                   self.tiempoespera.update({str(self.colanuevo[i][0]):self.tiempo})
                   #iniciar tiempo retorno
                   if str(self.colanuevo[i][0]) in self.tiemporetorno:
                     self.tiempo=self.tiemporetorno[str(self.colanuevo[i][0])]
                   else:
                     self.tiempo=[[],[],[],[],[]]
                   self.iniciartiempo()
                   self.tiemporetorno.update({str(self.colanuevo[i][0]):self.tiempo})

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
                   j=j+1
                   #i=i+1
           else:
               i=i+1  
   self.procesos_sin_asignar=self.listaprocesos.copy()
   self.procesos_sin_asignar.sort(key=lambda m: m[5])
   j=0
   self.b=True
   while self.b:
     self.seterminoalgo=False
     self.colaarribo=[]
     while j<len(self.procesos_sin_asignar) and self.procesos_sin_asignar[j][5]==self.clock:
       self.colaarribo.append(self.procesos_sin_asignar[j])
       j=j+1
     if len(self.colaarribo)>0:
       self.arribo()
     asignacion_f()
     self.colanuevoporclock.append(deepcopy(self.colanuevo))
     if self.Mq:
       aux=[]
       for i in self.colas_multinivel:
         aux.extend(deepcopy(i))
       self.colalistoporclock.append(deepcopy(aux))
     else:
       self.colalistoporclock.append(deepcopy(self.colalisto))
     self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
     self.show_colalistoybloq()
     
     self.ejecutar_algoritmos()
     self.entrada_salida()
     if len(self.colaauxiliarantirupturadegantt)>0:
       self.colabloqueado.append(self.colaauxiliarantirupturadegantt.copy())
       self.colaauxiliarantirupturadegantt=[]
     self.mapa_de_memoria_fija()

     plt.waitforbuttonpress(timeout=0.5)
     self.mapaporclock.append(deepcopy(self.lista_graficos))
     
     if self.seterminoalgo==True:
       #cerrar tiempo retorno
       self.tiempo=self.tiemporetorno[str(self.procactual)]
       self.cerrartiempo()
       self.tiemporetorno.update({str(self.procactual):self.tiempo})
       #liberar particion
       self.liberarparticion()
     self.clock=self.clock+1
     self.dialogresultsim.spinBoxClock.setValue(self.clock)
     #Condicion de fin
     if self.Mq:
       if (len(self.colanuevo)==0 and len(self.colaarribo)==0 and len(self.colabloqueado)==0 and len(self.procesos_sin_asignar)<=j and (len(self.colas_multinivel[0])==0) and (len(self.colas_multinivel[1])==0) and (len(self.colas_multinivel[2])==0) and (len(self.colas_multinivel[3])==0) and (len(self.colas_multinivel[4])==0)):
         self.b=False
         self.mapaporclock.append(deepcopy(self.lista_graficos))
         self.mapa_de_memoria_fija()
         self.colanuevoporclock.append(deepcopy(self.colanuevo))
         aux=[]
         for i in self.colas_multinivel:
           aux.extend(deepcopy(i))
         self.colalistoporclock.append(deepcopy(aux))
         self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
         self.show_colalistoybloq()
     else:
       if len(self.colalisto)==0 and len(self.colanuevo)==0 and len(self.colabloqueado)==0 and len(self.colaarribo)==0 and len(self.procesos_sin_asignar)<=j:
         self.b=False
         self.mapaporclock.append(deepcopy(self.lista_graficos))
         self.mapa_de_memoria_fija()
         self.colanuevoporclock.append(deepcopy(self.colanuevo))
         self.colalistoporclock.append(deepcopy(self.colalisto))
         self.colabloqueadoporclock.append(deepcopy(self.colabloqueado))
         self.show_colalistoybloq()

  
 def abortar(self):
   self.b=False
   self.stop=True
   self.enable_start()
   
   print('ENTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

 def mostrarResultSimulacion(self):
   #self.fig= plt.figure('Mapa de memoria',figsize=(15,2))
   #self.a,self.ax=plt.subplots(figsize=(15,2))
   #self.ax.set_title('Mapa de memoria')
   self.b=True
   self.rafagas={}
   self.mapaporclock=[]
   self.colanuevoporclock=[]
   self.colalistoporclock=[]
   self.colabloqueadoporclock=[]
   print('colalistoporclock',self.colalistoporclock)
   self.colagantt=[]
   self.colaesgantt=[]
   self.colaarribo=[]
   self.colanuevo=[]
   self.colalisto=[]
   self.colabloqueado=[]
   self.colaauxiliarantirupturadegantt=[]

   self.dialogresultsim.spinBoxClock.setMaximum(999999)
   self.show_colalistoybloq()
   if not self.dialogresultsim.pushButtonStart.isEnabled():
     self.dialogresultsim.pushButtonStart.setEnabled(True)
   self.fig= plt.figure('Mapa de memoria',figsize=(15,2))
   plt.ion()
   self.ax=self.fig.subplots()
   global cont_sim_2davez
   if cont_sim_2davez >=0:
    self.dialogresultsim.move(640,315)
    self.dialogresultsim.exec_()
    cont_sim_2davez = 0
    if self.dialogresultsim.pushButton_verGantt.isEnabled():
      self.dialogresultsim.pushButton_verGantt.setEnabled(False)
   
 def limpiarComparacion(self):
   for i1 in range(0,self.dialogcompara.tableWidgetTEspera.rowCount()):
     self.dialogcompara.tableWidgetTEspera.removeRow(0)
   for i2 in range(0,self.dialogcompara.tableWidgetTRetorno.rowCount()):
     self.dialogcompara.tableWidgetTRetorno.removeRow(0)
   for i3 in range(0,self.dialogcompara.tableWidgetTEsperaP.rowCount()):
     self.dialogcompara.tableWidgetTEsperaP.removeRow(0)
   for i3 in range(0,self.dialogcompara.tableWidgetTRetornoP.rowCount()):
     self.dialogcompara.tableWidgetTRetornoP.removeRow(0)

 def mostrarComparacion(self):
   self.limpiarComparacion()
   print("holaaaa entre")
   tiempoespera=[]
   tiemporetorno=[]
   promTE=[[],[],[],[],[]]
   promTR=[[],[],[],[],[]]
   nTE=[0,0,0,0,0]
   nTR=[0,0,0,0,0]
   ultima_fila_tabla_TE=0
   ultima_fila_tabla_TR=0
   #fcfs,prioridad,rr,srtf,mq
   #Tiempo espera
   for keye in self.tiempoespera:
     #print("aberrrr",self.tiempoespera[keye])
     tiempoespera=(self.tiempoespera[keye])
     nueva_idpc= QTableWidgetItem(str(keye))
     self.dialogcompara.tableWidgetTEspera.insertRow(ultima_fila_tabla_TE)
     self.dialogcompara.tableWidgetTEspera.setItem(ultima_fila_tabla_TE,0,nueva_idpc)
     col=0
     for i in tiempoespera:
       print('tiempo espera',i)
       if i:
         valor=i[1]-i[0]
         if promTE[col]:
           promTE[col]=promTE[col]+valor
         else:
           promTE[col]=valor
           print('aber que pasa aca con TE',promTE[col])
         valor=str(valor)
         nTE[col]=nTE[col]+1
       else:
         valor='-'
       col=col+1
       item=QTableWidgetItem(valor)
       self.dialogcompara.tableWidgetTEspera.setItem(ultima_fila_tabla_TE,col,item)
     ultima_fila_tabla_TE=ultima_fila_tabla_TE+1
   #Promedio Tiempo Espera
   self.dialogcompara.tableWidgetTEsperaP.insertRow(0)
   for i in range(5):
     if promTE[i] or promTE[i]==0:
       if promTE[i]==0:
         valor=str(0)
       else:
         valor=str(round((promTE[i]/nTE[i]),2))
     else:
       valor='-'
     item=QTableWidgetItem(valor)
     self.dialogcompara.tableWidgetTEsperaP.setItem(0,i,item)
   #Tiempo retorno
   for keyr in self.tiemporetorno:
     #print("aberrrr",self.tiemporetorno[keyr])
     tiemporetorno=(self.tiemporetorno[keyr])
     nueva_idpc= QTableWidgetItem(str(keyr))
     self.dialogcompara.tableWidgetTRetorno.insertRow(ultima_fila_tabla_TR)
     self.dialogcompara.tableWidgetTRetorno.setItem(ultima_fila_tabla_TR,0,nueva_idpc)
     col=0
     for i in tiemporetorno:
       if i:
         valor=i[1]-i[0]
         if promTR[col]:
           promTR[col]=promTR[col]+valor
           print('aber que pasa aca',promTR[col])
         else:
           promTR[col]=valor
         valor=str(valor)
         nTR[col]=nTR[col]+1
       else:
         valor='-'
       col=col+1
       item=QTableWidgetItem(valor)
       self.dialogcompara.tableWidgetTRetorno.setItem(ultima_fila_tabla_TR,col,item)
     ultima_fila_tabla_TR=ultima_fila_tabla_TR+1
   #Promedio Tiempo Retorno
   self.dialogcompara.tableWidgetTRetornoP.insertRow(0)
   for i in range(5):
     if promTR[i] or promTR[i]==0:
       if promTR[i]==0:
         valor=str(0)
       else:
         valor=str(round((promTR[i]/nTR[i]),2))
     else:
       valor='-' 
     item=QTableWidgetItem(valor)
     self.dialogcompara.tableWidgetTRetornoP.setItem(0,i,item)
   
   self.dialogcompara.exec_()


 def limpiar_ventanaImportar(self):
   self.listaImportarProcesos=[]
   for i6 in range(0,self.dialogoImportar.tableWidgetImportar.rowCount()):
     self.dialogoImportar.tableWidgetImportar.removeRow(0)
   self.listaIDprocesosventImportar=[]
   self.dialogoImportar.label_PC.setText("Procesos:") 
   self.dialogoImportar.label_error.setText("")
   self.dialogoImportar.labelEPI.setText("")
   if self.dialogoImportar.pushButtonImportar.isEnabled():
     self.dialogoImportar.pushButtonImportar.setEnabled(False)

 def update_tablaProcesos(self):
   print(self.listaImportarProcesos)
   #
   print("Esta es la lista de los que puedo",self.listaIDprocesosventImportar)
   self.dialogoImportar.label_error.setText("")
   self.dialogoImportar.labelEPI.setText("")
   supera_tam=False
   proceso_cargado=False

   for i in self.listaImportarProcesos:
     
     print(self.result[i-1])
     
     if self.radioButton_Variables.isChecked():
       print("lista id de procesoooos ",self.listaIDprocesos)
       
       if self.result[i-1][3] >self.valor_memoria_procesos:
           supera_tam=True
       else: 
         if self.result[i-1][0] not in self.listaIDprocesos:
           #self.dialogoImportar.label_error.setText("")
           self.listaIDprocesos.append(self.result[i-1][0])
           self.listaprocesos.append([self.result[i-1][0],self.result[i-1][1],self.result[i-1][2],self.result[i-1][3],self.result[i-1][4],self.result[i-1][6],self.result[i-1][5]])
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
           proceso_cargado=True
           
     if self.radioButton_Fijas.isChecked():
       if self.result[i-1][3]>self.tamPartFijMax:
         supera_tam=True
         #self.dialogoImportar.labelEPI.setText("Tamaño procesos invalidos. Controlar procesos cargados")
         """if self.comboBox_Algoritmos.isEnabled():
           self.comboBox_Algoritmos.setEnabled(False)

         if self.label_Algoritmo.isEnabled():
           self.label_Algoritmo.setEnabled(False)
    
         if self.spinBox_Quantum.isEnabled():
           self.spinBox_Quantum.setEnabled(False)

         if self.label_Quantum.isEnabled():
           self.label_Quantum.setEnabled(False)
        
         if self.pushButton_AceptarProc.isEnabled():
           self.pushButton_AceptarProc.setEnabled(False)

         if self.pushButtonComparar.isEnabled():
           self.pushButtonComparar.setEnabled(True)

         if self.pushButton_Simular.isEnabled():
           self.pushButton_Simular.setEnabled(False)"""
       else:
         """
         self.dialogoImportar.labelEPI.setText("")
         if not self.comboBox_Algoritmos.isEnabled():
           
           self.comboBox_Algoritmos.setEnabled(True)

         if not self.label_Algoritmo.isEnabled():
           self.label_Algoritmo.setEnabled(True)
    
         if not self.spinBox_Quantum.isEnabled():
           self.spinBox_Quantum.setEnabled(True)

         if not self.label_Quantum.isEnabled():
           self.label_Quantum.setEnabled(True)
        
         if not self.pushButton_AceptarProc.isEnabled():
           self.pushButton_AceptarProc.setEnabled(True)

         if not self.pushButtonComparar.isEnabled():
           self.pushButtonComparar.setEnabled(True)

         if not self.pushButton_Simular.isEnabled():
           self.pushButton_Simular.setEnabled(True)
         """
         if self.result[i-1][0] not in self.listaIDprocesos:
           #self.dialogoImportar.label_error.setText("")
           self.listaIDprocesos.append(self.result[i-1][0])
           self.listaprocesos.append([self.result[i-1][0],self.result[i-1][1],self.result[i-1][2],self.result[i-1][3],self.result[i-1][4],self.result[i-1][6],self.result[i-1][5]])
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
           proceso_cargado=True
           #self.dialogoImportar.label_error.setText("Error: el proceso seleccionado ya esta cargado")
   
     
     
     print('aaaaa',self.listaIDprocesos)
   
   if supera_tam:
     self.dialogoImportar.labelEPI.setText("Tamaño procesos invalidos. Controlar procesos cargados")
     """if self.comboBox_Algoritmos.isEnabled():
       self.comboBox_Algoritmos.setEnabled(False)
     if self.label_Algoritmo.isEnabled():
       self.label_Algoritmo.setEnabled(False)
     if self.spinBox_Quantum.isEnabled():
       self.spinBox_Quantum.setEnabled(False)
     if self.label_Quantum.isEnabled():
       self.label_Quantum.setEnabled(False) 
     if self.pushButton_AceptarProc.isEnabled():
       self.pushButton_AceptarProc.setEnabled(False)
     if self.pushButtonComparar.isEnabled():
       self.pushButtonComparar.setEnabled(True)
     if self.pushButton_Simular.isEnabled():
       self.pushButton_Simular.setEnabled(False)"""
      #si, parece que si

   if proceso_cargado:
     self.dialogoImportar.label_error.setText("Error: el proceso seleccionado ya esta cargado")
  


   """  
   if not self.pushButton_AceptarProc.isEnabled():
     self.pushButton_AceptarProc.setEnabled(True)
   if not self.comboBox_Algoritmos.isEnabled():
     self.comboBox_Algoritmos.setEnabled(True)
   if not self.spinBox_Quantum.isEnabled():
     self.spinBox_Quantum.setEnabled(True)
   if not self.pushButton_Simular.isEnabled():
     self.pushButton_Simular.setEnabled(True)
   """
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
     #self.mem_variable=[[0,0,self.valor_memoria_procesos,0]]
     self.mapa_de_memoria_variable()
 
 def animate_variable(self):
   category_names=[]
   ys=[]
   i=0
   for elemento in self.mem_variable:
     if len(elemento)>1:
       if elemento[3]==0:
         category_names.append('Idpart: '+str(elemento[0])+'\nIdpc: Libre\nFragInt:'+str(0))
       else:
         category_names.append('Idpart: '+str(elemento[0])+'\nIdpc:    '+ str(elemento[3])+'\nFragInt:'+str(0))
       ys.append(elemento[2])
       i=i+1
   results={'mem':ys}
   #print(results)
   labels = list(results.keys())
   data = np.array(list(results.values()))
   data_cum = data.cumsum(axis=1)
   category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[1]))
   #fig, ax = plt.subplots(figsize=(9.2, 5))
   self.ax.clear()
   self.ax.invert_yaxis()
   self.ax.xaxis.set_visible(True)
   self.ax.set_xlim(0, np.sum(data, axis=1).max())
   #print('llegue aqui')
   #verrrrrrrrrrrrr
   for i, (colname, color) in enumerate(zip(category_names, category_colors)):
     widths = data[:, i]
     starts = data_cum[:, i] - widths
     self.ax.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)
     xcenters = starts + widths / 2
     r, g, b, _ = color
     text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
     for y, (x, c) in enumerate(zip(xcenters, widths)):
       self.ax.text(x, y, str(int(c)), ha='center', va='center',color=text_color)
   self.ax.legend(bbox_to_anchor=(1,1))
   #plt.show()

 def mapa_de_memoria_variable(self):
   self.ax.remove()
   self.ax=self.fig.subplots()
   self.animate_variable()
   plt.show() 

 def animate_fija(self):
   category_names=[]
   ys=[]
   i=0
   for elemento in self.lista_graficos:
     #print(elemento)
     if len(elemento)>1:
       category_names.append('Idpart: '+str(elemento[0])+'\nIdpc:    '+ str(elemento[4])+'\nFragInt:'+str(elemento[5]))
       ys.append(elemento[3])
       i=i+1       
   results={'mem':ys}
   #print(results)
   labels = list(results.keys())
   data = np.array(list(results.values()))
   data_cum = data.cumsum(axis=1)
   category_colors = plt.get_cmap('RdYlGn')(
   np.linspace(0.15, 0.45, data.shape[1]))
   #fig, ax = plt.subplots(figsize=(9.2, 5))
   self.ax.clear()
   self.ax.invert_yaxis()
   self.ax.xaxis.set_visible(True)
   self.ax.set_xlim(0, np.sum(data, axis=1).max())
   #print('llegue aqui')
   for i, (colname, color) in enumerate(zip(category_names, category_colors)):
     widths = data[:, i]
     starts = data_cum[:, i] - widths
     self.ax.barh(labels, widths, left=starts, height=0.5,label=colname, color=color)
     xcenters = starts + widths / 2
     r, g, b, _ = color
     text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
     for y, (x, c) in enumerate(zip(xcenters, widths)):
       self.ax.text(x, y, str(int(c)), ha='center', va='center', color=text_color)
   self.ax.legend(bbox_to_anchor=(1,1),loc='best')

 def mapa_de_memoria_fija (self):
   self.ax.remove()
   self.ax=self.fig.subplots()
   self.animate_fija()
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
     print("result",self.result)
     print("listaidprocesos",self.listaIDprocesosventImportar)
     for i in self.result:
       
       if i[0] not in self.listaIDprocesosventImportar:
        self.listaIDprocesosventImportar.append(i[0])
        idpc= QTableWidgetItem(str(i[0]))
        desc =QTableWidgetItem(str(i[1]))
        prioridad = QTableWidgetItem(str(i[2]))
        tam= QTableWidgetItem(str(i[3]))
        ti= QTableWidgetItem(str(i[4]))
        ta= QTableWidgetItem(str(i[6]))
        print("estoy tratando de mostrar en la tablaaaa")
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
   self.limpiar_ventanaImportar()

 def borrarProcesoCargado(self):
   nrorow=0
   nropro=0
   booleano=False
   for i in range(self.dialogo.tableWidgetProcesos.rowCount()):
     item=int(self.dialogo.tableWidgetProcesos.item(i,0).text())
     if (self.dialogo.spinBoxQuitar.value())==item:
       nropro=item
       nrorow=i
       booleano=True
   if booleano:
     self.dialogo.tableWidgetProcesos.removeRow(nrorow)
     noseencontro=True
     i=0
     while noseencontro:
       if self.listaprocesos[i][0]==nropro:
         self.listaprocesos.pop(i)
         noseencontro=False
       else:
         i=i+1
       print(self.listaprocesos)
     i=0
     noseencontro=True
     while noseencontro:
       print(self.listaIDprocesos[i])
       print('nropro',nropro)
       if self.listaIDprocesos[i]==nropro:
         self.listaIDprocesos.pop(i)
         noseencontro=False
       else:
         i=i+1
     self.checkproceso()
     print(self.listaIDprocesos)

         
   
   

   
 def agregar_fila_particiones(self):
   global cont_agregar_particion
   cont_agregar_particion=self.carga_particionFijas.tableWidgetCargaParticion.rowCount()
   tampart= int(self.carga_particionFijas.spinBoxTam.value())
   global rli
   global conts
   if cont_agregar_particion==0:
     rli=0
   if ((self.valor_memoria_procesos - tampart>=0) and self.valor_memoria_procesos != 0):
     self.valor_memoria_procesos= self.valor_memoria_procesos - tampart
     self.carga_particionFijas.label_MemDisp.setText("Memoria Disponible: "+str(round(self.valor_memoria_procesos,2)) + " KB")
     self.carga_particionFijas.tableWidgetCargaParticion.insertRow(cont_agregar_particion)
     id_sim = QTableWidgetItem(str(conts))
     tam_part = QTableWidgetItem(str(self.carga_particionFijas.spinBoxTam.value()))
     id_part=QTableWidgetItem(str(cont_agregar_particion+1))
     dir_rli=QTableWidgetItem(str(rli))
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,0,id_sim)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,3,tam_part)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,1,id_part)
     self.carga_particionFijas.tableWidgetCargaParticion.setItem(cont_agregar_particion,2,dir_rli)
     cont_agregar_particion+=1
     self.lista_graficos.append([cont_agregar_particion,rli,'disponible',tampart,0,0])
     rli=rli+tampart
     if(tampart>self.tamPartFijMax):
       self.tamPartFijMax=tampart
       print("tamano de particion fija maxima",self.tamPartFijMax)
     
     print("particion fija",self.lista_graficos)
     self.carga_particionFijas.spinBoxTam.setValue(0)
     self.carga_particionFijas.spinBoxTam.setMaximum(int(self.valor_memoria_procesos))

     
 def agregar_fila_rafagas(self):
   if not self.dialogo.spinBoxTiempo.value() ==0:
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
    tiempo = QTableWidgetItem(str(self.dialogo.spinBoxTiempo.value()))
    #tiempo = QTableWidgetItem(str(self.dialogo.lineEdit_Tiempo.text()))
    if self.dialogo.radioButtonES.isChecked():
      tipo = QTableWidgetItem("ES")
    if self.dialogo.radioButtonCPU.isChecked():
      tipo = QTableWidgetItem("CPU")


    
    self.dialogo.tableWidgetRafaga.setItem(contr,0,tipo)
    self.dialogo.tableWidgetRafaga.setItem(contr,1,tiempo)
    self.dialogo.spinBoxTiempo.setValue(0)
    #self.dialogo.lineEdit_Tiempo.setText('')
    contr=contr+1
    if self.dialogo.pushButtonAgregarRafaga.isEnabled():
      self.dialogo.pushButtonAgregarRafaga.setEnabled(False)
  
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
     connection = mysql.connector.connect(host=self.host,
     database = self.database,
     user=self.user,
     password=self.password)
     mySql_insert_query= """DELETE FROM part_fija WHERE idsim =(%s)""" 
     recordTuple=(conts,)
     cursor= connection.cursor()
     cursor.execute(mySql_insert_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
     connection.commit()
     print("se elimino las particiones anteriores") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
   except mysql.connector.Error as error:
     print("Fallo al conectarse {}",format(error))
   else:
     pass
   finally:
     if(connection.is_connected()):
      connection.close()
      print("Conexion cerrada")    
   #Insertar particiones
   try:
     #global conts
     connection = mysql.connector.connect(host=self.host,
     database = self.database,
     user=self.user,
     password=self.password)
     for elemento in self.lista_graficos:
       #print(elemento)
       if len(elemento)>1:
         category_names.append(elemento[0])
         ys.append(elemento[3])
         #print(conts, elemento[0], elemento[1], elemento[2], elemento[5],elemento[3])
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
   #print(results)
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
     self.tamPartFijMax=0;
     self.carga_particionFijas.spinBoxTam.setMinimum(1)
     self.carga_particionFijas.spinBoxTam.setMaximum(int(self.valor_memoria_procesos))
     self.carga_particionFijas.exec_()
     

   if self.radioButton_Variables.isChecked():
     if not self.boton_GestProcesos.isEnabled():
       #self.tamPartFijMax=9999999;
       self.boton_GestProcesos.setEnabled(True)
   
 def variableselected(self):
   if self.AceptarMem.isEnabled():
     self.AceptarMem.setEnabled(False)
   self.radioButton_Worst.setEnabled(True)
   if self.radioButton_Best.isChecked():
     self.radioButton_Best.setChecked(False)
   self.radioButton_Best.setEnabled(False)
   if not self.radioButton_First.isEnabled():
     self.radioButton_First.setEnabled(True)
   #nota: el set enable anda con los line Edit
 
 def fijaselected(self):
   #hace un disable del radio button de worst fit
   if self.AceptarMem.isEnabled():
     self.AceptarMem.setEnabled(False)
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
   if not self.comboBox_Algoritmos.isEnabled():
     self.comboBox_Algoritmos.setEnabled(True)
   if not self.spinBox_Quantum.isEnabled():
     self.spinBox_Quantum.setEnabled(True)

   def limpiar_carga_rafagas():
     global contr
     contr = 0
     self.dialogo.tableWidgetRafaga.setRowCount(0)
     self.dialogo.spinBoxTiempo.setValue(0)
     #self.dialogo.lineEdit_Tiempo.setText(" ")
     self.dialogo.lineEditDescrip.setText("")
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
     #['idpc','Descripcion','Prioridad','Tamaño','TI','TA','TI-ES','InicioGantt','FinGantt']
     sumti=0
     sumties=0
     for i in range(self.dialogo.tableWidgetRafaga.rowCount()):
         if self.dialogo.tableWidgetRafaga.item(i,0).text()=='CPU':
           sumti=sumti+int(self.dialogo.tableWidgetRafaga.item(i,1).text())
         if self.dialogo.tableWidgetRafaga.item(i,0).text()=='ES':
           sumties=sumties+int(self.dialogo.tableWidgetRafaga.item(i,1).text())
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
     mySql_update_query="""update procesos set ti=(%s), ti_es=(%s) where idpc = (%s)"""
     cursor= connection.cursor()
     recordTuple=(sumti,sumties,codpc)
     cursor.execute(mySql_update_query,recordTuple) # aca le paso la tupla, para que remplaze por los %s en la consulta
     connection.commit()
     print("ti actualizado") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
     cursor.close()
     #mostrar en la tabla el proceso cargado
     global contpc
     if codpc not in self.listaIDprocesos:
      self.listaIDprocesos.append(codpc)
      self.listaprocesos.append([codpc,descripcion,p_priori,tam_pro,sumti,t_arribo,sumties])
      id_pc = QTableWidgetItem(str(codpc))
      desc = QTableWidgetItem(descripcion)
      prio= QTableWidgetItem(str(p_priori))
      tampc = QTableWidgetItem(str(tam_pro))
      ti = QTableWidgetItem(str(sumti))
      ta = QTableWidgetItem(str(t_arribo))
      contpc=self.dialogo.tableWidgetProcesos.rowCount()
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
   if self.dialogo.pushButtonCargar.isEnabled():
     self.dialogo.pushButtonCargar.setEnabled(False)
   #aca limpio los valores que quedaron antes de cargar 
   
 def abrirDialogoCarga(self): #bueno, sentiende por el nombre lo que hace el metodo supongo, ejecuta la nueva ventana o dialogo de carga
   self.dialogo.spinBoxTamProc.setMinimum(1)
   self.dialogo.exec_()
   self.dialogo.lineEditDescrip.setText('')
   #self.dialogo.spinBoxTiempoarr.setText('')
   self.dialogo.spinBoxTamProc.setValue(0)
   self.dialogo.spinBoxPriori.setValue(0)
   #self.dialogo.pushButtonAgregarRafaga.setEnabled(False)
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
    print('MIRA ACA',self.colagantt)
    df = []
    
    for x in self.colagantt:
      res= 'Proceso '+str(x[0])
      #asumiendo que todo el formato de aca abajo esta en cada x que voy iterando
      #['idpc','Descripcion','Prioridad','Tamaño','TI','TA','TI-ES','InicioGantt','FinGantt']
      df.append(dict(Task="CPU",Start=x[7],Finish=x[8],Resource=res))
    
    for y in self.colaesgantt:
      res= 'Proceso '+str(y[0])
      df.append(dict(Task="ES", Start=y[7], Finish = y[8],Resource=res))
      

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
    self.web.load(local_url) #cargo la url, que seria la ruta del archivo generado .html
    self.web.setWindowTitle("Diagrama de Gantt")
    self.web.resize(1500,400) #defino nombre y tamaño de la ventana
    self.web.move(0,700)
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


