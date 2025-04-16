from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, cedula, nombre, correo, contraseña, direccion, telefono, idCargoFK, id_usuario=None):
        self.id = id_usuario
        self.cedula = cedula #1
        self.nombre = nombre #2
        self.correo = correo #3
        self.contraseña = contraseña #4
        self.direccion = direccion #5
        self.telefono = telefono #6
        self.idCargoFK = idCargoFK #7
        self.cargo = None  # Se llenará posteriormente con el objeto Role


    @classmethod
    def check_password(self, hashed_password, password):
        # Para simplificar, no estamos usando hash por ahora, pero deberías implementarlo
        return check_password_hash(hashed_password, password)
    
    def is_admin(self):
        return self.idCargoFK == 1
    
    def is_regular_user(self):
        return self.idCargoFK == 2