from flask import request, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from models.modelUser import ModelUser

class UserController:
    @classmethod
    def login_post(cls, db):
     if request.method == 'POST':
        correo = request.form['username']
        contraseña = request.form['password']
        user = ModelUser.login(db, correo, contraseña)
        
        if user is not None:
            login_user(user)
            if user.is_admin(): 
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('usuario_dashboard'))
        else:
            flash("Usuario o contraseña incorrectos")
            # Este es el error - debes usar url_for en lugar de la ruta del archivo
            return redirect(url_for('login'))
    
    # También aquí
     return redirect(url_for('login'))
    
    @classmethod
    def logout(cls):    
        logout_user()
        return redirect(url_for('login'))