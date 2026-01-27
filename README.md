# 📖 GUÍA DE EJECUCIÓN DEL CRUD VOLUNTEER TECH

## 🚀 DESCRIPCIÓN

Sistema completo de gestión de voluntarios con arquitectura frontend-backend:

- **Backend**: API REST con FastAPI + SQLAlchemy + Alembic + JWT authentication
- **Frontend**: Aplicación web interactiva con Streamlit
- **Base de datos**: MySQL 8.0+ con migraciones automatizadas
- **Funcionalidades**: Gestión completa de usuarios, voluntarios, proyectos, habilidades, categorías y asignaciones

---

## 🛠️ PRERREQUISITOS

### **Requisitos del sistema:**

- Python 3.14+
- MySQL 8.0+
- Git

---

## 📁 ESTRUCTURA DEL PROYECTO

```
Proyecto2_CRUD_Equipo4/
├── app/                           # 🚀 Backend FastAPI
│   ├── config/                    # ⚙️ Configuración y logging
│   ├── controllers/               # 🎮 Lógica de negocio
│   ├── database/                  # 🗄️ Configuración de base de datos
│   ├── domain/                    # 📋 Enums y constantes
│   ├── models/                    # 📊 Modelos SQLAlchemy
│   ├── routes/                    # 🌐 Endpoints FastAPI
│   ├── schemas/                   # 📄 Schemas Pydantic (DTOs)
│   ├── utils/                     # 🔧 Utilidades (CSV, seguridad)
│   └── main.py                    # 🚀 Aplicación principal FastAPI
├── streamlit_ui/                  # 🖥️ Frontend Streamlit
│   ├── config/                    # ⚙️ Configuración de Streamlit
│   ├── components/                # 🧩 Componentes reutilizables
│   ├── pages/                     # 📄 Páginas de la aplicación
│   └── app.py                     # 🚀 Aplicación principal Streamlit
├── alembic/                       # 📊 Migraciones de base de datos
├── .env                           # ⚠️ Variables de entorno (NO subir a git)
├── alembic.ini                    # ⚙️ Configuración de Alembic
└── requirements.txt               # 📦 Dependencias
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

# En macOS:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
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

# Windows:
net start mysql


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

### **Opción A: Iniciar solo el backend (API REST)**

```bash

uvicorn main:app --reload
```

### **Opción B: Iniciar el sistema completo (Backend + Frontend)**

#### 2. Iniciar ambos servicios

```bash
# Terminal 1: Iniciar backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Iniciar frontend Streamlit
source .venv/bin/activate
cd streamlit_ui
streamlit run app.py
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

### **Sistema de autenticación JWT**

El sistema incluye autenticación basada en tokens JWT con los siguientes roles:

- **Administrador**: Acceso completo a todas las funcionalidades
- **Voluntario**: Acceso limitado a su perfil y proyectos asignados

### **Flujo de autenticación**

1. **Inicio de sesión**: Email + contraseña
2. **Generación de token JWT**: Validez configurable
3. **Acceso a recursos**: Verificación de token en cada petición
4. **Roles y permisos**: Control de acceso basado en roles

### **Variables de entorno para seguridad**

```bash
# Configuración JWT
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

````

---

## 🐛 PROBLEMAS COMUNES Y SOLUCIONES

### **Error: "Table doesn't exist"**

```bash
# Solución: Aplicar migraciones
alembic upgrade head
````

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
