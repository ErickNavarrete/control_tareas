import time
import MySQLdb
import os

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

	time.sleep(10)
	
	lcd.lcd_byte(lcd.LCD_LINE_1,lcd.LCD_CMD)
	lcd.lcd_string(mensaje3,2)
	lcd.lcd_byte(lcd.LCD_LINE_2,lcd.LCD_CMD)
	lcd.lcd_string(mensaje4,2)
	
def base():
	global db
	db = MySQLdb.connect(host="192.168.0.13",
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
			id_usuario = b
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
	
	print(id_usuario)
	
	if origen == "OT":		
		base()
		cur = db.cursor()
		cur.execute("select estado from historial where id_proceso = " + id_proceso + " and id_usuario = " + id_usuario + " and estado <> 'COMPLETADO' ")
		for row in cur.fetchall():
			estado = row[2]
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
					
			mensajes_lcd("TAREA","TERMINADA","ESPERANDO","USUARIO")
			
		else:
			#INSERTAMOS EN EL HISTORIAL
			base()
			cur = db.cursor()
			fecha = str(time.strftime("20%y/%m/%d %X"))
			
			sql = " insert into historial (id_detalle, id_proceso, id_usuario, estado, fecha) values (%s, %s, %s, 'EN CURSO', %s) "
			val = (id_detalle,id_proceso,id_usuario,fecha)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR")
				db.rollback()			
			db.close()
			

			mensajes_lcd("TAREA","EN CURSO","ESPERANDO","USUARIO")
			
	elif origen == "USUARIOS":
		mensajes_lcd("USUARIO","IDENTIFICADO","ESPERANDO","DETALLE")

if __name__=="__main__":
	try:
		while True:
			get_event()
	except KeyboardInterrupt:
		pass