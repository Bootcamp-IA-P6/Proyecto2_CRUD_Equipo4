import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth
from components.tables import status_badge, format_date
from components.forms import user_form
from typing import Dict, List, Any

def show():
    """Página de perfil personal para voluntarios"""
    require_auth()
    
    user = auth.get_current_user()
    
    st.markdown("# 👤 Mi Perfil")
    
    # Manejar acciones
    handle_actions()
    
    # Obtener datos del voluntario
    volunteer = get_my_volunteer(user)
    
    if not volunteer:
        st.warning("No se encontró tu perfil de voluntario. Contacta al administrador.")
        return
    
    # Mostrar contenido principal
    if st.session_state.get('edit_profile'):
        show_edit_profile(user, volunteer)
    else:
        show_profile_view(user, volunteer)

def handle_actions():
    """Maneja acciones desde session state"""
    
    # Añadir skill
    if st.session_state.get('add_skill_to_profile'):
        show_add_skill()
        return
    
    # Eliminar skill
    if st.session_state.get('remove_skill'):
        confirm_remove_skill()
        return

def get_my_volunteer(user: Dict) -> Dict:
    """Obtiene el perfil de voluntario del usuario actual"""
    try:
        volunteers_response = api_client.get_volunteers(size=1000)
        volunteers = volunteers_response.get('items', [])
        
        for volunteer in volunteers:
            if volunteer.get('user_id') == user['id']:
                return volunteer
        
        return None
    except Exception as e:
        st.error(f"Error al obtener tu perfil: {e}")
        return None

def show_profile_view(user: Dict, volunteer: Dict):
    """Muestra vista del perfil"""
    # Información personal
    st.markdown("## 📋 Información Personal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**👤 Nombre:** {user.get('name', 'N/A')}")
        st.write(f"**📧 Email:** {user.get('email', 'N/A')}")
    
    with col2:
        st.write(f"**📱 Teléfono:** {user.get('phone', 'N/A')}")
        st.write(f"**🎯 Estado Voluntario:** {status_badge(volunteer.get('status'))}")
    
    with col3:
        st.write(f"**📅 Nacimiento:** {user.get('birth_date', 'N/A')}")
        st.write(f"**📅 Miembro desde:** {format_date(user.get('created_at'))}")
    
    # Skills
    st.markdown("## 🛠️ Mis Skills")
    
    skills = volunteer.get('skills', [])
    
    if skills:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for skill in skills:
                with st.expander(f"🛠️ {skill.get('name', 'N/A')}"):
                    # Mostrar estadísticas de uso de esta skill
                    show_skill_usage_for_volunteer(skill['id'], volunteer['id'])
        
        with col2:
            if st.button("➕ Añadir Skill"):
                st.session_state.add_skill_to_profile = True
                st.rerun()
    else:
        st.info("No tienes skills registradas")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Añadir mi primera Skill"):
                st.session_state.add_skill_to_profile = True
                st.rerun()
        
        with col2:
            if st.button("🎯 Explorar Skills"):
                st.info("Explora skills populares para añadir a tu perfil")
    
    # Estadísticas personales
    st.markdown("## 📊 Mis Estadísticas")
    
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if assignments:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_assignments = len(assignments)
                st.metric("📋 Total Asignaciones", total_assignments)
            
            with col2:
                completed = len([a for a in assignments if a.get('status') == 'completed'])
                st.metric("✅ Completadas", completed)
            
            with col3:
                active = len([a for a in assignments if a.get('status') == 'accepted'])
                st.metric("🔄 Activas", active)
            
            with col4:
                pending = len([a for a in assignments if a.get('status') == 'pending'])
                st.metric("⏳ Pendientes", pending)
            
            # Skills más usadas
            if skills:
                st.subheader("🛠️ Mis Skills Más Usadas")
                
                skill_usage = {}
                for assignment in assignments:
                    skill_name = assignment.get('skill', {}).get('name', 'Unknown')
                    skill_usage[skill_name] = skill_usage.get(skill_name, 0) + 1
                
                if skill_usage:
                    for skill_name, count in skill_usage.items():
                        st.write(f"**{skill_name}:** {count} asignaciones")
                else:
                    st.info("Aún no has usado tus skills en asignaciones")
        
        else:
            st.info("No tienes asignaciones para mostrar estadísticas")
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    # Acciones
    st.markdown("## ⚡ Acciones Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Editar Perfil"):
            st.session_state.edit_profile = True
            st.rerun()
    
    with col2:
        if st.button("📋 Ver Mis Asignaciones"):
            st.session_state.page = "assignments"
            st.rerun()
    
    with col3:
        if st.button("🎯 Buscar Proyectos"):
            st.session_state.page = "projects"
            st.rerun()
    
    with col4:
        if st.button("🔙 Volver al Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

def show_edit_profile(user: Dict, volunteer: Dict):
    """Formulario para editar perfil"""
    st.markdown("## ✏️ Editar Mi Perfil")
    
    with st.form("edit_profile_form"):
        st.subheader("📋 Información Personal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nombre Completo *",
                value=user.get('name', ''),
                key="edit_name"
            )
            email = st.text_input(
                "Email *",
                value=user.get('email', ''),
                key="edit_email"
            )
        
        with col2:
            phone = st.text_input(
                "Teléfono",
                value=user.get('phone', ''),
                key="edit_phone"
            )
            birth_date = st.date_input(
                "Fecha de Nacimiento",
                value=user.get('birth_date', '2000-01-01'),
                key="edit_birth_date"
            )
        
        # Estado de voluntario
        st.subheader("🤝 Estado de Voluntario")
        
        status_options = ["active", "inactive", "suspended"]
        current_status = st.selectbox(
            "Estado",
            options=status_options,
            index=status_options.index(volunteer.get('status', 'active')),
            key="edit_status"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("🔙 Cancelar")
        
        if submitted:
            try:
                # Actualizar usuario
                user_data = {
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'birth_date': birth_date.isoformat()
                }
                
                api_client.update_user(user['id'], user_data)
                
                # Actualizar estado de voluntario
                volunteer_data = {
                    'status': current_status
                }
                
                api_client.update_volunteer(volunteer['id'], volunteer_data)
                
                st.success("✅ Perfil actualizado exitosamente")
                st.session_state.edit_profile = None
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error al actualizar perfil: {e}")
        
        if cancelled:
            st.session_state.edit_profile = None
            st.rerun()

def show_add_skill():
    """Formulario para añadir skill al perfil"""
    st.markdown("## ➕ Añadir Skill a Mi Perfil")
    
    try:
        # Obtener skills disponibles
        skills_response = api_client.get_skills(size=1000)
        all_skills = skills_response.get('items', [])
        
        # Obtener voluntario actual
        user = auth.get_current_user()
        volunteer = get_my_volunteer(user)
        
        if not volunteer:
            st.error("No se encontró tu perfil de voluntario")
            return
        
        # Obtener skills actuales del voluntario
        current_skills = volunteer.get('skills', [])
        current_skill_ids = [s['id'] for s in current_skills]
        
        # Filtrar skills no asignadas aún
        available_skills = [s for s in all_skills if s['id'] not in current_skill_ids]
        
        if available_skills:
            skill_options = {s['name']: s['id'] for s in available_skills}
            selected_skill_name = st.selectbox(
                "Seleccionar Skill",
                options=list(skill_options.keys())
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("➕ Añadir Skill", type="primary"):
                    try:
                        api_client.add_skill_to_volunteer(volunteer['id'], skill_options[selected_skill_name])
                        st.success("✅ Skill añadida exitosamente")
                        st.session_state.add_skill_to_profile = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al añadir skill: {e}")
            
            with col2:
                if st.button("🔙 Cancelar"):
                    st.session_state.add_skill_to_profile = None
                    st.rerun()
            
            # Mostrar información de la skill seleccionada
            selected_skill = next(s for s in available_skills if s['name'] == selected_skill_name)
            
            st.markdown("### 📊 Información de la Skill")
            st.write(f"**🛠️ Nombre:** {selected_skill.get('name', 'N/A')}")
            st.write(f"**🆔 ID:** {selected_skill.get('id', 'N/A')}")
            st.write(f"**📅 Creada:** {format_date(selected_skill.get('created_at'))}")
            
            # Mostrar proyectos que requieren esta skill
            try:
                projects_response = api_client.get_projects(size=1000)
                projects = projects_response.get('items', [])
                
                projects_with_skill = [
                    p for p in projects 
                    if any(s.get('id') == selected_skill['id'] for s in p.get('skills', []))
                ]
                
                if projects_with_skill:
                    st.write(f"**📋 Usada en {len(projects_with_skill)} proyectos:**")
                    
                    for project in projects_with_skill[:5]:  # Mostrar solo primeros 5
                        st.write(f"• {project.get('name', 'N/A')} - {status_badge(project.get('status'))}")
                    
                    if len(projects_with_skill) > 5:
                        st.write(f"... y {len(projects_with_skill) - 5} más")
                else:
                    st.info("Esta skill no está siendo usada en proyectos actualmente")
            
            except Exception as e:
                st.error(f"Error al cargar información de proyectos: {e}")
        
        else:
            st.info("Ya tienes todas las skills disponibles registradas")
            if st.button("🔙 Volver"):
                st.session_state.add_skill_to_profile = None
                st.rerun()
    
    except Exception as e:
        st.error(f"Error al cargar skills: {e}")

def confirm_remove_skill():
    """Confirma eliminación de skill"""
    skill_to_remove = st.session_state.get('remove_skill')
    
    st.markdown(f"## ❌ Eliminar Skill: {skill_to_remove.get('name', 'N/A')}")
    
    st.warning("⚠️ **Atención:** Esta acción eliminará la skill de tu perfil y podría afectar tus asignaciones actuales y futuras.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Confirmar Eliminación", type="primary"):
            try:
                user = auth.get_current_user()
                volunteer = get_my_volunteer(user)
                
                if volunteer:
                    api_client.remove_skill_from_volunteer(volunteer['id'], skill_to_remove['id'])
                    st.success("✅ Skill eliminada exitosamente")
                    st.session_state.remove_skill = None
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error al eliminar skill: {e}")
    
    with col2:
        if st.button("🔙 Cancelar"):
            st.session_state.remove_skill = None
            st.rerun()

def show_skill_usage_for_volunteer(skill_id: int, volunteer_id: int):
    """Muestra estadísticas de uso de una skill específica para el voluntario"""
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer_id)
        assignments = assignments_response.get('items', [])
        
        # Filtrar asignaciones que usan esta skill
        skill_assignments = [
            a for a in assignments 
            if a.get('skill', {}).get('id') == skill_id
        ]
        
        if skill_assignments:
            st.write(f"**📊 Usada en {len(skill_assignments)} asignaciones:**")
            
            for assignment in skill_assignments:
                project = assignment.get('project', {})
                st.write(f"• {project.get('name', 'N/A')} - {status_badge(assignment.get('status'))}")
            
            # Botón para eliminar
            if st.button("❌", key=f"remove_{skill_id}", help="Eliminar esta skill"):
                skill_data = {'id': skill_id, 'name': assignment.get('skill', {}).get('name', 'N/A')}
                st.session_state.remove_skill = skill_data
                st.rerun()
        else:
            st.write("Aún no has usado esta skill en asignaciones")
            if st.button("❌", key=f"remove_{skill_id}", help="Eliminar esta skill"):
                skill_data = {'id': skill_id}
                st.session_state.remove_skill = skill_data
                st.rerun()
    
    except Exception as e:
        st.error(f"Error al cargar uso de skill: {e}")