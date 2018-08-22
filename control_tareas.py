import time
import MySQLdb


#VARIABLES GLOBALES
global id_usuario
global id_detalle
global id_ot
global origen

global db

def base():
	global db
	db = MySQLdb.connect(host="192.168.15.6",
			     user="root",
			     passwd="ZMalqp10",
			     db="tablero_dmm2")

def get_event():
	global id_detalle, id_ot, id_usuario, origen

	codigo =raw_input()

	#DETERMINAMOS SI ES USUARIO U OT
	if len(codigo)  > 0:
		if codigo[:4] == "000.":
			a,b  = codigo.split(".")
			origen = "USUARIOS"
		else:
			id_ot,id_unidad,id_detalle = codigo.split(".")
			origen = "OT"
		set_tarea()

def set_tarea():
	global id_detalle, id_ot, id_usuario, origen, db
	bandera =  "False"

	if origen == "OT":
		base()

		cur = db.cursor()
		cur.execute("SELECT ID_PROCESO, ID_ESTACION, ESTADO, NUM_PROC FROM PROCESO_OT WHERE ID_DETALLE = " + id_detalle + " AND ESTADO = 'EN CURSO' ORDER BY NUM_PROC")

		for row in cur.fetchall():
			id_proceso = row[0]
			id_estacion = row[1]
			estado = row[2]
			num_proceso = row[3]
			bandera = "True"
		db.close()

		if bandera == "False":
			base()
			cur = db.cursor()
			cur.execute("select id_proceso, id_estacion, estado, num_proc from proceso_ot where id_detalle = " + id_detalle + " and estado <> 'EN CURSO' and estado <> 'TERMINADO' order by num_proc desc ")
			for row in cur.fetchall():
				id_proceso = row[0]
				id_estacion = row[1]
				estado = row[2]
				num_proceso = row[3]
			db.close()
				
		if estado == "EN CURSO":
			base()
			cur = db.cursor()
			fecha = str(time.strftime("20%y/%m/%d %X"))
			print(" update historial set fecha_t = '"+ fecha +"' , estado = 'Otro' where id_detalle = " + str(id_detalle) + " and id_proceso = " + str(id_proceso) + " and estado = 'COMPLETADO' ")
			cur.execute(" update historial set fecha_t = '"+ fecha +"' , estado = 'Otro' where id_detalle = " + str(id_detalle) + " and id_proceso = " + str(id_proceso) + " and estado = 'COMPLETADO' ")
			

			

	elif origen == "USUARIOS":
		print("ORIGEN")


if __name__=="__main__":
	try:
		while True:
			get_event()
	except KeyboardInterrupt:
		pass
