# 📖 GUÍA DE EJECUCIÓN DEL PROYECTO VOLUNTEER CRUD

## 🚀 DESCRIPCIÓN

Proyecto backend FastAPI + SQLAlchemy + Alembic para la gestión de voluntarios y sus entidades relacionadas (usuarios, habilidades, proyectos, categorías).

---

## 🛠️ PRERREQUISITOS

### **Requisitos del sistema:**

- Python 3.14+
- MySQL 8.0+
- Git

### **Dependencias Python:**

```bash
pip install -r requirements.txt
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
Proyecto2_CRUD_Equipo4/
├── .env                          # ⚠️ Variables de entorno (NO subir a git)
├── alembic/                      # 📊 Migraciones de base de datos
│   ├── versions/                   # Archivos de migración generados
│   ├── env.py                      # Configuración de Alembic
│   └── script.py.mako              # Template para migraciones
├── config/                        # ⚙️ Configuración
│   └── config_variables.py          # Variables de entorno con defaults
├── controllers/                   # 🎮 Lógica de negocio
│   ├── users_controller.py
│   ├── volunteer_controller.py
│   ├── project_controller.py
│   ├── category_controller.py
│   └── skill_controller.py
├── database/                      # 🗄️ Configuración de base de datos
│   └── database.py                 # Engine, sesión y modelo base
├── domain/                        # 📋 Enums
│   ├── projects_enums.py
│   └── volunteer_enum.py
├── models/                        # 📊 Modelos SQLAlchemy
│   ├── users_model.py
│   ├── volunteers_model.py
│   ├── project_model.py
│   ├── category_model.py
│   └── skill_model.py
├── routes/                        # 🌐 Endpoints FastAPI
│   ├── users_routes.py
│   ├── volunteer_routes.py
│   ├── project_routes.py
│   └── category_routes.py
├── schemas/                       # 📄 Schemas Pydantic (DTOs)
│   ├── users_schema.py
│   ├── volunteer_schema.py
│   ├── project_schema.py
│   └── category_schemas.py
├── main.py                        # 🚀 Aplicación principal
├── alembic.ini                   # ⚙️ Configuración de Alembic
└── requirements.txt                # 📦 Dependencias
```

---

## 🚀 PASOS DE EJECUCIÓN

### **1. Configuración inicial**

#### **1.1 Clonar repositorio:**

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto2_CRUD_Equipo4
```

#### **1.2 Crear entorno virtual:**

```bash
python -m venv .venv
source .venv/bin/activate
```

#### **1.3 Instalar dependencias:**

```bash
pip install -r requirements.txt
```

#### **1.4 Configurar variables de entorno:**

```bash
# Copiar y editar el archivo .env.example
cp .env.example .env

```

#### **1.5 Iniciar base de datos MySQL:**

```bash
# En macOS con Homebrew:
brew services start mysql

# En Ubuntu/Debian:
sudo systemctl start mysql

# Verificar estado:
brew services list | grep mysql
```

### **2. Configuración de base de datos**

#### **2.1 Crear base de datos:**

```sql


-- Crear la base de datos en MySQLWorkbench:
CREATE DATABASE volunteer_crud


```

#### **2.2 Ejecutar migraciones Alembic:**

```bash
source .venv/bin/activate
source .env
alembic upgrade head
```

### **3. Iniciar aplicación**

```bash

uvicorn main:app --reload
```

---

## 🌐 ENDPOINTS DISPONIBLES

### **URL base:** `http://localhost:8000`

### **API Documentation:**

- **TESTING API -> Swagger UI:** `http://localhost:8000/docs`

- **DOCUMENTATION & INFO -> ReDoc:** `http://localhost:8000/redoc`

---

## 📊 MIGRACIONES DE BASE DE DATOS (ALEMBIC)

### **Comandos principales:**

```bash
# Ver versión actual:
alembic current

# Ver historial de migraciones:
alembic history

# Generar nueva migración:
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones pendientes:
alembic upgrade head

# Revertir última migración:
alembic downgrade -1

# Revertir a versión específica:
alembic downgrade <revision_id>
```

### **Flujo de trabajo con migraciones:**

1. **Modificar modelos** en `/models/`
2. **Generar migración:** `alembic revision --autogenerate -m "descripción"`
3. **Revisar migración generada** en `/alembic/versions/`
4. **Aplicar migración:** `alembic upgrade head`
5. **Probar cambios**
6. **Comitear cambios** y migración juntos

---

## 🔐 AUTENTICACIÓN Y SEGURIDAD

### **Variables sensibles:**

- **Nunca subir** `.env` a Git
- **Usar siempre** `os.getenv()` para leer variables
- **Defaults seguros** en `config_variables.py`

- Cambiar contraseña por defecto de MySQL
- Usar variables de entorno para passwords

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### **Error: "Table doesn't exist"**

```bash
# Solución: Aplicar migraciones
alembic upgrade head
```

### **Error: "Access denied for user"**

```bash
# Verificar variables de entorno
echo $DB_USERNAME
echo $DB_PASSWORD
# Verificar archivo .env existe
ls -la .env
```

### **Error: "Target database is not up to date"**

```bash
# Solución: Actualizar a última versión
alembic upgrade head
```

### **Error: Cannot add foreign key constraint**

```bash
# Verificar que los datos referenciados existan
SELECT * FROM categories WHERE id = <valor_del_fk>;
```

---

## 🚀 DEPLOYMENT

### **Para producción:**

1. **Configurar variables de entorno** en servidor
2. **Instalar dependencias:** `pip install -r requirements.txt`
3. **Aplicar migraciones:** `alembic upgrade head`
4. **Iniciar con workers:** `uvicorn main:app --workers 4`

### **Donde buscar ayuda:**

1. **Logs del servidor:** Consola donde se ejecuta `uvicorn`
2. **Documentación API:** `http://localhost:8000/docs`
3. **Errores de base de datos:** Logs de MySQL
4. **Estado migraciones:** `alembic history`

### **Comandos de depuración:**

```bash
# Verificar conexión a BD:
python -c "from database.database import engine; print('Conexión OK' if engine.connect() else 'Error')"


# Verificar endpoints:
curl -X GET http://localhost:8000/docs
```

---

**🎯 LISTO PARA EMPEZAR!**

Con esta guía tienes todo lo necesario para poner en marcha el proyecto Voluntario CRUD.

**Recuerda:** El archivo `.env` nunca debe subirse a Git. Usa `.env.example` como plantilla.
