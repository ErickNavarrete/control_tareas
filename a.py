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
			print(a)
			origen = "USUARIOS"
		else:
			id_ot,id_unidad,id_detalle = codigo.split(".")
			origen = "OT"
		set_tarea()

if __name__=="__main__":
	try:
		while True:
			get_event()
	except KeyboardInterrupt:
		pass