from werkzeug.security import check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_usuario, nombre, correo, contraseña, direccion, telefono, idCargoFK):
        self.id = id_usuario #0
        self.nombre = nombre #1
        self.correo = correo #2
        self.contraseña = contraseña #3
        self.direccion = direccion #4
        self.telefono = telefono #5
        self.idCargoFK = idCargoFK #6
        self.cargo = None  # Se llenará posteriormente con el objeto Role


    @classmethod
    def check_password(self, hashed_password, password):
        # Para simplificar, no estamos usando hash por ahora, pero deberías implementarlo
        return password == hashed_password
        # En producción, deberías usar:
        # return check_password_hash(hashed_password, password)
    
    def is_admin(self):
        return self.idCargoFK == 1
    
    def is_regular_user(self):
        return self.idCargoFK == 2