from sqlalchemy import text
# Asegúrate de que este import apunte a donde tienes tu código de conexión
# Si lo guardaste como database.py, es así:
from database.database import engine



def probar_conexion():
    try:
        # Intentamos abrir una conexión real
        with engine.connect() as connection:
            # Ejecutamos una consulta muy simple para probar
            # SELECT 1 es el "Hola Mundo" de las bases de datos
            result = connection.execute(text("SELECT 1"))
            print("✅ ¡Conexión exitosa! La base de datos responde.")
            print(f"Resultado de prueba: {result.fetchone()}")

    except Exception as e:
        print(f"❌ Error en la conexión: {e}")


if __name__ == "__main__":
    probar_conexion()