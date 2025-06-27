import os
from datetime import datetime
from random import sample
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_mysqldb import MySQL
import MySQLdb.cursors

# --- Crear aplicación Flask ---
app = Flask(__name__)

# --- Configuración base de datos MySQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'calzado_sas'

mysql = MySQL(app)

# --- Configuración Flask-Login ---
app.secret_key = 'ASD234GDFV435GDFGB'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Función para generar string aleatorio ---
def stringAleatorio():
    caracteres = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud = 20
    secuencia = caracteres.upper()
    return "".join(sample(secuencia, longitud))

# --- Función para guardar imagen ---
def recibeFoto(file):
    try:
        filename = file.filename
        extension = os.path.splitext(filename)[1]
        nuevoNombreFile = datetime.now().strftime('%Y%H%M%S') + extension
        upload_path = os.path.join(os.path.dirname(__file__), 'static/img/', nuevoNombreFile)
        file.save(upload_path)
        return nuevoNombreFile
    except Exception as e:
        print(f"Error guardando foto: {e}")
        return None

# --- Funciones de productos ---
def listaZapatos():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.stock, p.precio, p.descripcion, p.imagen, p.id_categoria,
                   c.descripcion_categoria
            FROM productos p
            JOIN categoria c ON p.id_categoria = c.id_categoria
            ORDER BY p.id_producto DESC
        """)
        zapatos = cursor.fetchall()
        cursor.close()
        return zapatos
    except Exception as e:
        print(f"Error en listaZapatos: {e}")
        return []

def getZapatoById(id_producto):
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        zapato = cursor.fetchone()
        cursor.close()
        return zapato
    except Exception as e:
        print(f"Error en getZapatoById: {e}")
        return None

def registrarZapatos(nombre_producto, stock, precio, descripcion, imagen, id_categoria):
    try:
        cursor = mysql.connection.cursor()
        sql = """
            INSERT INTO productos (nombre_producto, stock, precio, descripcion, imagen, id_categoria)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (nombre_producto, stock, precio, descripcion, imagen, id_categoria))
        mysql.connection.commit()
        resultado = cursor.rowcount
        cursor.close()
        return resultado
    except Exception as e:
        print(f"Error en registrarZapatos: {e}")
        return 0

def actualizarZapatos(id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria):
    try:
        cursor = mysql.connection.cursor()
        sql = """
            UPDATE productos
            SET nombre_producto=%s, stock=%s, precio=%s, descripcion=%s, imagen=%s, id_categoria=%s
            WHERE id_producto=%s
        """
        cursor.execute(sql, (nombre_producto, stock, precio, descripcion, imagen, id_categoria, id_producto))
        mysql.connection.commit()
        resultado = cursor.rowcount
        cursor.close()
        return resultado
    except Exception as e:
        print(f"Error en actualizarZapatos: {e}")
        return 0

def eliminarProducto(id_producto, nombre_imagen):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM productos WHERE id_producto = %s', (id_producto,))
        mysql.connection.commit()
        filas = cursor.rowcount
        cursor.close()

        if nombre_imagen:
            path = os.path.join(os.path.dirname(__file__), 'static/img', nombre_imagen)
            if os.path.exists(path):
                os.remove(path)

        return filas
    except Exception as e:
        print(f"Error eliminando producto: {e}")
        return 0

@app.route('/registrar-producto')
@login_required
def registrar_producto():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_categoria, descripcion_categoria FROM Categoria")
    categorias = cursor.fetchall()
    cursor.close()
    print(categorias)
    return render_template('administrador/acciones/add.html', categorias=categorias)
    

def obtenerCategorias():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias
    except Exception as e:
        print(f"Error en obtenerCategorias: {e}")
        return []

# --- Flask-Login: cargar usuario ---
from models.modelUser import ModelUser

@login_manager.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

# --ver productos---
@app.route('/listar-productos')
def listar_productos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT p.id_producto, p.nombre_producto, p.stock, p.precio, p.descripcion, 
               p.imagen, c.descripcion_categoria
        FROM productos p
        JOIN categoria c ON p.id_categoria = c.id_categoria
        ORDER BY p.id_producto DESC
    """)
    productos = cursor.fetchall()
    cursor.close()
    return render_template('productos/view.html', productos=productos)

# --- Rutas ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from controllers.registroController import RegistroController
    if request.method == 'POST':
        return RegistroController.register_post(mysql)
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    from controllers.userController import UserController
    if request.method == 'POST':
        return UserController.login_post(mysql)
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    from controllers.userController import UserController
    return UserController.logout()

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.is_admin():
        return render_template('administrador/admin_dashboard.html', miData=listaZapatos())
    flash("Acceso no autorizado.")
    return redirect(url_for('usuario_dashboard'))

@app.route('/registrar-producto', methods=['GET', 'POST'])
@login_required
def addProducto():
    return render_template('administrador/acciones/add.html', categorias=obtenerCategorias())

@app.route('/form-add-producto', methods=['POST'])
@login_required
def formAddProducto():
    nombre_producto = request.form['nombre_producto']
    stock = request.form['stock']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    id_categoria = request.form['id_categoria']
    file = request.files['imagen']
    imagen = recibeFoto(file) if file else None

    resultado = registrarZapatos(nombre_producto, stock, precio, descripcion, imagen, id_categoria)
    flash('Producto registrado exitosamente.' if resultado == 1 else 'Error al registrar producto.', 'success' if resultado == 1 else 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/ver-detalles-del-zapato/<int:id_producto>')
@login_required
def verDetalleZapato(id_producto):
    zapato = getZapatoById(id_producto)
    if zapato:
        return render_template('administrador/acciones/view.html', zapato=zapato)
    flash('Producto no encontrado.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/form-update-producto/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def formUpdateProducto(id_producto):
    if request.method == 'GET':
        zapato = getZapatoById(id_producto)
        if zapato:
            return render_template('administrador/acciones/update.html', dataInfo=zapato, categorias=obtenerCategorias())
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    nombre_producto = request.form['nombre_producto']
    stock = request.form['stock']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    id_categoria = request.form['id_categoria']
    file = request.files['imagen']
    imagen = recibeFoto(file) if file else request.form['imagen_actual']

    resultado = actualizarZapatos(id_producto, nombre_producto, stock, precio, descripcion, imagen, id_categoria)
    flash('Producto actualizado.' if resultado == 1 else 'Error al actualizar.', 'success' if resultado == 1 else 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/borrar-producto', methods=['POST'])
@login_required
def formViewBorrarProducto():
    id_producto = request.form['id_producto']
    imagen = request.form['imagen']
    resultado = eliminarProducto(id_producto, imagen)
    return jsonify([1 if resultado == 1 else 0])

@app.route('/usuario')
@login_required
def usuario_dashboard():
    return render_template('usuario/usuario_dashboard.html')

@app.route('/novedades_destacados')
def novedades():
    return render_template('novedades.html')

@app.route('/categoria_mujer')
def mujer():
    return render_template('mujer.html')

@app.route('/categoria_hombre')
def hombre():
    return render_template('hombre.html')

@app.route('/categoria_niños')
def niños():
    return render_template('niños.html')

@app.route('/categoria_oferta')
def ofertas():
    return render_template('ofertas.html')

# --- Manejo de errores ---
@app.errorhandler(401)
def error_401(error):
    return redirect(url_for('login'))

@app.errorhandler(404)
def error_404(error):
    return "<h1>Página no encontrada</h1>", 404

# --- Iniciar la aplicación ---
if __name__ == '__main__':
    app.run(debug=True)
