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
#para bd 
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
  
  self.cont=0
  self.carga_particionFijas = Particiones_Fijas()
  self.dialogresultsim = DialogoresultSim()
  self.dialogcompara = DialogoComparacion()
  #una vez que cargue la interfaz .ui e hice una instancia de Dialogo. me puedo referir a los elementos que fui poniendo en la interfaz, con sus nombres
  self.boton_GestProcesos.clicked.connect(self.abrirDialogoCarga)
  #self.botonGantt.clicked.connect(self.gantt)
  self.dialogo.pushButtonCargar.clicked.connect(self.cargarProcesosYRafagasenBD)
  self.AceptarMem.clicked.connect(self.mostrarCargaProcesos)
  self.tam_Memoria=0
  self.por_so=0 
  self.checkbox=QTableWidgetItem()
  self.valor_memoria_procesos=0
  self.contabla_raf=0
  self.lista_graficos=[]
  self.procesos_importados=[]
  self.result= []
  self.contador_act = 0
  self.label_MemProcesos.setText('')
  self.label_MemSO.setText('')
  self.spinBoxTamMemoria.setMaximum(1000000)
  self.spinBoxTamMemoria.setSingleStep(2**2)
  self.spinBoxPorcSO.setMaximum(90)
  self.spinBoxPorcSO.setSingleStep(5)
  self.spinBoxTamMemoria.valueChanged.connect(self.actTamMemoria)
  #self.spinBoxTamMemoria.valueChanged.connect(self.updateLabels)
  self.spinBoxPorcSO.valueChanged.connect(self.actPorcSO)
  self.spinBoxPorcSO.valueChanged.connect(self.updateLabels)
  self.spinBoxTamMemoria.valueChanged.connect(self.updateLabels)
  self.radioButton_Fijas.toggled.connect(self.fijaselected)
  self.radioButton_Variables.toggled.connect(self.variableselected)
  self.dialogo.tableWidgetRafaga.setColumnCount(2)
  self.dialogo.tableWidgetRafaga.setHorizontalHeaderLabels(['Tipo','Tiempo'])
  self.carga_particionFijas.botonFinalizar.clicked.connect(self.graficar)
  self.dialogo.pushButtonAgregarRafaga.clicked.connect(self.agregar_fila_rafagas)
  self.dialogo.tableWidgetProcesos.setColumnCount(6)
  self.dialogo.tableWidgetProcesos.setHorizontalHeaderLabels(['idpc','Descripcion','Prioridad','Tamano','TI','TA'])
  self.carga_particionFijas.tableWidgetCargaParticion.setColumnCount(4)
  self.carga_particionFijas.tableWidgetCargaParticion.setHorizontalHeaderLabels(['idSim','idPart','dirRli','partSize'])
  self.carga_particionFijas.pushButtonAgregarParticion.clicked.connect(self.agregar_fila_particiones)
  self.pushButton_Simular.clicked.connect(self.gantt)
  self.pushButton_Simular.clicked.connect(self.generar_grafico_durante_simulacion)
  self.pushButton_Simular.clicked.connect(self.mostrarResultSimulacion)
  self.pushButtonComparar.clicked.connect(self.mostrarComparacion)
  self.dialogo.pushButtonImportar.clicked.connect(self.mostrarTablaImportar)
  self.dialogoImportar.tableWidgetImportar.setColumnCount(7)
  self.dialogoImportar.tableWidgetImportar.setHorizontalHeaderLabels([' ','idpc','Descripcion','Prioridad','Tamaño','TI','TA'])
  self.dialogcompara.tableWidgetComparacion.setColumnCount(2)
  self.dialogcompara.tableWidgetComparacion.setHorizontalHeaderLabels(['Tiempo1','Tiempo2'])
  self.dialogoImportar.pushButtonImportar.clicked.connect(self.update_tablaProcesos)

  
     
  #considero que el calculo de los labels de tam de memoria para procesos y so, se hace recien cuando le 
  #di algun valor al spinbox de so, sino estaria dividiendo por el valor 0
 def mostrarResultSimulacion(self):
   self.dialogresultsim.move(910,325)
   self.dialogresultsim.exec_()

 def mostrarComparacion(self):
   self.dialogcompara.exec_()


 def update_tablaProcesos(self):
   

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


 def generar_grafico_durante_simulacion(self):
   global conts
   fig= plt.figure(figsize=(15,2))
   ax=fig.subplots()
   category_names=[]
   procesosejemplos=['P1','P2','P3','P4','P5','P6','P7','P8','P9','P10']
   ys=[]
   i=0
   for elemento in self.lista_graficos:
     print(elemento)
     if len(elemento)>1:
       category_names.append(str(elemento[0])+':  '+ procesosejemplos[i])
       ys.append(elemento[1])
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
   ax.legend(bbox_to_anchor=(1,1))
   #ncol=len(category_names), bbox_to_anchor=(0,1),
   #          loc='lower left', fontsize='small')
   #ani=animation.FuncAnimation(fig,animate(), interval=3000,repeat=True)

   
   plt.show()



 def cargarTabla(self):
   print("entre")
   try:
     connection = mysql.connector.connect(host='localhost',
     database = 'simulador',
     user='root',
     password='letra123')
     print("conecto")
     cur=connection.cursor()
     cur.execute("SELECT * FROM procesos")
     self.result=cur.fetchall()
     contador_rows_importar =0
     for i in self.result:
       
       self.checkbox=QTableWidgetItem()
       self.checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
       self.checkbox.setCheckState(Qt.Unchecked)
       idpc= QTableWidgetItem(str(i[0]))
       desc =QTableWidgetItem(str(i[1]))
       prioridad = QTableWidgetItem(str(i[2]))
       tam= QTableWidgetItem(str(i[3]))
       ti= QTableWidgetItem(str(i[4]))
       ta= QTableWidgetItem(str(i[5]))
       self.dialogoImportar.tableWidgetImportar.insertRow(contador_rows_importar)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,0,self.checkbox)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,1,idpc)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,2,desc)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,3,prioridad)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,4,tam)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,5,ti)
       self.dialogoImportar.tableWidgetImportar.setItem(contador_rows_importar,6,ta)
       



       contador_rows_importar = contador_rows_importar + 1

       
 #HAY QUE TERMINAR
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
     self.valor_memoria_procesos -= tampart
     self.carga_particionFijas.label_MemDisp.setText("Memoria Disponible: "+str(self.valor_memoria_procesos) + " KB")
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
     self.lista_graficos.append([cont_agregar_particion,tampart,rli])
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
   fig= plt.figure(figsize=(9.2, 5))
   ax=fig.subplots()
   #graph_data= open('prueba.txt','r').read()
   #lines=graph_data.split('\n')
   category_names=[]
   ys=[]
   try:
     global conts
     connection = mysql.connector.connect(host='localhost',
     database = 'simulador',
     user='root',
     password='letra123')
     for elemento in self.lista_graficos:
       print(elemento)
       if len(elemento)>1:
         category_names.append(elemento[0])
         ys.append(elemento[1])
         mySql_insert_query= """INSERT INTO part_fija (idsim, idpart, dir_rli, estado, part_size)
         VALUES (%s,%s,%s,%s,%s)""" 
         recordTuple=(conts, elemento[0], elemento[2], '0', elemento[1])
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
 
 def mostrarCargaProcesos(self):
   self.carga_particionFijas.label_MemDisp.setText('Memoria disponible:'+str(self.valor_memoria_procesos) + " KB")
   #Carga o actualiza en BD el tamaño memoria y porcentaje so ingresado
   try:
     global conts
     connection = mysql.connector.connect(host='localhost',
     database = 'simulador',
     user='root',
     password='letra123')
        
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
         print("ti actualizado") #esto es un control que hago que se muestre en terminal para saber si los datos se insertaron o no
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

 def updateLabels(self):
   if self.por_so >0:
    self.valor_so = ((self.tam_Memoria)*(self.por_so))/100
    self.valor_memoria_procesos = self.tam_Memoria-self.valor_so
    self.label_MemProcesos.setText('\n'+str(self.valor_memoria_procesos) + " KB")
    self.label_MemSO.setText('\n'+str(self.valor_so) + " KB") 

 def actTamMemoria(self):
   self.tam_Memoria = self.spinBoxTamMemoria.value()
   print(self.tam_Memoria)

 def actPorcSO(self):
   self.por_so=self.spinBoxPorcSO.value()
   print(self.por_so)

 def cargarProcesosYRafagasenBD(self):
   try:
     connection = mysql.connector.connect(host='localhost',
     database = 'simulador',
     user='root',
     password='letra123')
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

 def abrirDialogoCarga(self): #bueno, sentiende por el nombre lo que hace el metodo supongo, ejecuta la nueva ventana o dialogo de carga
   self.dialogo.exec_()
   self.dialogo.lineEditDescrip.setText('')
   #self.dialogo.spinBoxTiempoarr.setText('')
   self.dialogo.spinBoxTamProc.setText('')
   self.dialogo.spinBoxPriori.setText('')
   while (self.dialogo.tableWidgetRafaga.rowCount()>0):
    self.dialogo.tableWidgetRafaga.removeRow(0)
  
 def gantt(self):
  #aca armo el diagrama de gantt
  #es un ej nomas, con fechas y demas
  #tabla= QTableWidget()
  #tabla.setColumnCount(2)
  #tabla.setHorizontalHeaderLabels(['hola','jajaja'])
  df = [dict(Task="CPU", Start='0', Finish='2',Resource='Proceso1'),
  dict(Task="CPU", Start='1', Finish='3',Resource='Proceso2'),
  dict(Task='CPU',Start='3',Finish='6',Resource='Proceso3'),
  dict(Task="ES", Start='2', Finish='5',Resource='Proceso1'),
  dict(Task="ES", Start='4', Finish='6',Resource='Proceso2'),
  dict(Task="ES", Start='5', Finish='9',Resource='Proceso3'),
  dict(Task="CPU", Start='5', Finish='9',Resource='Proceso1'),]
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
cont_agregar_particion=0
rli=0
app = QApplication(sys.argv) 
ventana = Ventana()
ventana.show()
app.exec_()