import time
import MySQLdb
import os
import mysql.connector
os.chdir('/home/pi/control_tareas/')
import lcd

#VARIABLES GLOBALES
global id_usuario
global id_detalle
global id_ot
global origen
global mydb

global db

def mensajes_lcd(mensaje1,mensaje2, mensaje3, mensaje4):
	lcd.lcd_byte(lcd.LCD_LINE_1,lcd.LCD_CMD)
	lcd.lcd_string(mensaje1,2)
	lcd.lcd_byte(lcd.LCD_LINE_2,lcd.LCD_CMD)
	lcd.lcd_string(mensaje2,2)

	time.sleep(5)
	
	lcd.lcd_byte(lcd.LCD_LINE_1,lcd.LCD_CMD)
	lcd.lcd_string(mensaje3,2)
	lcd.lcd_byte(lcd.LCD_LINE_2,lcd.LCD_CMD)
	lcd.lcd_string(mensaje4,2)
	
def base():
	global db
	db = MySQLdb.connect(host="192.168.15.14",
			     user="root",
			     passwd="ZMalqp10",
			     db="tablero_dmm2")
				 
def get_event():
	global id_detalle, id_ot, id_usuario, origen

	codigo = raw_input()

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
	global id_detalle, id_ot, id_usuario, origen, db, mydb
	bandera =  "False"
	estado_t = "True"
	estado = "TERMINADO"
	
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
			#ACTUALIZA ESTADO DEL HISTORIAL
			base()
			cur = db.cursor()
			fecha = str(time.strftime("20%y/%m/%d %X"))
			
			sql = "update historial set fecha_t = %s , estado = 'COMPLETADO' where id_detalle = %s and id_proceso = %s and estado = 'EN CURSO' "
			val = (fecha,id_detalle,id_proceso)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR 1")
				db.rollback()			
			db.close()
			
			#ACTUALIZA PROCESO OT
			base()
			cur = db.cursor()
			sql = "update proceso_ot set estado = 'TERMINADO' where id_detalle = %s and id_proceso = %s and num_proc = %s"
			val = (id_detalle,id_proceso,num_proceso)
			
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR 2")
				db.rollback()			
			db.close()
			
			#ACTUALIZA ESTACION
			base()
			cur = db.cursor()
			sql = "update estacion set estado = %s where id_estacion = %s "
			val = ('LIBRE',id_estacion)
			
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR 3")
				db.rollback()			
			db.close()
			
			#VERIFICAMOS SI LA ORDEN DE TRABAJO YA FUE COMPLETADA
			base()
			cur = db.cursor()
			sql = "select estado from proceso_ot where id_detalle = %s "
			val = (id_detalle)
			cur.execute(sql,val)
			
			for row in cur.fetchall():
				if row[0] <> "TERMINADO":
					estado_t = "False"					
			db.close()
			
			if estado_t == "True":
				#ACTUALIZA PROCESO OT
				base()
				cur = db.cursor()
				sql = "update orden_trabajo set momento = 'TERMINADO' where id_ot = %s "
				val = (id_ot)
				
				try:
					cur.execute(sql,val)
					db.commit()
				except:
					# Rollback in case there is any error
					print("ERROR 4")
					db.rollback()			
				db.close()
		
			mensajes_lcd("TAREA","TERMINADA","ESPERANDO","USUARIO")
			
		elif estado == "TERMINADO":
			mensajes_lcd("DETALLE","TERMINADO","ESPERANDO","USUARIO")
		
		else:
			#CONSULTAMOS SI LA ESTACION ESTA LIBRE PARA COMENZAR EL PROCESO
			base()
			cur = db.cursor()
			sql = " "
			cur.execute("select estado from estacion where id_estacion = " + str(id_estacion))
			
			for row in cur.fetchall():
				if row[0] == "OCUPADO":
					mensajes_lcd("ESTACION","OCUPADA","HABLE CON EL","ADMINISTRADOR")
					mensajes_lcd("ESPERANDO","USUARIO","ESPERANDO","USUARIO")
					return			
			db.close()
			
			#INSERTAMOS EN EL HISTORIAL
			base()
			cur = db.cursor()
			fecha = str(time.strftime("20%y/%m/%d %X"))
			
			sql = " insert into historial (id_detalle, id_proceso, id_usuario, estado, fecha) values (%s, %s, '1', 'EN CURSO', %s) "
			val = (id_detalle,id_proceso,fecha)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR")
				db.rollback()			
			db.close()
			
			#ACTUALIZA PORCESO_OT
			base()
			cur = db.cursor()
			
			sql = " update proceso_ot set estado = 'EN CURSO' where id_detalle = %s and id_proceso = %s and num_proc = %s "
			val = (id_detalle,id_proceso,num_proceso)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR 5")
				db.rollback()			
			db.close()
			
			#ACTUALIZA ESTADO DE LA ESTACION
			base()
			cur = db.cursor()
			
			sql = " update estacion set estado = %s where id_estacion = %s "
			val = ('OCUPADO',id_estacion)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR 6")
				db.rollback()			
			db.close()

			mensajes_lcd("TAREA","EN CURSO","ESPERANDO","USUARIO")
			
	elif origen == "USUARIOS":
		mensajes_lcd("USUARIO","IDENTIFICADO","ESPERANDO","DETALLE")


if __name__=="__main__":
	lcd.GPIO.cleanup()
	lcd.lcd_init()
	mensajes_lcd("BIENVENIDO","","ESPERANDO","USUARIO")

	try:
		while True:
			get_event()
	except KeyboardInterrupt:
		pass
