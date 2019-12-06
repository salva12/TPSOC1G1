# -*- coding: UTF-8 -*- 
import sys
import os
from copy import deepcopy
from datetime import date
from PyQt5.QtWidgets import QApplication,QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox, QWidget, QMainWindow, QDialog, QPushButton, QLabel
from PyQt5 import uic

from PyQt5.QtCore import *

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import time

#update:26/11set

class Ventana(QMainWindow):
 def __init__(self):
  QMainWindow.__init__(self)
  self.resize(600, 600)
  self.setWindowTitle("Ventana principal")
  #cargo la interfaz .ui para la ventana principal
  uic.loadUi("MainWindowbd.ui",self)
  self.pushButtonCrear.clicked.connect(self.crearBase)
  self.lineEditP.setEchoMode(QLineEdit.Password)

 def crearBase(self):
     self.host='localhost'
     self.database='simulador'
     self.user=self.lineEditU.text()
     self.password=self.lineEditP.text()
     cnx = mysql.connector.connect(user=self.user,
                             password=self.password,
                             host=self.host,
                             database=self.database)
     cursor =cnx.cursor()

     def executeScriptsFromFile(filename):
         fd = open(filename, 'r')
         sqlFile = fd.read()
         fd.close()
         sqlCommands = sqlFile.split(';')
 
         for command in sqlCommands:
             try:
                 if command.strip() != '':
                     cursor.execute(command)
             except mysql.connector.Error as error:
                 print("Fallo al conectarse {}",format(error))

     executeScriptsFromFile('simuejec.sql')
     cnx.commit()

app = QApplication(sys.argv) 
ventana = Ventana()
ventana.show()
app.exec_()


