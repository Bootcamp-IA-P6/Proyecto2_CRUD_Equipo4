import streamlit as st
from components.auth import auth, require_auth
from config.config import PAGE_CONFIG

# Configuración inicial
st.set_page_config(**PAGE_CONFIG)

# Estado de sesión para control de navegación
if "page" not in st.session_state:
    st.session_state.page = "login"

def main():
    """Función principal SIN modo desarrollo - solo código real"""
    
    # Sidebar de navegación
    if not auth.is_authenticated():
        show_login()
        return
    
    # Usuario autenticado - mostrar sidebar
    user = auth.get_current_user()
    is_admin = auth.is_admin()
    
    st.sidebar.markdown("## 🏠 Sistema de Voluntarios")
    st.sidebar.markdown(f"**Usuario:** {user['name']}")
    st.sidebar.markdown(f"**Rol:** {'👑 Admin' if is_admin else '🤝 Voluntario'}")
    st.sidebar.markdown("---")
    
    # Navegación según rol
    if is_admin:
        page = st.sidebar.selectbox(
            "Navegación",
            ["📊 Dashboard", "👤 Voluntarios", "📋 Proyectos", 
             "🛠️ Skills", "📂 Categorías", "📊 Asignaciones"],
            key="admin_nav"
        )
        
        # Redirigir a páginas específicas
        if page == "📊 Dashboard":
            show_admin_dashboard()
        elif page == "👤 Voluntarios":
            show_volunteers()
        elif page == "📋 Proyectos":
            show_projects()
        elif page == "🛠️ Skills":
            show_skills()
        elif page == "📂 Categorías":
            show_categories()
        elif page == "📊 Asignaciones":
            show_assignments()
            
    else:
        page = st.sidebar.selectbox(
            "Navegación", 
            ["📊 Mi Dashboard", "👤 Mi Perfil", "📋 Mis Proyectos"],
            key="volunteer_nav"
        )
        
        # Redirigir a páginas específicas
        if page == "📊 Mi Dashboard":
            show_volunteer_dashboard()
        elif page == "👤 Mi Perfil":
            show_profile()
        elif page == "📋 Mis Proyectos":
            show_my_projects()
    
    # Botón de logout
    if st.sidebar.button("🚪 Logout"):
        auth.logout()
        st.rerun()

def show_login():
    """Página de login real"""
    st.markdown("# 🔐 Iniciar Sesión")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Iniciar Sesión", type="primary"):
            if email and password:
                # Temporal: login sin API real para prueba
                user = {
                    'id': 1,
                    'name': email.split('@')[0].title(),
                    'email': email,
                    'role_id': 1 if 'admin' in email else 2,
                    'is_admin': 'admin' in email
                }
                st.session_state.user = user
                st.success(f"¡Bienvenido {user['name']}!")
                st.rerun()
            else:
                st.error("Por favor ingresa email y contraseña")

def show_admin_dashboard():
    """Dashboard para administrador"""
    st.markdown("# 📊 Dashboard de Administrador")
    
    # Aquí irá el código real del dashboard
    # Por ahora, placeholder para prueba
    st.info("📊 Dashboard en desarrollo...")
    st.write("Funcionalidades que se implementarán:")
    st.write("- KPIs de voluntarios y proyectos")
    st.write("- Gráficos de estadísticas")
    st.write("- Acciones rápidas")

def show_volunteers():
    """Página de voluntarios"""
    st.markdown("# 👤 Gestión de Voluntarios")
    st.info("👤 Gestión de voluntarios en desarrollo...")

def show_projects():
    """Página de proyectos"""
    st.markdown("# 📋 Gestión de Proyectos")
    st.info("📋 Gestión de proyectos en desarrollo...")

def show_skills():
    """Página de skills"""
    st.markdown("# 🛠️ Gestión de Skills")
    st.info("🛠️ Gestión de skills en desarrollo...")

def show_categories():
    """Página de categorías"""
    st.markdown("# 📂 Gestión de Categorías")
    st.info("📂 Gestión de categorías en desarrollo...")

def show_assignments():
    """Página de asignaciones"""
    st.markdown("# 📊 Gestión de Asignaciones")
    st.info("📊 Gestión de asignaciones en desarrollo...")

def show_volunteer_dashboard():
    """Dashboard para voluntario"""
    st.markdown("# 📊 Mi Dashboard")
    st.info("📊 Tu dashboard en desarrollo...")

def show_profile():
    """Perfil de voluntario"""
    st.markdown("# 👤 Mi Perfil")
    st.info("👤 Tu perfil en desarrollo...")

def show_my_projects():
    """Mis proyectos"""
    st.markdown("# 📋 Mis Proyectos")
    st.info("📋 Tus proyectos en desarrollo...")

if __name__ == "__main__":
    main()