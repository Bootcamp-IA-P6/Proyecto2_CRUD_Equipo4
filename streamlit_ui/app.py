import streamlit as st
from components.auth import auth, require_auth
from config.config import PAGE_CONFIG
from components.api_client import api_client
from components.tables import format_date, status_badge
from components.forms import user_form, volunteer_form
from components.forms import project_form

# Configuración inicial
st.set_page_config(**PAGE_CONFIG)

# Inicializar estado de navegación
def init_session_state():
    """Inicializar estado de sesión si no existe"""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    if "navigation_trigger" not in st.session_state:
        st.session_state.navigation_trigger = 0
    if "create_project" not in st.session_state:
        st.session_state.create_project = False
    if "create_volunteer" not in st.session_state:
        st.session_state.create_volunteer = False
    if "create_skill" not in st.session_state:
        st.session_state.create_skill = False

# Llamar al inicio
init_session_state()

def navigate_to_page(page_name: str):
    """Función centralizada para navegación"""
    st.session_state.current_page = page_name
    st.session_state.navigation_trigger += 1
    st.rerun()

def show_sidebar():
    """Sidebar inteligente con manejo de estado"""
    
    # Usuario no autenticado
    if not auth.is_authenticated():
        st.sidebar.markdown("# LOGIN REQUERIDO")
        st.sidebar.info("Por favor, inicia sesión para continuar.")
        if st.sidebar.button("🔙 Ir al Login", use_container_width=True):
            navigate_to_page("login")
        return "login"
    
    # Usuario autenticado
    st.sidebar.markdown("# 🏠 Sistema de Voluntarios")
    user = auth.get_current_user()
    is_admin = auth.is_admin()
    
    # Info del usuario
    st.sidebar.markdown(f"**👤 {user.get('name', 'Usuario')}**")
    st.sidebar.markdown(f"**🎯 {'👑 Administrador' if is_admin else '🤝 Voluntario'}**")
    st.sidebar.markdown("---")
    
    # Navegación por rol
    if is_admin:
        st.sidebar.subheader("📋 Administración")
        
        # Botones de navegación directos
        if st.sidebar.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
            navigate_to_page("dashboard_admin")
        
        if st.sidebar.button("👤 Voluntarios", key="nav_volunteers", use_container_width=True):
            navigate_to_page("volunteers")
        
        if st.sidebar.button("📋 Proyectos", key="nav_projects", use_container_width=True):
            navigate_to_page("projects")
        
        if st.sidebar.button("🛠️ Skills", key="nav_skills", use_container_width=True):
            navigate_to_page("skills")
        
        if st.sidebar.button("📂 Categorías", key="nav_categories", use_container_width=True):
            navigate_to_page("categories")
        
        if st.sidebar.button("📊 Asignaciones", key="nav_assignments", use_container_width=True):
            navigate_to_page("assignments")
        
    else:
        st.sidebar.subheader("📋 Mi Espacio")
        
        if st.sidebar.button("📊 Mi Dashboard", key="nav_my_dashboard", use_container_width=True):
            navigate_to_page("dashboard_volunteer")
        
        if st.sidebar.button("👤 Mi Perfil", key="nav_my_profile", use_container_width=True):
            navigate_to_page("profile")
        
        if st.sidebar.button("📋 Mis Proyectos", key="nav_my_projects", use_container_width=True):
            navigate_to_page("my_projects")
    
    st.sidebar.markdown("---")
   
    
    # Logout
    if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
        auth.logout()
        navigate_to_page("login")
    
    return st.session_state.current_page

def show_login():
    st.markdown("# 🔐 Sistema de Voluntarios")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Contenedor para mensajes: se limpia y se llena según la acción
        placeholder = st.empty()
        
        with st.form("login_form", clear_on_submit=False): # Cambié a False para que no se borre el email si falla
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            submitted = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
            
            if submitted:
                if email and password:
                    
                    user, error = auth.login(email, password)
                    
                    if user:
                        placeholder.success(f"¡Bienvenido {user['name']}!")
                        navigate_to_page("dashboard_admin" if auth.is_admin() else "dashboard_volunteer")
                        st.rerun() 
                    else:
                        # Si hay error, lo mostramos arriba del formulario
                        placeholder.error(error)
                else:
                    placeholder.warning("Por favor, completa todos los campos")

def show_dashboard_admin():
    """Dashboard de administrador funcional"""
    require_auth()
    
    if not auth.is_admin():
        st.error("Acceso denegado: Se requieren permisos de administrador")
        navigate_to_page("login")
        return
    
    st.markdown("# 📊 Dashboard de Administrador")
    
    # Estado de creación
    if st.session_state.create_project:
        return show_create_project_form()
    if st.session_state.create_volunteer:
        return show_create_volunteer_form()
    if st.session_state.create_skill:
        return show_create_skill_form()
    
    try:
        # Obtener datos
        volunteers_response = api_client.get_volunteers(size=100)
        projects_response = api_client.get_projects(size=100)
        skills_response = api_client.get_skills(size=100)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        skills = skills_response.get('items', [])
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👤 Voluntarios", len(volunteers))
        with col2:
            st.metric("📋 Proyectos", len(projects))
        with col3:
            st.metric("🛠️ Skills", len(skills))
        with col4:
            st.metric("🔄 Activos", len([p for p in projects if p.get('status') in ['not_assigned', 'assigned', 'in_progress']]))
        
        # ACCIONES RÁPIDAS - BOTONES FUNCIONALES
        st.markdown("---")
        st.subheader("⚡ Acciones Rápidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Nuevo Proyecto", type="primary", use_container_width=True, key="btn_create_project"):
                st.session_state.create_project = True
                st.rerun()
        
        with col2:
            if st.button("➕ Nuevo Voluntario", type="primary", use_container_width=True, key="btn_create_volunteer"):
                st.session_state.create_volunteer = True
                st.rerun()
        
        with col3:
            if st.button("➕ Nueva Skill", use_container_width=True, key="btn_create_skill"):
                st.session_state.create_skill = True
                st.rerun()
        
        with col4:
            if st.button("📊 Ver Asignaciones", use_container_width=True, key="btn_assignments"):
                navigate_to_page("assignments")
        
        # Lista de proyectos recientes
        st.markdown("---")
        st.subheader("📋 Proyectos Recientes")
        
        if projects:
            for project in projects[:5]:
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"📝 {project.get('description', 'N/A')[:100]}...")
                        st.write(f"📅 Inicio: {format_date(project.get('start_date'))}")
                    with col2:
                        st.write(f"🎯 Estado: {status_badge(project.get('status'))}")
                        st.write(f"📅 Fin: {format_date(project.get('end_date'))}")
        else:
            st.info("No hay proyectos para mostrar")
    
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        if st.checkbox("Mostrar error detallado"):
            import traceback
            st.code(traceback.format_exc())

def show_create_project_form():
    """Formulario para crear proyecto"""
    st.markdown("## ➕ Crear Nuevo Proyecto")
    
    
    with st.form("create_project_form", clear_on_submit=True):
        st.subheader("📋 Información del Proyecto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre del Proyecto *", key="proj_name")
            start_date = st.date_input("Fecha de Inicio *", key="proj_start")
            status_options = ["planning", "in_progress", "completed", "cancelled"]
            status = st.selectbox("Estado", options=status_options, key="proj_status")
        
        with col2:
            end_date = st.date_input("Fecha de Fin *", key="proj_end")
            priority_options = ["high", "medium", "low"]
            priority = st.selectbox("Prioridad", options=priority_options, key="proj_priority")
            
            # Obtener categorías
            try:
                categories_response = api_client.get_categories(size=100)
                categories = categories_response.get('items', [])
                if categories:
                    category_options = {cat['name']: cat['id'] for cat in categories}
                    category_name = st.selectbox("Categoría *", options=list(category_options.keys()), key="proj_category")
                    category_id = category_options[category_name]
                else:
                    st.error("No hay categorías disponibles")
                    return
            except:
                st.error("Error al cargar categorías")
                return
        
        description = st.text_area("Descripción *", key="proj_description")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Crear Proyecto", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted:
            try:
                project_data = {
                    'name': name,
                    'description': description,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'status': status,
                    'priority': priority,
                    'category_id': category_id
                }
                
                result = api_client.create_project(project_data)
                st.success("✅ Proyecto creado exitosamente!")
                st.session_state.create_project = False
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error al crear proyecto: {e}")
        
        if cancelled:
            st.session_state.create_project = False
            st.rerun()

def show_create_volunteer_form():
    """Formulario para crear voluntario"""
    st.markdown("## ➕ Crear Nuevo Voluntario")
    
    # Botón para volver al dashboard
    if st.button("🔙 Volver al Dashboard", key="back_to_dashboard"):
        st.session_state.create_volunteer = False
        st.rerun()
    
    # Formulario de usuario
    with st.form("create_volunteer_form"):
        st.subheader("📝 Información de Usuario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre Completo *", key="create_user_name")
            email = st.text_input("Email *", key="create_user_email")
        
        with col2:
            phone = st.text_input("Teléfono", key="create_user_phone")
            birth_date = st.date_input("Fecha de Nacimiento", key="create_user_birth_date")
        
        password = st.text_input("Contraseña *", type="password", key="create_user_password")
        confirm_password = st.text_input("Confirmar Contraseña *", type="password", key="create_user_confirm_password")
        
        if password and password != confirm_password:
            st.error("Las contraseñas no coinciden")
        
        # Obtener roles
        roles = []
        role_options = {}
        selected_role_id = None
        
        try:
            roles_response = api_client.get_roles()
            roles = roles_response.get('items', []) if isinstance(roles_response, dict) else []
            
            if roles:
                role_options = {role['name']: role['id'] for role in roles}
                selected_role_name = st.selectbox(
                    "Rol *",
                    options=list(role_options.keys()),
                    index=0,
                    key="create_user_role"
                )
                selected_role_id = role_options[selected_role_name]
            else:
                st.error("No hay roles disponibles. Contacte al administrador.")
        except Exception as e:
            st.error(f"Error al cargar roles: {e}")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Crear Voluntario", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted and password == confirm_password and selected_role_id:
            try:
                # Paso 1: Crear usuario
                user_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'birth_date': birth_date.isoformat(),
                    'password': password,
                    'role_id': selected_role_id
                }
                
                created_user = api_client.create_user(user_data)
                st.success(f"✅ Usuario creado exitosamente con ID: {created_user['id']}")
                
                # Paso 2: Activar como voluntario
                volunteer_data = {
                    'user_id': created_user['id'],
                    'status': 'active'  # Valor por defecto según el schema
                }
                
                result = api_client.create_volunteer(volunteer_data)
                st.success("✅ Usuario activado como voluntario exitosamente!")
                
                # Limpiar estado y volver al dashboard
                st.session_state.create_volunteer = False
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        if cancelled:
            st.session_state.create_volunteer = False
            st.rerun()

def show_create_skill_form():
    """Formulario para crear skill"""
    st.markdown("## ➕ Crear Nueva Skill")
    
    with st.form("create_skill_form", clear_on_submit=True):
        name = st.text_input("Nombre de la Skill *", key="skill_name")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Crear Skill", type="primary", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted:
            try:
                skill_data = {'name': name}
                result = api_client.create_skill(skill_data)
                st.success("✅ Skill creada exitosamente!")
                st.session_state.create_skill = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al crear skill: {e}")
        
        if cancelled:
            st.session_state.create_skill = False
            st.rerun()

def render_page():
    """Renderizado principal de páginas"""
    current_page = st.session_state.current_page
    
    
    # Routing
    if current_page == "login":
        show_login()
    elif current_page == "dashboard_admin":
        show_dashboard_admin()
    elif current_page == "volunteers":
        import pages.volunteers
        pages.volunteers.show()
    elif current_page == "projects":
        import pages.projects
        pages.projects.show()
    elif current_page == "skills":
        import pages.skills
        pages.skills.show()
    elif current_page == "categories":
        import pages.categories
        pages.categories.show()
    elif current_page == "assignments":
        import pages.assignments
        pages.assignments.show()
    elif current_page == "dashboard_volunteer":
        import pages.dashboard
        pages.dashboard.show()
    elif current_page == "profile":
        import pages.profile
        pages.profile.show()
    elif current_page == "my_projects":
        import pages.projects
        pages.projects.show()
    else:
        st.error(f"Página no encontrada: {current_page}")
        navigate_to_page("dashboard_admin" if auth.is_admin() else "dashboard_volunteer")

def main():
    """Función principal"""
    # Mostrar sidebar
    show_sidebar()
    
    # Renderizar página actual
    render_page()

if __name__ == "__main__":
    main()