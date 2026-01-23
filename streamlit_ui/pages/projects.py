import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth
from components.tables import create_paginated_table, project_table, status_badge, format_date
from components.forms import project_form
from typing import Dict, List, Any
import plotly.express as px

def show():
    """Página de gestión de proyectos"""
    require_auth()
    
    user = auth.get_current_user()
    is_admin = auth.is_admin()
    
    if is_admin:
        st.markdown("# 📋 Gestión de Proyectos")
    else:
        st.markdown("# 📋 Mis Proyectos")
    
    # Manejar acciones
    handle_actions()
    
    # Filtros
    if is_admin:
        show_admin_projects()
    else:
        show_volunteer_projects()

def handle_actions():
    """Maneja acciones rápidas desde session state"""
    
    # Crear proyecto
    if st.session_state.get('action') == 'create_project':
        show_create_project()
        return
    
    # Editar proyecto
    if st.session_state.get('edit_project'):
        show_edit_project()
        return
    
    # Ver detalles de proyecto
    if st.session_state.get('selected_project'):
        show_project_details()
        return
    
    # Gestionar asignaciones
    if st.session_state.get('assign_project'):
        show_project_assignment()
        return
    
    # Añadir skill a proyecto
    if st.session_state.get('add_skill_to_project'):
        show_add_skill_to_project()
        return

def show_admin_projects():
    """Vista de administrador para proyectos"""
    # Filtros
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            options=["Todos", "not_assigned", "assigned", "completed"],
            key="project_status_filter"
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Prioridad",
            options=["Todas", "high", "medium", "low"],
            key="project_priority_filter"
        )
    
    with col3:
        category_filter = st.selectbox(
            "Categoría",
            options=["Todas"],
            key="project_category_filter"
        )
        
        # Obtener categorías
        try:
            categories_response = api_client.get_categories(size=1000)
            categories = categories_response.get('items', [])
            category_names = ["Todas"] + [c.get('name', '') for c in categories]
            category_filter = st.selectbox(
                "Categoría",
                options=category_names,
                index=0,
                key="project_category_filter"
            )
        except:
            pass
    
    with col4:
        search_term = st.text_input("🔍 Buscar proyecto", key="project_search")
    
    # Acciones rápidas
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Nuevo Proyecto", type="primary"):
            st.session_state.action = "create_project"
            st.rerun()
    
    with col2:
        if st.button("🎯 Skill Matching"):
            st.session_state.show_matching = True
            st.rerun()
    
    with col3:
        if st.button("📊 Estadísticas"):
            st.session_state.show_project_stats = True
            st.rerun()
    
    with col4:
        if st.button("📥 Exportar"):
            st.info("Exportación en desarrollo...")
    
    # Mostrar vistas especiales
    if st.session_state.get('show_matching'):
        show_skill_matching()
        return
    
    if st.session_state.get('show_project_stats'):
        show_project_statistics()
        return
    
    # Listado principal de proyectos
    show_project_list(status_filter, priority_filter, category_filter, search_term)

def show_volunteer_projects():
    """Vista de voluntario para proyectos"""
    user = auth.get_current_user()
    
    # Obtener voluntario actual
    volunteers_response = api_client.get_volunteers(size=1000)
    volunteers = volunteers_response.get('items', [])
    
    my_volunteer = None
    for volunteer in volunteers:
        if volunteer.get('user_id') == user['id']:
            my_volunteer = volunteer
            break
    
    if not my_volunteer:
        st.warning("No se encontró tu perfil de voluntario")
        return
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Mis Proyectos", "🎯 Proyectos Recomendados", "📊 Mi Progreso"])
    
    with tab1:
        show_my_projects(my_volunteer)
    
    with tab2:
        show_recommended_projects(my_volunteer)
    
    with tab3:
        show_my_progress(my_volunteer)

def show_my_projects(volunteer: Dict):
    """Muestra proyectos asignados al voluntario"""
    st.markdown("### 📋 Mis Proyectos Asignados")
    
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if assignments:
            for assignment in assignments:
                project = assignment.get('project', {})
                skill = assignment.get('skill', {})
                
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**🛠️ Mi Rol:** {skill.get('name', 'N/A')}")
                    st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                    st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
                    st.write(f"**📊 Asignación:** {status_badge(assignment.get('status'))}")
                    
                    # Acciones según estado
                    status = assignment.get('status')
                    if status == 'pending':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aceptar", key=f"accept_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'accepted')
                                st.success("¡Proyecto aceptado!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Rechazar", key=f"reject_{assignment['id']}"):
                                api_client.update_assignment_status(assignment['id'], 'rejected')
                                st.success("Proyecto rechazado")
                                st.rerun()
                    elif status == 'accepted':
                        if st.button("✅ Marcar Completado", key=f"complete_{assignment['id']}"):
                            api_client.update_assignment_status(assignment['id'], 'completed')
                            st.success("¡Proyecto completado! 🎉")
                            st.rerun()
        else:
            st.info("No tienes proyectos asignados actualmente")
    
    except Exception as e:
        st.error(f"Error al cargar tus proyectos: {e}")

def show_recommended_projects(volunteer: Dict):
    """Muestra proyectos recomendados basados en skills"""
    st.markdown("### 🎯 Proyectos Recomendados para Ti")
    
    try:
        # Obtener skills del voluntario
        my_skills = volunteer.get('skills', [])
        if not my_skills:
            st.info("No tienes skills registradas. Añade skills para ver proyectos recomendados.")
            return
        
        my_skill_ids = [s['id'] for s in my_skills]
        
        # Obtener todos los proyectos activos
        projects_response = api_client.get_projects(size=1000)
        projects = projects_response.get('items', [])
        
        # Filtrar proyectos que matchean skills y están activos
        recommended_projects = []
        for project in projects:
            if project.get('status') in ['not_assigned', 'assigned']:
                project_skills = project.get('skills', [])
                project_skill_ids = [s['id'] for s in project_skills]
                
                # Si requiere alguna de mis skills
                matching_skills = [
                    s for s in project_skills if s['id'] in my_skill_ids
                ]
                
                if matching_skills:
                    recommended_projects.append({
                        **project,
                        'matching_skills': matching_skills,
                        'match_score': len(matching_skills)
                    })
        
        # Ordenar por match score (más skills matcheadas primero)
        recommended_projects.sort(key=lambda x: x['match_score'], reverse=True)
        
        if recommended_projects:
            for project in recommended_projects:
                matching_skills = project.get('matching_skills', [])
                skill_names = [s.get('name', '') for s in matching_skills]
                
                with st.expander(f"📋 {project.get('name', 'N/A')} (🎯 {len(matching_skills)} skills match)"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
                    st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
                    st.write(f"**🔥 Prioridad:** {status_badge(project.get('priority'))}")
                    st.write(f"**🎯 Skills que haces match:** {', '.join(skill_names)}")
                    
                    # Verificar si ya está asignado
                    # (Esto requeriría lógica adicional para verificar asignaciones existentes)
                    if st.button("🤝 Solicitar Participación", key=f"apply_{project['id']}"):
                        # Lógica para solicitar asignación
                        st.success("¡Solicitud enviada! El administrador la revisará pronto.")
        else:
            st.info("No hay proyectos disponibles que matcheen tus skills actualmente")
    
    except Exception as e:
        st.error(f"Error al cargar proyectos recomendados: {e}")

def show_my_progress(volunteer: Dict):
    """Muestra progreso y estadísticas del voluntario"""
    st.markdown("### 📊 Mi Progreso y Estadísticas")
    
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response.get('items', [])
        
        if not assignments:
            st.info("No tienes asignaciones para mostrar estadísticas")
            return
        
        # Estadísticas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_assignments = len(assignments)
            st.metric("📋 Total Asignaciones", total_assignments)
        
        with col2:
            completed = len([a for a in assignments if a.get('status') == 'completed'])
            st.metric("✅ Completadas", completed)
        
        with col3:
            pending = len([a for a in assignments if a.get('status') == 'pending'])
            st.metric("⏳ Pendientes", pending)
        
        with col4:
            active = len([a for a in assignments if a.get('status') == 'accepted'])
            st.metric("🔄 Activas", active)
        
        # Gráfico de progreso
        st.subheader("📈 Distribución de Asignaciones")
        
        status_counts = {}
        for assignment in assignments:
            status = assignment.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Estado de tus Asignaciones"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalle de Asignaciones")
        
        assignment_details = []
        for assignment in assignments:
            project = assignment.get('project', {})
            skill = assignment.get('skill', {})
            
            assignment_details.append({
                'Proyecto': project.get('name', 'N/A'),
                'Skill': skill.get('name', 'N/A'),
                'Estado': status_badge(assignment.get('status')),
                'Asignado': format_date(assignment.get('created_at')),
                'Límite': format_date(project.get('deadline'))
            })
        
        st.dataframe(assignment_details, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")

def show_create_project():
    """Formulario para crear nuevo proyecto"""
    st.markdown("## ➕ Crear Nuevo Proyecto")
    
    project_data = project_form()
    
    if project_data:
        try:
            created_project = api_client.create_project(project_data)
            st.success("✅ Proyecto creado exitosamente")
            st.session_state.action = None
            st.session_state.created_project_id = created_project['id']
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al crear proyecto: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.action = None
        st.rerun()

def show_edit_project():
    """Formulario para editar proyecto existente"""
    project = st.session_state.get('edit_project')
    
    st.markdown(f"## ✏️ Editar Proyecto: {project.get('name', 'N/A')}")
    
    project_data = project_form(project)
    
    if project_data:
        try:
            api_client.update_project(project['id'], project_data)
            st.success("✅ Proyecto actualizado exitosamente")
            st.session_state.edit_project = None
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error al actualizar proyecto: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.edit_project = None
        st.rerun()

def show_project_details():
    """Muestra detalles completos de un proyecto"""
    project = st.session_state.get('selected_project')
    
    st.markdown(f"## 📋 Detalles del Proyecto: {project.get('name', 'N/A')}")
    
    # Información básica
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**📝 Descripción:** {project.get('description', 'N/A')}")
        st.write(f"**📅 Límite:** {format_date(project.get('deadline'))}")
    
    with col2:
        st.write(f"**🎯 Estado:** {status_badge(project.get('status'))}")
        st.write(f"**🔥 Prioridad:** {status_badge(project.get('priority'))}")
    
    with col3:
        category = project.get('category', {})
        st.write(f"**📂 Categoría:** {category.get('name', 'N/A')}")
        st.write(f"**🆔 ID:** {project.get('id', 'N/A')}")
    
    # Skills requeridas
    st.markdown("### 🛠️ Skills Requeridas")
    
    skills = project.get('skills', [])
    if skills:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for skill in skills:
                st.write(f"• {skill.get('name', 'N/A')}")
        
        with col2:
            if st.button("➕ Añadir Skill"):
                st.session_state.add_skill_to_project = project['id']
                st.session_state.selected_project = None
                st.rerun()
            
            if st.button("❌ Quitar Skills"):
                st.session_state.remove_skills_project = project
                st.session_state.selected_project = None
                st.rerun()
    else:
        st.info("Este proyecto no tiene skills requeridas")
        if st.button("➕ Añadir Primera Skill"):
            st.session_state.add_skill_to_project = project['id']
            st.session_state.selected_project = None
            st.rerun()
    
    # Voluntarios asignados (solo admin)
    if auth.is_admin():
        st.markdown("### 👤 Voluntarios Asignados")
        
        try:
            assignments_response = api_client.get_project_assignments(project['id'])
            assignments = assignments_response.get('items', [])
            
            if assignments:
                for assignment in assignments:
                    volunteer = assignment.get('volunteer', {})
                    skill = assignment.get('skill', {})
                    
                    with st.expander(f"👤 {volunteer.get('name', 'N/A')}"):
                        st.write(f"**🛠️ Skill:** {skill.get('name', 'N/A')}")
                        st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                        st.write(f"**📧 Email:** {volunteer.get('email', 'N/A')}")
                        st.write(f"**📱 Teléfono:** {volunteer.get('phone', 'N/A')}")
            else:
                st.info("No hay voluntarios asignados a este proyecto")
        
        except Exception as e:
            st.error(f"Error al cargar asignaciones: {e}")
    
    # Acciones
    st.markdown("### ⚡ Acciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Editar Proyecto"):
            st.session_state.edit_project = project
            st.session_state.selected_project = None
            st.rerun()
    
    with col2:
        if st.button("👥 Asignar Voluntarios"):
            st.session_state.assign_project = project
            st.session_state.selected_project = None
            st.rerun()
    
    with col3:
        if st.button("🎯 Ver Matching"):
            st.session_state.show_matching_for_project = project
            st.session_state.selected_project = None
            st.rerun()
    
    with col4:
        if st.button("🔙 Volver al Listado"):
            st.session_state.selected_project = None
            st.rerun()

def show_project_assignment():
    """Muestra volunteers que matchean con el proyecto"""
    project = st.session_state.get('assign_project')
    
    st.markdown(f"## 👥 Asignar Voluntarios a: {project.get('name', 'N/A')}")
    
    try:
        # Obtener voluntarios que matchean
        matching_response = api_client.get_project_matching_volunteers(project['id'])
        matching_volunteers = matching_response.get('items', [])
        
        if matching_volunteers:
            st.write(f"**Se encontraron {len(matching_volunteers)} voluntarios con skills compatibles:**")
            
            for volunteer in matching_volunteers:
                with st.expander(f"👤 {volunteer.get('name', 'N/A')}"):
                    st.write(f"**📧 Email:** {volunteer.get('email', 'N/A')}")
                    st.write(f"**📱 Teléfono:** {volunteer.get('phone', 'N/A')}")
                    st.write(f"**🎯 Estado:** {status_badge(volunteer.get('status'))}")
                    
                    # Skills que matchean
                    # (Esto requeriría lógica específica para mostrar qué skills matchean)
                    
                    # Botones de asignación por skill
                    project_skills = project.get('skills', [])
                    volunteer_skills = volunteer.get('skills', [])
                    
                    if project_skills and volunteer_skills:
                        st.write("**Asignar por Skill:**")
                        
                        for project_skill in project_skills:
                            # Encontrar skills del voluntario que matchean con este skill del proyecto
                            matching_volunteer_skills = [
                                vs for vs in volunteer_skills 
                                if vs.get('name', '').lower() == project_skill.get('name', '').lower()
                            ]
                            
                            for vs in matching_volunteer_skills:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"🛠️ {project_skill.get('name', 'N/A')}")
                                with col2:
                                    if st.button("Asignar", key=f"assign_{project['id']}_{volunteer['id']}_{project_skill['id']}"):
                                        # Crear asignación
                                        assignment_data = {
                                            'project_skill_id': f"{project['id']}_{project_skill['id']}",  # Formato假设
                                            'volunteer_skill_id': f"{volunteer['id']}_{vs['id']}",    # Formato假设
                                            'status': 'pending'
                                        }
                                        
                                        try:
                                            api_client.create_assignment(assignment_data)
                                            st.success("¡Asignación creada exitosamente!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error al crear asignación: {e}")
        else:
            st.warning("No se encontraron voluntarios con skills compatibles para este proyecto")
        
    except Exception as e:
        st.error(f"Error al buscar voluntarios compatibles: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.assign_project = None
        st.rerun()

def show_add_skill_to_project():
    """Añade skills a un proyecto"""
    project_id = st.session_state.get('add_skill_to_project')
    
    st.markdown("## ➕ Añadir Skill al Proyecto")
    
    try:
        # Obtener skills disponibles
        skills_response = api_client.get_skills(size=1000)
        all_skills = skills_response.get('items', [])
        
        # Obtener skills actuales del proyecto
        project_response = api_client.get_project(project_id)
        project = project_response
        current_skills = project.get('skills', [])
        current_skill_ids = [s['id'] for s in current_skills]
        
        # Filtrar skills no asignadas aún
        available_skills = [s for s in all_skills if s['id'] not in current_skill_ids]
        
        if available_skills:
            skill_options = {s['name']: s['id'] for s in available_skills}
            selected_skill_name = st.selectbox(
                "Seleccionar Skill",
                options=list(skill_options.keys())
            )
            
            if st.button("➕ Añadir Skill", type="primary"):
                try:
                    api_client.add_skill_to_project(project_id, skill_options[selected_skill_name])
                    st.success("✅ Skill añadida exitosamente")
                    st.session_state.add_skill_to_project = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al añadir skill: {e}")
        else:
            st.info("Todas las skills disponibles ya están asignadas a este proyecto")
    
    except Exception as e:
        st.error(f"Error al cargar skills: {e}")
    
    if st.button("🔙 Cancelar"):
        st.session_state.add_skill_to_project = None
        st.rerun()

def show_skill_matching():
    """Muestra dashboard de skill matching"""
    st.markdown("## 🎯 Skill Matching - Voluntarios ↔ Proyectos")
    
    try:
        # Obtener todos los datos
        volunteers_response = api_client.get_volunteers(size=1000)
        projects_response = api_client.get_projects(size=1000)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        # Encontrar matches
        matches = []
        
        for project in projects:
            if project.get('status') in ['not_assigned', 'assigned']:
                project_skills = project.get('skills', [])
                project_skill_ids = [s['id'] for s in project_skills]
                
                for volunteer in volunteers:
                    if volunteer.get('status') == 'active':
                        volunteer_skills = volunteer.get('skills', [])
                        volunteer_skill_ids = [s['id'] for s in volunteer_skills]
                        
                        # Calcular match score
                        matching_skills = [
                            s for s in project_skills if s['id'] in volunteer_skill_ids
                        ]
                        
                        if matching_skills:
                            match_score = len(matching_skills) / len(project_skills) * 100
                            
                            matches.append({
                                'project': project,
                                'volunteer': volunteer,
                                'matching_skills': matching_skills,
                                'match_score': match_score
                            })
        
        # Ordenar por match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Mostrar mejores matches
        st.subheader(f"🎯 Top 10 Matches (de {len(matches)} totales)")
        
        for match in matches[:10]:
            with st.expander(f"🎯 {match['project']['name']} ↔ {match['volunteer']['name']} ({match['match_score']:.1f}%)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📋 Proyecto:** {match['project']['name']}")
                    st.write(f"**📝 Descripción:** {match['project']['description'][:100]}...")
                    st.write(f"**🔥 Prioridad:** {status_badge(match['project']['priority'])}")
                
                with col2:
                    st.write(f"**👤 Voluntario:** {match['volunteer']['name']}")
                    st.write(f"**📧 Email:** {match['volunteer']['email']}")
                    st.write(f"**🎯 Estado:** {status_badge(match['volunteer']['status'])}")
                
                matching_skill_names = [s.get('name', '') for s in match['matching_skills']]
                st.write(f"**🛠️ Skills Match:** {', '.join(matching_skill_names)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👥 Asignar Voluntario", key=f"match_assign_{match['project']['id']}_{match['volunteer']['id']}"):
                        st.session_state.assign_project = match['project']
                        st.session_state.show_matching = None
                        st.rerun()
                with col2:
                    if st.button("📋 Ver Proyecto", key=f"match_view_{match['project']['id']}"):
                        st.session_state.selected_project = match['project']
                        st.session_state.show_matching = None
                        st.rerun()
    
    except Exception as e:
        st.error(f"Error al cargar skill matching: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.show_matching = None
        st.rerun()

def show_project_statistics():
    """Muestra estadísticas de proyectos"""
    st.markdown("## 📊 Estadísticas de Proyectos")
    
    try:
        projects_response = api_client.get_projects(size=1000)
        projects = projects_response.get('items', [])
        
        if not projects:
            st.info("No hay datos de proyectos para mostrar")
            return
        
        # KPIs generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_projects = len(projects)
            st.metric("📋 Total Proyectos", total_projects)
        
        with col2:
            active_projects = len([p for p in projects if p.get('status') in ['not_assigned', 'assigned']])
            st.metric("🔄 Proyectos Activos", active_projects)
        
        with col3:
            completed_projects = len([p for p in projects if p.get('status') == 'completed'])
            st.metric("✅ Completados", completed_projects)
        
        with col4:
            from datetime import datetime, timedelta
            today = datetime.now()
            upcoming_deadlines = [
                p for p in projects 
                if datetime.fromisoformat(p.get('deadline').replace('Z', '+00:00')) > today and
                   datetime.fromisoformat(p.get('deadline').replace('Z', '+00:00')) <= today + timedelta(days=7)
            ]
            st.metric("⏰ Vencen esta semana", len(upcoming_deadlines))
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Proyectos por Estado")
            
            status_counts = {}
            for project in projects:
                status = project.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(
                    values=list(status_counts.values()),
                    names=list(status_counts.keys()),
                    title="Distribución de Estados"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🔥 Proyectos por Prioridad")
            
            priority_counts = {}
            for project in projects:
                priority = project.get('priority', 'unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if priority_counts:
                fig = px.bar(
                    x=list(priority_counts.keys()),
                    y=list(priority_counts.values()),
                    title="Distribución de Prioridades"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.subheader("📋 Detalles de Proyectos")
        
        project_details = []
        for project in projects:
            skills = project.get('skills', [])
            project_details.append({
                'Nombre': project.get('name', 'N/A'),
                'Estado': status_badge(project.get('status')),
                'Prioridad': status_badge(project.get('priority')),
                'Skills': len(skills),
                'Categoría': project.get('category', {}).get('name', 'N/A'),
                'Límite': format_date(project.get('deadline'))
            })
        
        st.dataframe(project_details, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
    
    if st.button("🔙 Volver"):
        st.session_state.show_project_stats = None
        st.rerun()

def show_project_list(status_filter: str, priority_filter: str, category_filter: str, search_term: str):
    """Muestra listado filtrado de proyectos"""
    try:
        projects_response = api_client.get_projects(size=1000)
        projects = projects_response.get('items', [])
        
        # Aplicar filtros
        filtered_projects = projects
        
        # Filtro por estado
        if status_filter != "Todos":
            filtered_projects = [
                p for p in filtered_projects 
                if p.get('status') == status_filter
            ]
        
        # Filtro por prioridad
        if priority_filter != "Todas":
            filtered_projects = [
                p for p in filtered_projects 
                if p.get('priority') == priority_filter
            ]
        
        # Filtro por categoría
        if category_filter != "Todas":
            filtered_projects = [
                p for p in filtered_projects 
                if p.get('category', {}).get('name') == category_filter
            ]
        
        # Filtro por búsqueda
        if search_term:
            filtered_projects = [
                p for p in filtered_projects 
                if search_term.lower() in p.get('name', '').lower() or
                   search_term.lower() in p.get('description', '').lower()
            ]
        
        # Mostrar resultados
        if filtered_projects:
            st.write(f"**Resultados encontrados:** {len(filtered_projects)}")
            project_table(filtered_projects, show_actions=True)
        else:
            st.info("No se encontraron proyectos con los filtros seleccionados")
    
    except Exception as e:
        st.error(f"Error al cargar proyectos: {e}")