import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_required, current_user
from flask import request, jsonify
from flask_mysqldb import MySQL 
from werkzeug.utils import secure_filename
from config import config
from controllers.registroController import RegistroController
from models.modelUser import ModelUser
from models.entities.user import User
from controllers.userController import UserController
from controllers.productoController import listaZapatos 
from controllers.productoController import updateZapatos
from controllers.productoController import registrarZapatos 
from controllers.productoController import recibeActualizarZapatos
from datetime import datetime


# Crea la aplicación
app = Flask(__name__)

# Configura la aplicación primero
app.config.from_object(config['development'])
app.secret_key = config['development'].SECRET_KEY

# Inicializa MySQL después de la configuración
mysql = MySQL(app)

# Configura login manager
login_manager = LoginManager(app)

# Vista a la que redirige si no estás logueado
login_manager.login_view = 'login'

msg  =''
tipo =''

@login_manager.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)


# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return RegistroController.register_post(mysql)
    else:
        return render_template('./auth/register.html')




# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return UserController.login_post(mysql)
    else:
        return render_template('./auth/login.html')


# Ruta para logout
@app.route('/logout')
def logout():
    return UserController.logout()


# Ruta de dashboard para administradores
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.is_admin():
        return render_template('administrador/admin_dashboard.html', miData = listaZapatos())
    else:
        flash("Acceso no autorizado.")
        return redirect(url_for('usuario_dashboard'))

@app.route('/registrar-producto', methods=['GET','POST'])
@login_required
def addProducto():
    return render_template('administrador/acciones/add.html')

    
#ACCIONES AGREGAR - ADMINISTRADOR
@app.route('/form-add-producto', methods=['GET', 'POST'])
@login_required
def formAddProducto():
    categorias = obtenerCategorias()  # Cargar siempre las categorías
    print("CATEGORÍAS:", categorias)

    if request.method == 'POST':
        nombre_producto     = request.form['nombre_producto']
        stock               = request.form['stock']
        precio              = request.form['precio']
        descripcion         = request.form['descripcion']
        id_categoria        = request.form['id_categoria']

        if request.files['imagen'] != '':
            file = request.files['imagen']
            nuevoNombreFile = recibeFoto(file)
            
            resultData = registrarZapatos(
                nombre_producto, stock, precio,
                descripcion, nuevoNombreFile, id_categoria
            )
            
            if resultData == 1:
                return render_template('administrador/acciones/add.html', miData=listaZapatos(), msg='El registro fue un éxito', tipo=1, categorias=categorias)
            else:
                return render_template('administrador/admin_dashboard.html', miData=listaZapatos(), msg='Ocurrió un error al registrar', tipo=0)
        else:
            return render_template('administrador/acciones/add.html', msg='Debe cargar una imagen', tipo=0, categorias=categorias)

    return render_template('administrador/acciones/add.html', categorias=categorias)

def obtenerCategorias():
    try:
        cursor = mysql.connection.cursor() 
        cursor.execute("SELECT id_categoria, nombre_categoria FROM Categoria")
        categorias = cursor.fetchall()
        cursor.close()
        print(" Categorías obtenidas:", categorias)  # Esto va a decir si está vacío o no
        return categorias
    except Exception as e:
        print("Error al obtener categorías:", str(e))
        return [] # Devuelve lista vacía en caso de error
    
#Acciones VER - ADMINISTRADOR
@app.route('/ver-detalles-del-zapato/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def verDetalleZapato(id_producto):
    msg =''
    if request.method == 'GET':
        resultData = verDetalleZapato(id_producto) #Funcion que almacena los detalles del carro
        
        if resultData:
            return render_template('administrador/acciones/view.html', infoZapatos = resultData, msg='Detalles del Zapato', tipo=1)
        else:
            return render_template('administrador/admin_dashboard.html', msg='No existe el Zapato', tipo=1)
    return redirect(url_for('admin_dashboard'))

#ACCIONES EDITAR - ADMINISTRADOR
@app.route('/form-update-producto/<string:id_producto>', methods=['GET', 'POST'])
@login_required
def formViewUpdate(id_producto):
    if request.method == 'GET':
        # Obtener los datos del producto por ID
        resultData = updateZapatos(id_producto)
        
        # Si se encuentra el producto, renderiza el formulario de actualización
        if resultData:
            return render_template('administrador/acciones/update.html', dataInfo=resultData)
        else:
            # Si no se encuentra el producto, muestra un mensaje
            return render_template('administrador/admin_dashboard.html', miData=listaZapatos(), msg='No existe el producto', tipo=1)
    
    # Si se recibe un método HTTP incorrecto, mostrar un error
    else:
        return render_template('administrador/admin_dashboard.html', miData=listaZapatos(), msg='Método HTTP incorrecto', tipo=1)

@app.route('/actualizar-producto/<string:id_producto>', methods=['POST'])
@login_required
def formActualizarProducto(idProducto):
    nombre        = request.form.get('nombre_producto')
    descripcion   = request.form.get('descripcion')
    precio        = request.form.get('precio')
    categoria     = request.form.get('categoria')
    stock         = request.form.get('stock')
    
    # Manejo de imagen opcional
    foto_producto = None
    file = request.files.get('foto')
    if file and file.filename:
        foto_producto = recibeFoto(file)

    # Llamar a la función para actualizar el producto
    resultData = recibeActualizarZapatos(
        nombre, descripcion, precio, categoria, stock, foto_producto, idProducto
    )

    msg = 'Producto actualizado correctamente' if resultData == 1 else 'No se pudo actualizar el producto'
    tipo = 1

    return render_template('administrador/admin_dashboard.html', miData=listaZapatos(), msg=msg, tipo=tipo)


#ACCIONES ELIMINAR - ADMINISTRADOR
@app.route('/borrar-producto', methods=['POST'])
@login_required
def formViewBorrarProducto():
    if request.method == 'POST':
        id_producto   = request.form['id_producto']
        nombre_imagen = request.form['imagen']
        
        resultado = eliminarProducto(id_producto, nombre_imagen)

        if resultado == 1:
            return jsonify([1])
        else:
            return jsonify([0])
def eliminarProducto(id_producto='', nombre_imagen=''):
    try:
        db_config = config['development']
        conexion_MySQLdb = mysql.connector.connect(
            host=db_config.MYSQL_HOST,
            user=db_config.MYSQL_USER,
            password=db_config.MYSQL_PASSWORD,
            database=db_config.MYSQL_DB
        )

        cur = conexion_MySQLdb.cursor(dictionary=True)

        # Eliminar el producto por ID
        cur.execute('DELETE FROM productos WHERE id_producto = %s', (id_producto,))
        conexion_MySQLdb.commit()
        resultado_eliminar = cur.rowcount  # Retorna 1 si se eliminó, 0 si no

        cur.close()
        conexion_MySQLdb.close()

        # Borrar la imagen del producto si existe
        if nombre_imagen:
            basepath = os.path.dirname(__file__)
            ruta_imagen = os.path.join(basepath, 'static/img/', nombre_imagen)
            
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)

        return resultado_eliminar
    
    except Exception as e:
        print(f"Ocurrió un error al eliminar el producto: {e}")
        return 0
    

# funcion imagen
def recibeFoto(file):
    # Obtener la ruta base del proyecto
    basepath = os.path.dirname(__file__)

    # Obtener el nombre del archivo y la extensión (ej: .jpg, .png)
    filename = file.filename
    extension = os.path.splitext(filename)[1]

    # Crear un nombre único usando la fecha y hora actual
    nuevoNombreFile = datetime.now().strftime('%Y%H%M%S') + extension

    # Crear la ruta completa de guardado
    upload_path = os.path.join(basepath, '../static/img/', nuevoNombreFile)

    # Guardar la imagen
    file.save(upload_path)

    # Devolver el nuevo nombre del archivo
    return nuevoNombreFile

# Ruta de dashboard para usuarios
@app.route('/usuario')
@login_required
def usuario_dashboard():
    return render_template('usuario/usuario_dashboard.html')


# Ruta para ver novedades
@app.route('/novedades_destacados')
def novedades():
    return render_template('novedades.html')


# Ruta para categorías (por ejemplo, mujeres)
@app.route('/categoria_mujer')
def mujer():
    return render_template('mujer.html')


# Ruta para categorías (por ejemplo, hombres)
@app.route('/categoria_hombre')
def hombre():
    return render_template('hombre.html')


# Ruta para categorías (por ejemplo, niños)
@app.route('/categoria_niños')
def niños():
    return render_template('niños.html')


# Ruta para ofertas
@app.route('/categoria_oferta')
def ofertas():
    return render_template('ofertas.html')


# Manejadores de error 401 y 404
def status_401(error):
    return redirect(url_for('login'))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


if __name__ == '__main__':
    # Registrar manejadores de error
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()