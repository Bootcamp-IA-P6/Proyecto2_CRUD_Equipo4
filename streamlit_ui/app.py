import streamlit as st
from components.auth import auth, require_auth
from config.config import PAGE_CONFIG

# Configuración inicial
st.set_page_config(**PAGE_CONFIG)

# Estado de sesión para control de navegación
if "page" not in st.session_state:
    st.session_state.page = "login"

# Sidebar de navegación
def show_sidebar():
    st.sidebar.markdown("## 🏠 Sistema de Voluntarios")
    
    if auth.is_authenticated():
        user = auth.get_current_user()
        st.sidebar.markdown(f"**Usuario:** {user['name']}")
        st.sidebar.markdown(f"**Rol:** {'👑 Admin' if auth.is_admin() else '🤝 Voluntario'}")
        st.sidebar.markdown("---")
        
        # Navegación según rol
        if auth.is_admin():
            page = st.sidebar.selectbox(
                "Navegación",
                ["📊 Dashboard", "👤 Voluntarios", "📋 Proyectos", 
                 "🛠️ Skills", "📂 Categorías", "📊 Asignaciones"],
                key="admin_nav"
            )
        else:
            page = st.sidebar.selectbox(
                "Navegación", 
                ["📊 Mi Dashboard", "👤 Mi Perfil", "📋 Mis Proyectos"],
                key="volunteer_nav"
            )
        
        if st.sidebar.button("🚪 Logout"):
            auth.logout()
            st.rerun()
        
        return page
    else:
        return "login"


def show_login():
    """Página de login"""
    st.markdown("# 🔐 Iniciar Sesión")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Iniciar Sesión", type="primary"):
            user = auth.login(email, password)
            if user:
                st.session_state.user = user
                st.success(f"¡Bienvenido {user['name']}!")
                st.rerun()
            else:
                st.error("Email o contraseña incorrectos")

def main():
    """Función principal de la aplicación"""
    # Determinar página actual
    if not auth.is_authenticated():
        show_login()
        return
    
    page = show_sidebar()
    
    # Redirigir a página correspondiente
    if page == "login" or not auth.is_authenticated():
        show_login()
    elif page == "📊 Dashboard" or page == "📊 Mi Dashboard":
        import pages.dashboard
        pages.dashboard.show()
    elif page == "👤 Voluntarios":
        import pages.volunteers
        pages.volunteers.show()
    elif page == "👤 Mi Perfil":
        import pages.profile
        pages.profile.show()
    elif page == "📋 Proyectos" or page == "📋 Mis Proyectos":
        import pages.projects
        pages.projects.show()
    elif page == "🛠️ Skills":
        import pages.skills
        pages.skills.show()
    elif page == "📂 Categorías":
        import pages.categories
        pages.categories.show()
    elif page == "📊 Asignaciones":
        import pages.assignments
        pages.assignments.show()

if __name__ == "__main__":
    main()