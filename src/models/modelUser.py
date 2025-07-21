from .entities.user import User
from .entities.rol import Role


class ModelUser:

    @classmethod
    def login(cls, mysql, correo, contraseña):
        cursor = None
        try:
            cursor = mysql.connection.cursor()
            sql = """SELECT u.id_usuario,u.cedula, u.nombre, u.correo, u.contraseña, 
                    u.direccion, u.telefono, u.idCargoFK,
                    c.idCargo, c.nombreCargo, c.Estado
                    FROM usuarios u 
                    INNER JOIN Cargo c ON u.idCargoFK = c.idCargo
                    WHERE u.correo = %s"""
            cursor.execute(sql, (correo,))
            row = cursor.fetchone()
            
            if row is not None:
                user = User(
                    cedula=row[1],
                    nombre=row[2],
                    correo=row[3],
                    contraseña=row[4],
                    direccion=row[5],
                    telefono=row[6],
                    idCargoFK=row[7],
                    id_usuario=row[0]  # id_usuario al final
                )
                user.cargo = Role(row[8], row[9], row[10])
                print("HASH DB:", user.contraseña)
                print("INPUT PASSWORD:", contraseña)
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
            sql = """SELECT u.id_usuario, u.cedula, u.nombre, u.correo, u.contraseña, 
                    u.direccion, u.telefono, u.idCargoFK,
                    c.idCargo, c.nombreCargo, c.Estado
                    FROM usuarios u 
                    INNER JOIN Cargo c ON u.idCargoFK = c.idCargo
                    WHERE u.id_usuario = %s"""
            cursor.execute(sql, (id_usuario,))
            row = cursor.fetchone()
            
            if row is not None:
                user = User(
                    cedula=row[1],
                    nombre=row[2],
                    correo=row[3],
                    contraseña=row[4],
                    direccion=row[5],
                    telefono=row[6],
                    idCargoFK=row[7],
                    id_usuario=row[0]  # id_usuario al final
                )
                user.cargo = Role(row[8], row[9], row[10])
                return user
            return None
        except Exception as ex:
            print(f"Error en get_by_id: {ex}")
            raise Exception(f"Error al obtener usuario por ID: {ex}")
        finally:
            if cursor:
                cursor.close()
    @classmethod
    def register(cls, db, user):
        cursor = None
        try: 
            cursor = db.connection.cursor()
            # Consulta SQL para insertar un nuevo usuario
            sql = """INSERT INTO usuarios (cedula, nombre, correo, contraseña, direccion, telefono, idCargoFK)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                user.cedula,   
                user.nombre,    
                user.correo,
                user.contraseña,  # Usar la contraseña hasheada
                user.direccion, 
                user.telefono, 
                user.idCargoFK
            ))
            db.connection.commit()
            print("Usuario registrado exitosamente.")
        except Exception as ex:
            print(f"Error al registrar usuario: {ex}")
            raise Exception("No se pudo registrar el usuario.")
        finally: 
            if cursor: 
                cursor.close()