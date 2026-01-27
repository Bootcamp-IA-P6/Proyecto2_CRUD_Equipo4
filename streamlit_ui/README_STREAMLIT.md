# Documentación del Proyecto: Backend y Flujos de Usuario

## 🛠️ Instalación Frontend (Streamlit)

Sigue estos pasos para levantar la interfaz de usuario:

```bash
# Abrir nueva terminal
cd streamlit_ui

# Instalar dependencias
pip install -r requirements.txt

# Iniciar Streamlit
streamlit run app.py


## 🔗 Comunicación con Backend
### Endpoints Faltantes Clave

| Método | Endpoint | Descripción | Rol |
| :--- | :--- | :--- | :--- |
| **GET** | `/assignments/all` | Todas las asignaciones del sistema | Admin |
| **GET** | `/statistics/summary` | KPIs globales y métricas | Admin |
| **POST** | `/notifications` | Sistema de alertas y notificaciones | Admin |

---

## ✅ Funcionalidades Operativas
1. **Autenticación**: Login/logout con manejo de roles (admin/voluntario).
2. **Dashboard Admin**: Visualización de KPIs y accesos directos de creación.
3. **Creación de Voluntarios**: Formulario de alta de usuario + proceso de activación.
4. **Asignaciones**: Matching inteligente, creación manual y gestión de estados.

---

## 🔍 Flujo de Usuario Actual

### **Admin**
`Login` → `Dashboard` → `Nuevo Voluntario` → `Crear usuario` → `Activar voluntario`

### **Voluntario**
`Login` → `Dashboard` → `Mis Asignaciones` → `Ver/Aceptar/Rechazar/Completar`

---

## ☑️ Checklist de Verificación Funcional

### 🔸 Autenticación
- [ ] Login correcto con usuario/contraseña.
- [ ] Redirección correcta según rol (admin/voluntario).
- [ ] Logout limpia sesión y redirige al login.

### 🔸 Dashboard Admin
- [ ] KPIs de proyectos/voluntarios/skills se cargan correctamente.
- [ ] Botón "Nuevo Voluntario" abre formulario.
- [ ] Botón "Nuevo Proyecto" funciona.
- [ ] Enlaces laterales a otras secciones funcionan.

### 🔸 Creación de Voluntario
- [ ] Formulario de usuario se muestra con campos requeridos.
- [ ] Validación de contraseña funciona.
- [ ] Selección de rol funciona.
- [ ] Creación exitosa activa automáticamente al voluntario.
- [ ] Botón "Cancelar" vuelve al dashboard.

### 🔸 Asignaciones (Admin)
- [ ] Acceso desde menú lateral.
- [ ] Botón "Crear Asignación Manual" abre formulario.
- [ ] Selección de proyecto muestra sus skills.
- [ ] Selección de voluntario valida skill matching.
- [ ] Botón "Crear Asignación" crea registro.
- [ ] Botón "Ver Matches" muestra voluntarios compatibles.

### 🔸 Asignaciones (Voluntario)
- [ ] Pestaña "Mis Asignaciones" muestra asignaciones actuales.
- [ ] Botones "Aceptar"/"Rechazar" funcionan para estados `PENDING`.
- [ ] Botón "Marcar Completado" funciona para estados `ACCEPTED`.
- [ ] Pestaña "Disponibles" muestra proyectos según skills.

---

## 🧪 Pruebas Específicas

### 1. Test de Creación Voluntario
> **Ruta:** Admin login → Dashboard → "Nuevo Voluntario" → Completar formulario → "Crear Usuario" → Ver éxito → Volver al dashboard.

### 2. Test de Asignación Manual
> **Ruta:** Admin login → Asignaciones → "Crear Manual" → Seleccionar proyecto → Seleccionar voluntario → Ver match de skills → "Crear Asignación" → Ver éxito.

### 3. Test de Flujo Voluntario
> **Ruta:** Voluntario login → Mis Asignaciones → Ver asignación `PENDING` → "Aceptar" → Ver cambio a `ACCEPTED` → "Marcar Completado".
```
