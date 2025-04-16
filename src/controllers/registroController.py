from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from models.modelUser import ModelUser
from models.entities.user import User

class RegistroController:
    @classmethod
    def register_post(cls, db):
        if request.method == 'POST':
            # Obtener datos del formulario
            cedula = request.form['cedula']
            nombre = request.form['nombre']
            correo = request.form['correo']
            contraseña = request.form['contraseña']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            idCargoFK = 2  # formulario solo para usuarios

            # Validar datos (opcional)
            if not cedula or not nombre or not correo or not contraseña:
                flash("Todos los campos son obligatorios", "danger")
                return redirect(url_for('register'))

            # Hashear contraseña
            hashed_password = generate_password_hash(contraseña)

            # Crear usuario con cédula como id
            nuevo_usuario = User(
                id_usuario=None,  # ID se generará automáticamente en la base de datos
                cedula=cedula,
                nombre=nombre,
                correo=correo,
                contraseña=hashed_password,  # Usar contraseña hasheada
                direccion=direccion,
                telefono=telefono,
                idCargoFK=idCargoFK
            )

            try:
                # Registrar usuario en la base de datos
                ModelUser.register(db, nuevo_usuario)
                flash("¡Registro exitoso! Ahora puedes iniciar sesión", "success")
                return redirect(url_for('usuario_dashboard'))
            except Exception as e:
                # Manejar errores
                flash(f"Error al registrar: {str(e)}", "danger")
                return redirect(url_for('register'))

        # Redirigir al formulario de registro si no es POST
        return redirect(url_for('register'))