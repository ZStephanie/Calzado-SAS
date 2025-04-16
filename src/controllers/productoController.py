from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from random import sample
from config import config
import mysql.connector


def listaZapatos():
    db_config = config['development'] #creando mi instancia a la conexion de BD
    
    conexion_MySQLdb = mysql.connector.connect(
        host=db_config.MYSQL_HOST,
        user=db_config.MYSQL_USER,
        password=db_config.MYSQL_PASSWORD,
        database=db_config.MYSQL_DB
    )

    cur = conexion_MySQLdb.cursor(dictionary=True)

    querySQL = "SELECT * FROM Productos ORDER BY id_producto DESC;" #Consulta SQL para obtener todos los productos
    cur.execute(querySQL) 
    resultadoBusqueda = cur.fetchall() #fetchall () Obtener todos los registros
    totalBusqueda = len(resultadoBusqueda) #Total de busqueda
    
    cur.close() #Cerrando conexion SQL
    conexion_MySQLdb.close() #cerrando conexion de la BD    
    return resultadoBusqueda

def updateZapatos(id=''):
        db_config = config['development'] #creando mi instancia a la conexion de BD
        

        conexion_MySQLdb = mysql.connector.connect(
            host=db_config.MYSQL_HOST,
            user=db_config.MYSQL_USER,
            password=db_config.MYSQL_PASSWORD,
            database=db_config.MYSQL_DB
        )
        cur = conexion_MySQLdb.cursor(dictionary=True)
        cur.execute("SELECT * FROM productos WHERE id_producto = %s LIMIT 1", [id])
        resultQueryData = cur.fetchone() #Devolviendo solo 1 registro
        return resultQueryData

def registrarZapatos(id_producto, nombre_producto='', stock='', precio='', descripcion='', imagen='', id_categoria=''):
    db_config = config['development']  # Instancia de configuración

    conexion_MySQLdb = mysql.connector.connect(
        host=db_config.MYSQL_HOST,
        user=db_config.MYSQL_USER,
        password=db_config.MYSQL_PASSWORD,
        database=db_config.MYSQL_DB
    )
    
    cursor = conexion_MySQLdb.cursor(dictionary=True)

    sql = """
        INSERT INTO productos
        (id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores = (id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria)
    
    cursor.execute(sql, valores)
    conexion_MySQLdb.commit()

    resultado_insert = cursor.rowcount  # 1 si se insertó, 0 si no
    ultimo_id = cursor.lastrowid        # ID del último insertado

    cursor.close()
    conexion_MySQLdb.close()

    return resultado_insert


def detallesZapatos(id_producto):
        db_config = config['development'] #creando mi instancia a la conexion de BD
        
        conexion_MySQLdb = mysql.connector.connect(
            host=db_config.MYSQL_HOST,
            user=db_config.MYSQL_USER,
            password=db_config.MYSQL_PASSWORD,
            database=db_config.MYSQL_DB
        )
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM productos WHERE id_producto ='%s'" % (id_producto,))
        resultadoQuery = cursor.fetchone()
        cursor.close() #cerrando conexion de la consulta sql
        conexion_MySQLdb.close() #cerrando conexion de la BD
        
        return resultadoQuery

def recibeActualizarZapatos(id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria):
    try:
        # Conectarse a la base de datos
        db_config = config['development']
        conexion_MySQLdb = mysql.connector.connect(
            host=db_config.MYSQL_HOST,
            user=db_config.MYSQL_USER,
            password=db_config.MYSQL_PASSWORD,
            database=db_config.MYSQL_DB
        )

        cur = conexion_MySQLdb.cursor()

        # Consulta base de actualización
        query = """
            UPDATE productos
            SET 
                nombre_producto = %s,
                stock = %s,
                precio = %s,
                descripcion = %s,
                imagen = %s,
                id_categoria = %s
            WHERE id_producto = %s
        """

        params = (
            nombre_producto,
            stock,
            precio,
            descripcion,
            imagen,
            id_categoria,
            id_producto
        )

        # Ejecutar la actualización
        cur.execute(query, params)
        conexion_MySQLdb.commit()

        filas_afectadas = cur.rowcount

        cur.close()
        conexion_MySQLdb.close()

        return filas_afectadas

    except Exception as e:
        print(f"Ocurrió un error en recibeActualizarZapatos: {e}")
        return 0
#eliminar


#Crear un string aleatorio para renombrar la foto 
# y evitar que exista una foto con el mismo nombre
def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud         = 20
    secuencia        = string_aleatorio.upper()
    resultado_aleatorio  = sample(secuencia, longitud)
    string_aleatorio     = "".join(resultado_aleatorio)
    return string_aleatorio