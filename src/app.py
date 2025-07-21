import os
from datetime import datetime
from random import sample
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session
from flask_login import LoginManager, login_required, current_user
from flask_mysqldb import MySQL
import MySQLdb.cursors
from models.modelUser import ModelUser
from decimal import Decimal



# --- Crear aplicación Flask ---
app = Flask(__name__)



# --- Configuración base de datos MySQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'calzado_sas'

mysql = MySQL(app)


@app.route('/index-usuario')
def index_usuario():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT p.id_producto, p.nombre_producto, p.precio, p.descripcion, 
                   p.imagen, c.descripcion_categoria
            FROM productos p
            JOIN categoria c ON p.id_categoria = c.id_categoria 
        """)
        productos = cursor.fetchall()
        return render_template('usuario/index_usuario.html', productos=productos)
    except Exception as e:
        print("Error al cargar productos:", e)
        return render_template('usuario/index_usuario.html', productos=[])
    finally:
        cursor.close()

@app.route('/add-carrito', methods=['POST'])
def agregar_al_carrito():
    id = request.form['id']
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    imagen = request.form['imagen']
    cantidad = int(request.form['cantidad'])

    carrito = session.get('carrito', {})

    if id in carrito:
        carrito[id]['cantidad'] += cantidad
    else:
        carrito[id] = {
            'nombre': nombre,
            'precio': precio,
            'imagen': imagen,
            'cantidad': cantidad
        }

    session['carrito'] = carrito
    return redirect(url_for('mostrar_carrito'))

@app.route('/vaciar-carrito', methods=['POST'])
def vaciar_carrito():
    session.pop('carrito', None)  # Elimina el carrito de la sesión
    flash('Carrito vaciado correctamente.')
    return redirect(url_for('mostrar_carrito')) 

@app.route('/carrito')
def mostrar_carrito():
    carrito = session.get('carrito', {})
    subtotal = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render_template('usuario/car/carrito.html', carrito=carrito, subtotal=subtotal)

@app.route('/actualizar-carrito', methods=['POST'])
def actualizar_carrito():
    id_producto = request.form['id_producto']
    nueva_cantidad = int(request.form['cantidad'])

    if 'carrito' in session and id_producto in session['carrito']:
        session['carrito'][id_producto]['cantidad'] = nueva_cantidad
        session.modified = True  # 🔥 Necesario para que se guarde el cambio

    return redirect(url_for('mostrar_carrito'))



@app.route('/eliminar/<id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    print("ID a eliminar:", id_producto)
    print("Claves en carrito:", session.get('carrito', {}).keys())

    if 'carrito' in session and id_producto in session['carrito']:
        session['carrito'].pop(id_producto)
        session.modified = True  # 🔥 Esto es clave
        flash('Producto eliminado del carrito.', 'success')
    else:
        flash('Producto no encontrado en el carrito.', 'danger')

    return redirect(url_for('mostrar_carrito'))


@app.route('/checkout')
def checkout():
    carrito = session.get('carrito', {})
    total = sum(i['precio']*i['cantidad'] for i in carrito.values())
    return render_template('usuario/car/checkout.html', carrito=carrito, total=total)

@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    # Aquí guardas pedido en BD y limpias sesión
    # session.pop('carrito', None)
    return render_template('usuario/car/gracias.html')  # plantilla de agradecimiento


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

def logout():
    from controllers.userController import UserController
    return UserController.logout()

@app.route('/admin')

def admin_dashboard():
    if current_user.is_authenticated and current_user.is_admin():
        return render_template('administrador/admin_dashboard.html', miData=listaZapatos())
    flash("Acceso no autorizado.")
    return redirect(url_for('login'))


@app.route('/registrar-producto', methods=['GET', 'POST'])

def addProducto():
    return render_template('administrador/acciones/add.html', categorias=obtenerCategorias())

@app.route('/form-add-producto', methods=['POST'])

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

def verDetalleZapato(id_producto):
    zapato = getZapatoById(id_producto)
    if zapato:
        return render_template('administrador/acciones/view.html', zapato=zapato)
    flash('Producto no encontrado.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/form-update-producto/<int:id_producto>', methods=['GET', 'POST'])

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

def formViewBorrarProducto():
    id_producto = request.form['id_producto']
    imagen = request.form['imagen']
    resultado = eliminarProducto(id_producto, imagen)
    return jsonify([1 if resultado == 1 else 0])

@app.route('/usuario')

# ---
def usuario_dashboard():
    if current_user.is_authenticated and current_user.is_regular_user():
        return render_template('usuario/usuario_dashboard.html')
    flash("Acceso no autorizado.")
    return redirect(url_for('login'))

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

# --- Rutas protegidas ---
@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

def status_401():
    return redirect(url_for('login'))

def status_404():
    return "<h1>Página no encontrada</h1>", 404

# --- Iniciar la aplicación ---
if __name__ == '__main__':
    app.register_error_handler(401, error_401)
    app.register_error_handler(404, error_404)
    app.run(debug=True)
    
