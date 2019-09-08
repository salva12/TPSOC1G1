NOTAS Y EXPLICACIONES 

Actualizado al: 7/09/19
NOTA: El codigo fue probado con Windows 10 y Mac OS Catalina. Despues actualizo y pruebo con Ubuntu Studio


Instalacion de librerias 

Primero necesitan Pyqt. Es muy importante porque de acá sacamos las clases
que tenemos que usar para manejar y configurar la interfaz.
La version que estoy usando de PyQt es la ultima, PyQt5
para instalarla, escriben en terminal:

pip3 install PyQt5

tambien van a necesitar instalar una libreria para poder abrir el .html que se genera para el diagrama de gantt
escribiendo lo siguiente, tambien en terminal:

pip3 install PyQtWebEngine

tambien tienen que instalar plotly para poder hacer el diagrama de gantt
para eso escriben

pip3 install plotly==4.1.0

o si tienen conda tambien pueden hacer:

conda install -c plotly plotly=4.1.0



Por uuultimo(Creo), esta el tema de la base de datos:


en el codigo esta bien comentado todo, pero aca escribo de vuelta los datos que use para la base de datos
(corre en localhost)

host='localhost',
database = 'pruebasso',
user='root',
password='root'       (aca obvio tiene que cambiar por su usuario y contraseña que usan en mysql)


para esto entonces tienen que crear en su pc una bd (fui haciendo esto en MySQL Workbench)

CREATE DATABASE pruebasso;
USE pruebasso;


aca creo la tabla de procesos que se usa en el codigo

CREATE TABLE procesos(
	id_proceso INT AUTO_INCREMENT,
	Descripcion VARCHAR(40) NOT NULL,
	Tiempo_arribo INT NOT NULL,
	Rafagas_cpu_es INT NOT NULL,
	Tam_memoria INT NOT NULL,
	PRIMARY KEY(id_proceso)
);
