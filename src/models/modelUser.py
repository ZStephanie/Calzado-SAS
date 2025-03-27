from .entities.user import User
from .entities.rol import Role

class ModelUser:
    @classmethod
    def login(cls, mysql, correo, contraseña):
        cursor = None
        try:
            cursor = mysql.connection.cursor()
            sql = """SELECT u.id_usuario, u.nombre, u.correo, u.contraseña, 
                    u.direccion, u.telefono, u.idCargoFK,
                    c.idCargo, c.nombreCargo, c.Estado
                    FROM usuarios u 
                    INNER JOIN Cargo c ON u.idCargoFK = c.idCargo
                    WHERE u.correo = %s"""
            cursor.execute(sql, (correo,))
            row = cursor.fetchone()
            
            if row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                user.cargo = Role(row[7], row[8], row[9])
                
                if User.check_password(user.contraseña, contraseña):
                    return user
            return None
        except Exception as ex:
            print(f"Error en login: {ex}")
            raise Exception(f"Error en el inicio de sesión: {ex}")
        finally:
            if cursor:
                cursor.close()
    
    @classmethod
    def get_by_id(cls, mysql, id_usuario):
        cursor = None
        try:
            cursor = mysql.connection.cursor()
            sql = """SELECT u.id_usuario, u.nombre, u.correo, u.contraseña, 
                    u.direccion, u.telefono, u.idCargoFK,
                    c.idCargo, c.nombreCargo, c.Estado
                    FROM usuarios u 
                    INNER JOIN Cargo c ON u.idCargoFK = c.idCargo
                    WHERE u.id_usuario = %s"""
            cursor.execute(sql, (id_usuario,))
            row = cursor.fetchone()
            
            if row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                user.cargo = Role(row[7], row[8], row[9])
                return user
            return None
        except Exception as ex:
            print(f"Error en get_by_id: {ex}")
            raise Exception(f"Error al obtener usuario por ID: {ex}")
        finally:
            if cursor:
                cursor.close()