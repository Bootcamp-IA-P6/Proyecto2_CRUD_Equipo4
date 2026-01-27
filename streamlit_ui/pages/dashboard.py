import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth
from components.tables import status_badge, format_date
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show():
    """Dashboard principal adaptado según rol"""
    require_auth()
    
    user = auth.get_current_user()
    
    if auth.is_admin():
        show_admin_dashboard()
    else:
        show_volunteer_dashboard()

def show_admin_dashboard():
    """Dashboard para administrador"""
    st.markdown("# 📊 Dashboard de Administrador")
    
    # Obtener datos principales
    try:
        volunteers_response = api_client.get_volunteers(size=100)
        projects_response = api_client.get_projects(size=100)
        skills_response = api_client.get_skills(size=100)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        skills = skills_response.get('items', [])
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👤 Total Voluntarios", len(volunteers))
            
            # Activos
            active_volunteers = len([v for v in volunteers if v.get('status') == 'active'])
            st.metric("✅ Voluntarios Activos", active_volunteers)
        
        with col2:
            st.metric("📋 Total Proyectos", len(projects))
            
            # Activos
            active_projects = len([p for p in projects if p.get('status') in ['not_assigned', 'assigned']])
            st.metric("🔄 Proyectos Activos", active_projects)
        
        with col3:
            st.metric("🛠️ Total Skills", len(skills))
            
            # Skills más usadas
            skill_usage = {}
            for project in projects:
                for skill in project.get('skills', []):
                    skill_name = skill.get('name', 'Unknown')
                    skill_usage[skill_name] = skill_usage.get(skill_name, 0) + 1
            
            if skill_usage:
                most_used_skill = max(skill_usage, key=skill_usage.get)
                st.metric("🔥 Skill Más Popular", most_used_skill)
        
        with col4:
            # Proyectos por vencer
            today = datetime.now()
            upcoming_deadlines = [
            p for p in projects 
            if p.get('end_date') and
            datetime.fromisoformat(p.get('end_date').replace('Z', '+00:00')) > today and
               datetime.fromisoformat(p.get('end_date').replace('Z', '+00:00')) <= today + timedelta(days=7)
        ]
        st.metric("⏰ Próximos vencimientos", len(upcoming_deadlines))
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Estado de Proyectos")
            
            project_status = {}
            for project in projects:
                status = project.get('status', 'unknown')
                project_status[status] = project_status.get(status, 0) + 1
            
            if project_status:
                fig = px.pie(
                    values=list(project_status.values()),
                    names=list(project_status.keys()),
                    title="Distribución de Estados"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Voluntarios por Estado")
            
            volunteer_status = {}
            for volunteer in volunteers:
                status = volunteer.get('status', 'unknown')
                volunteer_status[status] = volunteer_status.get(status, 0) + 1
            
            if volunteer_status:
                fig = px.bar(
                    x=list(volunteer_status.keys()),
                    y=list(volunteer_status.values()),
                    title="Voluntarios por Estado"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Tablas recientes
        st.markdown("---")
        st.subheader("📋 Actividad Reciente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Proyectos Recientes**")
            recent_projects = sorted(
                projects, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )[:5]
            
            for project in recent_projects:
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"📝 {project.get('description', 'N/A')[:100]}...")
                    st.write(f"📅 Creado: {format_date(project.get('created_at'))}")
                    st.write(f"🎯 Estado: {status_badge(project.get('status'))}")
                    st.write(f"🔥 Prioridad: {status_badge(project.get('priority'))}")
        
        with col2:
            st.write("**Voluntarios Activos Recientes**")
            active_volunteers = [
                v for v in volunteers if v.get('status') == 'active'
            ]
            
            for volunteer in active_volunteers[:5]:
                with st.expander(f"👤 {volunteer.get('name', 'N/A')}"):
                    st.write(f"📧 {volunteer.get('email', 'N/A')}")
                    st.write(f"📱 {volunteer.get('phone', 'N/A')}")
                    
                    # Skills
                    skills = volunteer.get('skills', [])
                    if skills:
                        skill_names = [s.get('name', '') for s in skills[:3]]
                        st.write(f"🛠️ Skills: {', '.join(skill_names)}")
        
        # Quick Actions
        st.markdown("---")
        st.subheader("⚡ Acciones Rápidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Nuevo Proyecto", type="primary"):
                st.session_state.action = "create_project"
                st.rerun()
        
        with col2:
            if st.button("➕ Nuevo Voluntario", type="primary"):
                st.session_state.action = "create_volunteer"
                st.rerun()
        
        with col3:
            if st.button("➕ Nueva Skill"):
                st.session_state.action = "create_skill"
                st.rerun()
        
        with col4:
            if st.button("📊 Ver Asignaciones"):
                st.session_state.page = "assignments"
                st.rerun()
                
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def show_volunteer_dashboard():
    """Dashboard para voluntario"""
    user = auth.get_current_user()
    
    st.markdown(f"# 📊 Mi Dashboard - {user['name']}")
    
    try:
        # Ya tenemos los datos del usuario actual
        user_id = user['id']
        
        # Obtener información completa del usuario por si hay datos adicionales
        user_data = api_client.get_user(user_id)
        volunteer=api_client.get_volunteer(user_id)
        
        # Encontrar voluntario correspondiente al usuario actual
        volunteer_id = volunteer.get('id')
        
        
        if not volunteer:
            st.warning("No se encontró tu perfil de voluntario. Contacta al administrador.")
            if st.button("Crear Perfil de Voluntario"):
                st.session_state.action = "create_volunteer"
                st.rerun()
            return
        
        # Información personal
        st.markdown("## 👤 Mi Perfil")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Nombre:** {user['name']}")
            st.write(f"**Email:** {user['email']}")
        
        with col2:
            st.write(f"**Teléfono:** {user.get('phone', 'N/A')}")
            st.write(f"**Estado:** {status_badge(volunteer.get('status'))}")
        
        with col3:
            if st.button("✏️ Editar Perfil"):
                st.session_state.edit_profile = True
                st.rerun()
        
        # Skills
        skills_response = api_client.get_volunteer_skills(volunteer_id)
    
        skills = skills_response.get('skills', [])
        
        st.markdown("## 🛠️ Mis Skills")
        
        if skills:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                for skill in skills:
                    st.write(f"• {skill.get('name', 'N/A')}")
            
            with col2:
                if st.button("➕ Añadir Skill"):
                    st.session_state.add_skill = True
                    st.rerun()
        else:
            st.info("No tienes skills registradas. ¡Añade algunas para poder participar en proyectos!")
            if st.button("➕ Añadir mi primera Skill"):
                st.session_state.add_skill = True
                st.rerun()
        
        # Mis Asignaciones
        st.markdown("## 📋 Mis Asignaciones")
        
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if assignments:
            for assignment in assignments:
                with st.expander(f"📋 {assignment.get('project', {}).get('name', 'N/A')}"):
                    project = assignment.get('project', {})
                    skill = assignment.get('skill', {})
                    
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:100]}...")
                    st.write(f"**🛠️ Skill:** {skill.get('name', 'N/A')}")
                    st.write(f"**📅 Asignado:** {format_date(assignment.get('created_at'))}")
                    st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                    
                    # Acciones según estado
                    status = assignment.get('status')
                    if status == 'pending':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aceptar", key=f"accept_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'accepted')
                                st.rerun()
                        with col2:
                            if st.button("❌ Rechazar", key=f"reject_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'rejected')
                                st.rerun()
                    elif status == 'accepted':
                        if st.button("✅ Marcar Completado", key=f"complete_{assignment['id']}"):
                            api_client.update_assignment_status(assignment['id'], 'completed')
                            st.rerun()
        else:
            st.info("No tienes asignaciones activas.")
        
        # Proyectos Disponibles (basado en skills)
        if skills:
            st.markdown("## 🎯 Proyectos Recomendados")
            
            projects_response = api_client.get_projects(size=100)
            all_projects = projects_response.get('items', [])
            
            # Filtrar proyectos que matchean mis skills
            my_skill_ids = [s['id'] for s in skills]
            recommended_projects = []
            
            for project in all_projects:
                project_skills = project.get('skills', [])
                project_skill_ids = [s['id'] for s in project_skills]
                
                # Si el proyecto requiere alguna de mis skills y está activo
                if (project.get('status') in ['not_assigned', 'assigned'] and
                    any(skill_id in my_skill_ids for skill_id in project_skill_ids)):
                    recommended_projects.append(project)
            
            if recommended_projects:
                for project in recommended_projects[:5]:  # Máximo 5 recomendaciones
                    with st.expander(f"📋 {project.get('name', 'N/A')}"):
                        st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:100]}...")
                        st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                        st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
                        st.write(f"**🔥 Prioridad:** {status_badge(project.get('priority'))}")
                        
                        # Skills requeridas que matchean
                        project_skills = project.get('skills', [])
                        matching_skills = [
                            s for s in project_skills if s['id'] in my_skill_ids
                        ]
                        
                        if matching_skills:
                            skill_names = [s.get('name', '') for s in matching_skills]
                            st.write(f"**🎯 Skills que haces match:** {', '.join(skill_names)}")
                        
                        # Botón para solicitar asignación
                        if st.button("🤝 Solicitar Participación", key=f"apply_{project['id']}"):
                            # Lógica para crear asignación
                            st.success("¡Solicitud enviada! El administrador la revisará pronto.")
            
    except Exception as e:
        st.error(f"Error al cargar tu dashboard: {e}")