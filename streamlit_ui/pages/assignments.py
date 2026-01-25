import streamlit as st
from components.api_client import api_client
from components.auth import auth, require_auth
from components.tables import create_paginated_table, assignment_table, status_badge, format_date
from typing import Dict, List, Any
import plotly.express as px

def show():
    """Página de gestión de asignaciones"""
    require_auth()
    
    user = auth.get_current_user()
    is_admin = auth.is_admin()
    
    if is_admin:
        st.markdown("# 📊 Gestión de Asignaciones")
        show_admin_assignments()
    else:
        st.markdown("# 📋 Mis Asignaciones")
        show_volunteer_assignments(user)

def show_admin_assignments():
    """Vista de administrador para gestionar asignaciones"""
    
    # KPIs generales (sin endpoint de todas las asignaciones)
    st.markdown("## 📊 Estadísticas Generales")
    
    try:
        # Opción 1: Mostrar mensaje informativo
        st.info("📊 Para ver estadísticas generales, selecciona un proyecto específico")
        
        # Opción 2: KPIs básicos de proyectos y voluntarios
        projects_response = api_client.get_projects(size=100)
        volunteers_response = api_client.get_volunteers(size=100)
        
        projects = projects_response.get('items', [])
        volunteers = volunteers_response.get('items', [])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Proyectos", len(projects))
        with col2:
            active_projects = len([p for p in projects if p.get('status') in ['not_assigned', 'assigned', 'in_progress']])
            st.metric("🔄 Proyectos Activos", active_projects)
        with col3:
            st.metric("👤 Voluntarios", len(volunteers))
        with col4:
            active_volunteers = len([v for v in volunteers if v.get('status') == 'active'])
            st.metric("✅ Voluntarios Activos", active_volunteers)
        
    except Exception as e:
        st.error(f"Error al cargar estadísticas básicas: {e}")
    
    # Filtros funcionales
    st.markdown("---")
    st.markdown("## 🔍 Filtros de Búsqueda")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            options=["Todos", "PENDING", "ACCEPTED", "REJECTED", "COMPLETED"],
            key="admin_status_filter"
        )
    
    with col2:
        # Obtener proyectos reales
        try:
            projects_response = api_client.get_projects(size=100)
            projects = projects_response.get('items', [])
            project_options = {p['name']: p['id'] for p in projects}
            selected_project_name = st.selectbox(
                "Proyecto",
                options=["Todos"] + list(project_options.keys()),
                key="admin_project_filter"
            )
            selected_project_id = None if selected_project_name == "Todos" else project_options[selected_project_name]
        except:
            selected_project_id = None
    
    with col3:
        search_term = st.text_input("🔍 Buscar voluntario...", key="admin_search")
    
    # Acciones principales
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Ver Matches", type="primary", key="btn_matches"):
            st.session_state.show_matching = True
            st.rerun()
    
    with col2:
        if st.button("➕ Crear Asignación Manual", type="primary", key="btn_manual"):
            st.session_state.create_manual = True
            st.rerun()
    
    # Vistas especiales
    if st.session_state.get('show_matching'):
        show_matching_interface()
        return
    
    if st.session_state.get('create_manual'):
        show_manual_assignment_creation()
        return
    
    # Listado de asignaciones filtrado
    show_admin_assignments_list(status_filter, selected_project_id, search_term)

def show_volunteer_assignments(user: Dict):
    """Vista de voluntario para sus asignaciones"""
    
    # Obtener voluntario actual
    try:
        volunteers_response = api_client.get_volunteers(size=100)
        volunteers = volunteers_response.get('items', [])
        
        my_volunteer = None
        for volunteer in volunteers:
            if volunteer.get('user_id') == user['id']:
                my_volunteer = volunteer
                break
        
        if not my_volunteer:
            st.warning("No se encontró tu perfil de voluntario")
            return
        
        # Pestañas funcionales
        tab1, tab2, tab3 = st.tabs(["📋 Mis Asignaciones", "📊 Mi Progreso", "🎯 Disponibles"])
        
        with tab1:
            show_my_assignments(my_volunteer)
        
        with tab2:
            show_volunteer_progress(my_volunteer)
        
        with tab3:
            show_available_projects(my_volunteer)
            
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def show_my_assignments(volunteer: Dict):
    """Muestra las asignaciones reales del voluntario"""
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response  # El endpoint ya devuelve la lista directamente
        
        if assignments:
            for assignment in assignments:
                project = assignment.get('project', {})
                skill = assignment.get('matched_skill', {})
                
                with st.expander(f"📋 {project.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**🛠️ Mi Rol:** {skill.get('name', 'N/A')}")
                    st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                    st.write(f"**📅 Asignado:** {format_date(assignment.get('created_at'))}")
                    
                    # Acciones según estado
                    status = assignment.get('status')
                    assignment_id = assignment.get('id')
                    
                    if status == 'PENDING':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Aceptar", key=f"accept_{assignment_id}"):
                                api_client.update_assignment_status(assignment_id, 'ACCEPTED')
                                st.success("¡Asignación aceptada!")
                                st.rerun()
                        with col2:
                            if st.button("❌ Rechazar", key=f"reject_{assignment_id}"):
                                api_client.update_assignment_status(assignment_id, 'REJECTED')
                                st.success("Asignación rechazada")
                                st.rerun()
                    
                    elif status == 'ACCEPTED':
                        if st.button("✅ Marcar Completado", key=f"complete_{assignment_id}"):
                            api_client.update_assignment_status(assignment_id, 'COMPLETED')
                            st.success("¡Asignación completada! 🎉")
                            st.rerun()
        else:
            st.info("No tienes asignaciones actualmente")
    
    except Exception as e:
        st.error(f"Error al cargar tus asignaciones: {e}")

def show_volunteer_progress(volunteer: Dict):
    """Muestra estadísticas reales del voluntario"""
    try:
        assignments_response = api_client.get_volunteer_assignments(volunteer['id'])
        assignments = assignments_response
        
        if not assignments:
            st.info("No hay asignaciones para mostrar estadísticas")
            return
        
        # Estadísticas reales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Asignaciones", len(assignments))
        
        with col2:
            completed = len([a for a in assignments if a.get('status') == 'COMPLETED'])
            st.metric("✅ Completadas", completed)
        
        with col3:
            pending = len([a for a in assignments if a.get('status') == 'PENDING'])
            st.metric("⏳ Pendientes", pending)
        
        with col4:
            active = len([a for a in assignments if a.get('status') == 'ACCEPTED'])
            st.metric("🔄 Activas", active)
        
        # Gráfico real de distribución
        status_counts = {}
        skill_counts = {}
        
        for assignment in assignments:
            # Contar por estado
            status = assignment.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Contar por skill
            skill_name = assignment.get('matched_skill', {}).get('name', 'Unknown')
            skill_counts[skill_name] = skill_counts.get(skill_name, 0) + 1
        
        # Gráfico de estados
        if status_counts:
            st.subheader("📈 Distribución por Estado")
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Estado de tus Asignaciones"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de skills más usadas
        if skill_counts:
            st.subheader("🛠️ Skills Más Utilizadas")
            fig = px.bar(
                x=list(skill_counts.values()),
                y=list(skill_counts.keys()),
                orientation='h',
                title="Frecuencia de Skills"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")

def show_available_projects(volunteer: Dict):
    """Muestra proyectos que matchean con las skills del voluntario"""
    st.info("🔍 Buscando proyectos que requieren tus skills...")
    
    try:
        # Obtener skills del voluntario
        volunteer_skills = volunteer.get('skills', [])
        if not volunteer_skills:
            st.warning("No tienes skills registradas. Añade skills para ver proyectos disponibles.")
            return
        
        # Obtener todos los proyectos activos
        projects_response = api_client.get_projects(size=100)
        projects = projects_response.get('items', [])
        
        # Buscar proyectos que requieran las skills del voluntario
        matching_projects = []
        volunteer_skill_ids = [s['id'] for s in volunteer_skills]
        
        for project in projects:
            project_skills = project.get('skills', [])
            
            # Si el proyecto requiere alguna de las skills del voluntario
            required_skill = None
            for project_skill in project_skills:
                if project_skill['id'] in volunteer_skill_ids:
                    required_skill = project_skill
                    break
            
            if required_skill:
                matching_projects.append({
                    'project': project,
                    'required_skill': required_skill
                })
        
        if matching_projects:
            st.write(f"**Se encontraron {len(matching_projects)} proyectos que requieren tus skills:**")
            
            for match in matching_projects:
                project = match['project']
                skill = match['required_skill']
                
                with st.expander(f"📋 {project.get('name', 'N/A')} - Necesita: {skill.get('name', 'N/A')}"):
                    st.write(f"**📝 Descripción:** {project.get('description', 'N/A')[:150]}...")
                    st.write(f"**🛠️ Skill Requerida:** {skill.get('name', 'N/A')}")
                    st.write(f"**🎯 Estado del Proyecto:** {status_badge(project.get('status'))}")
                    
                    # Botón para solicitar asignación (solo para admin, volunteers necesitan otro flujo)
                    if auth.is_admin():
                        if st.button("🤝 Asignar Voluntario", key=f"assign_{project['id']}_{skill['id']}"):
                            st.session_state.assign_project = project
                            st.session_state.assign_skill = skill
                            st.session_state.assign_volunteer = volunteer
                            st.rerun()
                    else:
                        st.info("Contacta a un administrador para solicitar esta asignación")
        else:
            st.info("No hay proyectos disponibles para tus skills en este momento")
    
    except Exception as e:
        st.error(f"Error al buscar proyectos: {e}")

def show_matching_interface():
    """Interfaz para ver matches entre proyectos y voluntarios"""
    st.markdown("## 🔍 Matching de Proyectos y Voluntarios")
    
    try:
        # Obtener todos los proyectos
        projects_response = api_client.get_projects(size=100)
        projects = projects_response.get('items', [])
        
        # Seleccionar proyecto
        project_options = {p['name']: p['id'] for p in projects}
        selected_project_name = st.selectbox(
            "Selecciona un proyecto para ver voluntarios matching:",
            options=list(project_options.keys()),
            key="match_project_select"
        )
        
        if selected_project_name:
            project_id = project_options[selected_project_name]
            
            # Obtener voluntarios que hacen match
            matching_volunteers = api_client.get_project_matching_volunteers(project_id)
            
            if matching_volunteers:
                st.write(f"**{len(matching_volunteers)} voluntarios hacen match con este proyecto:**")
                
                for volunteer in matching_volunteers:
                    with st.expander(f"👤 {volunteer.get('volunteer_name', 'N/A')}"):
                        st.write(f"**ID Voluntario:** {volunteer.get('volunteer_id', 'N/A')}")
                        
                        matched_skills = volunteer.get('matched_skills', [])
                        st.write("**Skills Matching:**")
                        for skill in matched_skills:
                            st.write(f"- {skill.get('name', 'N/A')}")
                        
                        # Botón para crear asignación
                        if st.button("🤝 Crear Asignación", key=f"match_{volunteer.get('volunteer_id')}"):
                            # Guardar información para el formulario de creación
                            st.session_state.create_from_match = {
                                'project_id': project_id,
                                'volunteer_id': volunteer.get('volunteer_id'),
                                'matched_skills': matched_skills
                            }
                            st.session_state.create_manual = True  # Redirigir al formulario manual
                            st.session_state.show_matching = False  # Cerrar vista de matching
                            st.rerun()
            else:
                st.info("No hay voluntarios que hagan match con este proyecto")
    
    except Exception as e:
        st.error(f"Error al buscar matches: {e}")
    
    # Botón para volver - ASEGURARSE DE QUE FUNCIONE
    if st.button("🔙 Volver a Gestión", key="back_from_matching"):
        st.session_state.show_matching = False
        st.rerun()

def show_manual_assignment_creation():
    """Formulario para crear asignación manualmente"""
    st.markdown("## ➕ Crear Asignación Manual")
    
    # Botón de volver al principio
    if st.button("🔙 Volver a Gestión", key="back_from_manual"):
        st.session_state.create_manual = False
        st.rerun()
    
    try:
        # Obtener datos necesarios
        volunteers_response = api_client.get_volunteers(size=100)
        projects_response = api_client.get_projects(size=100)
        
        volunteers = volunteers_response.get('items', [])
        projects = projects_response.get('items', [])
        
        # VALIDACIÓN ANTES DEL FORMULARIO
        if not volunteers:
            st.error("❌ No hay voluntarios disponibles en el sistema")
            return
        
        if not projects:
            st.error("❌ No hay proyectos disponibles en el sistema")
            return
        
        # Verificar si los proyectos tienen skills
        projects_with_skills = [p for p in projects if p.get('skills')]
        if not projects_with_skills:
            st.error("❌ No hay proyectos con skills registradas")
            return
        
        with st.form("create_assignment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Seleccionar proyecto (solo con skills)
                project_options = {p.get('name', ''): p for p in projects_with_skills}
                selected_project_name = st.selectbox(
                    "Proyecto *",
                    options=list(project_options.keys()),
                    key="project_select"
                )
                selected_project = project_options[selected_project_name]
                
                # Mostrar skills del proyecto
                project_skills = selected_project.get('skills', [])
                selected_skill = None
                
                if project_skills:
                    skill_options = {s.get('name', ''): s for s in project_skills}
                    selected_skill_name = st.selectbox(
                        "Skill Requerida *",
                        options=list(skill_options.keys()),
                        key="skill_select"
                    )
                    selected_skill = skill_options[selected_skill_name]
                else:
                    st.error("El proyecto no tiene skills registradas")
            
            with col2:
                # Seleccionar voluntario
                volunteer_options = {f"{v.get('name', '')} (ID:{v.get('id')})": v for v in volunteers}
                selected_volunteer_name = st.selectbox(
                    "Voluntario *",
                    options=list(volunteer_options.keys()),
                    key="volunteer_select"
                )
                selected_volunteer = volunteer_options[selected_volunteer_name]
                
                # Verificar si el voluntario tiene la skill requerida
                volunteer_skill = None
                volunteer_skills = selected_volunteer.get('skills', [])
                
                if selected_skill:
                    for vs in volunteer_skills:
                        if vs.get('id') == selected_skill.get('id'):
                            volunteer_skill = vs
                            break
                
                if selected_skill:
                    if volunteer_skill:
                        st.success(f"✅ El voluntario tiene la skill: {selected_skill.get('name')}")
                    else:
                        st.error(f"❌ El voluntario no tiene la skill: {selected_skill.get('name')}")
            
            # BOTONES SIEMPRE PRESENTES
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("💾 Crear Asignación", type="primary")
            
            with col2:
                cancelled = st.form_submit_button("🔙 Cancelar")
            
            # Lógica después del envío
            if submitted:
                if selected_skill and volunteer_skill:
                    try:
                        assignment_data = {
                            'project_skill_id': selected_skill.get('id'),
                            'volunteer_skill_id': volunteer_skill.get('id'),
                            'status': 'PENDING'
                        }
                        
                        result = api_client.create_assignment(assignment_data)
                        st.success("✅ Asignación creada exitosamente!")
                        st.session_state.create_manual = False
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error al crear asignación: {e}")
                else:
                    st.error("❌ No se puede crear la asignación - no hay match de skills")
            
            if cancelled:
                st.session_state.create_manual = False
                st.rerun()
    
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

def show_admin_assignments_list(status_filter, project_id, search_term):
    """Muestra listado de asignaciones con filtros"""
    
    if not project_id:
        st.info("🔍 Selecciona un proyecto para ver sus asignaciones")
        return
    
    try:
        # Obtener asignaciones solo del proyecto seleccionado
        assignments_response = api_client.get_project_assignments(project_id)
        assignments = assignments_response  # El endpoint ya devuelve la lista directamente
        
        # Aplicar filtros adicionales
        filtered_assignments = []
        
        for assignment in assignments:
            # Filtro por estado
            if status_filter != "Todos":
                if assignment.get('status') != status_filter:
                    continue
            
            # Filtro por búsqueda
            if search_term:
                volunteer = assignment.get('volunteer', {})
                volunteer_name = volunteer.get('user_name', '').lower()
                if search_term.lower() not in volunteer_name:
                    continue
            
            filtered_assignments.append(assignment)
        
        if filtered_assignments:
            st.write(f"**{len(filtered_assignments)} asignaciones encontradas:**")
            
            for assignment in filtered_assignments:
                project = assignment.get('project', {})
                volunteer = assignment.get('volunteer', {})
                skill = assignment.get('matched_skill', {})
                
                with st.expander(f"📋 {project.get('name', 'N/A')} - {volunteer.get('user_name', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**👤 Voluntario:** {volunteer.get('user_name', 'N/A')}")
                        st.write(f"**📋 Proyecto:** {project.get('name', 'N/A')}")
                    
                    with col2:
                        st.write(f"**🛠️ Skill:** {skill.get('name', 'N/A')}")
                        st.write(f"**🎯 Estado:** {status_badge(assignment.get('status'))}")
                    
                    with col3:
                        st.write(f"**📅 Creada:** {format_date(assignment.get('created_at'))}")
                        
                        # Acciones según estado
                        status = assignment.get('status')
                        assignment_id = assignment.get('id')
                        
                        if status == 'PENDING':
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("✅ Aprobar", key=f"admin_accept_{assignment_id}"):
                                    api_client.update_assignment_status(assignment_id, 'ACCEPTED')
                                    st.success("Asignación aprobada")
                                    st.rerun()
                            with col_btn2:
                                if st.button("❌ Rechazar", key=f"admin_reject_{assignment_id}"):
                                    api_client.update_assignment_status(assignment_id, 'REJECTED')
                                    st.error("Asignación rechazada")
                                    st.rerun()
                        
                        elif status == 'ACCEPTED':
                            if st.button("✅ Completar", key=f"admin_complete_{assignment_id}"):
                                api_client.update_assignment_status(assignment_id, 'COMPLETED')
                                st.success("Asignación completada")
                                st.rerun()
        else:
            st.info("No hay asignaciones que coincidan con los filtros")
    
    except Exception as e:
        st.error(f"Error al cargar asignaciones: {e}")