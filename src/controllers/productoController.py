from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from random import sample
from app import mysql
import MySQLdb.cursors

# ===============================
# FUNCIONES DE PRODUCTOS
# ===============================

# Obtener todos los zapatos (con categoría)
def listaZapatos():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.stock, p.precio, p.descripcion, 
            p.imagen, c.descripcion_categoria
            FROM productos p
            JOIN categoria c ON p.id_categoria = c.id_categoria;
        """)
        zapatos = cursor.fetchall()
        cursor.close()
        return zapatos
    except Exception as e:
        print(f"Error en listaZapatos: {e}")
        return []

# Obtener zapatos por categoría
def listaZapatosPorCategoria(id_categoria):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT * FROM productos
            WHERE id_categoria = %s
            ORDER BY id_producto DESC
        """, (id_categoria,))
        resultado = cursor.fetchall()
        cursor.close()
        return resultado
    except Exception as e:
        print(f"Error en listaZapatosPorCategoria: {e}")
        return []

# Obtener un zapato por su ID
def getZapatoById(id_producto):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s LIMIT 1", (id_producto,))
        zapato = cursor.fetchone()
        cursor.close()
        return zapato
    except Exception as e:
        print(f"Error en getZapatoById: {e}")
        return None


# Registrar un nuevo zapato
def registrarZapatos(nombre_producto, stock, precio, descripcion, imagen, id_categoria):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre_producto, stock, precio, descripcion, imagen, id_categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre_producto, stock, precio, descripcion, imagen, id_categoria))
        mysql.connection.commit()
        resultado = cursor.rowcount
        cursor.close()
        return resultado
    except Exception as e:
        print(f"Error en registrarZapatos: {e}")
        return 0

# Actualizar un zapato existente
def actualizarZapatos(id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre_producto = %s,
                stock = %s,
                precio = %s,
                descripcion = %s,
                imagen = %s,
                id_categoria = %s
            WHERE id_producto = %s
        """, (nombre_producto, stock, precio, descripcion, imagen, id_categoria, id_producto))
        mysql.connection.commit()
        filas_afectadas = cursor.rowcount
        cursor.close()
        return filas_afectadas
    except Exception as e:
        print(f"Error en actualizarZapatos: {e}")
        return 0

# ===============================
# FUNCIONES AUXILIARES
# ===============================

# Obtener todas las categorías
def obtenerCategorias():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias
    except Exception as e:
        print(f"Error al obtener categorias: {e}")
        return []

# Generar string aleatorio para nombres de archivos
def stringAleatorio():
    caracteres = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud = 20
    secuencia = caracteres.upper()
    resultado = sample(secuencia, longitud)
    return "".join(resultado)
