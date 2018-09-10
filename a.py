import time
import MySQLdb
import os

os.chdir('/home/pi/control_tareas/')
import lcd

#VARIABLES GLOBALES
global id_usuario
global id_detalle
global id_ot
global uso
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
	global id_detalle, id_ot, id_usuario, origen, uso

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
			uso = 1
		set_tarea()
		
def set_tarea():
	global id_detalle, id_ot, id_usuario, origen, db, mydb
	bandera =  "False"
	estado_t = "True"
	estado = "TERMINADO"
	
	
	if origen == "OT":		
		
		try:
			if id_usuario == 0 :
				mensajes_lcd("USUARIO","OBLIGATORIO","ESPERANDO","USUARIO")
		except:
			id_usuario = 0
			
		if id_usuario == 0:
			mensajes_lcd("USUARIO","OBLIGATORIO","ESPERANDO","USUARIO")
			return
				
		base()
		cur = db.cursor()
		cur.execute("select estado from historial where id_detalle = " + id_detalle + " and id_usuario = " + id_usuario + " and estado <> 'COMPLETADO' ")
		for row in cur.fetchall():
			estado = row[0]
		db.close()
									
		if estado == "EN CURSO":
			#ACTUALIZA ESTADO DEL HISTORIAL
			base()
			cur = db.cursor()
			fecha = str(time.strftime("20%y/%m/%d %X"))
			
			sql = "update historial set fecha_t = %s , estado = 'COMPLETADO' where id_detalle = %s and estado = 'EN CURSO' "
			val = (fecha,id_detalle)
			 
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
			
			sql = " insert into historial (id_detalle, id_proceso, id_usuario, estado, fecha) values (%s, '0', %s, 'EN CURSO', %s) "
			val = (id_detalle,id_usuario,fecha)
			 
			try:
				cur.execute(sql,val)
				db.commit()
			except:
				# Rollback in case there is any error
				print("ERROR")
				db.rollback()			
			db.close()
			
			
			mensajes_lcd("TAREA","EN CURSO","ESPERANDO","USUARIO")
			
		id_usuario = 0
			
	elif origen == "USUARIOS":
		mensajes_lcd("USUARIO","IDENTIFICADO","ESPERANDO","DETALLE")
		uso = 0

if __name__=="__main__":
	global uso
	uso = 0
	cont = 0
	lcd.GPIO.cleanup()
	lcd.lcd_init()
	mensajes_lcd("BIENVENIDO","","ESPERANDO","USUARIO")
	try:
		while True:
			get_event()
			if uso == 0:
				cont += 1
				print(cont)
				if con == 1000:					
					mensajes_lcd("BIENVENIDO","","ESPERANDO","USUARIO")
					cont = 0
	except KeyboardInterrupt:
		pass