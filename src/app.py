from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_required, current_user
from flask_mysqldb import MySQL
from config import config

# Crea la aplicación
app = Flask(__name__)

# Configura la aplicación primero
app.config.from_object(config['development'])
app.secret_key = config['development'].SECRET_KEY

# Inicializa MySQL después de la configuración
mysql = MySQL(app)

# Configura login manager
login_manager = LoginManager(app)

# Importaciones de modelos y controladores
from models.modelUser import ModelUser
from models.entities.user import User
from controllers.userController import UserController

@login_manager.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return UserController.login_post(mysql)
    else: 
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    return UserController.logout()

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.is_admin():
        return render_template('administrador/admin_dashboard.html')
    else:
        flash("Acceso no autorizado.")
        return redirect(url_for('usuario/usuario_dashboard.html'))

@app.route('/usuario')
@login_required
def usuario_dashboard():
    return render_template('usuario/usuario_dashboard.html')



@app.route('/index_login')
def inicio_usuarios():
    return render_template('auth/login.html')

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

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

if __name__ == '__main__': 
    # Manejadores de error
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404) 
    app.run()