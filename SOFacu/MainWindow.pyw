import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog, QPushButton, QLabel
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.figure_factory as ff
import plotly
#para bd 
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


class Dialogo(QDialog):
  def __init__(self):
    super().__init__()
    self.resize(300,300)
    self.setWindowTitle("Carga de procesos")
    #cargo la interfaz de la ventana de carga de procesos
    uic.loadUi("nuevoproceso.ui",self)
   

class Ventana(QMainWindow):
 def __init__(self):
  QMainWindow.__init__(self)
  self.resize(600, 600)
  self.setWindowTitle("Ventana principal")
  #cargo la interfaz .ui para la ventana principal
  uic.loadUi("MainWindow.ui",self)
  self.dialogo = Dialogo()
  #una vez que cargue la interfaz .ui e hice una instancia de Dialogo. me puedo referir a los elementos que fui poniendo en la interfaz, con sus nombres
  self.botonini.clicked.connect(self.abrirDialogoCarga)
  self.botonGantt.clicked.connect(self.gantt)
  self.dialogo.boton.clicked.connect(self.cargarenBD)
  #estos 3 comandos hacen se ejecuten los metodos entre () con apreto cada boton

  #este metodo es para cargar los datos en la tabla de la base de datos 
 def cargarenBD(self):
   try:
     connection = mysql.connector.connect(host='localhost',
     database = 'pruebasso',
     user='root',
     password='root')
     #guardo en variables los datos del formulario, para despues ponerlos en el INSERT
     descripcion = self.dialogo.lineDesc.text() #cada uno de estos comandos .text() obtiene el texto que fui poniendo en cada linea del formulario
     t_arribo = int(self.dialogo.lineTarribo.text()) #hago un casting a int, pq en la bd los declaro como INT
     rafaga_cpu_es = int(self.dialogo.lineRafaga.text())
     tam_mem = int(self.dialogo.lineMem.text())
  
     mySql_insert_query= """INSERT INTO procesos(Descripcion,Tiempo_arribo,Rafagas_cpu_es,Tam_memoria)
     VALUES
     (%s,%s,%s,%s)""" #este seria el script para MySQL, para meter una fila a la tabla procesos
     #no incluyo el campo de id(que es clave) porque lo declare como auto incremental en la tabla, aumenta solo
     #en (%s,%s,%s,%s) se ponen luego los valores que estan acontinuacion, en recordTuple
     recordTuple=(descripcion,t_arribo,rafaga_cpu_es,tam_mem)
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

 def abrirDialogoCarga(self): #bueno, sentiende por el nombre lo que hace el metodo supongo, ejecuta la nueva ventana o dialogo de carga
  #los 2 if's que estan aca son para ver que accion hago, segun que boton eligo para cargar los datos
  #por ahora como estoy probando, los dos puse que hagan lo mismo
  if self.base_Datos.isChecked(): #si el boton de base de datos esta tildado
    self.dialogo.exec_() 
  if self.otros.isChecked(): #si el boton de otros esta tildado
    self.dialogo.exec_()
  
 def gantt(self):
  #aca armo el diagrama de gantt
  #es un ej nomas, con fechas y demas
  df = [dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28'),
  dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15'),
  dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30'),
  dict(Task="Job D", Start='2009-05-25', Finish='2009-06-18'),
  dict(Task="Job E", Start='2009-06-05', Finish='2009-06-15'),]
  fig = ff.create_gantt(df)
  #con el auto_open = False hago que no se me abra automaticamente una ventana del navegador
  plotly.offline.plot(fig, filename='diagrama_gantt.html',auto_open=False)
  #guardo el diagrama en la carpeta donde esta este archivo .pyw, en un formato .html
  file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "diagrama_gantt.html")) #obtengo la direccion abosuluta del archivo
  local_url = QUrl.fromLocalFile(file_path)
  self.web = QWebEngineView() #aca hago una instancia de QWebEngineView, que es necesario para que se pueda mostrar el diagrama en una ventana
  self.web.load(local_url) #cargo la url, que seria la ruta del archivo generado .html
  self.web.setWindowTitle("Diagrama de Gantt")
  self.web.resize(600,600) #defino nombre y tamaño de la ventana
  self.web.show() #muestro la ventana

  
#estas 4 lineas son para que se ejecute la ventana al inciar o ejecutar este archivo .pyw
app = QApplication(sys.argv) 
ventana = Ventana()
ventana.show()
app.exec_()